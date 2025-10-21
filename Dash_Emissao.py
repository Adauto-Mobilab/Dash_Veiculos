import streamlit as st
import plotly.express as px
import re
import unicodedata
import pandas as pd

def limpar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    novas_colunas = []
    for col in df.columns:
        c = str(col)
        c = c.replace("\r", " ").replace("\n", " ").replace("\t", " ")
        c = "".join(ch for ch in unicodedata.normalize("NFKD", c) if not unicodedata.combining(ch))
        c = re.sub(r"\s+", " ", c).strip()
        novas_colunas.append(c)
    df.columns = novas_colunas
    return df

def fator_emissao(df):
    lista_poluentes = [
        "CO (g/km)", "HC (g/km)", "NMHC (g/km)", "CH4 (g/km)",
        "NMHC-ETOH (g/km)", "ETOH (g/km)", "NOx (g/km)",
        "CH3CHO (g/km)", "HCOH (g/km)", "RCHO (g/km)",
        "MP (g/km)", "CO2 (g/km)", "N2O (g/km)", "NH3 (ppm)"
    ]

    option = st.selectbox("Selecione o Poluente desejado", options=lista_poluentes)

    choice = st.radio(
        "Selecione o tipo de combustível",
        options=["Gasolina Comum", "Etanol", "GNV", "Flex Etanol", "Flex Gasolina Comum"],
        key="combustivel"
    )

    # Limpa colunas do DataFrame
    df = limpar_colunas(df)
    poluente_pesquisa = option + " " + choice
    print(poluente_pesquisa)

     # Cria DataFrame de emissões
    df_emissao = df[["Ano", poluente_pesquisa]].copy()
    print(df_emissao)

    df_emissao = df_emissao.fillna(0)

    df_emissao = df_emissao[df_emissao[poluente_pesquisa] != 0]
    print(df_emissao)

    # Cria gráfico
    fig = px.line(
        df_emissao,
        x='Ano',
        y=poluente_pesquisa,
        markers=True,
        title=f"Emissões de {option} - {choice}",
    )

    fig.update_traces(
        line=dict(color="#FFB300", width=3),
        marker=dict(color="#FFB300"),
        hovertemplate="Ano: %{x}<br>Valor: %{y:.6f}<extra></extra>"
    )
    fig.update_yaxes(tickformat=".6f")

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df_emissao.style.format(precision=8))