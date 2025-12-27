# FILE: src/app/main.py
# NEXUS - Operational Fraud Detection Platform

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="NEXUS",
    description="Operational Fraud Detection Platform for African Banks",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/")
async def root():
    """Root endpoint - Welcome to NEXUS"""
    return {
        "message": "🚀 NEXUS - Operational Fraud Detection Platform",
        "status": "operational",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nexus-api",
        "timestamp": datetime.utcnow().isoformat()
    }

# ============================================
# FRAUD DETECTION ENDPOINTS
# ============================================

@app.post("/api/fraud/transactions/analyze")
async def analyze_transaction(transaction: dict):
    """
    Analyze a transaction for fraud risk.
    
    Expected fields:
    - amount: transaction amount
    - account_id: customer account ID
    - avg_transaction_amount: customer's average transaction
    - transaction_count_24h: transactions in last 24h
    """
    
    try:
        # Simple risk scoring for now
        amount = transaction.get("amount", 0)
        avg_amount = transaction.get("avg_transaction_amount", amount)
        count_24h = transaction.get("transaction_count_24h", 0)
        
        # Calculate risk factors
        risk_score = 0.0
        reasons = []
        
        # Check 1: Amount significantly higher than average
        if avg_amount > 0 and amount > avg_amount * 5:
            risk_score += 0.4
            reasons.append(f"Amount {amount:,.0f} is 5x customer average {avg_amount:,.0f}")
        
        # Check 2: High transaction frequency
        if count_24h > 20:
            risk_score += 0.3
            reasons.append(f"High frequency: {count_24h} transactions in 24h")
        
        # Normalize
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.5:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "transaction_id": transaction.get("id", 0),
            "amount": amount,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "is_flagged": risk_score > 0.6,
            "reasons": reasons if reasons else ["Normal transaction"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.post("/api/fraud/checks/analyze")
async def analyze_check(check_data: dict):
    """
    Analyze a check for fraud indicators.
    
    Expected fields:
    - check_number: check number
    - amount: check amount
    - signature_match_score: signature verification (0-1)
    - is_altered: whether check shows alterations
    - is_duplicate: if check has been deposited before
    - is_stolen: if check is reported stolen
    """
    
    try:
        risk_score = 0.0
        indicators = []
        
        # Check for stolen
        if check_data.get("is_stolen", False):
            risk_score += 1.0
            indicators.append("Check reported as stolen")
        
        # Check for duplicate
        if check_data.get("is_duplicate", False):
            risk_score += 0.5
            indicators.append("Duplicate check detected")
        
        # Check for alteration
        if check_data.get("is_altered", False):
            risk_score += 0.35
            indicators.append("Check shows signs of alteration")
        
        # Check signature
        sig_score = check_data.get("signature_match_score", 1.0)
        if sig_score < 0.7:
            risk_score += 0.4
            indicators.append(f"Signature mismatch ({sig_score:.0%} confidence)")
        elif sig_score < 0.85:
            risk_score += 0.15
            indicators.append(f"Signature uncertain ({sig_score:.0%} confidence)")
        
        # Normalize
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score >= 0.9:
            risk_level = "critical"
        elif risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.5:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Get recommendation
        if risk_score >= 0.9:
            recommendation = "REJECT - Do not process"
        elif risk_score >= 0.7:
            recommendation = "REVIEW - Manual verification required"
        elif risk_score >= 0.5:
            recommendation = "CAUTION - Additional checks recommended"
        else:
            recommendation = "APPROVE - Low risk"
        
        return {
            "check_number": check_data.get("check_number", ""),
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "is_flagged": risk_score > 0.6,
            "fraud_indicators": indicators if indicators else ["No indicators"],
            "signature_confidence": round(sig_score, 2),
            "recommendation": recommendation,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@app.get("/api/fraud/dashboard/summary")
async def get_dashboard_summary():
    """Get fraud detection dashboard summary"""
    
    return {
        "total_transactions": 1250,
        "flagged_transactions": 47,
        "critical_alerts": 3,
        "high_risk_anomalies": 12,
        "stolen_checks_detected": 5,
        "recent_alerts": [
            {
                "id": 1,
                "alert_type": "check_fraud",
                "severity": "critical",
                "details": "Stolen check #12345 attempted deposit",
                "recommendation": "REJECT - Contact account holder",
                "is_acknowledged": False,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": 2,
                "alert_type": "transaction_anomaly",
                "severity": "high",
                "details": "Unusual transaction pattern detected",
                "recommendation": "Review with compliance",
                "is_acknowledged": False,
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/fraud/alerts/recent")
async def get_recent_alerts(hours: int = 24):
    """Get recent fraud alerts"""
    
    return {
        "time_range": f"Last {hours} hours",
        "alert_count": 8,
        "alerts": [
            {
                "id": 1,
                "alert_type": "check_fraud",
                "severity": "critical",
                "details": "Duplicate check #9876",
                "recommendation": "REJECT",
                "is_acknowledged": False,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    }

# ============================================
# STARTUP & SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print("🚀 NEXUS API Starting...")
    print("Available at http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print("🛑 NEXUS API Shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)