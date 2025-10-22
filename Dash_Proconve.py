import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu


def fase_proconv(df):

    COR_DESTAQUE = '#FFB300'  # Laranja/Amarelo do logo
    COR_CINZA = '#555555'     # Cinza escuro do logo
    ordem_fases_proconv = [
    'Não se aplica',
    'Pré-L1',
    'L-1',
    'L-2',
    'L-3',
    'L-4',
    'L-5',
    'L-6',
    'L-7',
    'L-8'
]
    # --- 1. PREPARAÇÃO E LIMPEZA ---
    
    # CONVERSÃO: Converte a coluna de veículos para int no DataFrame principal (df)
    # Isso garante que o agrupamento use números. Use .copy() se df não for o original.
    # Usando .loc para evitar o SettingWithCopyWarning
    df.loc[:, "Frota circulante - DETRAN/DF"] = df["Frota circulante - DETRAN/DF"].astype(int)

    
    # --- 2. AGRUPAMENTO ---
    
    df_agrupado = df.groupby('Fase do PROCONVE - Veículos Leves')['Frota circulante - DETRAN/DF'].sum().reset_index()
    
    # CORREÇÃO CRÍTICA: Renomeia a coluna para o nome que você quer usar no gráfico
    df_agrupado.rename(
        columns={'Frota circulante - DETRAN/DF': 'Total de Veículos'}, 
        inplace=True
    )

    # print('DF AGRUPADO (Corrigido)')
    # print(df_agrupado)

    # --- 3. CRIAÇÃO E EXIBIÇÃO DO GRÁFICO (Plotly Express) ---
    
    fig = px.bar(
        df_agrupado,
        x='Fase do PROCONVE - Veículos Leves', 
        y='Total de Veículos',                 # AGORA ESTA COLUNA EXISTE
        title='Veículos Leves por Fases Proconve 1925 - 2025',
        labels={
            'Fase do PROCONVE - Veículos Leves': 'Fase PROCONVE',
            'Total de Veículos': 'Nº Total de Veículos'
        },
        # color='Fase do PROCONVE - Veículos Leves' # Adiciona cores por categoria
        color_discrete_sequence=[COR_DESTAQUE, COR_CINZA, '#888888', '#CCCCCC']
    )

    # 🎯 NOVO CÓDIGO: Adiciona os valores (data labels) acima das barras
    fig.update_traces(
        # texttemplate='%{y}',  # Exibe o valor do eixo Y
        text=df_agrupado['Total de Veículos'], # Usa a coluna de valores para o texto
        textposition='outside', # Posiciona o texto fora (acima) da barra
        textfont=dict(size=14, color='black') # Opcional: Estiliza o texto
    )

    limite_superior =  df_agrupado['Total de Veículos'].max() *1.2
    fig.update_yaxes(
    # Define o novo limite superior para o eixo Y
    range=[0, limite_superior]
)
    # 4. APLICA A ORDEM NO EIXO X
    fig.update_xaxes(
        categoryorder='array',  # Diz ao Plotly para usar uma ordem de array
        categoryarray=ordem_fases_proconv # Passa a lista com a ordem
    )

    fig.update_layout(
        title_x=0.05,
        title_font=dict(size=20)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Fonte: DETRAN/DF e Base PROCONVE")

    st.subheader("Dados")
    st.dataframe(df_agrupado, use_container_width=True)
    
    # Opcional: Retorne o DF agrupado se for usá-lo depois
    # return df_agrupado
def plotar_frota_anual(df_proconv_ano):
    """
    Gera um gráfico interativo (Plotly) da frota anual por fases PROCONVE.

    Parâmetros:
        df_proconv_ano (pd.DataFrame): DataFrame contendo as colunas:
            - 'Ano'
            - 'Fase do PROCONVE - Veículos Leves'
            - 'Frota circulante - DETRAN/DF'
    """

    # --- Definição das faixas PROCONVE ---
    limites_fase = [
        {"nome": "PP",  "inicio": 1987, "fim": 1987},
        {"nome": "L-1", "inicio": 1988, "fim": 1991},
        {"nome": "L-2", "inicio": 1992, "fim": 1996},
        {"nome": "L-3", "inicio": 1997, "fim": 2002},
        {"nome": "L-4", "inicio": 2003, "fim": 2008},
        {"nome": "L-5", "inicio": 2009, "fim": 2013},
        {"nome": "L-6", "inicio": 2014, "fim": 2021},
        {"nome": "L-7", "inicio": 2022, "fim": 2024},
        {"nome": "L-8", "inicio": 2025, "fim": 2025},
    ]

    # --- Paleta personalizada ---
    PALETA_MOBILAB = [
        '#FFB300', '#e4b41c', '#c9b539', '#afb755','#94b871', '#79b98e','#5ebaaa', '#29bde3', '#0ebeff'
        
    ]

    # --- 1. Preparação dos dados ---
    df_proconv_ano = df_proconv_ano.copy()

    # Conversões
    df_proconv_ano['Ano'] = df_proconv_ano['Ano'].astype(int)
    df_proconv_ano['Frota circulante - DETRAN/DF'] = (
        df_proconv_ano['Frota circulante - DETRAN/DF']
        .astype(str)
        .str.replace(r'\D', '', regex=True)
        .replace('', 0)
        .astype(int)
    )

    # 🔹 FILTRO: mostrar apenas a partir de 1987
    df_proconv_ano = df_proconv_ano[df_proconv_ano['Ano'] >= 1987]

    # Agrupa dados anuais
    df_agrupado_anual = (
        df_proconv_ano.groupby(['Ano', 'Fase do PROCONVE - Veículos Leves'])
        ['Frota circulante - DETRAN/DF']
        .sum()
        .reset_index()
        .rename(columns={'Frota circulante - DETRAN/DF': 'Total de Veículos'})
    )

    # --- 2. Criação do gráfico ---
    fig = px.bar(
        df_agrupado_anual,
        x='Ano',
        y='Total de Veículos',
        color='Fase do PROCONVE - Veículos Leves',
        title='Frota por Fases Proconve (Anual)',
        labels={
            'Ano': 'Ano',
            'Total de Veículos': 'Nº Total de Veículos',
            'Fase do PROCONVE - Veículos Leves': 'Fase PROCONVE'
        },
        color_discrete_sequence=PALETA_MOBILAB,
        barmode='stack'
    )

    # --- 3. Adiciona as faixas de fundo ---
    for fase in limites_fase:
        if fase["fim"] >= 1987:  # só mostra faixas após 1987
            fig.add_shape(
                type="rect",
                x0=fase["inicio"] - 0.5,
                x1=fase["fim"] + 0.5,
                y0=0,
                y1=1,
                yref="paper",
                # fillcolor=fase["cor"],
                opacity=0.3,
                layer="below",
                line_width=0,
            )

            ano_central = fase["inicio"] + (fase["fim"] - fase["inicio"]) / 2
            fig.add_annotation(
                x=ano_central,
                y=1.05,
                yref="paper",
                text=fase["nome"],
                showarrow=False,
                font=dict(size=14, color="#3A3A3A", family="Arial"),
            )

    # --- 4. Aparência final ---
    fig.update_layout(
        xaxis=dict(
            title="Ano",
            tickmode="linear",
            dtick=1,
            showgrid=False,
        ),
        yaxis=dict(
            title="Nº Total de Veículos",
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend_title_text="Fase PROCONVE",
        bargap=0,
        title_x=0.05,
        title_font=dict(size=20),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1.0,
            xanchor="left",
            x=1.05,
        )
    )

    # --- 5. Renderiza no Streamlit ---
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Fonte: DETRAN/DF e Base PROCONVE")
    st.subheader("Dados")
    st.dataframe(df_agrupado_anual, use_container_width=True)
        