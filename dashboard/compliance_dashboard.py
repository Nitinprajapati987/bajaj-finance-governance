# dashboard/compliance_dashboard.py
import dash
from dash import dcc, html, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.bias_detector  import run_bias_detection
from modules.pii_scanner    import run_pii_scan
from modules.cia_monitor    import run_cia_monitor
from modules.risk_registry  import run_risk_registry
from modules.aop_tracker    import run_aop_tracker

# ── Load Data ──────────────────────────────────────────────
bias = run_bias_detection()
pii  = run_pii_scan()
cia  = run_cia_monitor()
risk = run_risk_registry()
aop  = run_aop_tracker()

# ── App Init ───────────────────────────────────────────────
app = dash.Dash(__name__, title="ML Compliance Suite | Bajaj Finance")

COLORS = {
    'bg'      : '#0d1117',
    'card'    : '#161b22',
    'border'  : '#30363d',
    'blue'    : '#1a237e',
    'accent'  : '#3f51b5',
    'green'   : '#2e7d32',
    'red'     : '#c62828',
    'orange'  : '#e65100',
    'yellow'  : '#f9a825',
    'white'   : '#e6edf3',
    'grey'    : '#8b949e',
}

def kpi_card(title, value, status_color, subtitle=''):
    return html.Div([
        html.P(title, style={
            'color': COLORS['grey'], 'fontSize': '11px',
            'marginBottom': '4px', 'textTransform': 'uppercase',
            'letterSpacing': '1px'
        }),
        html.H2(str(value), style={
            'color': status_color, 'fontSize': '32px',
            'margin': '0', 'fontWeight': 'bold'
        }),
        html.P(subtitle, style={
            'color': COLORS['grey'], 'fontSize': '10px', 'marginTop': '4px'
        }),
    ], style={
        'backgroundColor': COLORS['card'],
        'border'         : f'1px solid {COLORS["border"]}',
        'borderTop'      : f'3px solid {status_color}',
        'borderRadius'   : '8px',
        'padding'        : '16px',
        'flex'           : '1',
        'minWidth'       : '140px',
    })

def section_title(text):
    return html.H3(text, style={
        'color'        : COLORS['white'],
        'borderLeft'   : f'4px solid {COLORS["accent"]}',
        'paddingLeft'  : '12px',
        'marginTop'    : '32px',
        'marginBottom' : '16px',
        'fontSize'     : '16px',
    })

# ── Charts ─────────────────────────────────────────────────

# 1. Gender Bias Bar
gender_fig = go.Figure(go.Bar(
    x=list(bias['gender_approval_rates'].keys()),
    y=[round(v*100,1) for v in bias['gender_approval_rates'].values()],
    marker_color=[COLORS['accent'], COLORS['red']],
    text=[f"{round(v*100,1)}%" for v in bias['gender_approval_rates'].values()],
    textposition='outside'
))
gender_fig.update_layout(
    title='Gender Approval Rate (%)',
    paper_bgcolor=COLORS['card'], plot_bgcolor=COLORS['card'],
    font_color=COLORS['white'], height=300,
    margin=dict(l=20, r=20, t=40, b=20),
    yaxis=dict(gridcolor=COLORS['border']),
)

# 2. City Approval Rate
city_fig = go.Figure(go.Bar(
    x=list(bias['city_approval_rates'].keys()),
    y=[round(v*100,1) for v in bias['city_approval_rates'].values()],
    marker_color=COLORS['accent'],
))
city_fig.update_layout(
    title='City-wise Approval Rate (%)',
    paper_bgcolor=COLORS['card'], plot_bgcolor=COLORS['card'],
    font_color=COLORS['white'], height=300,
    margin=dict(l=20, r=20, t=40, b=20),
    yaxis=dict(gridcolor=COLORS['border']),
)

