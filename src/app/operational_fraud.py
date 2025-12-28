import os
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
import hashlib
from functools import wraps

from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Body, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel, Field, validator
from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# ============================================================
# CONFIGURATION & ENVIRONMENT
# ============================================================

class Settings:
    """Production settings from environment"""
    DEBUG = os.getenv("DEBUG", "False") == "True"
    ENV = os.getenv("ENV", "production")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
    API_KEYS = os.getenv("API_KEYS", "").split(",")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fraud_detection.db")
    
    # ML Model
    MODEL_PATH = os.getenv("MODEL_PATH", "./models/fraud_detector.pkl")
    SCALER_PATH = os.getenv("SCALER_PATH", "./models/scaler.pkl")
    
    # Monitoring
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SENTRY_DSN = os.getenv("SENTRY_DSN", None)

settings = Settings()

# ============================================================
# LOGGING & MONITORING
# ============================================================

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fraud_detection.log')
    ]
)
logger = logging.getLogger(__name__)

if settings.SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENV)

# ============================================================
# DATABASE SETUP
# ============================================================

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================
# DATABASE MODELS
# ============================================================

class TransactionAudit(Base):
    """Audit log for all transactions"""
    __tablename__ = "transaction_audits"
    
    id = Column(String, primary_key=True)
    transaction_id = Column(String, index=True)
    user_id = Column(String, index=True)
    amount = Column(Float)
    risk_score = Column(Float)
    risk_level = Column(String)
    is_flagged = Column(Boolean, default=False)
    reasons = Column(JSON)
    action_taken = Column(String)  # "approved", "rejected", "review"
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_address = Column(String)
    raw_data = Column(JSON)

class AlertLog(Base):
    """Critical alerts"""
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True)
    alert_type = Column(String, index=True)
    risk_level = Column(String, index=True)
    message = Column(String)
    details = Column(JSON)
    resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class ModelVersion(Base):
    """ML model versioning"""
    __tablename__ = "model_versions"
    
    version = Column(String, primary_key=True)
    trained_date = Column(DateTime)
    training_samples = Column(Integer)
    validation_accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    active = Column(Boolean, default=True)
    metadata = Column(JSON)

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================
# AUTHENTICATION & SECURITY
# ============================================================

security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthCredentials = Depends(security)):
    """Verify API key"""
    token = credentials.credentials
    if token not in settings.API_KEYS:
        logger.warning(f"Invalid API key attempt: {token[:8]}...")
        raise HTTPException(status_code=403, detail="Invalid API key")
    return token

def rate_limit_key(request):
    """Custom rate limit key using API key"""
    auth = request.headers.get("Authorization", "").replace("Bearer ", "")
    return auth or get_remote_address(request)

limiter = Limiter(key_func=rate_limit_key)

# ============================================================
# ML MODEL MANAGEMENT
# ============================================================

