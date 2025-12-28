from fastapi import FastAPI
from app.main import app as nexus_core

app = FastAPI(
    title="NEXUS API Gateway",
    description="Edge gateway for the NEXUS Fraud Detection Platform",
    version="1.0.0"
)

# Mount core fraud platform
app.mount("/api", nexus_core)

@app.get("/")
async def root():
    return {
        "message": "🚀 NEXUS API Gateway is running",
        "core": "NEXUS Fraud Engine",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gateway": "online"
    }
