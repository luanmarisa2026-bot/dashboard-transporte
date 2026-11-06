import pandas as pd
import traceback

from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

import json

from dash.dependencies import (
    Input,
    Output,
    State,
)

# ==================================================
# CARREGAMENTO
# ==================================================

PASTA_ATUAL = Path(__file__).parent
ARQUIVO = PASTA_ATUAL / "5 - base_pedidos_tratada.csv"
ARQUIVO_GEOJSON = PASTA_ATUAL / "brasil_estados.json"

with open(ARQUIVO_GEOJSON, encoding="utf-8") as f:
    geojson_brasil = json.load(f)


df = pd.read_csv(ARQUIVO, sep=";", encoding="utf-8-sig")

df["Status_Prazo"] = df["Status_Prazo"].fillna("Não Coletado")

# ==================================================
# DATAS
# ==================================================

for coluna in [
    "Data_Base",
    "Data_Entrega",
    "DataColetadoTransportadora",
]:
    df[coluna] = pd.to_datetime(df[coluna], errors="coerce")


# ==================================================
# APP
# ==================================================

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

FILTROS_STORE = dcc.Store(id="filtros_globais")

TEMA_STORE = dcc.Store(id="tema_dashboard", data="escuro")


TEMAS = {
    "escuro": {
        "fundo": "#28183A",
        "card": "#37224D",
        "texto": "#FFFFFF",
        "texto2": "#757575",
        "borda": "#4D3766",
        "magenta": "#FF69B4",
        "linha_odd": "#332146",
        "linha_even": "#28183A",
        "input": "#37224D",
    },
    "claro": {
        "fundo": "#F5F7FA",
        "card": "#FFFFFF",
        "texto": "#202020",
        "texto2": "#757575",
        "borda": "#DADADA",
        "magenta": "#FF69B4",
        "linha_odd": "#F7F7F7",
        "linha_even": "#FFFFFF",
        "input": "#FFFFFF",
    },
}


TITULO_GRAFICO = {
    "backgroundColor": "#FF69B4",
    "color": "white",
    "fontWeight": "bold",
    "fontSize": "18px",
    "textAlign": "center",
    "padding": "10px",
    "borderTopLeftRadius": "12px",
    "borderTopRightRadius": "12px",
}

COR_FUNDO = "#28183A"
COR_CARD = "#37224D"
COR_TEXTO = "white"
COR_BORDA = "#4D3766"


ABAS = dbc.Tabs(
    [
        dbc.Tab(
            label="Performance",
            tab_id="performance",
            label_style={
                "color": "#FF69B4",
                "fontWeight": "bold",
            },
            active_label_style={
                "color": "#FF69B4",
                "fontWeight": "bold",
            },
            tab_style={
                "border": "none",
            },
        ),
        dbc.Tab(
            label="Geografia OTD",
            tab_id="geografico",
            label_style={
                "color": "#FF69B4",
                "fontWeight": "bold",
            },
            active_label_style={
                "color": "#FF69B4",
                "fontWeight": "bold",
            },
            tab_style={
                "border": "none",
            },
            active_tab_style={
                "border": "none",
            },
        ),
        dbc.Tab(
            label="Base de Dados",
            tab_id="base",
            label_style={
                "color": "#FF69B4",
                "fontWeight": "bold",
            },
            active_label_style={
                "color": "#FF69B4",
                "fontWeight": "bold",
            },
            tab_style={
                "border": "none",
            },
            active_tab_style={
                "border": "none",
            },
        ),
    ],
    id="abas",
    active_tab="performance",
)

server = app.server


@app.callback(
    Output("abas", "style"),
    Input("tema_dashboard", "data"),
)
def atualizar_abas(tema):

    return {"backgroundColor": TEMAS[tema]["fundo"]}


# ==================================================
# LAYOUT
# ==================================================


def aplicar_tema(fig, tema):

    cores = TEMAS[tema]

    fig.update_layout(
        paper_bgcolor=cores["fundo"],
        plot_bgcolor=cores["fundo"],
        font=dict(color=cores["texto"]),
        legend=dict(font=dict(color=cores["texto"])),
    )

    if tema == "escuro":

        grid = "rgba(255,255,255,0.10)"

    else:

        grid = "rgba(0,0,0,0.10)"

    fig.update_xaxes(gridcolor=grid, color=cores["texto"])

    fig.update_yaxes(gridcolor=grid, color=cores["texto"])

    return fig


