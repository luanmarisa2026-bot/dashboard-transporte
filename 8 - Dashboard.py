import pandas as pd
import traceback

from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc
import plotly.express as px

# ==================================================
# CARREGAMENTO
# ==================================================

from pathlib import Path

PASTA_ATUAL = Path(__file__).parent
ARQUIVO = PASTA_ATUAL / "5 - base_pedidos_tratada.csv"

df = pd.read_csv(
    ARQUIVO,
    sep=";",
    encoding="utf-8-sig"
)

df["Status_Prazo"] = df["Status_Prazo"].fillna("Não Coletado")
print("\nCOLUNAS ENCONTRADAS:")
print(df.columns.tolist())

print("\nTIPOS:")
print(df.dtypes)
# ==================================================
# DATAS
# ==================================================

for coluna in [
    "Data_Base",
    "Data_Entrega",
    "DataColetadoTransportadora",
]:
    df[coluna] = pd.to_datetime(df[coluna], errors="coerce")

print("\nDATAS")
print(df["Data_Base"].dtype)
print("Data_Base nulos:", df["Data_Base"].isna().sum())
print("Lead_Time_Real nulos:", df["Lead_Time_Real"].isna().sum())
print("Status_Prazo nulos:", df["Status_Prazo"].isna().sum())

# ==================================================
# APP
# ==================================================

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


ABAS = dbc.Tabs(
    [
        dbc.Tab(label="Performance", tab_id="performance"),
        dbc.Tab(label="Base de Dados", tab_id="base"),
    ],
    id="abas",
    active_tab="performance",
)

server = app.server

# ==================================================
# LAYOUT
# ==================================================

TITULO_GRAFICO = {
    "backgroundColor": "#E5007D",
    "color": "white",
    "fontWeight": "bold",
    "fontSize": "18px",
    "textAlign": "center",
    "padding": "10px",
    "borderTopLeftRadius": "12px",
    "borderTopRightRadius": "12px",
}

app.layout = dbc.Container(
    [
        html.H2("Performance Digital", className="text-center mt-3 mb-4"),
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
                                            "Fulfillments",
                                            style={"textAlign": "center"},
                                        ),
                                        html.H3(
                                            id="kpi_fulfillments",
                                            style={
                                                "textAlign": "center",
                                                "fontWeight": "bold",
                                                "fontSize": "42px",
                                                "color": "#333333",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "height": "120px",
                                    },
                                ),
                                style={
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.10)",
                                    "borderRadius": "12px",
                                    "border": "none",
                                },
                            )
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H6("OTD", style={"textAlign": "center"}),
                                        html.H3(
                                            id="kpi_otd",
                                            style={
                                                "textAlign": "center",
                                                "fontWeight": "bold",
                                                "fontSize": "42px",
                                                "color": "#333333",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "height": "120px",
                                    },
                                ),
                                style={
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.10)",
                                    "borderRadius": "12px",
                                    "border": "none",
                                },
                            )
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H6(
                                            "Lead Time", style={"textAlign": "center"}
                                        ),
                                        html.H3(
                                            id="kpi_lead",
                                            style={
                                                "textAlign": "center",
                                                "fontWeight": "bold",
                                                "fontSize": "42px",
                                                "color": "#333333",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "height": "120px",
                                    },
                                ),
                                style={
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.10)",
                                    "borderRadius": "12px",
                                    "border": "none",
                                },
                            )
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H6(
                                            "Saldo SLA", style={"textAlign": "center"}
                                        ),
                                        html.H3(
                                            id="kpi_saldo",
                                            style={
                                                "textAlign": "center",
                                                "fontWeight": "bold",
                                                "fontSize": "42px",
                                                "color": "#333333",
                                            },
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center",
                                        "height": "120px",
                                    },
                                ),
                                style={
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.10)",
                                    "borderRadius": "12px",
                                    "border": "none",
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
                                html.Div("Origem Faturamento", style=TITULO_GRAFICO),
                                dcc.Graph(
                                    id="graf_origem", config={"displayModeBar": False}
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Div("Status Prazo", style=TITULO_GRAFICO),
                                dcc.Graph(
                                    id="graf_status", config={"displayModeBar": False}
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.Div("Canal", style=TITULO_GRAFICO),
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
                        html.Div("OTD por UF", style=TITULO_GRAFICO),
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
                # LINHA 3
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div("Top Transportadoras", style=TITULO_GRAFICO),
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
                    sort_action="native",
                    sort_mode="multi",
                    page_size=20,
                    style_table={
                        "overflowX": "auto",
                        "minWidth": "100%",
                        "maxWidth": "100%",
                    },
                    style_cell={
                        "textAlign": "left",
                        "fontSize": 12,
                        "minWidth": "150px",
                        "width": "150px",
                        "maxWidth": "300px",
                        "whiteSpace": "normal"
                    },
                    style_data_conditional=[

                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#FFF5FA"
                        },

                        {
                            "if": {"row_index": "even"},
                            "backgroundColor": "white"
                        },

                        {
                            "if": {"state": "selected"},
                            "backgroundColor": "#E5007D",
                            "color": "white"
                        }

                    ],
                    style_header={

                    "backgroundColor": "#E5007D",

                    "color": "white",

                    "fontWeight": "bold",

                    "textAlign": "center"

                },
                ),
            ],
        ),
    ],
    fluid=True,
)


