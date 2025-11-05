import streamlit as st
import plotly.express as px
import re
import unicodedata
import pandas as pd
from Dash_Emissao import limpar_colunas

def _fmt_litros(n: float) -> str:
    # milhar com ponto e sem casas decimais (pt-BR friendly)
    return f"{n:,.0f}".replace(",", ".")


COLOR_MAP = {"Gasolina Comum": "#FFB300", "Etanol": "#29bde3"}

def grafico_por_ano(df_filtrado):
    base = (
        df_filtrado
        .groupby("Ano", as_index=False)[
            ["Venda de Combustivel Gasolina Comum (L)",
             "Venda de Combustivel Etanol (L)"]
        ].sum()
        .rename(columns={
            "Venda de Combustivel Gasolina Comum (L)": "Gasolina Comum",
            "Venda de Combustivel Etanol (L)": "Etanol",
        })
    )
    long = base.melt(id_vars="Ano", var_name="Combustível", value_name="Litros")

    st.subheader("Vendas por ano")
    colA, colB = st.columns([1,1])
    with colA:
        kind = st.radio("Tipo de gráfico", ["Barras", "Linhas"], horizontal=True, index=0)
    with colB:
        as_percent = st.toggle("Mostrar em % (100%)", value=False)

    if kind == "Barras":
        if as_percent:
            # ---- NORMALIZA POR ANO PARA TER 100% ----
            totals = long.groupby("Ano")["Litros"].transform("sum")
            long["Percent"] = (long["Litros"] / totals) * 100.0

            fig = px.bar(
                long, x="Ano", y="Percent", color="Combustível",
                color_discrete_map=COLOR_MAP, barmode="stack",
                labels={"Percent": "%"}
            )
            fig.update_yaxes(range=[0, 100], ticksuffix="%", title="%")
            fig.update_traces(hovertemplate="%{x}<br>%{legendgroup}: %{y:.1f}%")
        else:
            fig = px.bar(
                long, x="Ano", y="Litros", color="Combustível",
                color_discrete_map=COLOR_MAP, barmode="group",
                labels={"Litros": "Litros"}
            )
            fig.update_traces(hovertemplate="%{x}<br>%{legendgroup}: %{y:,.0f} L")
    else:
        fig = px.line(
            long, x="Ano", y="Litros", color="Combustível",
            markers=True, color_discrete_map=COLOR_MAP,
            labels={"Litros": "Litros"}
        )
        fig.update_traces(hovertemplate="%{x}<br>%{legendgroup}: %{y:,.0f} L")

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0)
    )

    st.container(height=480).plotly_chart(fig, use_container_width=True)




def Combustivel_Ano(df):
    df = limpar_colunas(df)

    cols = [
        "Ano",
        "Venda de Combustivel Gasolina Comum (L)",
        "Venda de Combustivel Etanol (L)",
        "Venda de Combustivel Gasolina Comum (%)",
        "Venda de Combustivel Etanol (%)",
        "Venda de Combustivel GC + Etanol",
    ]

    # filtra e garante cópia só com as colunas desejadas
    df_filtrado = df.loc[df["Ano"] >= 1960, cols].copy()

    # --- totais no período selecionado ---
    total_gas = df_filtrado["Venda de Combustivel Gasolina Comum (L)"].sum(skipna=True)
    total_etanol = df_filtrado["Venda de Combustivel Etanol (L)"].sum(skipna=True)
    total_litros = float(total_gas + total_etanol)

    # df para a pizza
    pie_df = pd.DataFrame({
        "Combustível": ["Gasolina Comum", "Etanol"],
        "Litros": [total_gas, total_etanol],
    })

    # --- layout: duas colunas com containers ---
    col1, col2 = st.columns(2, gap="large")
    col3 = st.columns(1, gap="large")


    with col1:
        tile = st.container(height=480)   # maior
        with tile:
            st.subheader("Participação por combustível (desde 1960)")

            fig = px.pie(
                pie_df,
                names="Combustível",
                values="Litros",
                hole=0.45,
                color="Combustível",
                color_discrete_map={
                    "Gasolina Comum": "#FFB300",   # amarelo
                    "Etanol": "#29bde3"            # azul aqua
                }
            )

            fig.update_traces(
                textposition="inside",
                texttemplate="%{label}<br>%{percent:.1%}"
            )

            fig.update_layout(
                legend=dict(
                    y=0,            # empurra a legenda pra parte de baixo
                    x=1.05,
                    valign="bottom"
                ),
                margin=dict(l=0, r=0, t=20, b=10)
            )

            st.plotly_chart(fig, use_container_width=True)


    with col2:
        tile = st.container(height=360)
        with tile:
            st.subheader("Vendas totais no período (L)")
            st.metric(
                label="Total de combustível vendido",
                value=_fmt_litros(total_litros) + " L",
                help="Soma de Gasolina Comum + Etanol no intervalo mostrado."
            )
            st.caption(
                f"Gasolina: **{_fmt_litros(total_gas)} L** • "
                f"Etanol: **{_fmt_litros(total_etanol)} L**"
            )

    grafico_por_ano(df_filtrado)

    # tabela abaixo (se quiser manter)
    st.dataframe(df_filtrado, use_container_width=True)



    