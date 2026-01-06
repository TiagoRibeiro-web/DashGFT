import pandas as pd

EXCEL_PATH = "banco_de_posts_gft.xlsx"
SHEET_NAME = "Planilha1"

KPIS = [
    "Reach",
    "Impressions",
    "Interactions",
    "Consumptions",
    "Video Views",
    "Score"
]

FILTERS = [
    "Month",
    "Channel",
    "Country",
    "Source",
    "Tag",
    "Sub Tag"
]

def load_data():
    # =========================
    # LOAD EXCEL
    # =========================
    df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

    # =========================
    # NORMALIZA NOMES DAS COLUNAS
    # =========================
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
    )

    # =========================
    # NORMALIZA CAMPOS TEXTUAIS (🔥 CORREÇÃO PRINCIPAL)
    # =========================
    text_cols = [
        "Month",
        "Channel",
        "Country",
        "Source",
        "Tag",
        "Sub Tag"
    ]

    for col in text_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.replace("\n", "", regex=False)
                .str.replace("\r", "", regex=False)
                .str.title()          # 🔥 PADRONIZA MAIÚSC./MINÚSC.
                .replace("Nan", None)
            )

    # =========================
    # NORMALIZA NUMÉRICOS
    # =========================
    numeric_cols = [
        "Reach",
        "Impressions",
        "Interactions",
        "Consumptions",
        "Video Views",
        "Score"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df, KPIS, FILTERS
