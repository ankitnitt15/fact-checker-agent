from common.gemini_client import generate_content
from shared.models import Claim, VerificationResult
from shared.retry import call_with_backoff
from verification.prompts import build_verification_prompt

VERIFICATION_TEMPERATURE = 0.7
CONFIDENCE_FLOOR = 0.4

def verify_claim(claim: Claim, sample_index: int) -> VerificationResult:
    prompt = build_verification_prompt(claim.text)
    response = call_with_backoff(
        generate_content,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": VerificationResult,
            "temperature": VERIFICATION_TEMPERATURE,
        }
    )
    result = response.parsed
    result.claim_id = claim.claim_id  # the model is never told the real claim_id, so it fabricates one -- overwrite it
    if result.confidence < CONFIDENCE_FLOOR:
        result.verdict = "UNVERIFIABLE"

    return result


if __name__ == "__main__":
    true_claim = Claim(
        claim_id="t1",
        text="The Eiffel Tower is located in Paris, France.",
        span_start=0,
        span_end=0,
    )
    false_claim = Claim(
        claim_id="f1",
        text="The Eiffel Tower is located in London, England.",
        span_start=0,
        span_end=0,
    )

    # kept small (2 calls, not 3) to limit API spend during manual testing
    for claim in (true_claim, false_claim):
        print(f"--- claim: {claim.text} ---")
        for i in range(2):
            result = verify_claim(claim, i)
            print(f"sample {i}: {result.model_dump_json()}")
        print()