# modules/cia_monitor.py
import os
import hashlib
import json
from datetime import datetime

MONITORED_FILES = [
    'data/loan_data.csv',
    'data/model_registry.csv',
    'data/aop_data.csv',
    'data/regulatory_mapping.csv',
]

HASH_STORE = 'database/file_hashes.json'

def compute_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def save_baseline():
    os.makedirs('database', exist_ok=True)
    hashes = {}
    for filepath in MONITORED_FILES:
        h = compute_hash(filepath)
        hashes[filepath] = {
            'hash'     : h,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status'   : 'BASELINE'
        }
    with open(HASH_STORE, 'w') as f:
        json.dump(hashes, f, indent=2)
    print(f"[OK] Baseline saved -> {HASH_STORE}")
    return hashes

def run_cia_monitor():
    results = {}
    findings = []

    # Load baseline
    if not os.path.exists(HASH_STORE):
        print("[INFO] No baseline found — creating baseline now...")
        save_baseline()

    with open(HASH_STORE, 'r') as f:
        baseline = json.load(f)

    file_checks = []

    for filepath in MONITORED_FILES:
        current_hash = compute_hash(filepath)
        baseline_info = baseline.get(filepath, {})
        baseline_hash = baseline_info.get('hash')

        file_exists = current_hash is not None

        if not file_exists:
            status = 'MISSING'
            tampered = True
        elif baseline_hash is None:
            status = 'NEW FILE'
            tampered = False
        elif current_hash != baseline_hash:
            status = 'TAMPERED'
            tampered = True
        else:
            status = 'INTACT'
            tampered = False

        file_size = os.path.getsize(filepath) if file_exists else 0

        file_checks.append({
            'file'    : filepath,
            'status'  : status,
            'tampered': tampered,
            'size_kb' : round(file_size / 1024, 2),
            'hash'    : current_hash[:16] + '...' if current_hash else 'N/A',
            'baseline': baseline_hash[:16] + '...' if baseline_hash else 'N/A',
        })

        if tampered:
            findings.append({
                'type'    : 'Integrity Violation',
                'file'    : filepath,
                'severity': 'CRITICAL',
                'detail'  : f"File status: {status}",
                'regulation': 'IT Act 2000 - Section 43A | CIA Triad'
            })

    # Confidentiality Check
    confidentiality_checks = []
    sensitive_cols = ['aadhar_number', 'pan_number', 'contact_number']
    try:
        import pandas as pd
        df = pd.read_csv('data/loan_data.csv')
        for col in sensitive_cols:
            if col in df.columns:
                exposed = df[col].astype(str).str.strip().replace('', float('nan')).dropna().shape[0]
                confidentiality_checks.append({
                    'column' : col,
                    'exposed': exposed,
                    'status' : 'RISK' if exposed > 0 else 'OK'
                })
    except Exception as e:
        confidentiality_checks.append({'error': str(e)})

    # Availability Check
    availability = []
    for filepath in MONITORED_FILES:
        availability.append({
            'file'     : filepath,
            'available': os.path.exists(filepath),
            'status'   : 'OK' if os.path.exists(filepath) else 'UNAVAILABLE'
        })

    results['integrity']        = file_checks
    results['confidentiality']  = confidentiality_checks
    results['availability']     = availability
    results['findings']         = findings
    results['integrity_status'] = 'FAIL' if findings else 'PASS'
    results['checked_at']       = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return results


if __name__ == '__main__':
    res = run_cia_monitor()
    print("\n=== CIA TRIAD MONITOR REPORT ===")
    print(f"Checked At       : {res['checked_at']}")
    print(f"Integrity Status : {res['integrity_status']}")
    print()
    print("-- INTEGRITY (Files) --")
    for f in res['integrity']:
        print(f"  {f['status']:10} | {f['file']:40} | {f['size_kb']} KB")
    print()
    print("-- CONFIDENTIALITY (PII Exposure) --")
    for c in res['confidentiality']:
        if 'error' not in c:
            print(f"  {c['status']:6} | {c['column']:20} | {c['exposed']} records exposed")
    print()
    print("-- AVAILABILITY --")
    for a in res['availability']:
        print(f"  {a['status']:12} | {a['file']}")
    print()
    if res['findings']:
        print("-- FINDINGS --")
        for f in res['findings']:
            print(f"  [CRITICAL] {f['type']}: {f['file']}")