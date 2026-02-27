# modules/aop_tracker.py
import pandas as pd
from datetime import datetime, date

def run_aop_tracker():
    df = pd.read_csv('data/aop_data.csv')
    today = date.today()
    results = []

    for _, row in df.iterrows():
        # Days calculation
        try:
            planned = datetime.strptime(row['planned_date'], '%Y-%m-%d').date()
            days_from_today = (planned - today).days
        except:
            days_from_today = None

        # Completion check
        completed = str(row['completed_date']).strip() not in ['', 'nan', 'NaT']

        # Status color
        status = str(row['status'])
        if status == 'Completed':
            status_color = 'GREEN'
            urgency      = 'DONE'
        elif status == 'In Progress':
            status_color = 'BLUE'
            urgency      = 'ONGOING'
        elif days_from_today is not None and days_from_today < 0:
            status_color = 'RED'
            urgency      = 'OVERDUE'
        elif days_from_today is not None and days_from_today <= 30:
            status_color = 'ORANGE'
            urgency      = 'DUE SOON'
        else:
            status_color = 'YELLOW'
            urgency      = 'UPCOMING'

        # Severity color
        severity = str(row['severity'])
        if severity == 'High':
            sev_color = 'RED'
        elif severity == 'Medium':
            sev_color = 'ORANGE'
        elif severity == 'Low':
            sev_color = 'YELLOW'
        else:
            sev_color = 'GREY'

        results.append({
            'review_id'     : row['review_id'],
            'model_name'    : row['model_name'],
            'review_type'   : row['review_type'],
            'planned_date'  : row['planned_date'],
            'completed_date': row['completed_date'] if completed else 'Pending',
            'status'        : status,
            'status_color'  : status_color,
            'urgency'       : urgency,
            'reviewer'      : row['reviewer'],
            'findings'      : row['findings'],
            'severity'      : severity,
            'sev_color'     : sev_color,
            'quarter'       : row['quarter'],
            'remarks'       : row['remarks'],
            'days_from_today': days_from_today,
            'completed'     : completed
        })

    # Quarter Summary
    q1 = [r for r in results if r['quarter'] == 'Q1']
    q2 = [r for r in results if r['quarter'] == 'Q2']

    summary = {
        'total_reviews'    : len(results),
        'completed'        : sum(1 for r in results if r['completed']),
        'in_progress'      : sum(1 for r in results if r['status'] == 'In Progress'),
        'planned'          : sum(1 for r in results if r['status'] == 'Planned'),
        'overdue'          : sum(1 for r in results if r['urgency'] == 'OVERDUE'),
        'due_soon'         : sum(1 for r in results if r['urgency'] == 'DUE SOON'),
        'high_severity'    : sum(1 for r in results if r['severity'] == 'High'),
        'total_findings'   : sum(r['findings'] for r in results),
        'q1_reviews'       : len(q1),
        'q1_completed'     : sum(1 for r in q1 if r['completed']),
        'q2_reviews'       : len(q2),
        'q2_completed'     : sum(1 for r in q2 if r['completed']),
        'completion_rate'  : round(sum(1 for r in results if r['completed']) / len(results) * 100, 1),
        'reviews'          : results
    }

    return summary


if __name__ == '__main__':
    res = run_aop_tracker()
    print("\n=== AOP TRACKER REPORT ===")
    print(f"Total Reviews  : {res['total_reviews']}")
    print(f"Completed      : {res['completed']}")
    print(f"In Progress    : {res['in_progress']}")
    print(f"Planned        : {res['planned']}")
    print(f"Overdue        : {res['overdue']}")
    print(f"Due Soon       : {res['due_soon']}")
    print(f"Completion Rate: {res['completion_rate']}%")
    print(f"Total Findings : {res['total_findings']}")
    print()
    print(f"{'ID':<8} {'Model':<30} {'Type':<25} {'Status':<12} {'Urgency':<10} {'Severity'}")
    print("-" * 100)
    for r in res['reviews']:
        print(f"{r['review_id']:<8} {r['model_name']:<30} {r['review_type']:<25} {r['status']:<12} {r['urgency']:<10} {r['severity']}")
    print()
    print(f"Q1: {res['q1_completed']}/{res['q1_reviews']} completed")
    print(f"Q2: {res['q2_completed']}/{res['q2_reviews']} completed")