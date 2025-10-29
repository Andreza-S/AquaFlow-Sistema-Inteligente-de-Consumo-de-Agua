"""
Prototipo de dashboard de monitoramento de consumo de água
Arquivo: prototipo_dashboard_agua.py
Descrição: App Dash que carrega um CSV com tempo e vazões (sensor geral + S1..S4), calcula métricas,
detecta possíveis vazamentos e exibe visualizações (cards, série temporal, consumo por sensor, heatmap,
log de alertas e dados brutos).

Como usar:
- Coloque seu CSV (ex: data.csv) na mesma pasta ou ajuste DATA_PATH.
- pip install -r requirements.txt
- python prototipo_dashboard_agua.py
- Abra http://127.0.0.1:8050

Formato esperado do CSV (colunas):
Timestamp,Pulsos,Vazão (L/min),S1 – Vazão (L/s),S2 – Vazão (L/s),S3- Vazão (L/s),S4 – Vazão (L/s)

Observações:
- O código trata S1..S4 como L/s. A coluna "Vazão (L/min)" é convertida para L/s para comparação com os sensores.
- Configure HOUSE_LAYOUT com coordenadas (x,y) de cada sensor para o heatmap.
- Alerta de vazamento: diferença absoluta entre sensor geral e soma dos sensores individuais acima de THRESH_LPS.

"""

import os
import math
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

import dash
from dash import html, dcc, dash_table, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------- CONFIG -----------------------------
DATA_PATH = "data.csv"  # caminho padrão do CSV
SENSOR_COLUMNS = ["S1 – Vazão (L/s)", "S2 – Vazão (L/s)", "S3- Vazão (L/s)", "S4 – Vazão (L/s)"]
GENERAL_FLOW_COL = "Vazão (L/min)"  # fluxo total em L/min (convertemos para L/s)
TIMESTAMP_COL = "Timestamp"

# Tarifas e limites
TARIFA_POR_M3 = 4.50  # R$ por metro cúbico (ajuste conforme sua região)
THRESH_LPS = 0.2  # limiar (L/s) para sinalizar diferença considerável (vazamento)

# Mapear sensores para coordenadas na planta da casa (para o heatmap / scatter)
# Ajuste as coordenadas conforme sua planta (valores entre 0 e 1 ajudam no escalonamento)
HOUSE_LAYOUT = {
    "S1 – Vazão (L/s)": {"label": "Banheiro", "x": 0.2, "y": 0.8},
    "S2 – Vazão (L/s)": {"label": "Cozinha / Máquina", "x": 0.5, "y": 0.6},
    "S3- Vazão (L/s)": {"label": "Jardim", "x": 0.85, "y": 0.3},
    "S4 – Vazão (L/s)": {"label": "Lavanderia", "x": 0.35, "y": 0.2},
}

REFRESH_INTERVAL_SECONDS = 5  # se usar leitura contínua do arquivo

# ----------------------------- FUNÇÕES AUXILIARES -----------------------------

def load_data(path=DATA_PATH):
    """Carrega o CSV e faz parsing básico. Retorna DataFrame com índice datetime."""
    if not os.path.exists(path):
        # cria um DataFrame vazio com colunas esperadas
        cols = [TIMESTAMP_COL, "Pulsos", GENERAL_FLOW_COL] + SENSOR_COLUMNS
        return pd.DataFrame(columns=cols)

    df = pd.read_csv(path)
    # Normalizar nomes de colunas às expectativas (remoção de espaços estranhos)
    df.columns = [c.strip() for c in df.columns]
    # Converter timestamp
    df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL])
    df = df.sort_values(TIMESTAMP_COL)
    df = df.set_index(TIMESTAMP_COL)
    # Preencher colunas faltantes com zeros
    for c in SENSOR_COLUMNS + [GENERAL_FLOW_COL]:
        if c not in df.columns:
            df[c] = 0
    return df


def preprocess(df):
    """Gera colunas úteis: total_sensors_Lps, geral_Lps, volume por segundo em litros, e uma coluna 'volume_l' agregada por linha.
    Assume que GENERAL_FLOW_COL está em L/min e sensores Sx em L/s."""
    if df.empty:
        return df

    # Converter vazão geral L/min -> L/s
    df = df.copy()
    df['geral_lps'] = pd.to_numeric(df[GENERAL_FLOW_COL], errors='coerce').fillna(0) / 60.0
    # Garantir numérico nos sensores (são L/s)
    for s in SENSOR_COLUMNS:
        df[s] = pd.to_numeric(df.get(s, 0), errors='coerce').fillna(0)

    df['soma_sensores_lps'] = df[SENSOR_COLUMNS].sum(axis=1)

    # Estimativa de volume por amostra: assumindo intervalo regular, mas temos timestamp -> calcular delta
    # Calculamos volume em litros entre amostras usando a média de vazões * delta_seconds
    df['delta_s'] = (df.index.to_series().diff().dt.total_seconds()).fillna(1)
    # volume estimado por linha em litros: geral_lps * delta_s
    df['volume_geral_l'] = (df['geral_lps'] * df['delta_s'])
    # volume por sensores (soma)
    df['volume_sensores_l'] = (df['soma_sensores_lps'] * df['delta_s'])

    # coluna diferença absoluta entre geral e soma sensores (L/s)
    df['diff_lps'] = (df['geral_lps'] - df['soma_sensores_lps']).abs()

    return df