class FraudDetector:
    """Production ML model manager"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.version = None
        self.is_ready = False
        self.load_model()
    
    def load_model(self):
        """Load model from disk or train new"""
        try:
            if os.path.exists(settings.MODEL_PATH):
                self.model = joblib.load(settings.MODEL_PATH)
                self.scaler = joblib.load(settings.SCALER_PATH)
                self.is_ready = True
                logger.info("✓ Model loaded from disk")
            else:
                self.train_model()
        except Exception as e:
            logger.error(f"❌ Model load failed: {e}")
            self.train_model()
    
    def train_model(self):
        """Train model on synthetic data + save"""
        try:
            np.random.seed(42)
            
            # Realistic transaction data (KES)
            normal = np.random.normal(
                loc=[5000, 3, 1.5],
                scale=[2000, 1.5, 0.8],
                size=(5000, 3)
            )
            
            fraud = np.random.normal(
                loc=[120000, 25, 8],
                scale=[30000, 8, 3],
                size=(250, 3)
            )
            
            train_data = np.vstack([normal, fraud])
            
            self.scaler = StandardScaler()
            scaled = self.scaler.fit_transform(train_data)
            
            self.model = IsolationForest(
                contamination=0.048,  # ~5% fraud rate (realistic)
                n_estimators=200,
                random_state=42,
                n_jobs=-1
            )
            self.model.fit(scaled)
            
            # Save model
            os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, settings.MODEL_PATH)
            joblib.dump(self.scaler, settings.SCALER_PATH)
            
            self.is_ready = True
            self.version = datetime.utcnow().isoformat()
            logger.info("✓ Model trained and saved")
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            self.is_ready = False
    
    def predict(self, features: np.ndarray) -> float:
        """Get anomaly score"""
        if not self.is_ready:
            raise ValueError("Model not ready")
        scaled = self.scaler.transform(features)
        return self.model.decision_function(scaled)[0]

detector = FraudDetector()

# ============================================================
# DATA MODELS (REQUEST/RESPONSE)
# ============================================================

class TransactionInput(BaseModel):
    id: Optional[str] = None
    user_id: str
    amount: float = Field(..., gt=0, le=10000000)
    avg_transaction_amount: float = Field(default=5000, gt=0)
    transaction_count_24h: int = Field(default=0, ge=0)
    unique_locations_24h: int = Field(default=1, ge=1)
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

class CheckInput(BaseModel):
    id: Optional[str] = None
    check_number: str
    amount: float = Field(..., gt=0)
    is_stolen: bool = False
    is_duplicate: bool = False
    is_altered: bool = False
    signature_match_score: float = Field(default=1.0, ge=0, le=1)

class TellerInput(BaseModel):
    teller_id: int
    transactions_today: int
    cash_variance: float
    overrides_used: int

class FraudAnalysisResponse(BaseModel):
    id: str
    type: str
    risk_score: float
    risk_level: str
    is_flagged: bool
    reasons: List[str]
    recommendation: str
    timestamp: str

# ============================================================
# CORE FRAUD LOGIC
# ============================================================

def classify_risk(score: float) -> tuple[str, str]:
    """Classify risk level and return recommendation"""
    if score >= 0.85:
        return "critical", "reject_immediately"
    if score >= 0.65:
        return "high", "manual_review"
    if score >= 0.45:
        return "medium", "flag_for_monitoring"
    return "low", "approve"

async def log_transaction(
    db: Session,
    transaction_id: str,
    user_id: str,
    amount: float,
    risk_score: float,
    risk_level: str,
    is_flagged: bool,
    reasons: List[str],
    ip_address: str,
    raw_data: Dict
):
    """Log to database"""
    try:
        audit = TransactionAudit(
            id=f"AUDIT_{hashlib.md5(f'{transaction_id}{datetime.utcnow()}'.encode()).hexdigest()}",
            transaction_id=transaction_id,
            user_id=user_id,
            amount=amount,
            risk_score=risk_score,
            risk_level=risk_level,
            is_flagged=is_flagged,
            reasons=reasons,
            ip_address=ip_address,
            raw_data=raw_data
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Database logging failed: {e}")

# ============================================================
# WEBSOCKET MANAGER (PRODUCTION)
# ============================================================

class SecureConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        async with self.lock:
            self.active_connections[client_id] = websocket
        logger.info(f"WS connected: {client_id}")
    
    async def disconnect(self, client_id: str):
        async with self.lock:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
        logger.info(f"WS disconnected: {client_id}")
    
    async def broadcast_alert(self, alert: Dict):
        """Broadcast only critical alerts"""
        if alert.get("risk_level") not in ["critical", "high"]:
            return
        
        payload = {
            **alert,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        async with self.lock:
            connections = list(self.active_connections.values())
        
        await asyncio.gather(
            *[self._safe_send(conn, payload) for conn in connections],
            return_exceptions=True
        )
    
    async def _safe_send(self, websocket: WebSocket, payload: Dict):
        try:
            await websocket.send_text(json.dumps(payload))
        except Exception as e:
            logger.error(f"WS send failed: {e}")

manager = SecureConnectionManager()

# ============================================================
# API ENDPOINTS
# ============================================================

app = FastAPI(
    title="NEXUS - Production Fraud Detection",
    description="Enterprise-grade fraud detection for African financial institutions",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,  # Strict CORS
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)

app.state.limiter = limiter

router = APIRouter(prefix="/api/v1", tags=["fraud-detection"])

# ============================================================
# TRANSACTION FRAUD ANALYSIS
# ============================================================

@router.post(
    "/fraud/transactions/analyze",
    response_model=FraudAnalysisResponse,
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit("100/minute")
async def analyze_transaction(
    request,
    data: TransactionInput,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Analyze transaction for fraud"""
    try:
        if not detector.is_ready:
            raise HTTPException(status_code=503, detail="Fraud detection model unavailable")
        
        transaction_id = data.id or f"TX_{hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()}"
        risk_score = 0.0
        reasons = []
        
        # Rule-based checks (explainable)
        if data.amount > data.avg_transaction_amount * 10:
            risk_score += 0.30
            reasons.append("Exceptionally high transaction amount")
        
        if data.transaction_count_24h > 50:
            risk_score += 0.25
            reasons.append("Extremely high transaction velocity")
        
        if data.unique_locations_24h > 5:
            risk_score += 0.20
            reasons.append("Suspicious multi-location activity")
        
        # ML anomaly detection
        try:
            features = np.array([[
                data.amount,
                data.transaction_count_24h,
                data.unique_locations_24h
            ]])
            anomaly_score = detector.predict(features)
            
            if anomaly_score < -0.10:
                risk_score += 0.30
                reasons.append("ML anomaly score flagged")
        
        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            risk_score += 0.15
            reasons.append("Model inference error - conservative flag")
        
        risk_score = min(risk_score, 1.0)
        risk_level, recommendation = classify_risk(risk_score)
        
        # Database logging
        await log_transaction(
            db=db,
            transaction_id=transaction_id,
            user_id=data.user_id,
            amount=data.amount,
            risk_score=risk_score,
            risk_level=risk_level,
            is_flagged=risk_score >= 0.65,
            reasons=reasons or ["Transaction within normal parameters"],
            ip_address=data.ip_address or "unknown",
            raw_data=data.dict()
        )
        
        response = FraudAnalysisResponse(
            id=transaction_id,
            type="transaction",
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            is_flagged=risk_score >= 0.65,
            reasons=reasons or ["Transaction within normal parameters"],
            recommendation=recommendation,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Broadcast critical alerts
        if response.is_flagged:
            await manager.broadcast_alert(response.dict())
            logger.warning(f"⚠️  High-risk transaction flagged: {transaction_id} - {risk_level}")
        
        return response
    
    except Exception as e:
        logger.error(f"Transaction analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

# ============================================================
# CHECK FRAUD ANALYSIS
# ============================================================

@router.post(
    "/fraud/checks/analyze",
    response_model=FraudAnalysisResponse,
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit("100/minute")
async def analyze_check(
    request,
    data: CheckInput,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Analyze check for fraud"""
    check_id = data.id or f"CHK_{data.check_number}"
    risk_score = 0.0
    reasons = []
    
    if data.is_stolen:
        risk_score = 1.0
        reasons.append("Check reported as stolen")
    
    if data.is_duplicate:
        risk_score += 0.40
        reasons.append("Duplicate check detected")
    
    if data.is_altered:
        risk_score += 0.35
        reasons.append("Physical alteration detected")
    
    if data.signature_match_score < 0.7:
        risk_score += 0.35
        reasons.append(f"Signature match low: {data.signature_match_score:.2f}")
    
    risk_score = min(risk_score, 1.0)
    risk_level, recommendation = classify_risk(risk_score)
    
    await log_transaction(
        db=db,
        transaction_id=check_id,
        user_id="unknown",
        amount=data.amount,
        risk_score=risk_score,
        risk_level=risk_level,
        is_flagged=risk_score >= 0.65,
        reasons=reasons,
        ip_address="unknown",
        raw_data=data.dict()
    )
    
    response = FraudAnalysisResponse(
        id=check_id,
        type="check",
        risk_score=round(risk_score, 2),
        risk_level=risk_level,
        is_flagged=risk_score >= 0.65,
        reasons=reasons or ["No fraud indicators"],
        recommendation=recommendation,
        timestamp=datetime.utcnow().isoformat()
    )
    
    if response.is_flagged:
        await manager.broadcast_alert(response.dict())
    
    return response

# ============================================================
# OPERATIONAL FRAUD ANALYSIS
# ============================================================

@router.post(
    "/operational/teller/analyze",
    response_model=FraudAnalysisResponse,
    dependencies=[Depends(verify_api_key)]
)
@limiter.limit("50/minute")
async def analyze_teller(
    request,
    data: TellerInput,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Analyze teller behavior"""
    teller_id = f"TELLER_{data.teller_id}"
    risk_score = 0.0
    reasons = []
    
    if data.cash_variance > 50000:
        risk_score += 0.50
        reasons.append(f"Critical cash variance: KES {data.cash_variance:,.0f}")
    elif data.cash_variance > 10000:
        risk_score += 0.30
        reasons.append(f"High cash variance: KES {data.cash_variance:,.0f}")
    
    if data.overrides_used > 10:
        risk_score += 0.35
        reasons.append(f"Excessive system overrides: {data.overrides_used}")
    
    if data.transactions_today > 500:
        risk_score += 0.25
        reasons.append(f"Unusual volume: {data.transactions_today} transactions")
    
    risk_score = min(risk_score, 1.0)
    risk_level, recommendation = classify_risk(risk_score)
    
    response = FraudAnalysisResponse(
        id=teller_id,
        type="teller_behavior",
        risk_score=round(risk_score, 2),
        risk_level=risk_level,
        is_flagged=risk_score >= 0.70,
        reasons=reasons or ["Normal teller activity"],
        recommendation=recommendation,
        timestamp=datetime.utcnow().isoformat()
    )
    
    if response.is_flagged:
        await manager.broadcast_alert(response.dict())
        logger.warning(f"⚠️  High-risk teller activity: {teller_id} - {risk_level}")
    
    return response

# ============================================================
# DASHBOARD & MONITORING
# ============================================================

@router.get("/fraud/dashboard/summary", dependencies=[Depends(verify_api_key)])
async def dashboard_summary(db: Session = Depends(get_db)):
    """Get fraud dashboard summary"""
    try:
        from sqlalchemy import func
        
        today = datetime.utcnow().date()
        
        total_tx = db.query(func.count(TransactionAudit.id)).filter(
            TransactionAudit.timestamp >= today
        ).scalar() or 0
        
        flagged = db.query(func.count(TransactionAudit.id)).filter(
            TransactionAudit.is_flagged == True,
            TransactionAudit.timestamp >= today
        ).scalar() or 0
        
        critical = db.query(func.count(TransactionAudit.id)).filter(
            TransactionAudit.risk_level == "critical",
            TransactionAudit.timestamp >= today
        ).scalar() or 0
        
        total_amount = db.query(func.sum(TransactionAudit.amount)).filter(
            TransactionAudit.timestamp >= today
        ).scalar() or 0
        
        flagged_amount = db.query(func.sum(TransactionAudit.amount)).filter(
            TransactionAudit.is_flagged == True,
            TransactionAudit.timestamp >= today
        ).scalar() or 0
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "transactions_today": total_tx,
            "flagged_count": flagged,
            "critical_alerts": critical,
            "total_volume_kes": float(total_amount),
            "flagged_volume_kes": float(flagged_amount),
            "system_status": "operational",
            "model_version": detector.version,
            "model_ready": detector.is_ready
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Dashboard unavailable")

@router.get("/health", dependencies=[Depends(verify_api_key)])
async def health():
    """Health check"""
    return {
        "status": "healthy" if detector.is_ready else "degraded",
        "ml_ready": detector.is_ready,
        "active_connections": len(manager.active_connections),
        "environment": settings.ENV,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================================
# SECURE WEBSOCKET
# ============================================================

@router.websocket("/ws/alerts/{client_id}")
async def websocket_alerts(websocket: WebSocket, client_id: str):
    """Secure WebSocket for real-time alerts"""
    # In production, verify client_id with auth token
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({"type": "heartbeat"}))
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(client_id)

# ============================================================
# APP STARTUP
# ============================================================

app.include_router(router)

@app.on_event("startup")
async def startup():
    logger.info("=" * 60)
    logger.info("🚀 NEXUS FRAUD DETECTION - PRODUCTION MODE")
    logger.info("=" * 60)
    logger.info(f"✓ Environment: {settings.ENV}")
    logger.info(f"✓ Database: {settings.DATABASE_URL}")
    logger.info(f"✓ ML Model: {'READY' if detector.is_ready else 'TRAINING'}")
    logger.info(f"✓ Logging: {settings.LOG_LEVEL}")
    logger.info(f"✓ API Rate Limiting: ENABLED")
    logger.info(f"✓ CORS: {settings.ALLOWED_HOSTS}")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 NEXUS shutting down gracefully...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level=settings.LOG_LEVEL.lower()
    )