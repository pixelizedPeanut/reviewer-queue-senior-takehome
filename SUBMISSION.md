# Submission

## Summary of changes
* **State Machine Implementation:** Locked down state validation on the FastAPI backend to ensure workflow rules (`unassigned` $\rightarrow$ `in_review` $\rightarrow$ terminal) are strictly enforced at the API layer.
* **Algorithmic Queue Ordering:** Rebuilt the `/review-items` endpoint sorting logic to strictly rank items using the requested three-tier urgency structure: Risk Level (`high` > `medium` > `low`), Customer Tier (`priority` > `standard`), and submission age (oldest first).
* **Defensive UI Architecture:** Refactored the Vue 3 component to conditionally evaluate item metadata, dynamically disabling forbidden operations based on state and instantly ejecting terminal items from the active view.

## Bugs fixed
* **State-Defying Actions (Backend):** Fixed a bug where a reviewer could call an action like `approve` or `reject` on an item that was still `unassigned`, bypassing the operations sequence.
* **Double-Processing & Race Conditions (Frontend):** Implemented frontend button blocking using a computed `canProcess` state wrapper. This physically blocks a reviewer from clicking actions on terminal items or running into unexpected `400/409` errors from the server.
* **Double-Click Financial Overhead Guard:** Wrapped async operations in a `pendingAction` flag that disables all execution blocks during flight, preventing duplicate backend invocations and redundant API overhead.

## Product/UX decisions
* **Defensive Action Disabling:** Instead of letting users click buttons and receive unhelpful error banners after a network roundtrip, buttons are structurally disabled based on the active item state. This lowers cognitive overhead for operators.
* **Instant Terminal Ejection:** As soon as an item is marked as `approved`, `rejected`, or `escalated`, the Vue client instantly filters it out of the active list and shifts focus to the next item, mimicking a seamless, real-time pipeline.
* **Ownership Transparency:** Added a prominent lock indicator (`🔒 Locked by: Alex`) at the top of the detail panel when an item is claimed, making it unmistakable who owns the current liability.
* **Fail-Safe Ingestion Pipeline & Telemetry Isolation:** Designed the seed-data loading loop to selectively quarantine unrecoverable record schemas (`ValidationError`) rather than allowing corrupt historical mock data to cause catastrophic server-boot failure. These anomalies are handled gracefully at the boundary, preserving platform uptime for operators, while telemetry error payloads are routed out to an isolated, dedicated observability layer to be triaged independently without impacting runtime application logic.

## Tests added
* Added a comprehensive suite inside `backend/tests/test_workflow.py` to assert the state machine limits under test conditions.
* Specifically verifies that:
  1. An item cannot be approved/rejected unless it is explicitly `in_review`.
  2. Transitioning to a terminal state works flawlessly.
  3. Re-claiming a closed terminal item throws a strict `400 Bad Request`.

## Known Gaps

* **Concurrent Claim Race Conditions (Multi-User Collisions):** The system currently relies on state mutations over a centralized data array. In a live multi-reviewer operations center, if two operators simultaneously attempt to claim the same `unassigned` item, a race condition will occur. To mitigate this in production, the application requires atomic database transactions—such as a pessimistic locking mechanism (`SELECT FOR UPDATE NOWAIT`) or an explicit conditional update clause (`WHERE status = 'unassigned'`)—to ensure strict single-ownership lockouts.
* **Real-time Queue Synchronization:** The frontend queue updates rely entirely on pull-based HTTP fetch requests triggered by manual navigation or page reloads. If a separate team member alters an item's status, other active reviewers will be left looking at a stale screen. A robust production solution would introduce push-based architecture via Server-Sent Events (SSE) or WebSockets to broadcast lightweight state transitions across all operational dashboards instantly.
* **Audit Logging and Compliance Trailing:** The backend currently modifies item records in-place without preserving a history of operational velocity. In a true compliance/trust-and-safety landscape, fields cannot be altered without leaving a permanent audit trial. Introducing an Event Sourcing or dedicated Audit Log pattern is a required next step to track ownership historical timelines, escalation paths, and calculate operational SLAs (e.g., Average Time to Review).
* **Component-State Architecture Coupling:** To move rapidly within the timebox, the state management and direct API invocations are housed locally inside the root `App.vue` component. While perfectly operational for a standalone slice, this creates a heavy component. For production scalability and isolated testability, this domain logic should be abstracted away into a clean Vue 3 composable pattern or a global reactive Pinia state store (`useReviewQueueStore.ts`).

## Files changed and why
* `backend/app/main.py`: Enforced Pydantic payload parsing, implemented the dynamic three-tier queue sorting sequence, and locked backend routes behind explicit state validation rules.
* `frontend/src/App.vue`: Rewrote button layouts with conditional tracking state variables (`canClaim`, `canProcess`, `pendingAction`), configured terminal item removal tracking, and improved data element visibility.
* `backend/tests/test_workflow.py`: Written to assert compliance-grade correctness over item state progression.

## AI assistance used
* Used AI to fast-track type hinting on the legacy FastAPI routers and serialize the custom three-tier list sorting lambda expression. 
* Used AI to audit potential frontend race-conditions and verify that the Vue component accurately synchronized with the strict parameters mandated in the take-home prompt.