# 3. Risk Gauge
avg_risk = round(sum(m['risk_score'] for m in risk['models']) / len(risk['models']))
risk_gauge = go.Figure(go.Indicator(
    mode='gauge+number',
    value=avg_risk,
    title={'text': 'Avg Risk Score', 'font': {'color': COLORS['white']}},
    gauge={
        'axis'      : {'range': [0, 100], 'tickcolor': COLORS['white']},
        'bar'       : {'color': COLORS['red'] if avg_risk > 70 else COLORS['orange']},
        'steps'     : [
            {'range': [0,  40], 'color': '#1b5e20'},
            {'range': [40, 70], 'color': '#e65100'},
            {'range': [70,100], 'color': '#7f0000'},
        ],
        'threshold' : {'line': {'color': 'white', 'width': 3}, 'value': avg_risk}
    }
))
risk_gauge.update_layout(
    paper_bgcolor=COLORS['card'], font_color=COLORS['white'],
    height=300, margin=dict(l=20, r=20, t=40, b=20)
)

# 4. AOP Pie
aop_pie = go.Figure(go.Pie(
    labels=['Completed', 'In Progress', 'Planned'],
    values=[aop['completed'], aop['in_progress'], aop['planned']],
    marker_colors=[COLORS['green'], COLORS['accent'], COLORS['yellow']],
    hole=0.4,
))
aop_pie.update_layout(
    title='AOP Review Status',
    paper_bgcolor=COLORS['card'], font_color=COLORS['white'],
    height=300, margin=dict(l=20, r=20, t=40, b=20)
)

# 5. Risk Registry Table
risk_table_data = [{
    'Model'     : m['model_name'],
    'Dept'      : m['department'],
    'Score'     : m['risk_score'],
    'Rating'    : m['risk_rating'],
    'Next Audit': m['next_audit'],
    'Days Left' : m['days_to_audit'],
} for m in risk['models']]

# 6. PII Table
pii_table_data = [{
    'PII Type'  : f['pii_type'],
    'Column'    : f['column'],
    'Records'   : f['count'],
    'Severity'  : f['severity'],
    'Action'    : f['action'],
} for f in pii['pii_findings']]

