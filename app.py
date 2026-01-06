import streamlit as st
import pandas as pd
from PIL import Image
from din import render_din
from tv_din import render_tv_din
# =========================
# Imports internos
# =========================
from auth import login_screen
from data_loader import load_data
from filters import apply_filters
from new_dash import render_new_dash
from posts import render_posts
from tags import render_tags
from exports import export_multi_excel, export_full_excel

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="GFT Technology | Social Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Controle de sessão
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

# =========================
# Login
# =========================
if not st.session_state.auth:
    login_screen()
    st.stop()

# ======================================================
# USUÁRIO AUTENTICADO
# ======================================================

# =========================
# Carregar dados
# =========================
df, KPIS, FILTERS = load_data()

# =========================
# Aplicar filtros globais
# =========================
df = apply_filters(df, FILTERS)

# =========================
# Header com logo
# =========================
logo = Image.open("assets/gft_logo.jpg")

col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image(logo, width=120)
with col_title:
    st.markdown("## Social Media Dashboard")
    st.markdown("Visão consolidada de performance de mídias sociais")

st.markdown("---")

# =========================
# DATAFRAMES PARA EXPORT
# =========================

# -------- NEW DASH (base filtrada)
df_new_dash = df.copy()

# -------- POSTS (FORMATO IGUAL AO EXCEL ORIGINAL)
df_posts_export = df.rename(columns={
    "description": "Description",
    "Permalink": "Link"
}).copy()

posts_columns = [
    "Channel",
    "Name",
    "Date",
    "Reach",
    "Impressions",
    "Engagement",
    "CTR",
    "Video Views",
    "Description",
    "Link",
    "Score"
]

# Mantém apenas colunas existentes
posts_columns = [c for c in posts_columns if c in df_posts_export.columns]

# =========================
# NORMALIZAÇÃO DEFINITIVA DA DATA
# =========================
if "Date" in df_posts_export.columns:
    df_posts_export["Date_norm"] = pd.to_datetime(
        df_posts_export["Date"].astype(str).str.strip(),
        errors="coerce",
        dayfirst=True
    )
else:
    df_posts_export["Date_norm"] = pd.NaT

# Ordenação segura
df_posts_export = (
    df_posts_export
    .sort_values("Date_norm", ascending=False)
    .loc[:, posts_columns]   # remove Date_norm antes do export
)

# -------- TAGS (AGREGADO)
df_tags_export = (
    df.groupby("Tag", dropna=False)[
        ["Impressions", "Reach", "Interactions", "Video Views"]
    ]
    .sum()
    .reset_index()
)

# =========================
# EXPORT EXCEL MULTI-ABA
# =========================
export_multi_excel(
    df_base=df_new_dash,
    df_posts=df_posts_export,
    df_tags=df_tags_export
)
# =========================
# EXPORT FULL (BASE COMPLETA)
# =========================
export_full_excel(df)

# =========================
# Abas do dashboard
# =========================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 NEW DASH",
    "📝 POSTS",
    "🏷️ TAGS",
    "📘 DIN",
    "📺 TV-DIN"
])

with tab1:
    render_new_dash(df.copy(), KPIS)

with tab2:
    render_posts(df.copy(), KPIS)

with tab3:
    render_tags(df.copy(), KPIS)

with tab4:
    render_din(df.copy())

with tab5:
    render_tv_din(df.copy())    

# =========================
# Logout
# =========================
st.sidebar.markdown("---")

if st.sidebar.button("Sair do sistema"):
    st.session_state.auth = False
    st.rerun()
