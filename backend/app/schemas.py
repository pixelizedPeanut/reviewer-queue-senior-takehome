from __future__ import annotations

import logging
from typing import List, Optional

from pydantic import BaseModel, ValidationError, field_validator

from app.constants import CustomerTier, ItemStatus, ReviewAction, RiskLevel

logger = logging.getLogger("queue_ingestion")


class ActionRequest(BaseModel):
    action: ReviewAction
    reviewer: str = "alex"


class ReviewItemIngestSchema(BaseModel):
    """Used strictly during JSON ingestion to cleanse data and prevent crashes."""

    id: str
    title: str
    status: ItemStatus
    risk_level: RiskLevel
    customer_tier: CustomerTier
    submitted_at: str
    assigned_reviewer: Optional[str] = None

    class Config:
        extra = "allow"

    @field_validator("status", mode="before")
    @classmethod
    def sanitize_status(cls, value: str) -> str:
        valid_statuses = {e.value for e in ItemStatus}
        if value not in valid_statuses:
            logger.warning(
                f"Corrupt status detected: '{value}'. Gracefully defaulting to 'unassigned'."
            )
            return ItemStatus.UNASSIGNED.value
        return value

    @field_validator("risk_level", mode="before")
    @classmethod
    def sanitize_risk(cls, value: str) -> str:
        valid_risks = {e.value for e in RiskLevel}
        if value not in valid_risks:
            logger.warning(
                f"Corrupt risk level detected: '{value}'. Gracefully defaulting to 'low'."
            )
            return RiskLevel.LOW.value
        return value


class ReviewItemResponse(BaseModel):
    """The strict contract returned to the web client frontend."""

    id: str
    status: ItemStatus
    risk_level: RiskLevel
    customer_tier: CustomerTier
    submitted_at: str
    assigned_reviewer: Optional[str] = None

    class Config:
        extra = "allow"
        from_attributes = True


class QueueResponse(BaseModel):
    items: List[ReviewItemResponse]


class ItemResponse(BaseModel):
    item: ReviewItemResponse