app.layout = dbc.Container(
    [
        FILTROS_STORE,
        TEMA_STORE,
        html.Div(id="css_tema"),
        dbc.Row(
            dbc.Col(
                dbc.Button(
                    "🌙 / ☀️ Alterar Tema",
                    id="btn_tema",
                    n_clicks=0,
                ),
                width="auto",
            ),
            justify="end",
            className="mt-2",
        ),
        html.H2(
            "Performance Digital",
            id="titulo_dashboard",
            className="text-center mt-3 mb-4",
            style={"fontWeight": "bold"},
        ),
        ABAS,
        html.Br(),
        html.Div(
            id="aba_performance",
            children=[
                # FILTROS
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.DatePickerRange(
                                id="filtro_data",
                                start_date=df["Data_Base"].min(),
                                end_date=df["Data_Base"].max(),
                                display_format="DD/MM/YYYY",
                                style={
                                    "width": "100%",
                                },
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="filtro_canal",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(df["Canal"].dropna().unique())
                                ],
                                multi=True,
                                placeholder="Canal",
                            ),
                            width=2,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="filtro_origem",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(
                                        df["Origem_Faturamento"].dropna().unique()
                                    )
                                ],
                                multi=True,
                                placeholder="Origem",
                            ),
                            width=2,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="filtro_transportadora",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(
                                        df["Transportadora"].dropna().unique()
                                    )
                                ],
                                multi=True,
                                placeholder="Transportadora",
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="filtro_uf",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(df["UF_ENTREGA"].dropna().unique())
                                ],
                                multi=True,
                                placeholder="UF",
                            ),
                            width=2,
                        ),
                    ],
                    className="justify-content-center align-items-center g-3",
                ),
                html.Div(style={"height": "20px"}),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H6(
                                            "Pacotes",
                                            id="titulo_kpi_1",
                                        ),
                                        html.H3(
                                            id="kpi_fulfillments",
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "height": "120px",
                                    },
                                ),
                                id="card_kpi_1",
                                style={
                                    "backgroundColor": COR_CARD,
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.30)",
                                    "borderRadius": "12px",
                                    "border": f"1px solid {COR_BORDA}",
                                },
                            )
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H6(
                                            "OTD",
                                            id="titulo_kpi_2",
                                        ),
                                        html.H3(
                                            id="kpi_otd",
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "height": "120px",
                                    },
                                ),
                                id="card_kpi_2",
                                style={
                                    "backgroundColor": COR_CARD,
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.30)",
                                    "borderRadius": "12px",
                                    "border": f"1px solid {COR_BORDA}",
                                },
                            )
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H6(
                                            "Lead Time Médio",
                                            id="titulo_kpi_3",
                                        ),
                                        html.H3(
                                            id="kpi_lead",
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "height": "120px",
                                    },
                                ),
                                id="card_kpi_3",
                                style={
                                    "backgroundColor": COR_CARD,
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.30)",
                                    "borderRadius": "12px",
                                    "border": f"1px solid {COR_BORDA}",
                                },
                            )
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H6(
                                            "Saldo Médio Lead Time",
                                            id="titulo_kpi_4",
                                        ),
                                        html.H3(
                                            id="kpi_saldo",
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "height": "120px",
                                    },
                                ),
                                id="card_kpi_4",
                                style={
                                    "backgroundColor": COR_CARD,
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.30)",
                                    "borderRadius": "12px",
                                    "border": f"1px solid {COR_BORDA}",
                                },
                            )
                        ),
                    ],
                    className="justify-content-center",
                ),
                html.Br(),
                # LINHA 1
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    "Origem Faturamento",
                                    id="titulo_origem",
                                    style=TITULO_GRAFICO,
                                ),
                                dcc.Graph(
                                    id="graf_origem", config={"displayModeBar": False}
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    "Status Prazo",
                                    id="titulo_status",
                                    style=TITULO_GRAFICO,
                                ),
                                dcc.Graph(
                                    id="graf_status", config={"displayModeBar": False}
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    "Canal", id="titulo_canal", style=TITULO_GRAFICO
                                ),
                                dcc.Graph(
                                    id="graf_canal", config={"displayModeBar": False}
                                ),
                            ],
                            width=4,
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Div("OTD por UF", id="titulo_uf", style=TITULO_GRAFICO),
                        dcc.Graph(
                            id="graf_uf",
                            config={"displayModeBar": False},
                            style={"width": "1800px"},
                        ),
                    ],
                    style={
                        "overflowX": "auto",
                        "marginTop": "15px",
                        "marginBottom": "15px",
                    },
                ),
                html.Div(
                    [
                        html.Div(
                            "OTD por Transportadora",
                            id="titulo_otd_transportadora",
                            style=TITULO_GRAFICO,
                        ),
                        dcc.Graph(
                            id="graf_otd_transportadora",
                            config={"displayModeBar": False},
                            style={"width": "100%"},
                        ),
                    ],
                    style={
                        "overflowX": "auto",
                        "marginTop": "15px",
                        "marginBottom": "15px",
                    },
                ),
                html.Br(),
                # LINHA 3
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    "Top Transportadoras",
                                    id="titulo_top_transportadora",
                                    style=TITULO_GRAFICO,
                                ),
                                dcc.Graph(
                                    id="graf_transportadora",
                                    config={"displayModeBar": False},
                                ),
                            ],
                            width=12,
                        )
                    ]
                ),
            ],
        ),
        html.Div(
            id="aba_geografico",
            style={"display": "none"},
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                dcc.DatePickerRange(
                                    id="geo_data",
                                    start_date=df["Data_Base"].min(),
                                    end_date=df["Data_Base"].max(),
                                    display_format="DD/MM/YYYY",
                                ),
                                style={
                                    "width": "100%",
                                },
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="geo_canal",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(df["Canal"].dropna().unique())
                                ],
                                multi=True,
                                placeholder="Canal",
                            ),
                            width=2,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="geo_origem",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(
                                        df["Origem_Faturamento"].dropna().unique()
                                    )
                                ],
                                multi=True,
                                placeholder="Origem",
                            ),
                            width=2,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="geo_transportadora",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(
                                        df["Transportadora"].dropna().unique()
                                    )
                                ],
                                multi=True,
                                placeholder="Transportadora",
                            ),
                            width=3,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="geo_uf",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(df["UF_ENTREGA"].dropna().unique())
                                ],
                                multi=True,
                                placeholder="UF",
                            ),
                            width=2,
                        ),
                    ],
                    className="justify-content-center align-items-center g-3",
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    "OTD Geral por UF",
                                    id="titulo_mapa",
                                    style=TITULO_GRAFICO,
                                ),
                                dcc.Graph(
                                    id="mapa_otd_uf", config={"scrollZoom": False}
                                ),
                            ],
                            width=12,
                        )
                    ]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    "OTD por Região",
                                    id="titulo_regiao",
                                    style=TITULO_GRAFICO,
                                ),
                                dcc.Graph(id="graf_regiao_otd"),
                                html.Br(),
                                html.Div(
                                    "OTD Transportadora x Região",
                                    id="titulo_heat_regiao",
                                    style=TITULO_GRAFICO,
                                ),
                                dcc.Graph(id="heatmap_regiao_transportadora"),
                                html.Br(),
                                html.Div(
                                    "OTD Transportadora x UF",
                                    id="titulo_heat_uf",
                                    style=TITULO_GRAFICO,
                                ),
                                dcc.Graph(id="heatmap_uf_transportadora"),
                            ],
                            width=12,
                        )
                    ]
                ),
            ],
        ),
        html.Div(
            id="aba_base",
            style={"display": "none"},
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id="base_canal",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(df["Canal"].dropna().unique())
                                ],
                                multi=True,
                                placeholder="Canal",
                            ),
                            width=2,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="base_origem",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(
                                        df["Origem_Faturamento"].dropna().unique()
                                    )
                                ],
                                multi=True,
                                placeholder="Origem",
                            ),
                            width=2,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="base_transportadora",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(
                                        df["Transportadora"].dropna().unique()
                                    )
                                ],
                                multi=True,
                                placeholder="Transportadora",
                            ),
                            width=4,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="base_uf",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(df["UF_ENTREGA"].dropna().unique())
                                ],
                                multi=True,
                                placeholder="UF",
                            ),
                            width=2,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id="base_status",
                                options=[
                                    {"label": x, "value": x}
                                    for x in sorted(
                                        df["Status_Prazo"].dropna().unique()
                                    )
                                ],
                                multi=True,
                                placeholder="Status",
                            ),
                            width=2,
                        ),
                    ],
                    className="mb-3",
                ),
                html.Br(),
                dash_table.DataTable(
                    id="tabela",
                    fixed_rows={"headers": True},
                    page_current=0,
                    page_size=1000,
                    page_action="custom",
                    style_table={
                        "overflowX": "auto",
                        "minWidth": "100%",
                        "maxWidth": "100%",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#332146",
                            "color": "white",
                        },
                        {
                            "if": {"row_index": "even"},
                            "backgroundColor": "#28183A",
                            "color": "white",
                        },
                    ],
                    style_header={
                        "backgroundColor": "#FF69B4",
                        "color": "white",
                        "fontWeight": "bold",
                        "textAlign": "center",
                    },
                ),
            ],
        ),
    ],
    id="container_principal",
    fluid=True,
    style={
        "minHeight": "100vh",
        "width": "100%",
        "paddingTop": "0px",
        "marginTop": "0px",
        "paddingBottom": "30px",
    },
)


