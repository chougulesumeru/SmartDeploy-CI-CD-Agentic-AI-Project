# app/main.py — FastAPI with Prometheus metrics
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, make_asgi_app
import time

app = FastAPI(title="AI Code Reviewer")

# Define metrics
review_counter = Counter(
    "ai_reviews_total",
    "Total AI code reviews performed",
    ["status", "severity"]
)
review_duration = Histogram(
    "ai_review_duration_seconds",
    "Time spent on AI review"
)

# Mount /metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.post("/review")
async def review_endpoint(code_diff: str):
    start = time.time()
    try:
        result = review_code_with_ai("api_call", code_diff)
        review_counter.labels(
            status="success",
            severity=result.get("severity", "info")
        ).inc()
        return result
    except Exception as e:
        review_counter.labels(status="error", severity="none").inc()
        raise
    finally:
        review_duration.observe(time.time() - start)