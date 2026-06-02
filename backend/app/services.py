import json
import logging
from copy import deepcopy
from pathlib import Path
from fastapi import HTTPException
from pydantic import ValidationError
from app.constants import ItemStatus, RiskLevel, CustomerTier, ReviewAction
from app.schemas import ReviewItemIngestSchema

logger = logging.getLogger("queue_ingestion")
DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "review_items.json"


def load_seed_items() -> list[dict]:
    """
    Reads the raw records from the local seed JSON file and pipes them
    sequentially through the Pydantic ingestion model. It filters out
    unrecoverable row setups without dropping execution context.

    Arguments:
        None

    Returns:
        list[dict]: An array of cleaned, type-validated data structures.
    """
    with DATA_FILE.open() as file:
        raw_data = json.load(file)

    cleaned_items = []
    for raw_item in raw_data:
        try:
            validated_item = ReviewItemIngestSchema(**raw_item)
            cleaned_items.append(validated_item.model_dump())
        except ValidationError as e:
            logger.error(f"Skipping record due to schema mismatch: {e}")
            continue
    return cleaned_items


# State Cache initialization
ITEMS: list[dict] = load_seed_items()


def find_item(item_id: str) -> dict:
    """
    Iterates through the active in-memory list cache to locate an entry
    matching the provided ID.

    Arguments:
        item_id (str): The absolute target identification token.

    Returns:
        dict: The matching operational reference dictionary.

    Raises:
        HTTPException (404): If the element does not exist.
    """
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Review item not found")


def status_for_action(action: ReviewAction) -> ItemStatus:
    """
    Resolves an administrative string instruction down to its absolute
    structural terminal Enum state using Python pattern matching.

    Arguments:
        action (ReviewAction): The action payload identifier string.

    Returns:
        ItemStatus: The appropriate target Enum variant object.
    """
    match action:
        case "approve":
            return ItemStatus.APPROVED
        case "reject":
            return ItemStatus.REJECTED
        case "escalate":
            return ItemStatus.ESCALATED
        case _:
            return ItemStatus.IN_REVIEW
