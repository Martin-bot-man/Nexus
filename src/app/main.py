from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import json
import random
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ============================================================
# APPLICATION METADATA
# ============================================================

app = FastAPI(
    title="NEXUS",
    description="Real-Time Operational & Financial Fraud Detection Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REAL-TIME WEBSOCKET MANAGER
# ============================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        async with self.lock:
            self.active_connections.append(websocket)
        print(f"📡 WS connected: {websocket.client}")

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        print(f"🔌 WS disconnected: {websocket.client}")

    async def broadcast(self, event: Dict):
        payload = {
            **event,
            "timestamp": datetime.utcnow().isoformat(),
            "geo": {
                "lat": round(random.uniform(-1.5, 1.5), 4), # Kenya-centric bounds
                "lng": round(random.uniform(36.0, 38.0), 4),
            }
        }
        async with self.lock:
            connections = list(self.active_connections)
        
        # Concurrent send to all browsers
        await asyncio.gather(
            *[self._safe_send(conn, payload) for conn in connections],
            return_exceptions=True
        )

    async def _safe_send(self, websocket: WebSocket, payload: Dict):
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception:
            await self.disconnect(websocket)

manager = ConnectionManager()
router = APIRouter()

# ============================================================
# ML MODEL (Isolation Forest)
# ============================================================

scaler = StandardScaler()
iso_forest = IsolationForest(contamination=0.05, n_estimators=100, random_state=42)

# Training with simulated African transaction patterns
normal_data = np.random.normal(loc=[3000, 4, 2], scale=[1000, 2, 1], size=(500, 3))
fraud_data = np.random.normal(loc=[95000, 25, 10], scale=[15000, 5, 2], size=(50, 3))
scaler.fit(np.vstack([normal_data, fraud_data]))
iso_forest.fit(scaler.transform(np.vstack([normal_data, fraud_data])))

# ============================================================
# BACKGROUND SIMULATOR (The "Live" Engine)
# ============================================================

async def fraud_simulator():
    """Generates a fake fraud event every 5-10 seconds to keep the UI busy."""
    print("🛠️ Fraud Simulator Started")
    types = ["transaction", "check", "teller_behavior"]
    levels = ["high", "critical"]
    
    while True:
        await asyncio.sleep(random.randint(5, 10))
        if len(manager.active_connections) > 0:
            mock_event = {
                "id": f"SIM_{random.randint(1000, 9999)}",
                "type": random.choice(types),
                "risk_score": round(random.uniform(0.75, 0.99), 2),
                "risk_level": random.choice(levels),
                "is_flagged": True,
                "reasons": ["Unusual high-value burst", "ML Anomaly detected"],
                "data": {"amount": random.randint(50000, 150000), "currency": "KES"}
            }
            await manager.broadcast(mock_event)

# ============================================================
# ROUTES
# ============================================================

@router.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    await manager.connect(websocket)
    try:
        while True:
            # Heartbeat to keep connection alive
            await websocket.send_text(json.dumps({"type": "heartbeat"}))
            await asyncio.sleep(20)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

@router.get("/fraud/dashboard/summary")
async def dashboard_summary():
    # Return dynamic numbers instead of hard-coded ones
    return {
        "transactions_today": random.randint(1200, 5000),
        "flagged": random.randint(40, 100),
        "critical_alerts": random.randint(5, 15),
        "system_status": "active"
    }

# ============================================================
# LIFECYCLE
# ============================================================

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    print("🚀 NEXUS CORE ONLINE")
    # Start the simulator in the background
    asyncio.create_task(fraud_simulator())