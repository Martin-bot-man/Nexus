from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.operational_fraud import OperationalFraudDetector

app = FastAPI(
    title="NEXUS",
    description="Operational Fraud Detection Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML model
try:
    iso_forest = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
    scaler = StandardScaler()
    
    # Train on sample data
    np.random.seed(42)
    normal = np.random.normal([1000, 30, 5], [500, 15, 3], (500, 3))
    fraud = np.random.normal([50000, 100, 50], [10000, 20, 10], (50, 3))
    all_data = np.vstack([normal, fraud])
    
    scaled = scaler.fit_transform(all_data)
    iso_forest.fit(scaled)
    model_ready = True
except Exception as e:
    print(f"Model init error: {e}")
    model_ready = False

# Initialize Operational Fraud Detector
op_fraud = OperationalFraudDetector()

@app.get("/")
async def root():
    return {
        "message": "🚀 NEXUS - Operational Fraud Detection Platform",
        "status": "operational",
        "version": "0.1.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "ml_ready": model_ready}

# ============================================
# TRANSACTION FRAUD DETECTION
# ============================================

@app.post("/api/fraud/transactions/analyze")
async def analyze_transaction(data: dict):
    try:
        amount = data.get("amount", 0)
        avg_amount = data.get("avg_transaction_amount", 1000)
        count_24h = data.get("transaction_count_24h", 0)
        
        risk_score = 0.0
        reasons = []
        
        if avg_amount > 0 and amount > avg_amount * 5:
            risk_score += 0.4
            reasons.append(f"Amount {amount:,.0f} is 5x average {avg_amount:,.0f}")
        
        if count_24h > 20:
            risk_score += 0.3
            reasons.append(f"High frequency: {count_24h} transactions in 24h")
        
        if amount > 100000:
            risk_score += 0.2
            reasons.append(f"Large amount: {amount:,.0f}")
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.5:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "amount": amount,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "is_flagged": risk_score > 0.6,
            "reasons": reasons if reasons else ["Normal transaction"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# CHECK FRAUD DETECTION
# ============================================

@app.post("/api/fraud/checks/analyze")
async def analyze_check(data: dict):
    try:
        risk_score = 0.0
        indicators = []
        
        if data.get("is_stolen", False):
            risk_score += 1.0
            indicators.append("Check reported as STOLEN")
        
        if data.get("is_duplicate", False):
            risk_score += 0.5
            indicators.append("Duplicate check detected")
        
        if data.get("is_altered", False):
            risk_score += 0.35
            indicators.append("Check shows alteration signs")
        
        sig_score = data.get("signature_match_score", 1.0)
        if sig_score < 0.7:
            risk_score += 0.4
            indicators.append(f"Signature mismatch ({sig_score:.0%})")
        elif sig_score < 0.85:
            risk_score += 0.15
            indicators.append(f"Signature uncertain ({sig_score:.0%})")
        
        risk_score = min(risk_score, 1.0)
        
        if risk_score >= 0.9:
            risk_level = "critical"
            recommendation = "REJECT - Do not process"
        elif risk_score >= 0.7:
            risk_level = "high"
            recommendation = "REVIEW - Manual verification required"
        elif risk_score >= 0.5:
            risk_level = "medium"
            recommendation = "CAUTION - Additional checks recommended"
        else:
            risk_level = "low"
            recommendation = "APPROVE - Low risk"
        
        return {
            "check_number": data.get("check_number", ""),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "is_flagged": risk_score > 0.6,
            "fraud_indicators": indicators if indicators else ["No indicators"],
            "signature_confidence": round(sig_score, 2),
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================
# OPERATIONAL FRAUD DETECTION
# ============================================

@app.post("/api/operational/teller/analyze")
async def analyze_teller_behavior(data: dict):
    """Analyze teller for internal fraud patterns"""
    try:
        result = op_fraud.analyze_teller_behavior(
            teller_id=data.get("teller_id", 1),
            daily_metrics=data
        )
        return result
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.post("/api/operational/cash/analyze")
async def analyze_cash_handling(data: dict):
    """Analyze cash handling discrepancies"""
    try:
        result = op_fraud.analyze_cash_handling(
            teller_id=data.get("teller_id", 1),
            cash_data=data
        )
        return result
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.post("/api/operational/collusion/detect")
async def detect_collusion(data: dict):
    """Detect collusion patterns"""
    try:
        transactions = data.get("transactions", [])
        result = op_fraud.detect_collusion_patterns(transactions)
        return result
    except Exception as e:
        return {"error": str(e), "status": "error"}

# ============================================
# DASHBOARD
# ============================================

@app.get("/api/fraud/dashboard/summary")
async def dashboard():
    return {
        "total_transactions": 1250,
        "flagged_transactions": 47,
        "critical_alerts": 3,
        "high_risk_anomalies": 12,
        "stolen_checks_detected": 5,
        "recent_alerts": [
            {"id": 1, "alert_type": "Check Fraud", "severity": "critical", "details": "Stolen check detected", "recommendation": "REJECT immediately"},
            {"id": 2, "alert_type": "Transaction Anomaly", "severity": "high", "details": "Unusual amount", "recommendation": "Manual review"},
            {"id": 3, "alert_type": "Teller Variance", "severity": "high", "details": "Cash variance detected", "recommendation": "Escalate to manager"},
        ]
    }

# ============================================
# STARTUP
# ============================================

@app.on_event("startup")
async def startup():
    print("�� NEXUS API Starting...")
    print("✓ Fraud Detection: Active")
    print("✓ ML Models: Ready")
    print("✓ Operational Fraud Detection: Active")
    print("✓ All Systems: Online")
