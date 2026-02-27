# modules/risk_registry.py
import pandas as pd
from datetime import datetime, date

def calculate_risk_score(model):
    score = 0
    reasons = []

    # 1. Risk Level
    if model['risk_level'] == 'High':
        score += 40
        reasons.append('High risk model (+40)')
    elif model['risk_level'] == 'Medium':
        score += 25
        reasons.append('Medium risk model (+25)')
    else:
        score += 10
        reasons.append('Low risk model (+10)')

    # 2. PII Involved
    if model['pii_involved'] == 'Yes':
        score += 20
        reasons.append('PII data involved (+20)')

    # 3. RBI Applicable
    if model['rbi_applicable'] == 'Yes':
        score += 15
        reasons.append('RBI regulated (+15)')

    # 4. Audit Overdue Check
    try:
        next_audit = datetime.strptime(model['next_audit'], '%Y-%m-%d').date()
        today = date.today()
        days_to_audit = (next_audit - today).days
        if days_to_audit < 0:
            score += 25
            reasons.append(f'Audit overdue by {abs(days_to_audit)} days (+25)')
        elif days_to_audit < 30:
            score += 15
            reasons.append(f'Audit due in {days_to_audit} days (+15)')
        elif days_to_audit < 90:
            score += 5
            reasons.append(f'Audit due in {days_to_audit} days (+5)')
    except:
        days_to_audit = None

    # 5. Production Status
    if model['status'] == 'Production':
        score += 10
        reasons.append('In production (+10)')

    return min(score, 100), reasons, days_to_audit

def run_risk_registry():
    df = pd.read_csv('data/model_registry.csv')
    results = []

    for _, model in df.iterrows():
        risk_score, reasons, days_to_audit = calculate_risk_score(model)

        if risk_score >= 80:
            risk_rating = 'CRITICAL'
            color       = 'RED'
        elif risk_score >= 60:
            risk_rating = 'HIGH'
            color       = 'ORANGE'
        elif risk_score >= 40:
            risk_rating = 'MEDIUM'
            color       = 'YELLOW'
        else:
            risk_rating = 'LOW'
            color       = 'GREEN'

        results.append({
            'model_id'     : model['model_id'],
            'model_name'   : model['model_name'],
            'department'   : model['department'],
            'owner'        : model['owner'],
            'status'       : model['status'],
            'risk_score'   : risk_score,
            'risk_rating'  : risk_rating,
            'color'        : color,
            'days_to_audit': days_to_audit,
            'next_audit'   : model['next_audit'],
            'pii_involved' : model['pii_involved'],
            'rbi_applicable': model['rbi_applicable'],
            'reasons'      : reasons
        })

    # Summary
    summary = {
        'total_models'   : len(results),
        'critical_models': sum(1 for r in results if r['risk_rating'] == 'CRITICAL'),
        'high_models'    : sum(1 for r in results if r['risk_rating'] == 'HIGH'),
        'medium_models'  : sum(1 for r in results if r['risk_rating'] == 'MEDIUM'),
        'low_models'     : sum(1 for r in results if r['risk_rating'] == 'LOW'),
        'overdue_audits' : sum(1 for r in results if r['days_to_audit'] is not None and r['days_to_audit'] < 0),
        'models'         : results
    }

    return summary


if __name__ == '__main__':
    res = run_risk_registry()
    print("\n=== RISK REGISTRY REPORT ===")
    print(f"Total Models   : {res['total_models']}")
    print(f"Critical       : {res['critical_models']}")
    print(f"High Risk      : {res['high_models']}")
    print(f"Medium Risk    : {res['medium_models']}")
    print(f"Overdue Audits : {res['overdue_audits']}")
    print()
    print(f"{'Model':<35} {'Score':>6} {'Rating':>10} {'Next Audit':>12} {'Days Left':>10}")
    print("-" * 80)
    for m in res['models']:
        days = m['days_to_audit']
        days_str = str(days) if days is not None else 'N/A'
        print(f"{m['model_name']:<35} {m['risk_score']:>6} {m['risk_rating']:>10} {m['next_audit']:>12} {days_str:>10}")