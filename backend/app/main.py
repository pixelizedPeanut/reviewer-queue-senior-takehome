from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import review_items

app = FastAPI(title="Reviewer Queue API")

if settings.is_development:
    # Only expose origin flexibility inside isolated developer sessions
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Production Mode: Zero cross-origin flexibility.
    # Assumes Frontend and Backend sit on the same domain, port, and path.
    pass

# Connect modular workspace routers cleanly
app.include_router(review_items.router)


@app.get("/health")
async def health() -> dict[str, str]:
    """
    Core diagnostic checkpoint checking if the app container responds correctly.

    Arguments:
        None

    Returns:
        dict[str, str]: Simple health verification status dictionary.
    """
    return {"status": "ok"}
