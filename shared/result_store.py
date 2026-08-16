_store: dict[str, dict] = {}


def get(article_id: str) -> dict | None:
    return _store.get(article_id)


def save(article_id: str, **fields) -> None:
    record = _store.setdefault(article_id, {})
    record.update(fields)


if __name__ == "__main__":
    print(get("nonexistent"))

    save("a1", status="VERIFYING", claims=["c1", "c2"])
    print(get("a1"))

    save("a1", status="DONE", report="fake report")
    print(get("a1"))
