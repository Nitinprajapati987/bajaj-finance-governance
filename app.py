# app.py
import subprocess
import sys
import os

def main():
    print("\n" + "="*55)
    print("   ML COMPLIANCE & GOVERNANCE SUITE")
    print("   Bajaj Finance Ltd. | IT Compliance Unit")
    print("="*55)

    print("\n[1] Running All Compliance Checks...\n")

    # Run all modules
    from modules.bias_detector  import run_bias_detection
    from modules.pii_scanner    import run_pii_scan
    from modules.cia_monitor    import run_cia_monitor
    from modules.risk_registry  import run_risk_registry
    from modules.aop_tracker    import run_aop_tracker
    from modules.report_generator import generate_pdf_report

    print("  → Bias Detection   :", end=' ')
    bias = run_bias_detection()
    print(f"{bias['status']} | Disparate Impact: {bias['disparate_impact_ratio']}")

    print("  → PII Scanner      :", end=' ')
    pii = run_pii_scan()
    print(f"{pii['status']} | Issues: {pii['total_pii_fields']}")

    print("  → CIA Monitor      :", end=' ')
    cia = run_cia_monitor()
    print(f"{cia['integrity_status']} | Files: {len(cia['integrity'])}")

    print("  → Risk Registry    :", end=' ')
    risk = run_risk_registry()
    print(f"Critical: {risk['critical_models']} | Total: {risk['total_models']}")

    print("  → AOP Tracker      :", end=' ')
    aop = run_aop_tracker()
    print(f"Completion: {aop['completion_rate']}% | Overdue: {aop['overdue']}")

    print("\n[2] Generating PDF Report...")
    report_path = generate_pdf_report()
    print(f"  → Report saved: {report_path}")

    print("\n[3] Launching Dashboard...")
    print("  → Opening: http://localhost:8050")
    print("  → Press Ctrl+C to stop\n")
    print("="*55 + "\n")

    # Launch dashboard
    from dashboard.compliance_dashboard import app
    app.run(debug=False, port=8050)

if __name__ == '__main__':
    main()