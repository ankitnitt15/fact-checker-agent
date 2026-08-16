REPORT_SYNTHESIS_PROMPT = """You are a fact-checking editor writing a summary of findings.

Below is an article followed by the verified verdicts for each factual claim extracted from it.
Your job is to write a 2-4 sentence summary paragraph for a reader who wants to know:
- How many claims were checked
- How many were supported, refuted, or unverifiable
- Which refuted or unverifiable claims are most significant

Rules:
- Do not re-adjudicate any verdict -- treat all verdicts as final
- Do not quote the article verbatim
- Be concise and neutral in tone
- Return only the summary paragraph, no preamble

Article:
{article_text}

Verdicts:
{verdicts_json}
"""


def build_synthesis_prompt(article_text: str, verdicts_json: str) -> str:
    return REPORT_SYNTHESIS_PROMPT.format(article_text=article_text, verdicts_json=verdicts_json)
