import random
import time


def call_with_backoff(fn, *args, max_retries=2, base_delay=1.0, **kwargs):
    for attempt in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception:
            if attempt == max_retries:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)


if __name__ == "__main__":
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError(f"simulated failure #{calls['count']}")
        return "success"

    result = call_with_backoff(flaky, max_retries=3, base_delay=0.1)
    print(f"result: {result!r}, total calls made: {calls['count']}")
