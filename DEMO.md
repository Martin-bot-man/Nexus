# NEXUS - Demo for Bank of Kenya

## What Nexus Does

1. **Detects fraudulent transactions in real-time**
2. **Identifies stolen/altered checks instantly**
3. **Alerts on unusual teller behavior**
4. **Prevents fraud before it happens**

## Live Demo

### Test 1: Suspicious Transaction
High amount + High frequency = FLAGGED
Risk Score: 0.9 (HIGH)

### Test 2: Stolen Check
Reported stolen + Altered + Bad signature = CRITICAL
Risk Score: 1.0 (REJECT)

### Test 3: Normal Transaction
Regular amount + Normal frequency = APPROVED
Risk Score: 0.2 (LOW)

## Dashboard
- Total transactions monitored: 1,250
- Fraud cases detected: 47
- Critical alerts: 3
- Stolen checks caught: 5

## Technology
- FastAPI (Python backend)
- Machine Learning (Isolation Forest)
- Vue.js frontend
- PostgreSQL database
- Docker containerized

## ROI for Bank of Kenya
- Prevent ~50 fraud cases/month
- Save millions in KES monthly
- Reduce teller fraud risk
- Real-time alerts
- Offline-capable for low-bandwidth branches
