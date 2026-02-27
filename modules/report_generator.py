# modules/report_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from modules.bias_detector  import run_bias_detection
from modules.pii_scanner    import run_pii_scan
from modules.cia_monitor    import run_cia_monitor
from modules.risk_registry  import run_risk_registry
from modules.aop_tracker    import run_aop_tracker

def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CoverTitle',
        fontSize=24, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1a237e'),
        alignment=TA_CENTER, spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        name='CoverSub',
        fontSize=13, fontName='Helvetica',
        textColor=colors.HexColor('#37474f'),
        alignment=TA_CENTER, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=14, fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=TA_LEFT, spaceAfter=4,
        spaceBefore=16, leftIndent=8
    ))
    styles.add(ParagraphStyle(
        name='BodyText2',
        fontSize=10, fontName='Helvetica',
        textColor=colors.HexColor('#212121'),
        spaceAfter=4, leading=14
    ))
    styles.add(ParagraphStyle(
        name='FindingText',
        fontSize=9, fontName='Helvetica',
        textColor=colors.HexColor('#b71c1c'),
        spaceAfter=3, leftIndent=12
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        fontSize=8, fontName='Helvetica',
        textColor=colors.grey,
        alignment=TA_CENTER
    ))
    return styles

def section_header(title, styles):
    header_table = Table(
        [[Paragraph(f"  {title}", styles['SectionHeader'])]],
        colWidths=[17 * cm]
    )
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a237e')),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return header_table

def status_color(status):
    mapping = {
        'PASS'    : colors.HexColor('#2e7d32'),
        'FAIL'    : colors.HexColor('#c62828'),
        'WARN'    : colors.HexColor('#e65100'),
        'CRITICAL': colors.HexColor('#c62828'),
        'HIGH'    : colors.HexColor('#e65100'),
        'MEDIUM'  : colors.HexColor('#f9a825'),
        'LOW'     : colors.HexColor('#2e7d32'),
        'DONE'    : colors.HexColor('#2e7d32'),
        'OVERDUE' : colors.HexColor('#c62828'),
        'INTACT'  : colors.HexColor('#2e7d32'),
        'TAMPERED': colors.HexColor('#c62828'),
    }
    return mapping.get(status, colors.HexColor('#37474f'))

