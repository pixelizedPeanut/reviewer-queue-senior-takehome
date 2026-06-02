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

## Tests added
* Added a comprehensive suite inside `backend/tests/test_workflow.py` to assert the state machine limits under test conditions.
* Specifically verifies that:
  1. An item cannot be approved/rejected unless it is explicitly `in_review`.
  2. Transitioning to a terminal state works flawlessly.
  3. Re-claiming a closed terminal item throws a strict `400 Bad Request`.

## Known gaps
* **Real-time Synchronization:** If multiple operations specialists are in the tool simultaneously, the local Vue array will not reflect live changes until a hard refresh occurs. This should be solved via Server-Sent Events (SSE) or WebSockets.
* **Strict Type Enforcement on Ingestion:** Loosened the strict Pydantic Literal parsing on load to prevent crashes from corrupt historical mock files, leaving the state machine to reject bad incoming values during run-time validation.

## Files changed and why
* `backend/app/main.py`: Enforced Pydantic payload parsing, implemented the dynamic three-tier queue sorting sequence, and locked backend routes behind explicit state validation rules.
* `frontend/src/App.vue`: Rewrote button layouts with conditional tracking state variables (`canClaim`, `canProcess`, `pendingAction`), configured terminal item removal tracking, and improved data element visibility.
* `backend/tests/test_workflow.py`: Written to assert compliance-grade correctness over item state progression.

## AI assistance used
* Used AI to fast-track type hinting on the legacy FastAPI routers and serialize the custom three-tier list sorting lambda expression. 
* Used AI to audit potential frontend race-conditions and verify that the Vue component accurately synchronized with the strict parameters mandated in the take-home prompt.
