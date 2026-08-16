import concurrent.futures
import hashlib
from pathlib import Path

from extraction.claim_extractor import extract_claims
from reporting.report_synthesizer import synthesize_report
from shared import result_store
from shared.models import Claim, ClaimVerdict, Report, VerificationResult
from verification.verifier import verify_claim
from verification.vote_aggregator import aggregate

K_SAMPLES = 1
BATCH_SIZE = 5

def run_verification_batch(claims: list[Claim]) -> dict[str, list[VerificationResult | None]]:
    verification_tasks = [(claim, i) for claim in claims for i in range(K_SAMPLES)]

    results_by_claim: dict[str, list[VerificationResult | None]] = {claim.claim_id: [] for claim in claims}

    with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        future_to_task = {
            executor.submit(verify_claim, claim, i): (claim, i)
            for claim, i in verification_tasks
        }

        for future in concurrent.futures.as_completed(future_to_task):
            claim, sample_index = future_to_task[future]
            try:
                result = future.result()
            except Exception as e:
                print(f"sample {sample_index} for claim {claim.claim_id} failed: {e}")
                result = None
            results_by_claim[claim.claim_id].append(result)

    return results_by_claim


def run_fact_check(article_text: str) -> Report:
    article_id = hashlib.sha256(article_text.encode()).hexdigest()

    existing = result_store.get(article_id)
    if existing is not None and existing["status"] == "DONE":
        print(f"[{article_id[:8]}] cache hit -- returning stored report")
        return existing["report"]

    print(f"[{article_id[:8]}] extracting claims...")
    claims = extract_claims(article_text)
    result_store.save(article_id, claims=claims, status="VERIFYING")
    print(f"[{article_id[:8]}] extracted {len(claims)} claims")

    print(f"[{article_id[:8]}] verifying claims ({K_SAMPLES} sample(s) each)...")
    results_by_claim = run_verification_batch(claims)
    print(f"[{article_id[:8]}] verification complete")

    claim_verdicts: list[ClaimVerdict] = [
        aggregate(claim, results_by_claim[claim.claim_id]) for claim in claims
    ]
    result_store.save(article_id, verdicts=claim_verdicts, status="AGGREGATING")
    print(f"[{article_id[:8]}] aggregated verdicts for {len(claim_verdicts)} claims")

    print(f"[{article_id[:8]}] synthesizing report...")
    summary = synthesize_report(article_text, claim_verdicts)

    report = Report(
        article_id=article_id,
        claims_checked=len(claims),
        supported_count=sum(1 for cv in claim_verdicts if cv.final_verdict == "SUPPORTED"),
        refuted_count=sum(1 for cv in claim_verdicts if cv.final_verdict == "REFUTED"),
        unverifiable_count=sum(1 for cv in claim_verdicts if cv.final_verdict == "UNVERIFIABLE"),
        claim_verdicts=claim_verdicts,
        summary=summary,
    )
    result_store.save(article_id, report=report, status="DONE")
    print(f"[{article_id[:8]}] done")

    return report


if __name__ == "__main__":
    article_text = (Path(__file__).parent / "sample_article.txt").read_text(encoding="utf-8")

    report = run_fact_check(article_text)
    print(report.model_dump_json(indent=2))

    print("\n--- running again on the same article (should hit cache) ---")
    report_again = run_fact_check(article_text)
    print(report_again.model_dump_json(indent=2))
