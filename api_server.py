"""FastAPI server exposing the NLP Query Understanding engine to the frontend.

Run with:
    uvicorn api_server:app --host 0.0.0.0 --port 8000
or:
    python api_server.py

The models are loaded once at startup (first run downloads them from HuggingFace).
Responses are shaped to match exactly what the Next.js UI components consume.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from data.sample_services import SAMPLE_SERVICES, SAMPLE_USER_PROFILES
from src.query_understanding import QueryUnderstandingSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_server")

# Holds the initialized engine. Populated on startup so the (heavy) model load
# happens once, not per request.
STATE: Dict[str, object] = {"system": None}

# Map optional user ids to the sample profiles for personalization demos.
USER_PROFILES = {p.user_id: p for p in SAMPLE_USER_PROFILES}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading Query Understanding System (this downloads models on first run)...")
    system = QueryUnderstandingSystem()
    system.load_services(SAMPLE_SERVICES)
    STATE["system"] = system
    logger.info("Engine ready. Loaded %d services.", len(SAMPLE_SERVICES))
    yield
    STATE["system"] = None


app = FastAPI(title="NLP Query Understanding API", version="1.0.0", lifespan=lifespan)

# Allow the Next.js dev server (and direct browser calls) to reach the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language search query")
    user_id: Optional[str] = Field(None, description="Optional sample user id for personalization")
    top_k: int = Field(6, ge=1, le=20, description="Number of ranked results to return")


def _price_label(price_range: Optional[int]) -> str:
    """Map a 1-4 price scale to a $-string; unknown -> '$$'."""
    if not price_range or price_range < 1:
        return "$$"
    return "$" * min(int(price_range), 4)


def _location_label(location: Optional[Tuple[float, float]]) -> str:
    """The sample dataset is all NYC; render a friendly label with coords."""
    if not location:
        return "Unknown"
    lat, lon = location
    return f"New York, NY ({lat:.3f}, {lon:.3f})"


def _to_ui_response(query: str, engine_result: dict, elapsed: float) -> dict:
    """Transform the engine's domain response into the UI-facing shape."""
    intent_raw = engine_result.get("intent", {})
    all_scores: Dict[str, float] = intent_raw.get("all_scores", {}) or {}
    primary = intent_raw.get("intent", "unknown")

    # Secondary intents = next best-scoring labels after the primary.
    secondary = [
        label
        for label, _score in sorted(all_scores.items(), key=lambda kv: kv[1], reverse=True)
        if label != primary
    ][:2]

    semantic_results: List[dict] = []
    rankings = {"semantic": [], "intent": [], "personalized": [], "location": []}

    for idx, item in enumerate(engine_result.get("results", []), start=1):
        service = item["service"]
        breakdown = item.get("score_breakdown", {})

        semantic_results.append(
            {
                "id": idx,
                "name": service.get("name", "Unknown"),
                "description": service.get("description", ""),
                "similarity": round(float(breakdown.get("semantic_similarity", 0.0)), 4),
                "category": (service.get("cuisine_type") or service.get("category") or "Service"),
                "location": _location_label(service.get("location")),
                "rating": service.get("rating") or 0,
                "price": _price_label(service.get("price_range")),
            }
        )

        rankings["semantic"].append(round(float(breakdown.get("semantic_similarity", 0.0)), 4))
        rankings["intent"].append(round(float(breakdown.get("intent_match", 0.0)), 4))
        rankings["personalized"].append(round(float(breakdown.get("user_preference", 0.0)), 4))
        rankings["location"].append(round(float(breakdown.get("location_proximity", 0.0)), 4))

    return {
        "query": query,
        "intent": {
            "primary": primary,
            "confidence": round(float(intent_raw.get("confidence", 0.0)), 4),
            "secondary": secondary,
        },
        "semanticResults": semantic_results,
        "rankings": rankings,
        "processingTime": round(elapsed, 3),
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "engine_ready": STATE["system"] is not None}


@app.get("/api/intents")
def list_intents() -> dict:
    system: QueryUnderstandingSystem = STATE["system"]  # type: ignore[assignment]
    if system is None:
        return {"intents": []}
    return {"intents": system.intent_classifier.get_all_intents()}


@app.post("/api/search")
def search(req: SearchRequest) -> dict:
    system: QueryUnderstandingSystem = STATE["system"]  # type: ignore[assignment]
    if system is None:
        return {"error": "Engine is still starting up. Try again in a moment."}

    profile = USER_PROFILES.get(req.user_id) if req.user_id else None

    start = time.time()
    engine_result = system.process_query(req.query, user_profile=profile, top_k=req.top_k)
    elapsed = time.time() - start

    return _to_ui_response(req.query, engine_result, elapsed)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)
