import sys
from pathlib import Path

from pipeline import run_fact_check

if __name__ == "__main__":
    if len(sys.argv) > 1:
        article_path = sys.argv[1]
    else:
        article_path = Path(__file__).parent / "sample_article.txt"

    article_text = Path(article_path).read_text(encoding="utf-8")
    report = run_fact_check(article_text)

    print(report.model_dump_json(indent=2))
    print()
    print(report.summary)
