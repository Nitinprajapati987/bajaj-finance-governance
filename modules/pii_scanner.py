# modules/pii_scanner.py
import pandas as pd
import re

def run_pii_scan(df=None):
    if df is None:
        df = pd.read_csv('data/loan_data.csv')

    results = {}
    pii_findings = []

    # 1. Aadhar Number Check
    aadhar_found = df['aadhar_number'].astype(str).str.strip()
    aadhar_exposed = aadhar_found[aadhar_found != ''].shape[0]
    if aadhar_exposed > 0:
        pii_findings.append({
            'pii_type'  : 'Aadhar Number',
            'column'    : 'aadhar_number',
            'count'     : aadhar_exposed,
            'severity'  : 'CRITICAL',
            'regulation': 'DPDP Act 2023 + Aadhar Act 2016',
            'action'    : 'Mask or remove immediately'
        })

    # 2. PAN Number Check
    pan_found = df['pan_number'].astype(str).str.strip()
    pan_exposed = pan_found[pan_found != ''].shape[0]
    if pan_exposed > 0:
        pii_findings.append({
            'pii_type'  : 'PAN Number',
            'column'    : 'pan_number',
            'count'     : pan_exposed,
            'severity'  : 'HIGH',
            'regulation': 'DPDP Act 2023 + IT Act 2000',
            'action'    : 'Encrypt or tokenize'
        })

    # 3. Phone Number Check
    phone_found = df['contact_number'].astype(str).str.strip()
    phone_exposed = phone_found[phone_found != ''].shape[0]
    if phone_exposed > 0:
        pii_findings.append({
            'pii_type'  : 'Contact Number',
            'column'    : 'contact_number',
            'count'     : phone_exposed,
            'severity'  : 'MEDIUM',
            'regulation': 'DPDP Act 2023',
            'action'    : 'Hash or pseudonymize'
        })

    # 4. PAN Format Validation (regex)
    pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
    valid_pans = pan_found[pan_found != ''].apply(lambda x: bool(pan_pattern.match(str(x))))
    invalid_pans = (~valid_pans).sum()
    if invalid_pans > 0:
        pii_findings.append({
            'pii_type'  : 'Invalid PAN Format',
            'column'    : 'pan_number',
            'count'     : int(invalid_pans),
            'severity'  : 'LOW',
            'regulation': 'Data Quality Standard',
            'action'    : 'Validate and clean data'
        })

    results['total_records']   = len(df)
    results['pii_findings']    = pii_findings
    results['total_pii_fields']= len(pii_findings)
    results['critical_count']  = sum(1 for f in pii_findings if f['severity'] == 'CRITICAL')
    results['status']          = 'FAIL' if results['critical_count'] > 0 else 'WARN' if pii_findings else 'PASS'

    return results


if __name__ == '__main__':
    res = run_pii_scan()
    print("\n=== PII SCAN REPORT ===")
    print(f"Status         : {res['status']}")
    print(f"Total Records  : {res['total_records']}")
    print(f"PII Issues     : {res['total_pii_fields']} found")
    print(f"Critical Issues: {res['critical_count']}")
    print()
    for f in res['pii_findings']:
        print(f"  [{f['severity']}] {f['pii_type']}")
        print(f"    Column    : {f['column']}")
        print(f"    Count     : {f['count']} records")
        print(f"    Regulation: {f['regulation']}")
        print(f"    Action    : {f['action']}")
        print()