"""
main.py
-------
FastAPI backend for the Phishing Email Detector.

Endpoints:
- GET  /health   -> simple health check
- POST /predict  -> classify an email text as "phishing" or "legitimate"

The trained model (TF-IDF vectorizer + classifier) is loaded ONCE at
application startup, not on every request, for performance reasons.
"""

import pickle
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Paths & configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "model" / "model.pkl"

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Phishing Email Detector API",
    description="Educational/defensive API that classifies email text as phishing or legitimate.",
    version="1.0.0",
)

# Allow the frontend (served from a different origin, e.g. file:// or localhost:xxxx)
# to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # For local/educational use. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Load model once at startup
# ---------------------------------------------------------------------------
_model_bundle = None  # will hold {"vectorizer": ..., "model": ..., "model_name": ...}


@app.on_event("startup")
def load_model():
    global _model_bundle
    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Model file not found at {MODEL_PATH}. "
            "Please run 'python train_model.py' inside the model/ folder first."
        )
    with open(MODEL_PATH, "rb") as f:
        _model_bundle = pickle.load(f)
    print(f"[startup] Loaded model: {_model_bundle.get('model_name')}")


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------
class EmailRequest(BaseModel):
    text: str = Field(..., description="The email text to classify")


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    """Simple health check to confirm the server is running."""
    return {"status": "ok", "model_loaded": _model_bundle is not None}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: EmailRequest):
    """Classify a given email text as 'phishing' or 'legitimate'."""
    if _model_bundle is None:
        raise HTTPException(status_code=503, detail="Model is not loaded yet.")

    text = payload.text.strip() if payload.text else ""
    if not text:
        raise HTTPException(status_code=400, detail="Email text must not be empty.")

    vectorizer = _model_bundle["vectorizer"]
    model = _model_bundle["model"]

    try:
        X = vectorizer.transform([text])
        prediction = model.predict(X)[0]

        # Confidence: use predict_proba if available (Logistic Regression, Naive Bayes).
        # LinearSVC has no predict_proba, so fall back to a decision-function-based score.
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X)[0]
            classes = list(model.classes_)
            confidence = float(probs[classes.index(prediction)])
        elif hasattr(model, "decision_function"):
            import math
            score = model.decision_function(X)[0]
            # Squash the raw SVM margin score into a (0, 1)-like confidence value.
            confidence = float(1 / (1 + math.exp(-abs(score))))
        else:
            confidence = 1.0

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return PredictionResponse(prediction=str(prediction), confidence=round(confidence, 4))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
