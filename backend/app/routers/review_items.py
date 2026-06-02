from copy import deepcopy

from fastapi import APIRouter, HTTPException

import app.services as svc
from app.constants import CustomerTier, ItemStatus, RiskLevel
from app.schemas import ActionRequest, ItemResponse, QueueResponse

router = APIRouter()


@router.post("/dev/reset", response_model=QueueResponse)
async def reset_items():
    """
    Triggers a cache wipe on the backend memory pipeline and re-seeds
    state values directly from disk.

    Arguments:
        None

    Returns:
        dict: A dictionary containing the newly reset list of items under the 'items' key.
    """
    svc.ITEMS = svc.load_seed_items()
    return {"items": deepcopy(svc.ITEMS)}


@router.get("/review-items", response_model=QueueResponse)
async def list_review_items(active_only: bool = True):
    """
    Retrieves and processes cached list workflows, selectively excluding
    closed states if requested, and ranks items according to the three-tier
    priority matrix.

    Arguments:
        active_only (bool): Toggles filtering of closed/terminal entries. Defaults to True.

    Returns:
        dict: A dictionary containing the sorted list of items under the 'items' key.
    """
    items = deepcopy(svc.ITEMS)

    if active_only:
        terminal_states = {
            ItemStatus.APPROVED.value,
            ItemStatus.REJECTED.value,
            ItemStatus.ESCALATED.value,
        }
        items = [item for item in items if item.get("status") not in terminal_states]

    risk_map = {
        ItemStatus.UNKNOWN.value: 0,
        RiskLevel.LOW.value: 1,
        RiskLevel.MEDIUM.value: 2,
        RiskLevel.HIGH.value: 3,
    }
    tier_map = {CustomerTier.STANDARD.value: 1, CustomerTier.PRIORITY.value: 2}

    items.sort(
        key=lambda x: (
            -risk_map.get(x.get("risk_level", "low"), 0),
            -tier_map.get(x.get("customer_tier", "standard"), 0),
            x.get("submitted_at", ""),
        )
    )
    return {"items": items}


@router.get("/review-items/{item_id}", response_model=ItemResponse)
async def get_review_item(item_id: str):
    """
    Pulls a copy of a distinct operational entry from storage.

    Arguments:
        item_id (str): Target identifier variable parameter.

    Returns:
        dict: A dictionary containing the matched entry object under the 'item' key.
    """
    item = svc.find_item(item_id)
    return {"item": deepcopy(item)}


@router.post("/review-items/{item_id}/actions", response_model=ItemResponse)
async def apply_action(item_id: str, request: ActionRequest):
    """
    Implements backend state-machine execution rules over active items,
    checking for invalid transitions before confirming changes.

    Arguments:
        item_id (str): Target identifier variable parameter.
        request (ActionRequest): The verified payload context schema.

    Returns:
        dict: A dictionary containing the updated object entry under the 'item' key.

    Raises:
        HTTPException (400): On non-compliant workflow steps.
    """
    item = svc.find_item(item_id)
    current_status = item.get("status", ItemStatus.UNASSIGNED.value)

    if request.action == "claim":
        if current_status != ItemStatus.UNASSIGNED.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot claim item. Item is currently '{current_status}', must be 'unassigned'.",
            )
        item["status"] = ItemStatus.IN_REVIEW.value
        item["assigned_reviewer"] = request.reviewer

    elif request.action in {"approve", "reject", "escalate"}:
        if current_status != ItemStatus.IN_REVIEW.value:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot perform action '{request.action}'. Item is currently '{current_status}', must be 'in_review'.",
            )
        item["status"] = svc.status_for_action(request.action).value
    else:
        raise HTTPException(
            status_code=400, detail="Unsupported or invalid action requested"
        )

    return {"item": deepcopy(item)}
