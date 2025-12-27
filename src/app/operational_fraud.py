# FILE: src/app/operational_fraud.py
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

class OperationalFraudDetector:
    def __init__(self):
        self.teller_profiles = {}
        self.alerts = []
    
    def analyze_teller_behavior(self, teller_id: int, daily_metrics: Dict) -> Dict:
        anomalies = []
        risk_score = 0.0
        if teller_id not in self.teller_profiles:
            self.teller_profiles[teller_id] = {'avg_variance': 500, 'avg_tx_count': 20, 'normal_hours': '9-5'}
        profile = self.teller_profiles[teller_id]
        daily_var = abs(daily_metrics.get('daily_cash_variance', 0))
        avg_var = abs(profile['avg_variance'])
        std_dev = max(avg_var * 0.3, 100)
        z_score = (daily_var - avg_var) / std_dev if std_dev > 0 else 0
        if z_score > 3.0:
            anomalies.append({'type': 'CRITICAL_CASH_VARIANCE', 'severity': 'critical', 'description': f'Cash variance {daily_var:,.0f} KES is {z_score:.1f} standard deviations above normal', 'risk': 0.5})
            risk_score += 0.5
        elif z_score > 2.0:
            anomalies.append({'type': 'HIGH_CASH_VARIANCE', 'severity': 'high', 'description': f'Cash variance {daily_var:,.0f} KES is significantly above normal {avg_var:,.0f} KES', 'risk': 0.3})
            risk_score += 0.3
        tx_count = daily_metrics.get('transaction_count', 0)
        avg_tx = profile['avg_tx_count']
        if tx_count > avg_tx * 2:
            anomalies.append({'type': 'HIGH_TRANSACTION_VOLUME', 'severity': 'high', 'description': f'Processed {tx_count} transactions (2x normal {avg_tx})', 'risk': 0.25})
            risk_score += 0.25
        large_tx_count = daily_metrics.get('large_transactions_count', 0)
        if large_tx_count > 5:
            anomalies.append({'type': 'UNUSUAL_LARGE_TRANSACTIONS', 'severity': 'high', 'description': f'{large_tx_count} large transactions (>100K) processed', 'risk': 0.2})
            risk_score += 0.2
        after_hours = daily_metrics.get('after_hours_work', 0)
        if after_hours > 3:
            anomalies.append({'type': 'UNUSUAL_HOURS', 'severity': 'medium', 'description': f'Worked {after_hours} hours after normal business hours', 'risk': 0.15})
            risk_score += 0.15
        consecutive_days = daily_metrics.get('consecutive_variance_days', 0)
        if consecutive_days > 2:
            anomalies.append({'type': 'PATTERN_OF_VARIANCE', 'severity': 'high', 'description': f'Cash variance detected on {consecutive_days} consecutive days', 'risk': 0.3})
            risk_score += 0.3
        risk_score = min(risk_score, 1.0)
        return {'teller_id': teller_id, 'risk_score': round(risk_score, 2), 'risk_level': self._get_risk_level(risk_score), 'anomalies_detected': len(anomalies) > 0, 'anomalies': anomalies, 'z_score': round(z_score, 2), 'recommendation': self._get_teller_recommendation(risk_score, anomalies), 'timestamp': datetime.utcnow().isoformat()}
    
    def detect_collusion_patterns(self, transactions: List[Dict]) -> Dict:
        patterns = []
        pairs = {}
        for tx in transactions:
            key = (tx.get('teller_id'), tx.get('account_id'))
            if key not in pairs:
                pairs[key] = []
            pairs[key].append(tx)
        for (teller_id, account_id), pair_txs in pairs.items():
            if len(pair_txs) < 2:
                continue
            if len(pair_txs) >= 5:
                try:
                    time_span = (pair_txs[-1].get('created_at') - pair_txs[0].get('created_at')).days
                    if time_span <= 7:
                        patterns.append({'pattern': 'STRUCTURING_SUSPECTED', 'severity': 'high', 'teller_id': teller_id, 'account_id': account_id, 'transaction_count': len(pair_txs), 'time_span_days': time_span, 'description': f'{len(pair_txs)} transactions in {time_span} days', 'risk': 0.4})
                except:
                    pass
            round_amount_count = sum(1 for tx in pair_txs if tx.get('amount', 0) % 1000 == 0 and tx.get('amount', 0) > 0)
            if round_amount_count > len(pair_txs) * 0.7:
                patterns.append({'pattern': 'ROUND_AMOUNTS', 'severity': 'medium', 'teller_id': teller_id, 'account_id': account_id, 'description': f'{round_amount_count}/{len(pair_txs)} round amounts', 'risk': 0.2})
            large_txs = [tx for tx in pair_txs if tx.get('amount', 0) > 100000]
            if len(large_txs) > 2:
                patterns.append({'pattern': 'RAPID_LARGE_TRANSFERS', 'severity': 'high', 'teller_id': teller_id, 'account_id': account_id, 'large_transaction_count': len(large_txs), 'description': f'{len(large_txs)} large transfers', 'risk': 0.35})
        return {'patterns_detected': len(patterns) > 0, 'pattern_count': len(patterns), 'patterns': patterns, 'severity': 'high' if patterns else 'low', 'timestamp': datetime.utcnow().isoformat()}
    
    def analyze_cash_handling(self, teller_id: int, cash_data: Dict) -> Dict:
        issues = []
        risk_score = 0.0
        expected = cash_data.get('expected_amount', 0)
        actual = cash_data.get('actual_amount', 0)
        discrepancy = abs(expected - actual)
        if discrepancy > expected * 0.05:
            issues.append({'type': 'SIGNIFICANT_DISCREPANCY', 'severity': 'high', 'description': f'Expected {expected:,.0f} KES, found {actual:,.0f} KES', 'discrepancy_amount': discrepancy, 'discrepancy_percent': round((discrepancy / expected * 100), 2) if expected > 0 else 0})
            risk_score += 0.4
        repeat_count = cash_data.get('discrepancies_this_month', 0)
        if repeat_count > 3:
            issues.append({'type': 'REPEAT_DISCREPANCIES', 'severity': 'critical', 'description': f'{repeat_count} discrepancies this month', 'risk': 0.5})
            risk_score += 0.5
        risk_score = min(risk_score, 1.0)
        return {'teller_id': teller_id, 'risk_score': round(risk_score, 2), 'risk_level': self._get_risk_level(risk_score), 'issues_detected': len(issues) > 0, 'issues': issues, 'expected_amount': expected, 'actual_amount': actual, 'discrepancy': round(discrepancy, 2), 'timestamp': datetime.utcnow().isoformat()}
    
    def _get_risk_level(self, risk_score: float) -> str:
        if risk_score >= 0.8:
            return 'critical'
        elif risk_score >= 0.6:
            return 'high'
        elif risk_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _get_teller_recommendation(self, risk_score: float, anomalies: List[Dict]) -> str:
        if risk_score >= 0.8:
            return '🚨 URGENT: Escalate to compliance immediately.'
        elif risk_score >= 0.6:
            return '⚠️ HIGH: Review with branch manager.'
        elif risk_score >= 0.4:
            return '📋 MEDIUM: Monitor closely.'
        else:
            return '✓ LOW: No action needed.'