# ==================================================
# CALLBACK
# ==================================================


@app.callback(
    Output("css_tema", "children"),
    Input("tema_dashboard", "data"),
)
def atualizar_css_dropdown(tema):

    cores = TEMAS[tema]

    return html.Style(f"""

    html,
    body,
    #react-entry-point,
    #_dash-app-content,
    .container-fluid {{
        background-color: {cores["fundo"]} !important;
    }}


    /* FUNDO DA PÁGINA */

    html {{
        background-color: {cores["fundo"]} !important;
    }}

    body {{
        background-color: {cores["fundo"]} !important;
    }}

    #react-entry-point {{
        background-color: {cores["fundo"]} !important;
    }}

    ._dash-loading {{
        background-color: {cores["fundo"]} !important;
    }}

    .container-fluid {{
        background-color: {cores["fundo"]} !important;
    }}

    /* DROPDOWNS */

    .Select-control {{
        background-color: {cores["input"]} !important;
        border: 1px solid {cores["borda"]} !important;
        color: {cores["texto"]} !important;
        height: 38px !important;
    }}

    .Select-placeholder {{
        color: {cores["texto"]} !important;
    }}

    .Select-value-label {{
        color: {cores["texto"]} !important;
    }}

    .Select-menu-outer {{
        background-color: {cores["card"]} !important;
    }}

    /* DATE PICKER */

    .DateRangePickerInput {{
        background-color: {cores["input"]} !important;
        border: 1px solid {cores["borda"]} !important;
        border-radius: 4px !important;
        height: 38px !important;
    }}

    .DateInput {{
        background-color: {cores["input"]} !important;
    }}

    .DateInput_input {{
        background-color: {cores["input"]} !important;
        color: {cores["texto"]} !important;
        border-radius: 0px !important;
    }}

    .DateRangePickerInput_arrow {{
        color: {cores["texto"]} !important;
    }}

    """)


