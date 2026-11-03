import pandas as pd
import numpy as np
import unicodedata

# ==================================================
# CAMINHOS
# ==================================================

PASTA = r"C:\Users\4126648\Downloads\código\Relatório de transporte"

arquivos = {
    "base_pedidos": rf"{PASTA}\1 - base_pedidos.csv",
    "feriados": rf"{PASTA}\2 - feriados_nacionais.csv",
    "localidades": rf"{PASTA}\3 - localidades_regioes.csv",
}


# ==================================================
# FUNÇÕES
# ==================================================


def carregar_csv(caminho):

    df = pd.read_csv(caminho, sep=";", encoding="utf-8", low_memory=False)

    # remove colunas totalmente vazias
    df = df.dropna(axis=1, how="all")

    # remove colunas unnamed
    df = df.loc[:, ~df.columns.astype(str).str.contains("^Unnamed")]

    # remove espaços dos nomes
    df.columns = df.columns.str.strip()

    return df


def remover_acentos(texto):

    if pd.isna(texto):
        return texto

    return "".join(
        c
        for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    )


# ==================================================
# CARREGAMENTO
# ==================================================

base_pedidos = carregar_csv(arquivos["base_pedidos"])
feriados = carregar_csv(arquivos["feriados"])
localidades = carregar_csv(arquivos["localidades"])

# ==================================================
# PADRONIZAÇÃO DAS CIDADES
# ==================================================

