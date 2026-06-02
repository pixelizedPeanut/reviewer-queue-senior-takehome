from __future__ import annotations

# import asyncio
import json
from copy import deepcopy
from pathlib import Path
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "review_items.json"

ReviewAction = Literal["claim", "approve", "reject", "escalate"]
ItemStatus = Literal["unassigned", "in_review", "approved", "rejected", "escalated"]
RiskLevel = Literal["high", "medium", "low"]
CustomerTier = Literal["priority", "standard"]


# --- PYDANTIC MODEL SCHEMAS (Type Safety Contracts) ---


# class ActionRequest(BaseModel):
#     action: ReviewAction
#     reviewer: str = "alex"


class ActionRequest(BaseModel):
    action: str  # Loosen literal checking here to let the state machine handle the 400
    reviewer: str = "alex"


class ReviewItemResponse(BaseModel):
    id: str
    status: str = "unassigned"  # Provide a fallback default string
    risk_level: str = "low"  # Provide a fallback default string
    customer_tier: str = "standard"
    submitted_at: str
    assigned_reviewer: Optional[str] = None

    class Config:
        extra = "allow"  # Do not choke on unexpected json properties
        from_attributes = True


# class ReviewItemResponse(BaseModel):
#     id: str
#     status: ItemStatus
#     risk_level: RiskLevel
#     customer_tier: CustomerTier
#     submitted_at: str
#     assigned_reviewer: Optional[str] = None
#     # If your JSON has other fields (like a description or payload),
#     # Pydantic will allow them if you use an extra config or define them here.

#     class Config:
#         extra = "allow"  # Ensures any hidden metadata fields don't get dropped


class QueueResponse(BaseModel):
    items: List[ReviewItemResponse]


class ItemResponse(BaseModel):
    item: ReviewItemResponse


# --- APP SETUP ---

app = FastAPI(title="Reviewer Queue API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_seed_items() -> list[dict]:
    with DATA_FILE.open() as file:
        return json.load(file)


ITEMS: list[dict] = load_seed_items()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/dev/reset", response_model=QueueResponse)
async def reset_items():
    global ITEMS
    ITEMS = load_seed_items()
    return {"items": deepcopy(ITEMS)}


# --- WORKFLOW & SORTING QUEUE ENGINE ---


@app.get("/review-items", response_model=QueueResponse)
async def list_review_items(active_only: bool = True):
    items = deepcopy(ITEMS)

    if active_only:
        # RULE: The active queue must completely exclude terminal items
        terminal_states = {"approved", "rejected", "escalated"}
        items = [item for item in items if item.get("status") not in terminal_states]

    # TAILORED AI-NATIVE PRIORITY ENGINE
    # 1. Map risk levels to clear sorting ranks
    risk_map = {"high": 3, "medium": 2, "low": 1}

    # 2. Map tiers so 'priority' sorting places it first
    tier_map = {"priority": 2, "standard": 1}

    # Sort hierarchy: Risk Level (Desc) -> Customer Tier (Desc) -> Submitted Timestamp (Asc, older first)
    items.sort(
        key=lambda x: (
            -risk_map.get(
                x.get("risk_level", "low"), 0
            ),  # Negative for descending order
            -tier_map.get(
                x.get("customer_tier", "standard"), 0
            ),  # Negative for descending order
            x.get(
                "submitted_at", ""
            ),  # String ISO timestamps sort perfectly ascending out-of-the-box
        )
    )

    return {"items": items}


@app.get("/review-items/{item_id}", response_model=ItemResponse)
async def get_review_item(item_id: str):
    item = find_item(item_id)
    return {"item": deepcopy(item)}


@app.post("/review-items/{item_id}/actions", response_model=ItemResponse)
async def apply_action(item_id: str, request: ActionRequest):
    item = find_item(item_id)
    current_status = item.get("status", "unassigned")

    # TAKEHOME: Structural Server-Side Enforcement of State Machine Rules
    if request.action == "claim":
        # Rule: Only items with status 'unassigned' can be claimed
        if current_status != "unassigned":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot claim item. Item is currently '{current_status}', must be 'unassigned'.",
            )
        item["status"] = "in_review"
        item["assigned_reviewer"] = request.reviewer

    elif request.action in {"approve", "reject", "escalate"}:
        # Rule: Only items with status 'in_review' can be processed
        if current_status != "in_review":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot perform action '{request.action}'. Item is currently '{current_status}', must be 'in_review'.",
            )

        # Rule: Route actions safely to their absolute terminal states
        item["status"] = status_for_action(request.action)

    else:
        raise HTTPException(
            status_code=400, detail="Unsupported or invalid action requested"
        )

    return {"item": deepcopy(item)}


# --- HELPER UTILITIES ---


def find_item(item_id: str) -> dict:
    for item in ITEMS:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Review item not found")


def status_for_action(action: ReviewAction) -> ItemStatus:
    if action == "approve":
        return "approved"
    if action == "reject":
        return "rejected"
    if action == "escalate":
        return "escalated"
    return "in_review"
