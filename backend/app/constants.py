from enum import Enum
from typing import Literal

ReviewAction = Literal["claim", "approve", "reject", "escalate"]


class ItemStatus(str, Enum):
    UNASSIGNED = "unassigned"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class CustomerTier(str, Enum):
    PRIORITY = "priority"
    STANDARD = "standard"