@app.callback(
    Output("tema_dashboard", "data"),
    Input("btn_tema", "n_clicks"),
    State("tema_dashboard", "data"),
)
def trocar_tema(n_clicks, tema):

    if not n_clicks:
        return tema

    return "claro" if tema == "escuro" else "escuro"


@app.callback(
    Output("filtros_globais", "data"),
    Input("filtro_data", "start_date"),
    Input("filtro_data", "end_date"),
    Input("filtro_canal", "value"),
    Input("filtro_origem", "value"),
    Input("filtro_transportadora", "value"),
    Input("filtro_uf", "value"),
)
def salvar_filtros(
    start_date,
    end_date,
    canal,
    origem,
    transportadora,
    uf,
):

    return {
        "start_date": start_date,
        "end_date": end_date,
        "canal": canal,
        "origem": origem,
        "transportadora": transportadora,
        "uf": uf,
    }


@app.callback(
    Output("geo_data", "start_date"),
    Output("geo_data", "end_date"),
    Output("geo_canal", "value"),
    Output("geo_origem", "value"),
    Output("geo_transportadora", "value"),
    Output("geo_uf", "value"),
    Input("filtros_globais", "data"),
)
def atualizar_filtros_geo(data):

    if not data:
        return (
            df["Data_Base"].min(),
            df["Data_Base"].max(),
            None,
            None,
            None,
            None,
        )

    return (
        data["start_date"],
        data["end_date"],
        data["canal"],
        data["origem"],
        data["transportadora"],
        data["uf"],
    )


@app.callback(
    Output("aba_performance", "style"),
    Output("aba_geografico", "style"),
    Output("aba_base", "style"),
    Input("abas", "active_tab"),
    Input("tema_dashboard", "data"),
)
def trocar_aba(aba, tema):

    fundo = TEMAS[tema]["fundo"]

    return (
        {
            "display": "block" if aba == "performance" else "none",
            "backgroundColor": fundo,
        },
        {
            "display": "block" if aba == "geografico" else "none",
            "backgroundColor": fundo,
        },
        {
            "display": "block" if aba == "base" else "none",
            "backgroundColor": fundo,
        },
    )


@app.callback(
    Output("tabela", "data"),
    Output("tabela", "columns"),
    Input("tabela", "page_current"),
    Input("base_canal", "value"),
    Input("base_origem", "value"),
    Input("base_transportadora", "value"),
    Input("base_uf", "value"),
    Input("base_status", "value"),
)
def atualizar_tabela(
    page_current,
    base_canal,
    base_origem,
    base_transportadora,
    base_uf,
    base_status,
):

    dff_base = df.copy()

    if base_canal:
        dff_base = dff_base[dff_base["Canal"].isin(base_canal)]

    if base_origem:
        dff_base = dff_base[dff_base["Origem_Faturamento"].isin(base_origem)]

    if base_transportadora:
        dff_base = dff_base[dff_base["Transportadora"].isin(base_transportadora)]

    if base_uf:
        dff_base = dff_base[dff_base["UF_ENTREGA"].isin(base_uf)]

    if base_status:
        dff_base = dff_base[dff_base["Status_Prazo"].isin(base_status)]

    page_size = 1000

    inicio = page_current * page_size
    fim = inicio + page_size

    tabela = dff_base.iloc[inicio:fim].copy()

    for coluna_data in [
        "DataColetadoTransportadora",
        "Data_Entrega",
        "Data_Prometida",
        "Data_Base",
    ]:

        if coluna_data in tabela.columns:

            tabela[coluna_data] = pd.to_datetime(
                tabela[coluna_data], errors="coerce"
            ).dt.strftime("%d/%m/%y")

    return (tabela.to_dict("records"), [{"name": c, "id": c} for c in tabela.columns])


