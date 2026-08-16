import json

from common.gemini_client import generate_content
from reporting.prompts import build_synthesis_prompt
from shared.models import ClaimVerdict
from shared.retry import call_with_backoff


def synthesize_report(article_text: str, claim_verdicts: list[ClaimVerdict]) -> str:
    verdicts_json = json.dumps([cv.model_dump() for cv in claim_verdicts])
    prompt = build_synthesis_prompt(article_text, verdicts_json)
    response = call_with_backoff(generate_content, contents=prompt)
    return response.text


if __name__ == "__main__":
    article_text = "The Eiffel Tower was completed in 1889 and stands 330 meters tall."

    claim_verdicts = [
        ClaimVerdict(
            claim={"claim_id": "c1", "text": "The Eiffel Tower was completed in 1889.", "span_start": 0, "span_end": 0},
            final_verdict="SUPPORTED",
            confidence=0.95,
            reasoning="Well-documented historical fact.",
            source_votes={"SUPPORTED": 2},
        ),
        ClaimVerdict(
            claim={"claim_id": "c2", "text": "The Eiffel Tower is 330 meters tall.", "span_start": 0, "span_end": 0},
            final_verdict="SUPPORTED",
            confidence=0.9,
            reasoning="Matches known measurements.",
            source_votes={"SUPPORTED": 2},
        ),
        ClaimVerdict(
            claim={"claim_id": "c3", "text": "The Eiffel Tower is located in London.", "span_start": 0, "span_end": 0},
            final_verdict="REFUTED",
            confidence=0.98,
            reasoning="The Eiffel Tower is located in Paris, not London.",
            source_votes={"REFUTED": 2},
        ),
        ClaimVerdict(
            claim={"claim_id": "c4", "text": "The tower was designed by a committee of 12 engineers.", "span_start": 0, "span_end": 0},
            final_verdict="UNVERIFIABLE",
            confidence=0.0,
            reasoning="Insufficient successful verification samples.",
            source_votes={},
        ),
    ]

    summary = synthesize_report(article_text, claim_verdicts)
    print(summary)
