from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from collections import deque
import uvicorn
import datetime
import sys
import os

# Import modules
try:
    from app.model_loader import get_model_loader
    from app.type_definitions import NetworkTrafficData
except ImportError:
    try:
        from src.app.model_loader import get_model_loader
        from src.app.type_definitions import NetworkTrafficData
    except ImportError:
        from model_loader import get_model_loader
        from type_definitions import NetworkTrafficData

app = FastAPI(
    title="IDS XGBoost API",
    description="API for Real-time Network Intrusion Detection using XGBoost",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
model_loader = None
HISTORY_LEN = 100
prediction_history = deque(maxlen=HISTORY_LEN)

@app.on_event("startup")
async def startup_event():
    global model_loader
    try:
        model_loader = get_model_loader()
        print("[API] Model loaded on startup.")
    except Exception as e:
        print(f"[API] CRITICAL ERROR: Could not load model. {e}")

@app.get("/")
def read_root():
    return {"status": "active", "service": "IDS XGBoost Inference API"}

@app.get("/health")
def health_check():
    if model_loader and model_loader.is_loaded:
        return {"status": "healthy", "model_loaded": True}
    return {"status": "unhealthy", "model_loaded": False}

@app.post("/predict")
def predict_traffic(custom_input: NetworkTrafficData):
    global model_loader
    if not model_loader or not model_loader.is_loaded:
        raise HTTPException(status_code=503, detail="Model service not ready")

    try:
        # Pydantic conversion
        features = custom_input.to_array()
        
        # Predict
        result = model_loader.predict(features)
        
        # Add timestamp and store in history
        result['timestamp'] = datetime.datetime.now().isoformat()
        prediction_history.append(result)
        
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    return list(prediction_history)

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