# ── Layout ─────────────────────────────────────────────────
app.layout = html.Div(style={
    'backgroundColor': COLORS['bg'],
    'minHeight'      : '100vh',
    'fontFamily'     : 'Segoe UI, Arial, sans-serif',
    'padding'        : '24px',
}, children=[

    # Header
    html.Div([
        html.H1("🏦 ML Compliance & Governance Suite",
                style={'color': COLORS['white'], 'margin': '0', 'fontSize': '24px'}),
        html.P("Bajaj Finance Ltd. | IT Compliance Unit | Real-time Audit Dashboard",
               style={'color': COLORS['grey'], 'margin': '4px 0 0 0', 'fontSize': '13px'}),
    ], style={
        'borderBottom': f'2px solid {COLORS["accent"]}',
        'paddingBottom': '16px', 'marginBottom': '24px'
    }),

    # KPI Row
    section_title("📊 Compliance Overview"),
    html.Div([
        kpi_card("Bias Status",    bias['status'],
                 COLORS['red'] if bias['status']=='FAIL' else COLORS['green'],
                 f"Disparate Impact: {bias['disparate_impact_ratio']}"),
        kpi_card("PII Issues",     pii['total_pii_fields'],
                 COLORS['red'] if pii['critical_count']>0 else COLORS['orange'],
                 f"Critical: {pii['critical_count']}"),
        kpi_card("CIA Status",     cia['integrity_status'],
                 COLORS['green'] if cia['integrity_status']=='PASS' else COLORS['red'],
                 f"Files Monitored: {len(cia['integrity'])}"),
        kpi_card("Critical Models",risk['critical_models'],
                 COLORS['red'] if risk['critical_models']>0 else COLORS['green'],
                 f"Total: {risk['total_models']} models"),
        kpi_card("AOP Completion", f"{aop['completion_rate']}%",
                 COLORS['green'] if aop['completion_rate']>50 else COLORS['orange'],
                 f"{aop['completed']}/{aop['total_reviews']} reviews"),
        kpi_card("Overdue Audits", aop['overdue'],
                 COLORS['red'] if aop['overdue']>0 else COLORS['green'],
                 "Require immediate action"),
    ], style={'display':'flex', 'gap':'12px', 'flexWrap':'wrap'}),

    # Charts Row 1
    section_title("⚖️ Bias Detection"),
    html.Div([
        html.Div(dcc.Graph(figure=gender_fig), style={'flex':'1'}),
        html.Div(dcc.Graph(figure=city_fig),   style={'flex':'1'}),
    ], style={'display':'flex', 'gap':'16px'}),

    # Bias Flags
    html.Div([
        html.Div([
            html.P(f"⚠ [{f['severity']}] {f['type']}: {f['detail']}",
                   style={'color': COLORS['red'], 'margin':'4px 0', 'fontSize':'13px'})
            for f in bias['bias_flags']
        ] + ([html.P("✅ No bias flags found",
                     style={'color':COLORS['green']})] if not bias['bias_flags'] else [])
        )
    ], style={
        'backgroundColor': COLORS['card'],
        'border'         : f'1px solid {COLORS["border"]}',
        'borderRadius'   : '8px',
        'padding'        : '16px',
        'marginBottom'   : '16px',
    }),

    # Charts Row 2
    section_title("📈 Risk & AOP Overview"),
    html.Div([
        html.Div(dcc.Graph(figure=risk_gauge), style={'flex':'1'}),
        html.Div(dcc.Graph(figure=aop_pie),    style={'flex':'1'}),
    ], style={'display':'flex', 'gap':'16px'}),

    # Risk Registry Table
    section_title("🎯 Risk Registry"),
    dash_table.DataTable(
        data=risk_table_data,
        columns=[{'name': c, 'id': c} for c in risk_table_data[0].keys()],
        style_table ={'overflowX': 'auto'},
        style_cell  ={
            'backgroundColor': COLORS['card'],
            'color'          : COLORS['white'],
            'border'         : f'1px solid {COLORS["border"]}',
            'padding'        : '10px',
            'fontSize'       : '12px',
            'textAlign'      : 'left',
        },
        style_header={
            'backgroundColor': COLORS['accent'],
            'color'          : 'white',
            'fontWeight'     : 'bold',
        },
        style_data_conditional=[
            {'if': {'filter_query': '{Rating} = CRITICAL'}, 'color': COLORS['red'],    'fontWeight': 'bold'},
            {'if': {'filter_query': '{Rating} = HIGH'},     'color': COLORS['orange'], 'fontWeight': 'bold'},
            {'if': {'filter_query': '{Days Left} < 0'},     'backgroundColor': '#3b0000'},
        ],
    ),

    # PII Table
    section_title("🔐 PII Scanner Results"),
    dash_table.DataTable(
        data=pii_table_data,
        columns=[{'name': c, 'id': c} for c in pii_table_data[0].keys()],
        style_table ={'overflowX': 'auto'},
        style_cell  ={
            'backgroundColor': COLORS['card'],
            'color'          : COLORS['white'],
            'border'         : f'1px solid {COLORS["border"]}',
            'padding'        : '10px',
            'fontSize'       : '12px',
            'textAlign'      : 'left',
        },
        style_header={
            'backgroundColor': COLORS['accent'],
            'color'          : 'white',
            'fontWeight'     : 'bold',
        },
        style_data_conditional=[
            {'if': {'filter_query': '{Severity} = CRITICAL'}, 'color': COLORS['red'],    'fontWeight': 'bold'},
            {'if': {'filter_query': '{Severity} = HIGH'},     'color': COLORS['orange'], 'fontWeight': 'bold'},
        ],
    ),

    # Footer
    html.Div([
        html.P("ML Compliance Suite v1.0 | Bajaj Finance Ltd. | IT Compliance Unit | CONFIDENTIAL",
               style={'color': COLORS['grey'], 'textAlign': 'center', 'fontSize': '11px'})
    ], style={'marginTop': '40px', 'borderTop': f'1px solid {COLORS["border"]}', 'paddingTop': '16px'}),
])

if __name__ == '__main__':
    app.run(debug=True, port=8050)