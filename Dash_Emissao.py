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

    # print(lista_emissoes)

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
        title=f"Emissões de {option} Totais por Ano",
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
    # print(poluente_pesquisa)

     # Cria DataFrame de emissões
    df_emissao = df[["Ano", poluente_pesquisa]].copy()
    # print(df_emissao)

    df_emissao = df_emissao.fillna(0)

    df_emissao = df_emissao[df_emissao[poluente_pesquisa] != 0]
    # print(df_emissao)
     
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
    if df_emissao.empty:
        st.warning("Esse combustível não emite esse tipo de poluente", icon="⚠️")
        return
    st.plotly_chart(fig, use_container_width=True)

    # fator_emissao_total(df, option, lista_combustivel, lista_emissoes)

    with st.expander("Dados de Emissões — clique para ver "):
        st.caption("Fonte: CETESB")
        st.subheader("Dataframe")
        st.dataframe(df_emissao.style.format(precision=casas_decimais_df))



def calc_emissoes_cetesb_ton(
    dic_emissoes: dict,
    poluentes_selecionados: list,
    exigir_ano: bool = True,
    inventario_path: str = "Inventario_DF_Observatorio.xlsx",
    frota_fixa: int = 2_159_413,
    perc_etanol_gasolina: float = 0.31  # aplica para Gasolina e Etanol em todos os poluentes
) -> pd.DataFrame:
    """
    Retorna DF longo com: Ano, Combustível, Poluente, Emissão (ton).
    Fórmula: E (g/ano) = Fr * Iu * Fe   (apenas para Gasolina Comum e Etanol)
             E (g/ano) = Iu * Fe        (demais combustíveis, ex.: Flex/GNV)
    Depois aplica multiplicador 0.31 para Gasolina Comum e Etanol em TODOS os poluentes.
    Converte g -> t e filtra Ano >= 1982.
    """

    # mapeia combustível -> aba do Excel onde está a intensidade de uso
    sheet_map = {
        "Gasolina Comum": "INVENTARIO GASOLINA",
        "Flex Gasolina Comum": "INVENTARIO GASOLINA",
        "Etanol": "INVENTARIO ETANOL",
        "Flex Etanol": "INVENTARIO ETANOL",
        "GNV": "INVENTARIO GNV",  # se não houver, será ignorado
    }

    # carrega intensidades de uso por aba
    intensidades = {}
    for combustivel, aba in sheet_map.items():
        try:
            df_inv = pd.read_excel(inventario_path, sheet_name=aba, engine="openpyxl")
        except Exception:
            continue

        df_inv = df_inv.rename(columns={c: c.strip() for c in df_inv.columns})
        cand = [c for c in df_inv.columns if c.upper().startswith("INTENSIDADE") and "KM" in c.upper()]
        if not cand or "Ano" not in df_inv.columns:
            continue

        iu_col = cand[0]
        intensidades[combustivel] = df_inv[["Ano", iu_col]].rename(
            columns={iu_col: "INTENSIDADE DE USO (KM/ANO)"}
        )

    registros = []

    for combustivel, df in dic_emissoes.items():
        if exigir_ano and "Ano" not in df.columns:
            raise KeyError(f"No DF de '{combustivel}' falta coluna 'Ano'.")

        # une Intensidade de Uso do inventário; se não houver, tenta achar no próprio DF
        if combustivel in intensidades:
            base = df.merge(intensidades[combustivel], on="Ano", how="left")
        else:
            cand_local = [c for c in df.columns if c.upper().startswith("INTENSIDADE") and "KM" in c.upper()]
            if not cand_local:
                raise KeyError(
                    f"Não encontrei 'INTENSIDADE DE USO (KM/ANO)' para '{combustivel}'. "
                    "Faltou aba no inventário e não há coluna de intensidade no DF local."
                )
            base = df.rename(columns={cand_local[0]: "INTENSIDADE DE USO (KM/ANO)"})

        for pol in poluentes_selecionados:
            col = f"{pol} {combustivel}"
            if col not in base.columns:
                continue

            Fe_g_km = base[col]                             # g/km
            Iu_km_ano = base["INTENSIDADE DE USO (KM/ANO)"] # km/ano por veículo

            # E (g/ano)
            if combustivel in ("Gasolina Comum", "Etanol"):
                g_ano = frota_fixa * Iu_km_ano * Fe_g_km
                # aplicar 0,31 para Gasolina e Etanol em TODOS os poluentes
                g_ano = g_ano * perc_etanol_gasolina
            else:
                g_ano = Iu_km_ano * Fe_g_km

            ton = g_ano * 1e-7  # g -> t

            if exigir_ano:
                for ano, val in zip(base["Ano"], ton):
                    registros.append({
                        "Ano": int(ano),
                        "Combustível": combustivel,
                        "Poluente": pol,
                        "Emissão (ton)": float(val)
                    })
            else:
                registros.append({
                    "Ano": None,
                    "Combustível": combustivel,
                    "Poluente": pol,
                    "Emissão (ton)": float(ton.sum())
                })

    out = pd.DataFrame(registros)

    if exigir_ano and not out.empty:
        out = out.groupby(["Ano", "Combustível", "Poluente"], as_index=False)["Emissão (ton)"].sum()

    # somente anos >= 1982
    if "Ano" in out.columns and out["Ano"].notna().any():
        out = out[out["Ano"] >= 1982]

    return out




