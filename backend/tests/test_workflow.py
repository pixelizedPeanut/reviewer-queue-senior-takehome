import app.services as svc
import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_terminal_state_enforcement() -> None:
    """
    Validates backend state machine boundaries via mock HTTP clients.
    Ensures that items must step through 'unassigned' -> 'in_review' -> 'terminal'
    sequentially, throwing 400 Bad Requests on illegal shortcuts.
    """
    # 1. Setup a clean mock item in our global state that is unassigned
    test_item = {
        "id": "test-lock-99",
        "title": "Test Item",
        "status": "unassigned",
        "risk_level": "high",
        "customer_tier": "standard",
        "submitted_at": "2026-06-01T12:00:00Z",
    }
    # Append to the list inside services where it now resides
    svc.ITEMS.append(test_item)

    # 2. Try to directly approve it without claiming it first (Should fail with 400)
    response = client.post(
        "/review-items/test-lock-99/actions",
        json={"action": "approve", "reviewer": "alex"},
    )
    assert response.status_code == 400
    assert "must be 'in_review'" in response.json()["detail"]

    # 3. Claim it successfully
    claim_resp = client.post(
        "/review-items/test-lock-99/actions",
        json={"action": "claim", "reviewer": "alex"},
    )
    assert claim_resp.status_code == 200
    assert claim_resp.json()["item"]["status"] == "in_review"

    # 4. Approve it successfully (moves to terminal state)
    approve_resp = client.post(
        "/review-items/test-lock-99/actions",
        json={"action": "approve", "reviewer": "alex"},
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["item"]["status"] == "approved"

    # 5. Try to claim an already approved terminal item (Should fail with 400)
    fail_resp = client.post(
        "/review-items/test-lock-99/actions",
        json={"action": "claim", "reviewer": "alex"},
    )
    assert fail_resp.status_code == 400
