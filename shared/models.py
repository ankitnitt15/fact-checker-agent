# Task 2: Claim, VerificationResult, ClaimVerdict, ArticleStatus, Report (Pydantic models)
from pydantic import BaseModel
from typing import Literal

Verdict = Literal["SUPPORTED", "REFUTED", "UNVERIFIABLE"]
ArticleStatus = Literal["VERIFYING", "AGGREGATING", "DONE"]

class Claim(BaseModel):
    claim_id: str
    text: str
    span_start: int
    span_end: int

class VerificationResult(BaseModel):
    claim_id: str
    reasoning: str
    confidence: float
    verdict: Verdict

class ClaimVerdict(BaseModel):
    claim: Claim
    final_verdict: Verdict
    confidence: float
    reasoning: str
    source_votes: dict[str, int]

class Report(BaseModel):
    article_id: str
    claims_checked: int
    supported_count: int
    refuted_count: int
    unverifiable_count: int
    claim_verdicts: list[ClaimVerdict]
    summary: str


if __name__ == "__main__":
    claim = Claim(claim_id="c1", text="The Eiffel Tower was completed in 1889.", span_start=0, span_end=40)
    print(claim.model_dump_json(indent=2))

    result = VerificationResult(
        claim_id=claim.claim_id,
        reasoning="This is a well-documented historical fact.",
        confidence=0.95,
        verdict="SUPPORTED",
    )
    print(result.model_dump_json(indent=2))

    verdict = ClaimVerdict(
        claim=claim,
        final_verdict="SUPPORTED",
        confidence=0.95,
        reasoning="This is a well-documented historical fact.",
        source_votes={"SUPPORTED": 3},
    )
    print(verdict.model_dump_json(indent=2))

    report = Report(
        article_id="hash123",
        claims_checked=1,
        supported_count=1,
        refuted_count=0,
        unverifiable_count=0,
        claim_verdicts=[verdict],
        summary="1 claim was checked and found to be supported.",
    )
    print(report.model_dump_json(indent=2))