@app.callback(
    [
        Output("kpi_fulfillments", "children"),
        Output("kpi_otd", "children"),
        Output("kpi_lead", "children"),
        Output("kpi_saldo", "children"),
        Output("graf_origem", "figure"),
        Output("graf_status", "figure"),
        Output("graf_canal", "figure"),
        Output("graf_uf", "figure"),
        Output("graf_otd_transportadora", "figure"),
        Output("graf_transportadora", "figure"),
    ],
    [
        Input("filtro_data", "start_date"),
        Input("filtro_data", "end_date"),
        Input("filtro_canal", "value"),
        Input("filtro_origem", "value"),
        Input("filtro_transportadora", "value"),
        Input("filtro_uf", "value"),
        Input("tema_dashboard", "data"),
    ],
)
def atualizar_dashboard(
    start_date,
    end_date,
    canal,
    origem,
    transportadora,
    uf,
    tema,
):

    try:

        print("\nCallback executado")

        dff = df.copy()

        data_ini = pd.to_datetime(start_date)
        data_fim = pd.to_datetime(end_date)

        dff = dff[(dff["Data_Base"] >= data_ini) & (dff["Data_Base"] <= data_fim)]

        if canal:
            dff = dff[dff["Canal"].isin(canal)]

        if origem:
            dff = dff[dff["Origem_Faturamento"].isin(origem)]

        if transportadora:
            dff = dff[dff["Transportadora"].isin(transportadora)]

        if uf:
            dff = dff[dff["UF_ENTREGA"].isin(uf)]

        total = dff["Pedido_Fulfillment"].nunique()

        base_otd = dff[dff["Status_Prazo"].isin(["No Prazo", "Fora do Prazo"])]

        otd = (
            (base_otd["Status_Prazo"].eq("No Prazo").sum()) / max(len(base_otd), 1)
        ) * 100

        lead = round(dff["Lead_Time_Real"].mean(), 1)

        saldo = round(dff["Dias_Diferenca"].mean(), 1)

        fig_origem = px.pie(
            dff,
            names="Origem_Faturamento",
            hole=0.6,
            title="",
            color="Origem_Faturamento",
            color_discrete_map={
                "Loja": "#636EFA",  # azul atual
                "CD": "#FF69B4",  # rosa
            },
        )

        fig_origem = aplicar_tema(fig_origem, tema)

        fig_origem.update_traces(textfont=dict(color=TEMAS[tema]["texto"]))

        fig_origem.update_layout(
            paper_bgcolor=TEMAS[tema]["fundo"],
        )

        dff["Status_Prazo_Ajustado"] = dff["Status_Prazo"].fillna("Não Coletado")

        fig_status = px.pie(
            dff,
            names="Status_Prazo_Ajustado",
            hole=0.6,
            title="",
            color="Status_Prazo_Ajustado",
            color_discrete_map={
                "No Prazo": "#636EFA",  # azul
                "Não Coletado": "#FF69B4",  # rosa
                "Fora do Prazo": "#FF0000",  # vermelho
            },
        )

        fig_status = aplicar_tema(fig_status, tema)
        fig_status.update_traces(textfont=dict(color=TEMAS[tema]["texto"]))

        canal_df = dff.groupby("Canal").size().reset_index(name="Fulfillments")

        canal_df["Rotulo"] = canal_df["Fulfillments"].apply(
            lambda x: f"{x:,}".replace(",", ".")
        )

        fig_canal = px.bar(
            canal_df,
            x="Canal",
            y="Fulfillments",
            text="Rotulo",
            title="",
        )

        fig_canal = aplicar_tema(fig_canal, tema)

        fig_canal.update_traces(
            textposition="outside", textfont=dict(color=TEMAS[tema]["texto"])
        )

        uf_otd = (
            base_otd.groupby("UF_ENTREGA")["Status_Prazo"]
            .apply(lambda x: (x.eq("No Prazo").mean() * 100))
            .reset_index(name="OTD")
        )

        uf_otd["OTD"] = uf_otd["OTD"].round(1)

        uf_otd = uf_otd.sort_values("OTD", ascending=False)

        fig_uf = px.line(
            uf_otd,
            x="UF_ENTREGA",
            y="OTD",
            markers=True,
            text="OTD",
            title="",
        )

        fig_uf = aplicar_tema(fig_uf, tema)

        fig_uf.update_traces(texttemplate="%{y:.1f}%", textposition="top center")

        fig_uf.update_layout(
            width=max(len(uf_otd) * 80, 1800),
            height=500,
            plot_bgcolor=TEMAS[tema]["fundo"],
            paper_bgcolor=TEMAS[tema]["fundo"],
            hovermode="x unified",
            margin=dict(t=80, l=60, r=30, b=60),  # aumente de 60 para 80 ou 100
        )

        fig_uf.update_yaxes(range=[max(0, uf_otd["OTD"].min() - 2), 100.5])

        transp = (
            base_otd.groupby("Transportadora")
            .agg(Fulfillments=("Pedido_Fulfillment", "count"))
            .reset_index()
            .sort_values("Fulfillments", ascending=False)
            .head(15)
        )

        transp_otd = (
            base_otd.groupby("Transportadora")
            .agg(
                OTD=("Status_Prazo", lambda x: x.eq("No Prazo").mean() * 100),
                Fulfillments=("Pedido_Fulfillment", "count"),
            )
            .reset_index()
        )

        transp_otd["OTD"] = transp_otd["OTD"].round(1)

        transp_otd = transp_otd.sort_values("OTD", ascending=False)

        transp["Rotulo"] = transp["Fulfillments"].apply(
            lambda x: f"{x:,}".replace(",", ".")
        )

        fig_otd_transportadora = px.bar(
            transp_otd,
            x="Transportadora",
            y="OTD",
            text="OTD",
        )

        fig_otd_transportadora.update_traces(
            marker_color=TEMAS[tema]["magenta"],
            texttemplate="%{y:.1f}%",
            textposition="outside",
            cliponaxis=False,
        )

        fig_otd_transportadora.update_traces(width=0.45)

        fig_otd_transportadora.update_layout(
            autosize=True,
            height=450,
            bargap=0.08,
            xaxis_title="",
            yaxis_title="OTD %",
            margin=dict(
                t=80,
                l=40,
                r=40,
                b=80,
            ),
        )

        fig_otd_transportadora.update_yaxes(
            range=[max(0, transp_otd["OTD"].min() - 5), 100]
        )

        fig_otd_transportadora = aplicar_tema(fig_otd_transportadora, tema)

        fig_transp = px.bar(
            transp.sort_values("Fulfillments"),
            x="Fulfillments",
            y="Transportadora",
            orientation="h",
            text="Rotulo",
            title="",
        )

        fig_transp = aplicar_tema(fig_transp, tema)

        fig_transp.update_traces(
            textposition="outside",
            cliponaxis=False,
            marker_color=TEMAS[tema]["magenta"],
        )

        fig_transp.update_layout(
            height=500,
            yaxis_title="",
            xaxis_title="Fulfillments",
            margin=dict(l=80, r=80, t=40, b=50),
        )

        fig_transp.update_traces(textposition="outside", cliponaxis=False)

        fig_transp.update_layout(margin=dict(t=80))

        return (
            f"{total:,.0f}",
            f"{otd:.2f}%",
            f"{lead:.1f}",
            f"{saldo:.1f}",
            fig_origem,
            fig_status,
            fig_canal,
            fig_uf,
            fig_otd_transportadora,
            fig_transp,
        )

    except Exception as e:

        print("\nERRO NO CALLBACK")
        traceback.print_exc()

        fig_vazia = go.Figure()

        return (
            "Erro",
            "Erro",
            "Erro",
            "Erro",
            fig_vazia,
            fig_vazia,
            fig_vazia,
            fig_vazia,
            fig_vazia,
            fig_vazia,
        )


