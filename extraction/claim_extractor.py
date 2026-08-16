from pathlib import Path

from common.gemini_client import generate_content
from extraction.prompts import build_extraction_prompt
from shared.models import Claim
from shared.retry import call_with_backoff


def extract_claims(article_text: str) -> list[Claim]:
    prompt = build_extraction_prompt(article_text)
    response = call_with_backoff(
        generate_content,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Claim],
        },
    )
    return response.parsed


if __name__ == "__main__":
    article_text = (Path(__file__).parent / "sample_article.txt").read_text(encoding="utf-8")
    claims = extract_claims(article_text)

    for claim in claims:
        print(claim.model_dump_json(indent=2))
        print(f"  span text: {article_text[claim.span_start:claim.span_end]!r}")
        print()

    print(f"Extracted {len(claims)} claims.")
