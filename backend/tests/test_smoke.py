import asyncio

from app.main import health
from app.routers.review_items import list_review_items


def run_async(coro):
    return asyncio.run(coro)


def test_health_check() -> None:
    assert run_async(health()) == {"status": "ok"}


def test_review_items_endpoint_returns_seed_data() -> None:
    response = run_async(list_review_items())
    assert len(response["items"]) > 0
