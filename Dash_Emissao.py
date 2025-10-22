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

def fator_emissao_total(df, option, lista_combustivel, lista_emissoes):

    df_emissao_total = pd.DataFrame()
    df_emissao_total["Ano"] = df['Ano']

    for i in lista_combustivel:
        lista_emissoes.append(option + ' ' + i)

    print(lista_emissoes)

    for i in lista_emissoes:
        df_emissao_total[i] = df[[i]]

    df_emissao_total = df_emissao_total.fillna(0)
    df_agrupado = df_emissao_total.groupby("Ano").sum(numeric_only=True)
    df_agrupado["Total"] = df_agrupado.sum(axis=1)
    df_agrupado = df_agrupado[["Total"]].reset_index()
    df_agrupado = df_agrupado[df_agrupado['Total'] != 0]


     # Cria gráfico
    fig = px.line(
        df_agrupado,
        x='Ano',
        y='Total',
        markers=True,
        title=f"Emissões de Totais por Ano {option}",
    )

    fig.update_traces(
        line=dict(color="#0ebeff", width=3),
        marker=dict(color="#555555"),
        # hovertemplate="Ano: %{x}<br>Valor: %{y:.casas_decimais_dff}<extra></extra>"
    )

    fig.update_layout(
        title_x=0.05,
        title_font=dict(size=20)
    )

    fig.update_yaxes(zeroline=True,
                    #  tickformat=casas_decimais
                     )

    st.plotly_chart(fig, use_container_width=True)



def fator_emissao(df):
    lista_poluentes = [
        "CO (g/km)", "HC (g/km)", "NMHC (g/km)", "CH4 (g/km)",
        "NMHC-ETOH (g/km)", "ETOH (g/km)", "NOx (g/km)",
        "CH3CHO (g/km)", "HCOH (g/km)", "RCHO (g/km)",
        "MP (g/km)", "CO2 (g/km)", "N2O (g/km)", "NH3 (ppm)"
    ]

    lista_emissoes = []
    lista_combustivel = ["Gasolina Comum", "Etanol", "GNV", "Flex Etanol", "Flex Gasolina Comum"]

    option = st.selectbox("Selecione o Poluente desejado", options=lista_poluentes)

    choice = st.radio(
        "Selecione o tipo de combustível",
        options=lista_combustivel,
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
     
    #formatação casas decimais eixo y
    if poluente_pesquisa.split()[0] == 'ETOH' or poluente_pesquisa.split()[0] == 'MP':
        casas_decimais = '.5f'
        casas_decimais_df = 8 

    else:
        casas_decimais = '.2f'
        casas_decimais_df = 2

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
        marker=dict(color="#555555"),
        hovertemplate="Ano: %{x}<br>Valor: %{y:.casas_decimais_dff}<extra></extra>"
    )

    fig.update_layout(
        title_x=0.05,
        title_font=dict(size=20)
    )

    fig.update_yaxes(zeroline=True,
                     tickformat=casas_decimais)

    st.plotly_chart(fig, use_container_width=True)

    fator_emissao_total(df, option, lista_combustivel, lista_emissoes)

    st.caption("Fonte: CETESB")
    st.subheader("Dados")
    st.dataframe(df_emissao.style.format(precision=casas_decimais_df))