def aggregate_period(df, freq='D'):
    """Agrega o DF por frequência: 'T' minuto, 'H' hora, 'D' dia, 'W' semana, 'M' mês."""
    if df.empty:
        return df
    agg = df.resample(freq).agg({
        'volume_geral_l': 'sum',
        'volume_sensores_l': 'sum',
        **{s: 'sum' for s in SENSOR_COLUMNS}
    })
    # custo estimado em R$
    agg['m3'] = agg['volume_geral_l'] / 1000.0
    agg['custo_R$'] = agg['m3'] * TARIFA_POR_M3
    return agg


def detect_leaks(df, threshold_lps=THRESH_LPS):
    """Detecta janelas em que diff_lps > threshold e também situações em que sensores todos zero mas geral > 0."""
    if df.empty:
        return pd.DataFrame(columns=['start','end','duration_s','max_diff_lps','type','volume_l'])

    alerts = []
    in_alert = False
    start = None
    alert_rows = []

    for ts, row in df.iterrows():
        diff = row['diff_lps']
        geral = row['geral_lps']
        soma = row['soma_sensores_lps']
        is_mismatch = diff > threshold_lps
        is_hidden_leak = (soma == 0) and (geral > 0)
        if is_mismatch or is_hidden_leak:
            if not in_alert:
                in_alert = True
                start = ts
                alert_rows = []
            alert_rows.append((ts, row))
        else:
            if in_alert:
                end = ts
                # compute summary
                times = [r[0] for r in alert_rows]
                rows = pd.DataFrame([r[1] for r in alert_rows])
                duration = (times[-1] - times[0]).total_seconds() if len(times) > 1 else rows['delta_s'].sum()
                max_diff = rows['diff_lps'].max()
                vol = rows['volume_geral_l'].sum()
                typ = 'hidden_leak' if (rows['soma_sensores_lps'] == 0).all() and (rows['geral_lps'] > 0).any() else 'mismatch'
                alerts.append({'start': times[0], 'end': times[-1], 'duration_s': duration, 'max_diff_lps': max_diff, 'type': typ, 'volume_l': vol})
                in_alert = False
                alert_rows = []
    # close last
    if in_alert and alert_rows:
        times = [r[0] for r in alert_rows]
        rows = pd.DataFrame([r[1] for r in alert_rows])
        duration = (times[-1] - times[0]).total_seconds() if len(times) > 1 else rows['delta_s'].sum()
        max_diff = rows['diff_lps'].max()
        vol = rows['volume_geral_l'].sum()
        typ = 'hidden_leak' if (rows['soma_sensores_lps'] == 0).all() and (rows['geral_lps'] > 0).any() else 'mismatch'
        alerts.append({'start': times[0], 'end': times[-1], 'duration_s': duration, 'max_diff_lps': max_diff, 'type': typ, 'volume_l': vol})

    return pd.DataFrame(alerts)

# ----------------------------- DASH APP -----------------------------

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Dashboard de Consumo de Água - Protótipo"), width=8),
        dbc.Col(dbc.Button("Recarregar dados", id='reload-btn', color='primary'), width=4, style={'textAlign':'right'})
    ], align='center', className='mb-2'),

    # Interval para atualização automática (opcional)
    dcc.Interval(id='interval-refresh', interval=REFRESH_INTERVAL_SECONDS*1000, n_intervals=0),

    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Consumo Hoje (L)"), html.H3(id='card-today')])]), md=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Consumo Semana (L)"), html.H3(id='card-week')])]), md=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Consumo Mês (L)"), html.H3(id='card-month')])]), md=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Estimativa Custo (R$) Mês"), html.H3(id='card-cost')])]), md=3),
    ], className='mb-3'),

    dbc.Row([
        dbc.Col(dcc.Graph(id='timeseries'), md=8),
        dbc.Col(dcc.Graph(id='bar-sensors'), md=4),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='heatmap-house'), md=6),
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6("Alertas de Vazamento")),
            dbc.CardBody(dcc.Loading(children=[dash_table.DataTable(id='alerts-table', page_size=6, style_table={'overflowX':'auto'})]))
        ]), md=6)
    ], className='mt-3'),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader(html.H6("Dados Brutos (preview)")),
            dbc.CardBody(dash_table.DataTable(id='raw-table', page_size=8, style_table={'overflowX':'auto'}))
        ]), md=12)
    ], className='mt-3'),

    # Inputs/Config
    dbc.Row([
        dbc.Col(dbc.Input(id='data-path-input', placeholder='Caminho para CSV (padrão data.csv)', value=DATA_PATH)),
        dbc.Col(dbc.Input(id='tarifa-input', placeholder='Tarifa R$/m3', value=str(TARIFA_POR_M3))),
        dbc.Col(dbc.Button('Aplicar', id='apply-config', color='secondary'))
    ], className='mt-3 mb-5')
], fluid=True)


