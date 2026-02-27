# modules/bias_detector.py
import pandas as pd
import numpy as np

def run_bias_detection(df=None):
    if df is None:
        df = pd.read_csv('data/loan_data.csv')

    results = {}

    # 1. Gender Bias
    gender_groups = df.groupby('gender')['loan_approved'].mean()
    results['gender_approval_rates'] = gender_groups.to_dict()

    male_rate   = gender_groups.get('Male', 0)
    female_rate = gender_groups.get('Female', 0)
    disparate_impact = female_rate / male_rate if male_rate > 0 else 0

    results['disparate_impact_ratio'] = round(disparate_impact, 3)
    results['gender_bias_detected']   = disparate_impact < 0.8  # RBI threshold

    # 2. City Bias
    city_groups = df.groupby('city')['loan_approved'].mean()
    results['city_approval_rates'] = city_groups.to_dict()
    city_std = city_groups.std()
    results['city_bias_detected'] = city_std > 0.05

    # 3. Education Bias
    edu_groups = df.groupby('education')['loan_approved'].mean()
    results['education_approval_rates'] = edu_groups.to_dict()

    # 4. Overall Summary
    results['total_records']    = len(df)
    results['overall_approval'] = round(df['loan_approved'].mean() * 100, 2)
    results['bias_flags']       = []

    if results['gender_bias_detected']:
        results['bias_flags'].append({
            'type'    : 'Gender Bias',
            'severity': 'HIGH',
            'detail'  : f"Disparate Impact Ratio: {results['disparate_impact_ratio']} (Threshold: 0.80)",
            'regulation': 'RBI Digital Lending Guidelines 2022'
        })
    if results['city_bias_detected']:
        results['bias_flags'].append({
            'type'    : 'Geographic Bias',
            'severity': 'MEDIUM',
            'detail'  : f"City approval rate std deviation: {round(city_std, 3)}",
            'regulation': 'Fair Lending Guidelines'
        })

    results['status'] = 'FAIL' if results['bias_flags'] else 'PASS'
    return results


if __name__ == '__main__':
    res = run_bias_detection()
    print("\n=== BIAS DETECTION REPORT ===")
    print(f"Status          : {res['status']}")
    print(f"Overall Approval: {res['overall_approval']}%")
    print(f"Gender Rates    : {res['gender_approval_rates']}")
    print(f"Disparate Impact: {res['disparate_impact_ratio']}")
    print(f"Bias Flags      : {len(res['bias_flags'])} found")
    for flag in res['bias_flags']:
        print(f"  [{flag['severity']}] {flag['type']}: {flag['detail']}")