base_pedidos["CIDADE_ENTREGA"] = (
    base_pedidos["CIDADE_ENTREGA"]
    .astype(str)
    .str.strip()
    .str.upper()
    .apply(remover_acentos)
    .str.replace("-", " ", regex=False)
    .str.replace("'", " ", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# ==================================================
# CORREÇÕES MANUAIS DE CIDADES
# ==================================================

correcoes_cidades = {
    "AGUAS LINDAS": "AGUAS LINDAS DE GOIAS",
    "BH": "BELO HORIZONTE",
    "BHTE": "BELO HORIZONTE",
    "CACHOEIRA DO CAMPO (OURO PRETO)": "OURO PRETO",
    "CURITIBANOSC": "CURITIBANOS",
    "DIAS DAVILA": "DIAS D AVILA",
    "EMBU DA ARTES": "EMBU DAS ARTES",
    "GOITACAZES": "CAMPOS DOS GOYTACAZES",
    "OLHO DAGUA DO CASADO": "OLHO D AGUA DO CASADO",
    "QUARACU CANDIDO SALES": "CANDIDO SALES",
    "ROBERTO (PINDORAMA)": "PINDORAMA",
    "SALVADOR BA": "SALVADOR",
    "SALVANDOR": "SALVADOR",
    "SANTA BARBARA DO OESTE": "SANTA BARBARA D OESTE",
    "SANTA BARBARA DOESTE": "SANTA BARBARA D OESTE",
    "SANTA RITA DE IBITIPOCA": "SANTA RITA DO IBITIPOCA",
    "SANTO AMARO DE CAMPOS (CAMPOS DOS GOYTACAZES)": "CAMPOS DOS GOYTACAZES",
    "SAO JOSE DO RIBEIRAO (BOM JARDIM)": "BOM JARDIM",
    "SAO PAULOQ": "SAO PAULO",
    "VILANOVA (MANHUACU)": "MANHUACU",
}

base_pedidos["CIDADE_ENTREGA"] = base_pedidos["CIDADE_ENTREGA"].replace(
    correcoes_cidades
)

localidades["Localidade Ajustada"] = (
    localidades["Localidade Ajustada"]
    .astype(str)
    .str.strip()
    .str.upper()
    .apply(remover_acentos)
    .str.replace("-", " ", regex=False)
    .str.replace("'", " ", regex=False)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# ==================================================
# LIMPEZA DAS DATAS
# ==================================================

colunas_limpeza = ["DataColetadoTransportadora", "Data_Entrega"]

for coluna in colunas_limpeza:

    base_pedidos[coluna] = (
        base_pedidos[coluna]
        .astype(str)
        .str.strip()
        .replace({"": np.nan, "nan": np.nan, "None": np.nan})
    )

# ==================================================
# CONVERSÃO DE DATAS
# ==================================================

base_pedidos["DataColetadoTransportadora"] = pd.to_datetime(
    base_pedidos["DataColetadoTransportadora"], dayfirst=True, errors="coerce"
)

base_pedidos["Data_Entrega"] = pd.to_datetime(
    base_pedidos["Data_Entrega"], dayfirst=True, errors="coerce"
)

# ==================================================
# CONSOLIDA POR PEDIDO
# ==================================================

base_pedidos_tratada = base_pedidos.groupby("Pedido_Fulfillment", as_index=False).agg(
    {
        "Pedido_Fulfillment": "first",
        "Pedido": "first",
        "LOJA_FATURAMENTO": "first",
        "Loja_Venda": "first",
        "DataColetadoTransportadora": "max",
        "Data_Entrega": "max",
        "Transportadora": "first",
        "UF_ENTREGA": "first",
        "CIDADE_ENTREGA": "first",
        "Dias_para_Entrega_Fulfillment": "max",
        "Entrega_Prazo_Transportadora": "max",
    }
)


# ==================================================
# MERGE LOCALIDADES
# ==================================================

print("Antes merge:", len(base_pedidos_tratada))

base_pedidos_tratada = base_pedidos_tratada.merge(
    localidades,
    left_on=["UF_ENTREGA", "CIDADE_ENTREGA"],
    right_on=["Estado", "Localidade Ajustada"],
    how="left",
    validate="many_to_one",
)

print("Depois merge:", len(base_pedidos_tratada))

# ==================================================
# PREENCHER LOCAIS NÃO IDENTIFICADOS
# ==================================================

base_pedidos_tratada["Região Geografica"] = base_pedidos_tratada[
    "Região Geografica"
].fillna("LOCAL NÃO IDENTIFICADO")

base_pedidos_tratada["Região"] = base_pedidos_tratada["Região"].fillna(
    "LOCAL NÃO IDENTIFICADO"
)

base_pedidos_tratada["Estado"] = base_pedidos_tratada["Estado"].fillna(
    base_pedidos_tratada["UF_ENTREGA"]
)

base_pedidos_tratada["Localidade"] = base_pedidos_tratada["Localidade"].fillna(
    "LOCAL NÃO IDENTIFICADO"
)

base_pedidos_tratada["Localidade Ajustada"] = base_pedidos_tratada[
    "Localidade Ajustada"
].fillna("LOCAL NÃO IDENTIFICADO")


# ==================================================
# ORIGEM FATURAMENTO
# ==================================================

base_pedidos_tratada["Origem_Faturamento"] = np.where(
    base_pedidos_tratada["LOJA_FATURAMENTO"].astype(str).str.strip() == "830",
    "CD",
    "Loja",
)


# ==================================================
# CANAL DE VENDA
# ==================================================

base_pedidos_tratada["Canal"] = np.where(
    base_pedidos_tratada["Loja_Venda"]
    .astype(str)
    .str.upper()
    .str.contains("MKTPMAGALU", na=False),
    "Magalu",
    "Marisa",
)


# ==================================================
# OTD - PRAZO DE ENTREGA
# ==================================================
# Data prometida

base_pedidos_tratada["Data_Prometida"] = base_pedidos_tratada[
    "DataColetadoTransportadora"
] + pd.to_timedelta(base_pedidos_tratada["Entrega_Prazo_Transportadora"], unit="D")

# Diferença entre entrega e prometido

base_pedidos_tratada["Dias_Diferenca"] = (
    base_pedidos_tratada["Data_Entrega"].dt.normalize()
    - base_pedidos_tratada["Data_Prometida"].dt.normalize()
).dt.days

base_pedidos_tratada["Dias_Diferenca"]

base_pedidos_tratada["Status_Prazo"] = pd.NA

base_pedidos_tratada.loc[
    base_pedidos_tratada["Dias_Diferenca"] <= 0, "Status_Prazo"
] = "No Prazo"

base_pedidos_tratada.loc[base_pedidos_tratada["Dias_Diferenca"] > 0, "Status_Prazo"] = (
    "Fora do Prazo"
)

base_pedidos_tratada.loc[
    (base_pedidos_tratada["Data_Entrega"].notna())
    & (base_pedidos_tratada["DataColetadoTransportadora"].isna()),
    "Status_Prazo",
] = "Problema Sistêmico"

base_pedidos_tratada["Dias_Atraso"] = np.where(
    base_pedidos_tratada["Dias_Diferenca"] > 0,
    base_pedidos_tratada["Dias_Diferenca"],
    0,
)

base_pedidos_tratada["Dias_Antecipacao"] = np.where(
    base_pedidos_tratada["Dias_Diferenca"] < 0,
    abs(base_pedidos_tratada["Dias_Diferenca"]),
    0,
)


base_pedidos_tratada["Lead_Time_Real"] = (
    base_pedidos_tratada["Data_Entrega"]
    - base_pedidos_tratada["DataColetadoTransportadora"]
).dt.days


base_pedidos_tratada["Mes_Ano"] = base_pedidos_tratada[
    "DataColetadoTransportadora"
].dt.strftime("%Y-%m")

base_pedidos_tratada["Ano"] = base_pedidos_tratada["DataColetadoTransportadora"].dt.year

base_pedidos_tratada["Mes"] = base_pedidos_tratada[
    "DataColetadoTransportadora"
].dt.month

base_pedidos_tratada["Data_Base"] = base_pedidos_tratada["DataColetadoTransportadora"]


# ==================================================
# STATUS
# ==================================================

base_pedidos_tratada["Status"] = np.where(
    (base_pedidos_tratada["Data_Entrega"].notna())
    & (base_pedidos_tratada["DataColetadoTransportadora"].isna()),
    "Problema Sistêmico",
    np.where(
        base_pedidos_tratada["Data_Entrega"].notna(),
        "Entregue",
        np.where(
            base_pedidos_tratada["DataColetadoTransportadora"].notna(),
            "Coletado",
            "Não Coletado",
        ),
    ),
)

# ==================================================
# PRIORIDADE
# ==================================================

prioridade = {
    "Problema Sistêmico": 0,
    "Não Coletado": 1,
    "Coletado": 2,
    "Entregue": 3,
}

base_pedidos_tratada["Prioridade_Status"] = base_pedidos_tratada["Status"].map(
    prioridade
)

# ==================================================
# VALIDAÇÃO DO MERGE
# ==================================================

sem_localidade = (
    base_pedidos_tratada["Região Geografica"].eq("LOCAL NÃO IDENTIFICADO").sum()
)

print("\nRESUMO")

print(f"Linhas originais: {len(base_pedidos):,}")
print(f"Fulfillments únicos: " f"{len(base_pedidos_tratada):,}")

print("\nStatus:")

print(base_pedidos_tratada["Status"].value_counts(dropna=False))

print(f"\nPedidos sem correspondência na tabela de localidades: " f"{sem_localidade:,}")


# ==================================================
# KPI - OTD E LEAD TIME
# ==================================================

total_pedidos = len(base_pedidos_tratada)

entregues = (base_pedidos_tratada["Status"] == "Entregue").sum()

coletados = (base_pedidos_tratada["Status"] == "Coletado").sum()

nao_coletados = (base_pedidos_tratada["Status"] == "Não Coletado").sum()

pedidos_otd = (base_pedidos_tratada["Status_Prazo"] == "No Prazo").sum()

pedidos_atrasados = (base_pedidos_tratada["Status_Prazo"] == "Fora do Prazo").sum()

base_entregues = base_pedidos_tratada[
    (base_pedidos_tratada["Status"] == "Entregue")
    & (base_pedidos_tratada["Status_Prazo"] != "Problema Sistêmico")
]

problema_sistemico = (base_pedidos_tratada["Status"] == "Problema Sistêmico").sum()

otd = (pedidos_otd / max(pedidos_otd + pedidos_atrasados, 1)) * 100

media_antecipacao = round(base_entregues["Dias_Antecipacao"].mean(), 2)

media_atraso = round(base_entregues["Dias_Atraso"].mean(), 2)

saldo_prazo = round(base_entregues["Dias_Diferenca"].mean(), 2)

lead_time_real = round(
    base_entregues["Lead_Time_Real"].mean(),
    2,
)

prazo_prometido_medio = round(base_entregues["Entrega_Prazo_Transportadora"].mean(), 2)

print("\n")
print("=" * 60)
print("KPIs GERAIS")
print("=" * 60)

print(f"Total de Pedidos: {total_pedidos:,}")
print(f"Entregues: {entregues:,}")
print(f"Coletados: {coletados:,}")
print(f"Não Coletados: {nao_coletados:,}")

print("\nOTD")

print(f"Problema Sistêmico: {problema_sistemico:,}")
print(f"No Prazo: {pedidos_otd:,}")
print(f"Fora do Prazo: {pedidos_atrasados:,}")
print(f"OTD: {otd:.2f}%")

print("\nLead Time")

print(f"Prazo Prometido Médio: {prazo_prometido_medio:.2f} dias")
print(f"Lead Time Real Médio: {lead_time_real:.2f} dias")

print("\nPerformance")

print(f"Dias de Antecipação Médio: {media_antecipacao:.2f}")
print(f"Dias de Atraso Médio: {media_atraso:.2f}")
print(f"Saldo Médio de Prazo: {saldo_prazo:.2f}")

print("\nTop 10 Regiões com maior antecipação")

print(
    base_entregues.groupby("Região Geografica")
    .agg(Fulfillments=("Pedido_Fulfillment", "count"), Saldo=("Dias_Diferenca", "mean"))
    .round(2)
    .sort_values("Saldo")
)

# ==================================================
# PEDIDOS SEM CORRESPONDÊNCIA DE LOCALIDADE
# ==================================================

pedidos_sem_localidade = base_pedidos_tratada[
    base_pedidos_tratada["Região Geografica"] == "LOCAL NÃO IDENTIFICADO"
].copy()

print(
    f"\nArquivo de auditoria (sem localidade): "
    f"{len(pedidos_sem_localidade):,} registros"
)

# ==================================================
# REMOVER COLUNAS REDUNDANTES
# ==================================================

base_pedidos_tratada = base_pedidos_tratada.drop(
    columns=["CIDADE_ENTREGA", "Localidade", "Loja_Venda"], errors="ignore"
)

# ==================================================
# SALVAR
# ==================================================

arquivo_saida = rf"{PASTA}\5 - base_pedidos_tratada.csv"

base_pedidos_tratada.to_csv(arquivo_saida, sep=";", index=False, encoding="utf-8-sig")

print(f"\nArquivo salvo:")
print(arquivo_saida)

# ==================================================
# SALVAR SOMENTE NÃO ENCONTRADOS
# ==================================================

arquivo_nao_encontrados = rf"{PASTA}\4 - pedidos_sem_correspondencia_localidade.csv"

pedidos_sem_localidade.to_csv(
    arquivo_nao_encontrados, sep=";", index=False, encoding="utf-8-sig"
)

print(f"\nArquivo de auditoria salvo:")
print(arquivo_nao_encontrados)