# ==================================================
# CALLBACK
# ==================================================


@app.callback(
    Output("aba_performance", "style"),
    Output("aba_base", "style"),
    Input("abas", "active_tab"),
)
def trocar_aba(aba):

    if aba == "performance":
        return ({"display": "block"}, {"display": "none"})

    return ({"display": "none"}, {"display": "block"})


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
        Output("graf_transportadora", "figure"),
        Output("tabela", "data"),
        Output("tabela", "columns"),
    ],
    [
        Input("filtro_data", "start_date"),
        Input("filtro_data", "end_date"),
        Input("filtro_canal", "value"),
        Input("filtro_origem", "value"),
        Input("filtro_transportadora", "value"),
        Input("filtro_uf", "value"),
        Input("base_canal", "value"),
        Input("base_origem", "value"),
        Input("base_transportadora", "value"),
        Input("base_uf", "value"),
        Input("base_status", "value"),
    ],
)
def atualizar_dashboard(
    start_date,
    end_date,
    canal,
    origem,
    transportadora,
    uf,
    base_canal,
    base_origem,
    base_transportadora,
    base_uf,
    base_status,
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

        fig_origem.update_layout(
            title={
                "text": "Origem Faturamento",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "color": "white"},
            },
            paper_bgcolor="white",
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

        fig_canal.update_traces(textposition="outside")

        fig_canal.update_traces(textposition="outside")

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

        fig_uf.update_traces(texttemplate="%{y:.1f}%", textposition="top center")

        largura = max(len(uf_otd) * 80, 1800)

        fig_uf.update_layout(
            width=max(len(uf_otd) * 80, 1800),
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white",
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

        transp["Rotulo"] = transp["Fulfillments"].apply(
            lambda x: f"{x:,}".replace(",", ".")
        )

        fig_transp = px.bar(
            transp.sort_values("Fulfillments"),
            x="Fulfillments",
            y="Transportadora",
            orientation="h",
            text="Rotulo",
            title="",
        )

        fig_transp.update_traces(
            textposition="outside", cliponaxis=False, marker_color="#E5007D"
        )

        fig_transp.update_layout(
            height=600,
            yaxis_title="",
            xaxis_title="Fulfillments",
            margin=dict(l=300, r=50, t=80, b=50),
        )

        fig_transp.update_traces(textposition="outside", cliponaxis=False)

        fig_transp.update_layout(margin=dict(t=80))

        dff_base = dff.copy()

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

        tabela = dff_base.copy()


        for coluna_data in [

            "DataColetadoTransportadora",
            "Data_Entrega",
            "Data_Prometida",
            "Data_Base",

        ]:

            if coluna_data in tabela.columns:

                tabela[coluna_data] = pd.to_datetime(
                    tabela[coluna_data],
                    errors="coerce"
                ).dt.strftime("%d/%m/%y")

        return (
            f"{total:,.0f}",
            f"{otd:.2f}%",
            f"{lead:.1f}",
            f"{saldo:.1f}",
            fig_origem,
            fig_status,
            fig_canal,
            fig_uf,
            fig_transp,
            tabela.to_dict("records"),
            [{"name": i, "id": i} for i in tabela.columns],
        )

    except Exception as erro:

        print("\nERRO NO CALLBACK:")
        traceback.print_exc()

        raise


# ==================================================
# EXECUÇÃO
# ==================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8050,
        debug=False
    )
