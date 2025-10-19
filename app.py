import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
<<<<<<< HEAD
import json
=======
from streamlit_option_menu import option_menu
from Dash_Proconve import fase_proconv, plotar_frota_anual

>>>>>>> 3c53623 (tabs update)

st.set_page_config(page_title="Dashboard - Frota de Veículos", layout="wide")

# @st.cache_data
def carregar_dados():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
<<<<<<< HEAD
    credentials_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
=======
    # -----------------------------------------------------------------------------------------------------------------------------------------------------
    
    # credentials_dict = st.secrets["gcp_service_account"]
    # creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)

    # -----------------------------------------------------------------------------------------------------------------------------------------------------
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    # -----------------------------------------------------------------------------------------------------------------------------------------------------

>>>>>>> 3c53623 (tabs update)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1hCXDALseNe30yMo39vtZiinhvZkCRPXpfAU4uuxNzo4/edit?gid=690305500")
    worksheet = spreadsheet.sheet1
    rows = worksheet.get_all_values()
    df = pd.DataFrame(rows[2:], columns=rows[1])
    df = df.dropna(how="all")
    if df.columns[0] == "":
        df = df.iloc[:, 1:]
            
    df = df.iloc[:-9]
    return df 

# === Carregar e mostrar dados ===
df = carregar_dados()
st.title("📊 Dashboard - Frota Veicular")


selected = option_menu(
    menu_title=None,
    options=["Frota X Fase (Anual)","Veículos Leves X Proconve"],
    # icons=["car-front", "cloud", "map"],
    orientation="horizontal",
    styles={
        "container": {
            "padding": "8px",
            "background-color": "#FFFFFF",
            "border-bottom": f"2px solid {'#CCCCCC'}",
        },
        "icon": {"color": "#555555", "font-size": "18px"},
        "nav-link": {
            "font-size": "16px",
            "font-weight": "500",
            "color": "#555555",
            "background-color": "transparent",
            "border-radius": "8px",
            "padding": "8px 20px",
            "margin": "0px 5px",
            "--hover-color": "#CCCCCC",
        },
        "nav-link-selected": {
            "background-color": "#555555",
            "color": "#FFB300",
            "font-weight": "700",
            "box-shadow": "0px 2px 5px rgba(0,0,0,0.1)",
        },
    },
)


# === Exemplo de gráfico ===
# st.bar_chart(df["Ano"].value_counts().sort_index())
if selected == "Frota X Fase (Anual)":
    plotar_frota_anual(df)
elif selected == "Veículos Leves X Proconve":
    fase_proconv(df)