def generate_pdf_report(output_path='reports/compliance_report.pdf'):
    os.makedirs('reports', exist_ok=True)
    styles  = get_styles()
    story   = []
    now     = datetime.now().strftime('%d %B %Y, %H:%M')

    # ── COVER PAGE ──────────────────────────────────────────
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("ML COMPLIANCE & GOVERNANCE SUITE", styles['CoverTitle']))
    story.append(Paragraph("Bajaj Finance Ltd. | IT Compliance Unit", styles['CoverSub']))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a237e')))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"Report Generated: {now}", styles['CoverSub']))
    story.append(Paragraph("Classification: CONFIDENTIAL | For Internal Use Only", styles['CoverSub']))
    story.append(Spacer(1, 1 * cm))

    # Cover summary table
    bias_res = run_bias_detection()
    pii_res  = run_pii_scan()
    cia_res  = run_cia_monitor()
    risk_res = run_risk_registry()
    aop_res  = run_aop_tracker()

    cover_data = [
        ['Module', 'Status', 'Key Finding'],
        ['Bias Detection',   bias_res['status'], f"Disparate Impact: {bias_res['disparate_impact_ratio']}"],
        ['PII Scanner',      pii_res['status'],  f"{pii_res['total_pii_fields']} PII issues found"],
        ['CIA Monitor',      cia_res['integrity_status'], f"{len(cia_res['findings'])} integrity issues"],
        ['Risk Registry',    'INFO', f"{risk_res['critical_models']} Critical models"],
        ['AOP Tracker',      'INFO', f"Completion: {aop_res['completion_rate']}%"],
    ]

    cover_table = Table(cover_data, colWidths=[5*cm, 3*cm, 9*cm])
    cover_table.setStyle(TableStyle([
        ('BACKGROUND',   (0, 0), (-1, 0),  colors.HexColor('#1a237e')),
        ('TEXTCOLOR',    (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',     (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',     (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),   [colors.HexColor('#f5f5f5'), colors.white]),
        ('GRID',         (0, 0), (-1, -1), 0.5, colors.HexColor('#b0bec5')),
        ('TOPPADDING',   (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 5),
        ('LEFTPADDING',  (0, 0), (-1, -1), 8),
    ]))

    # Color status cells
    status_map = {'FAIL': 1, 'WARN': 2, 'PASS': 3}
    for i, row in enumerate(cover_data[1:], 1):
        st = row[1]
        cover_table.setStyle(TableStyle([
            ('TEXTCOLOR', (1, i), (1, i), status_color(st)),
            ('FONTNAME',  (1, i), (1, i), 'Helvetica-Bold'),
        ]))

    story.append(cover_table)
    story.append(Spacer(1, 1 * cm))

    # ── SECTION 1: BIAS DETECTION ───────────────────────────
    story.append(section_header("1. BIAS DETECTION REPORT", styles))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(
        f"<b>Overall Status:</b> <font color='{'red' if bias_res['status']=='FAIL' else 'green'}'>{bias_res['status']}</font> | "
        f"Overall Approval Rate: {bias_res['overall_approval']}% | "
        f"Disparate Impact Ratio: {bias_res['disparate_impact_ratio']}",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 0.2 * cm))

    # Gender table
    gender_data = [['Gender', 'Approval Rate', 'Status']]
    for g, rate in bias_res['gender_approval_rates'].items():
        pct = f"{round(rate * 100, 1)}%"
        st  = 'RISK' if g == 'Female' and bias_res['gender_bias_detected'] else 'OK'
        gender_data.append([g, pct, st])

    g_table = Table(gender_data, colWidths=[5*cm, 6*cm, 6*cm])
    g_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#283593')),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#e8eaf6'), colors.white]),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#9fa8da')),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
    ]))
    story.append(g_table)
    story.append(Spacer(1, 0.3 * cm))

    for flag in bias_res['bias_flags']:
        story.append(Paragraph(
            f"⚠ [{flag['severity']}] {flag['type']}: {flag['detail']} | Regulation: {flag['regulation']}",
            styles['FindingText']
        ))
    story.append(Spacer(1, 0.5 * cm))

    # ── SECTION 2: PII SCANNER ──────────────────────────────
    story.append(section_header("2. PII SCANNER REPORT", styles))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"<b>Status:</b> {pii_res['status']} | Total Records: {pii_res['total_records']} | "
        f"PII Issues: {pii_res['total_pii_fields']} | Critical: {pii_res['critical_count']}",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 0.2 * cm))

    pii_data = [['PII Type', 'Column', 'Records', 'Severity', 'Action']]
    for f in pii_res['pii_findings']:
        pii_data.append([f['pii_type'], f['column'], str(f['count']), f['severity'], f['action']])

    if len(pii_data) > 1:
        p_table = Table(pii_data, colWidths=[3.5*cm, 3.5*cm, 2*cm, 2.5*cm, 5.5*cm])
        p_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#283593')),
            ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
            ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',      (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#fce4ec'), colors.white]),
            ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#ef9a9a')),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('WORDWRAP',      (0, 0), (-1, -1), True),
        ]))
        story.append(p_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── SECTION 3: CIA MONITOR ──────────────────────────────
    story.append(section_header("3. CIA TRIAD MONITOR", styles))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"<b>Integrity Status:</b> {cia_res['integrity_status']} | "
        f"Checked At: {cia_res['checked_at']}",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 0.2 * cm))

    cia_data = [['File', 'Status', 'Size (KB)', 'Hash (Preview)']]
    for f in cia_res['integrity']:
        cia_data.append([f['file'], f['status'], str(f['size_kb']), f['hash']])

    c_table = Table(cia_data, colWidths=[6*cm, 2.5*cm, 2.5*cm, 6*cm])
    c_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#283593')),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#e8f5e9'), colors.white]),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#a5d6a7')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
    ]))
    story.append(c_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── SECTION 4: RISK REGISTRY ────────────────────────────
    story.append(section_header("4. RISK REGISTRY", styles))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"Total Models: {risk_res['total_models']} | Critical: {risk_res['critical_models']} | "
        f"High: {risk_res['high_models']} | Overdue Audits: {risk_res['overdue_audits']}",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 0.2 * cm))

    risk_data = [['Model', 'Department', 'Score', 'Rating', 'Next Audit', 'Days Left']]
    for m in risk_res['models']:
        days = str(m['days_to_audit']) if m['days_to_audit'] is not None else 'N/A'
        risk_data.append([
            m['model_name'], m['department'],
            str(m['risk_score']), m['risk_rating'],
            m['next_audit'], days
        ])

    r_table = Table(risk_data, colWidths=[5*cm, 3.5*cm, 1.5*cm, 2.5*cm, 2.5*cm, 2*cm])
    r_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#283593')),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#fff8e1'), colors.white]),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#ffe082')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('FONTSIZE',      (0, 1), (0, -1),  7),
    ]))
    story.append(r_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── SECTION 5: AOP TRACKER ──────────────────────────────
    story.append(section_header("5. AOP TRACKER", styles))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        f"Total Reviews: {aop_res['total_reviews']} | Completed: {aop_res['completed']} | "
        f"In Progress: {aop_res['in_progress']} | Completion Rate: {aop_res['completion_rate']}%",
        styles['BodyText2']
    ))
    story.append(Spacer(1, 0.2 * cm))

    aop_data = [['Review ID', 'Model', 'Type', 'Status', 'Severity', 'Findings']]
    for r in aop_res['reviews']:
        aop_data.append([
            r['review_id'], r['model_name'][:25],
            r['review_type'][:20], r['status'],
            r['severity'], str(r['findings'])
        ])

    a_table = Table(aop_data, colWidths=[2*cm, 5*cm, 4*cm, 2.5*cm, 2*cm, 1.5*cm])
    a_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#283593')),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.HexColor('#e3f2fd'), colors.white]),
        ('GRID',          (0, 0), (-1, -1), 0.5, colors.HexColor('#90caf9')),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
    ]))
    story.append(a_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── FOOTER ──────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1a237e')))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"CONFIDENTIAL | Bajaj Finance Ltd. IT Compliance Unit | Generated: {now} | ML Compliance Suite v1.0",
        styles['Footer']
    ))

    # Build PDF
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    doc.build(story)
    print(f"\n[OK] PDF Report generated -> {output_path}")
    return output_path


if __name__ == '__main__':
    path = generate_pdf_report()
    print(f"Report saved at: {path}")