@app.callback(
    Output("mapa_otd_uf", "figure"),
    Output("graf_regiao_otd", "figure"),
    Output("heatmap_regiao_transportadora", "figure"),
    Output("heatmap_uf_transportadora", "figure"),
    Input("geo_data", "start_date"),
    Input("geo_data", "end_date"),
    Input("geo_canal", "value"),
    Input("geo_origem", "value"),
    Input("geo_transportadora", "value"),
    Input("geo_uf", "value"),
    Input("tema_dashboard", "data"),
)
def atualizar_geografia(
    start_date,
    end_date,
    canal,
    origem,
    transportadora,
    uf,
    tema,
):

    dff = df.copy()

    data_ini = pd.to_datetime(start_date)
    data_fim = pd.to_datetime(end_date)

    dff = dff[(dff["Data_Base"] >= data_ini) & (dff["Data_Base"] <= data_fim)]

    if canal:
        dff = dff[dff["Canal"].isin(canal)]

    if origem:
        dff = dff[dff["Origem_Faturamento"].isin(origem)]

    if transportadora:
        dff = dff[dff["Transportadora"].isin(transportadora)]

    if uf:
        dff = dff[dff["UF_ENTREGA"].isin(uf)]

    base_otd = dff[dff["Status_Prazo"].isin(["No Prazo", "Fora do Prazo"])]

    base_otd_regiao = base_otd[base_otd["Região"].notna()]

    base_otd_regiao = base_otd_regiao[
        base_otd_regiao["Região"] != "LOCAL NÃO IDENTIFICADO"
    ]

    regiao_otd = (
        base_otd_regiao.groupby("Região")["Status_Prazo"]
        .apply(lambda x: x.eq("No Prazo").mean() * 100)
        .reset_index(name="OTD")
    )

    fig_regiao_otd = px.bar(regiao_otd, x="Região", y="OTD", text="OTD")

    fig_regiao_otd = aplicar_tema(fig_regiao_otd, tema)

    fig_regiao_otd.update_traces(texttemplate="%{y:.1f}%")

    heat_regiao = (
        base_otd_regiao.groupby(["Transportadora", "Região"])["Status_Prazo"]
        .apply(lambda x: x.eq("No Prazo").mean() * 100)
        .reset_index(name="OTD")
    )

    heat_regiao = heat_regiao.pivot(
        index="Transportadora", columns="Região", values="OTD"
    )

    fig_heat_regiao = px.imshow(
        heat_regiao, text_auto=".1f", color_continuous_scale="RdYlGn", aspect="auto"
    )

    fig_heat_regiao = aplicar_tema(fig_heat_regiao, tema)

    fig_heat_regiao.update_xaxes(side="top")

    fig_heat_regiao.update_layout(height=600, xaxis_title="", yaxis_title="")

    fig_heat_regiao.update_xaxes(side="top", tickfont=dict(size=13))

    fig_heat_regiao.update_yaxes(tickfont=dict(size=11))

    fig_heat_regiao.update_traces(textfont={"color": TEMAS[tema]["texto"]})

    fig_heat_regiao.update_layout(height=600)

    heat_uf = (
        base_otd.groupby(["Transportadora", "UF_ENTREGA"])["Status_Prazo"]
        .apply(lambda x: x.eq("No Prazo").mean() * 100)
        .reset_index(name="OTD")
    )

    heat_uf = heat_uf.pivot(index="Transportadora", columns="UF_ENTREGA", values="OTD")

    fig_heat_uf = px.imshow(
        heat_uf, text_auto=".1f", color_continuous_scale="RdYlGn", aspect="auto"
    )

    fig_heat_uf = aplicar_tema(fig_heat_uf, tema)

    fig_heat_uf.update_layout(height=900, xaxis_title="", yaxis_title="")

    fig_heat_uf.update_xaxes(side="top", tickangle=0)

    fig_heat_uf.update_yaxes(tickfont=dict(size=10))

    fig_heat_uf.update_traces(textfont={"color": TEMAS[tema]["texto"]})

    fig_heat_uf.update_layout(height=500)

    uf_mapa = (
        base_otd.groupby("UF_ENTREGA")["Status_Prazo"]
        .apply(lambda x: x.eq("No Prazo").mean() * 100)
        .reset_index(name="OTD")
    )

    uf_mapa["OTD"] = uf_mapa["OTD"].round(1)

    uf_mapa["ROTULO"] = (
        uf_mapa["UF_ENTREGA"] + "<br>" + uf_mapa["OTD"].astype(str) + "%"
    )

    coordenadas_uf = {
        "AC": (-70.0, -9.0),
        "AL": (-36.5, -9.6),
        "AP": (-51.5, 1.0),
        "AM": (-63.0, -4.0),
        "BA": (-41.5, -12.5),
        "CE": (-39.5, -5.0),
        "DF": (-47.9, -15.8),
        "ES": (-40.3, -19.5),
        "GO": (-49.5, -16.0),
        "MA": (-45.5, -5.0),
        "MT": (-56.0, -13.0),
        "MS": (-54.5, -20.5),
        "MG": (-44.0, -18.5),
        "PA": (-52.0, -3.5),
        "PB": (-36.0, -7.0),
        "PE": (-37.5, -8.5),
        "PI": (-43.0, -7.0),
        "PR": (-51.0, -24.5),
        "RJ": (-43.5, -22.5),
        "RN": (-36.5, -5.5),
        "RO": (-63.0, -11.0),
        "RR": (-61.5, 2.0),
        "RS": (-53.0, -30.0),
        "SC": (-50.0, -27.0),
        "SE": (-37.3, -10.5),
        "SP": (-48.0, -22.0),
        "TO": (-48.3, -10.5),
    }

    mapa_otd_uf = px.choropleth(
        uf_mapa,
        geojson=geojson_brasil,
        locations="UF_ENTREGA",
        featureidkey="properties.SIGLA",
        color="OTD",
        color_continuous_scale=[
            "#D32F2F",
            "#F57C00",
            "#FBC02D",
            "#66BB6A",
            "#2E7D32",
        ],
        hover_data={"UF_ENTREGA": True, "OTD": ":.1f"},
    )

    mapa_otd_uf.update_geos(
        bgcolor=TEMAS[tema]["fundo"],
        lakecolor=TEMAS[tema]["fundo"],
        landcolor=TEMAS[tema]["fundo"],
        fitbounds="locations",
        showcountries=False,
        showcoastlines=False,
        showland=False,
        showframe=False,
        visible=False,
    )

    mapa_otd_uf.update_layout(
        height=750,
        paper_bgcolor=TEMAS[tema]["fundo"],
        plot_bgcolor=TEMAS[tema]["fundo"],
        coloraxis_colorbar=dict(
            title="OTD %",
            tickfont=dict(color=TEMAS[tema]["texto"]),
            title_font=dict(color=TEMAS[tema]["texto"]),
            y=0.45,  # desce a barra
            len=0.99,  # reduz altura
        ),
    )

    for _, row in uf_mapa.iterrows():

        uf_estado = row["UF_ENTREGA"]

        if uf_estado in coordenadas_uf:

            lon, lat = coordenadas_uf[uf_estado]

            mapa_otd_uf.add_trace(
                go.Scattergeo(
                    lon=[lon],
                    lat=[lat],
                    mode="markers+text",
                    marker=dict(
                        symbol="circle",
                        size=60,
                        color=(
                            TEMAS["claro"]["card"]
                            if tema == "escuro"
                            else TEMAS["escuro"]["card"]
                        ),
                        line=dict(
                            color="rgba(150,150,150,0.50)",
                            width=1,
                        ),
                    ),
                    text=[f"{uf_estado} {row['OTD']:.0f}%"],
                    textposition="middle center",
                    textfont=dict(
                        size=13,
                        color="#202020" if tema == "escuro" else "#FFFFFF",
                    ),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

    mapa_otd_uf.update_layout(
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0,
        ),
        height=700,
    )

    return (
        mapa_otd_uf,
        fig_regiao_otd,
        fig_heat_regiao,
        fig_heat_uf,
    )


@app.callback(
    Output("titulo_dashboard", "style"),
    Output("titulo_kpi_1", "style"),
    Output("titulo_kpi_2", "style"),
    Output("titulo_kpi_3", "style"),
    Output("titulo_kpi_4", "style"),
    Output("kpi_fulfillments", "style"),
    Output("kpi_otd", "style"),
    Output("kpi_lead", "style"),
    Output("kpi_saldo", "style"),
    Input("tema_dashboard", "data"),
)
def atualizar_textos(tema):

    cor = TEMAS[tema]["texto"]

    estilo_titulo = {
        "color": cor,
        "fontWeight": "bold",
    }

    estilo_h6 = {
        "textAlign": "center",
        "color": cor,
    }

    estilo_kpi = {
        "textAlign": "center",
        "fontWeight": "bold",
        "fontSize": "42px",
        "color": cor,
    }

    return (
        estilo_titulo,
        estilo_h6,
        estilo_h6,
        estilo_h6,
        estilo_h6,
        estilo_kpi,
        estilo_kpi,
        estilo_kpi,
        estilo_kpi,
    )


@app.callback(
    Output("tabela", "style_table"),
    Output("tabela", "style_cell"),
    Output("tabela", "style_data_conditional"),
    Output("tabela", "style_header"),
    Input("tema_dashboard", "data"),
)
def atualizar_tabela_tema(tema):

    return (
        {
            "overflowX": "auto",
            "minWidth": "100%",
            "maxWidth": "100%",
            "backgroundColor": TEMAS[tema]["fundo"],
        },
        {
            "backgroundColor": TEMAS[tema]["card"],
            "color": TEMAS[tema]["texto"],
            "textAlign": "left",
            "fontSize": 12,
            "minWidth": "150px",
            "width": "150px",
            "maxWidth": "300px",
        },
        [
            {
                "if": {"row_index": "odd"},
                "backgroundColor": TEMAS[tema]["linha_odd"],
                "color": TEMAS[tema]["texto"],
            },
            {
                "if": {"row_index": "even"},
                "backgroundColor": TEMAS[tema]["linha_even"],
                "color": TEMAS[tema]["texto"],
            },
        ],
        {
            "backgroundColor": TEMAS[tema]["magenta"],
            "color": "white",
            "fontWeight": "bold",
            "textAlign": "center",
        },
    )


@app.callback(
    Output("card_kpi_1", "style"),
    Output("card_kpi_2", "style"),
    Output("card_kpi_3", "style"),
    Output("card_kpi_4", "style"),
    Input("tema_dashboard", "data"),
)
def atualizar_cards(tema):

    estilo = {
        "backgroundColor": TEMAS[tema]["card"],
        "boxShadow": "0 4px 12px rgba(0,0,0,0.30)",
        "borderRadius": "12px",
        "border": f"1px solid {TEMAS[tema]['borda']}",
    }

    return estilo, estilo, estilo, estilo


@app.callback(
    Output("btn_tema", "style"),
    Input("tema_dashboard", "data"),
)
def atualizar_botao_tema(tema):

    return {
        "backgroundColor": TEMAS[tema]["input"],
        "color": TEMAS[tema]["texto"],
        "border": f"1px solid {TEMAS[tema]['borda']}",
        "height": "38px",
        "padding": "0px 15px",
        "borderRadius": "4px",
        "fontWeight": "500",
        "display": "flex",
        "alignItems": "center",
        "justifyContent": "center",
    }


@app.callback(
    Output("titulo_origem", "style"),
    Output("titulo_status", "style"),
    Output("titulo_canal", "style"),
    Output("titulo_uf", "style"),
    Output("titulo_otd_transportadora", "style"),
    Output("titulo_top_transportadora", "style"),
    Output("titulo_mapa", "style"),
    Output("titulo_regiao", "style"),
    Output("titulo_heat_regiao", "style"),
    Output("titulo_heat_uf", "style"),
    Input("tema_dashboard", "data"),
)
def atualizar_titulos(tema):

    estilo = {
        "backgroundColor": TEMAS[tema]["magenta"],
        "color": "white",
        "fontWeight": "bold",
        "fontSize": "18px",
        "textAlign": "center",
        "padding": "10px",
        "borderTopLeftRadius": "12px",
        "borderTopRightRadius": "12px",
    }

    return (estilo,) * 10


@app.callback(
    Output("filtro_data", "style"),
    Output("geo_data", "style"),
    Input("tema_dashboard", "data"),
)
def atualizar_datas(tema):

    return (
        {
            "width": "100%",
        },
        {
            "width": "100%",
        },
    )


@app.callback(
    Output("container_principal", "style"),
    Input("tema_dashboard", "data"),
)
def atualizar_container(tema):

    return {
        "backgroundColor": TEMAS[tema]["fundo"],
        "color": TEMAS[tema]["texto2"],
        "minHeight": "100vh",
        "width": "100%",
        "paddingTop": "0px",
        "marginTop": "0px",
        "paddingBottom": "30px",
        "transition": "0.3s",
    }


@app.callback(Output("abas", "colors"), Input("tema_dashboard", "data"))
def atualizar_cores_tabs(tema):

    return {
        "border": TEMAS[tema]["borda"],
        "primary": TEMAS[tema]["magenta"],
        "background": TEMAS[tema]["fundo"],
    }


# ==================================================
# EXECUÇÃO
# ==================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