# ----------------------------- CALLBACKS -----------------------------

@app.callback(
    Output('timeseries', 'figure'),
    Output('bar-sensors', 'figure'),
    Output('heatmap-house', 'figure'),
    Output('card-today', 'children'),
    Output('card-week', 'children'),
    Output('card-month', 'children'),
    Output('card-cost', 'children'),
    Output('alerts-table', 'data'),
    Output('alerts-table', 'columns'),
    Output('raw-table', 'data'),
    Output('raw-table', 'columns'),
    Input('interval-refresh', 'n_intervals'),
    Input('reload-btn', 'n_clicks'),
    Input('apply-config', 'n_clicks'),
    State('data-path-input', 'value'),
    State('tarifa-input', 'value')
)
def update_all(n_intervals, btn_reload, btn_apply, data_path, tarifa):
    # carregar e processar
    TARIFA = float(tarifa) if tarifa else TARIFA_POR_M3
    df = load_data(data_path or DATA_PATH)
    df = preprocess(df)

    # Cards: consumo hoje, semana, mes (usar agregação)
    now = df.index.max() if not df.empty else pd.Timestamp.now()
    today_start = pd.Timestamp(now.date())
    week_start = today_start - pd.Timedelta(days=7)
    month_start = today_start - pd.Timedelta(days=30)

    df_today = df[df.index >= today_start]
    df_week = df[df.index >= week_start]
    df_month = df[df.index >= month_start]

    total_today = df_today['volume_geral_l'].sum() if not df_today.empty else 0
    total_week = df_week['volume_geral_l'].sum() if not df_week.empty else 0
    total_month = df_month['volume_geral_l'].sum() if not df_month.empty else 0

    cost_month = (total_month / 1000.0) * TARIFA

    # Timeseries (últimos 7 dias por hora)
    if not df.empty:
        agg_hour = aggregate_period(df, 'H')
        fig_ts = px.line(agg_hour.reset_index(), x=agg_hour.reset_index().columns[0], y='volume_geral_l', title='Consumo por hora (últimos dias)', labels={'volume_geral_l':'Volume (L)'})
    else:
        fig_ts = go.Figure().update_layout(title='Sem dados')

    # Bar sensors (soma por sensor no período selecionado -> mês)
    if not df.empty:
        sums = df[SENSOR_COLUMNS].sum().reset_index()
        sums.columns = ['sensor', 'total_l']
        fig_bar = px.bar(sums, x='sensor', y='total_l', title='Consumo por sensor (soma)', labels={'total_l':'Volume (L)'})
    else:
        fig_bar = go.Figure().update_layout(title='Sem dados')

    # Heatmap / Scatter sobre planta
    if not df.empty:
        # soma por sensor nos últimos 30 dias
        sensor_sums = df[SENSOR_COLUMNS].sum()
        xs = []
        ys = []
        labels = []
        vals = []
        for s in SENSOR_COLUMNS:
            meta = HOUSE_LAYOUT.get(s, {'x': np.random.rand(), 'y': np.random.rand(), 'label': s})
            xs.append(meta['x'])
            ys.append(meta['y'])
            labels.append(meta['label'])
            vals.append(sensor_sums.get(s, 0.0))
        heat_df = pd.DataFrame({'x': xs, 'y': ys, 'label': labels, 'value': vals})
        fig_heat = px.scatter(heat_df, x='x', y='y', size='value', hover_name='label', title='Mapa de calor (por sensor)', size_max=60)
        fig_heat.update_xaxes(visible=False)
        fig_heat.update_yaxes(visible=False)
    else:
        fig_heat = go.Figure().update_layout(title='Sem dados')

    # Detectar vazamentos
    alerts_df = detect_leaks(df)
    if not alerts_df.empty:
        alerts_out = alerts_df.sort_values('start', ascending=False).to_dict('records')
        alerts_cols = [{'name': c, 'id': c} for c in alerts_df.columns]
    else:
        alerts_out = []
        alerts_cols = []

    # Dados brutos preview
    if not df.empty:
        raw_preview = df.reset_index().tail(200)
        raw_data = raw_preview.to_dict('records')
        raw_cols = [{'name': c, 'id': c} for c in raw_preview.columns]
    else:
        raw_data = []
        raw_cols = []

    return fig_ts, fig_bar, fig_heat, f"{total_today:.1f}", f"{total_week:.1f}", f"{total_month:.1f}", f"R$ {cost_month:.2f}", alerts_out, alerts_cols, raw_data, raw_cols


if __name__ == '__main__':
    app.run(debug=True)
