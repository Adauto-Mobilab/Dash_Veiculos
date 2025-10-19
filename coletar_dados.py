import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIGURAÇÕES ===
SHEET_URL = "https://docs.google.com/spreadsheets/d/1hCXDALseNe30yMo39vtZiinhvZkCRPXpfAU4uuxNzo4/edit?gid=690305500"
CRED_FILE = "credentials.json"

# === AUTENTICAÇÃO ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CRED_FILE, scope)
client = gspread.authorize(creds)

# === ABRIR A PLANILHA ===
spreadsheet = client.open_by_url(SHEET_URL)
worksheet = spreadsheet.sheet1  # ou o nome da aba, ex: spreadsheet.worksheet("Dados")

# === LER TODAS AS LINHAS ===
rows = worksheet.get_all_values()

# === CONVERTER PARA DATAFRAME (CABEÇALHO NA LINHA 2, DADOS A PARTIR DA LINHA 3) ===
df = pd.DataFrame(rows[2:], columns=rows[1])  # índice 2 = linha 3, índice 1 = linha 2
df = df.dropna(how="all")  # remove linhas totalmente vazias

# === REMOVER A PRIMEIRA COLUNA VAZIA (COLUNA A) ===
if df.columns[0] == "":
    df = df.iloc[:, 1:]

print(df.head())
