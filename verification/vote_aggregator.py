from collections import Counter

from shared.models import Claim, ClaimVerdict, VerificationResult

MIN_SUCCESS_RATIO = 0.6


def aggregate(claim: Claim, results: list[VerificationResult | None]) -> ClaimVerdict:
    successful = [r for r in results if r is not None]

    if len(successful) / len(results) < MIN_SUCCESS_RATIO:
        return ClaimVerdict(
            claim=claim,
            final_verdict="UNVERIFIABLE",
            confidence=0.0,
            reasoning="insufficient successful verification samples",
            source_votes=dict(Counter(r.verdict for r in successful)),
        )

    source_votes = Counter(r.verdict for r in successful)
    top_count = source_votes.most_common(1)[0][1]
    tied_verdicts = [verdict for verdict, count in source_votes.items() if count == top_count]

    if len(tied_verdicts) > 1:
        return ClaimVerdict(
            claim=claim,
            final_verdict="UNVERIFIABLE",
            confidence=0.0,
            reasoning="verification samples tied between multiple verdicts",
            source_votes=dict(source_votes),
        )

    final_verdict = tied_verdicts[0]
    agreeing = [r for r in successful if r.verdict == final_verdict]
    agg_confidence = sum(r.confidence for r in agreeing) / len(agreeing)

    best_result = agreeing[0]
    for r in agreeing:
        if r.confidence > best_result.confidence:
            best_result = r
    best_reasoning = best_result.reasoning

    return ClaimVerdict(
        claim=claim,
        final_verdict=final_verdict,
        confidence=agg_confidence,
        reasoning=best_reasoning,
        source_votes=dict(source_votes),
    )


if __name__ == "__main__":
    claim = Claim(claim_id="c1", text="dummy claim", span_start=0, span_end=0)

    def result(verdict, confidence, reasoning="dummy reasoning"):
        return VerificationResult(claim_id="c1", reasoning=reasoning, confidence=confidence, verdict=verdict)

    cases = {
        "all agree": [result("SUPPORTED", 0.9), result("SUPPORTED", 0.8), result("SUPPORTED", 0.95)],
        "2-1 split": [result("SUPPORTED", 0.9), result("SUPPORTED", 0.7), result("REFUTED", 0.6)],
        "1-1-1 tie": [result("SUPPORTED", 0.9), result("REFUTED", 0.8), result("UNVERIFIABLE", 0.5)],
        "mostly failures": [result("SUPPORTED", 0.9), None, None],
    }

    for name, results in cases.items():
        verdict = aggregate(claim, results)
        print(f"{name}: {verdict.model_dump_json()}")