def emissoes_total(df):

    limpar_colunas(df)

    # lista “completa” (nomes de colunas do DF)
    lista_poluentes = [
        "CO (g/km)", "HC (g/km)", "NMHC (g/km)", "CH4 (g/km)",
        "NMHC-ETOH (g/km)", "ETOH (g/km)", "NOx (g/km)",
        "CH3CHO (g/km)", "HCOH (g/km)", "RCHO (g/km)",
        "MP (g/km)", "CO2 (g/km)", "N2O (g/km)", "NH3 (ppm)"
    ]

    # mapa para exibir rótulos “curtos” no UI
    label_to_full = {
        "CO": "CO (g/km)",
        "HC": "HC (g/km)",
        "NMHC": "NMHC (g/km)",
        "CH4": "CH4 (g/km)",
        "NMHC-ETOH": "NMHC-ETOH (g/km)",
        "ETOH": "ETOH (g/km)",
        "NOx": "NOx (g/km)",
        "CH3CHO": "CH3CHO (g/km)",
        "HCOH": "HCOH (g/km)",
        "RCHO": "RCHO (g/km)",
        "MP": "MP (g/km)",
        "CO2": "CO2 (g/km)",
        "N2O": "N2O (g/km)",
        "NH3": "NH3 (ppm)",
    }
    full_to_label = {v: k for k, v in label_to_full.items()}
    options_ui = list(label_to_full.keys())  # ordem do UI

    # ——— montar dicionário de DFs por combustível
    dic_emissoes = {}
    lista_combustivel = ["Gasolina Comum", "Etanol", "GNV", "Flex Etanol", "Flex Gasolina Comum"]
    df_base = df

    for combustivel in lista_combustivel:
        cols = [f"{p} {combustivel}" for p in lista_poluentes] + ["Intensidade de uso (Km)", "Ano"]
        cols_existentes = [c for c in cols if c in df_base.columns]
        dic_emissoes[combustivel] = df_base[cols_existentes].copy()

    # ——— seleção de poluentes (rótulos curtos)
    selection_ui = st.segmented_control(
        "Poluentes",
        options_ui,
        selection_mode="multi",
        default=["CO2"]  # comece com CO2 marcado; ajuste se quiser
    )

    try:
        # converter para nomes completos (os do DF); se vazio, não calcula
        selection_full = [label_to_full[x] for x in selection_ui] if selection_ui else []
        if not selection_full:
            st.info("Selecione ao menos um poluente.")
            return

        df_emissoes_ton = calc_emissoes_cetesb_ton(
            dic_emissoes=dic_emissoes,
            poluentes_selecionados=selection_full,
            perc_etanol_gasolina=0.31  # conforme pedido
        )

        # totais por poluente (cards em toneladas)
        df_totais = (
            df_emissoes_ton
            .groupby("Poluente", as_index=False)["Emissão (ton)"]
            .sum()
        )

        for _, row in df_totais.iterrows():
            pol_label = full_to_label.get(row["Poluente"], row["Poluente"])
            st.metric(f"Total {pol_label}", f"{row['Emissão (ton)']:,.2f} t")

        # ---- DF em expander
        with st.expander("Dados de Emissões (t) — clique para ver"):
            st.dataframe(df_emissoes_ton, use_container_width=True)

    except Exception:
        st.warning("Opção em manutenção.")
        return

    # ----- rótulo curto no DF para os gráficos por ano
    df_plot = df_emissoes_ton.copy()
    df_plot["Poluente (label)"] = df_plot["Poluente"].map(full_to_label).fillna(df_plot["Poluente"])

    tab1, tab2 = st.tabs(["Por combustível", "Total (todos combustíveis)"])

    with tab1:
        st.caption("Linhas por poluente, com painéis por combustível")
        if df_plot.empty:
            st.info("Sem dados para plotar.")
        else:
            fig1 = px.line(
                df_plot,
                x="Ano",
                y="Emissão (ton)",
                color="Poluente (label)",
                facet_col="Combustível",
                facet_col_wrap=2,
                markers=True,
                title=None
            )
            fig1.update_layout(legend_title_text="Poluente", hovermode="x unified")
            st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        st.caption("Linhas por poluente somando todos os combustíveis")
        if df_plot.empty:
            st.info("Sem dados para plotar.")
        else:
            # linha (totais por ano)
            df_total = (
                df_plot.groupby(["Ano", "Poluente (label)"], as_index=False)["Emissão (ton)"].sum()
            )
            fig2 = px.line(
                df_total,
                x="Ano",
                y="Emissão (ton)",
                color="Poluente (label)",
                markers=True,
                title=None
            )
            fig2.update_layout(legend_title_text="Poluente", hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

            # barras (mesmos números dos cards)
            st.caption("Totais por poluente")
            df_totais_plot = df_totais.copy()
            df_totais_plot["Poluente (label)"] = df_totais_plot["Poluente"].map(full_to_label)
            df_totais_plot = df_totais_plot.sort_values("Emissão (ton)", ascending=False)

            fig_cards = px.bar(
                df_totais_plot,
                x="Poluente (label)",
                y="Emissão (ton)",
                text="Emissão (ton)",
                title=None
            )
            fig_cards.update_traces(texttemplate="%{y:,.2f} t", textposition="outside")
            fig_cards.update_layout(yaxis_title="Emissão (ton)", xaxis_title="Poluente", hovermode="x unified")
            st.plotly_chart(fig_cards, use_container_width=True)



    # print(f"DEBUG {dic_emissoes}")
        
