# data_loader.py
import pandas as pd
import streamlit as st

EXCEL_PATH = "banco_de_posts_gft.xlsx"
SHEET_NAME = "Planilha1"
TOP_VOICES_PATH = "topvoices.xlsx"  # Novo arquivo

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
    """
    Carrega os dados principais do dashboard e da planilha Top Voices.
    Retorna: (df_main, KPIS, FILTERS, df_top_voices)
    """
    try:
        # =========================
        # 1. LOAD EXCEL PRINCIPAL
        # =========================
        df_main = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
        
        # =========================
        # NORMALIZA NOMES DAS COLUNAS
        # =========================
        df_main.columns = (
            df_main.columns.astype(str)
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
            if col in df_main.columns:
                df_main[col] = (
                    df_main[col]
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
            if col in df_main.columns:
                df_main[col] = pd.to_numeric(df_main[col], errors="coerce").fillna(0)

        # =========================
        # 2. LOAD TOP VOICES EXCEL
        # =========================
        try:
            df_top_voices = pd.read_excel(TOP_VOICES_PATH)
            
            # Normalizar nomes das colunas do Top Voices
            df_top_voices.columns = (
                df_top_voices.columns.astype(str)
                .str.strip()
                .str.replace("\n", " ", regex=False)
                .str.replace("\r", "", regex=False)
            )
            
            # Normalizar colunas de data
            date_columns = ['Date', 'Data', 'Data de publicação']
            for date_col in date_columns:
                if date_col in df_top_voices.columns:
                    df_top_voices[date_col] = pd.to_datetime(
                        df_top_voices[date_col], 
                        errors='coerce'
                    )
            
            # Normalizar colunas numéricas
            numeric_columns_tv = [
                'Posts Developed', 'Reach', 'Engagement', 'Likes', 
                'Comments', 'Quantidade', 'Impressions', 'Video Views'
            ]
            
            for col in numeric_columns_tv:
                if col in df_top_voices.columns:
                    df_top_voices[col] = pd.to_numeric(
                        df_top_voices[col], 
                        errors='coerce'
                    ).fillna(0)
            
            # Normalizar colunas textuais
            text_columns_tv = [
                'País (LATAM/BR)', 'Tipo de Dado', 'Nome_tag_post',
                'Link', 'Channel', 'Source'
            ]
            
            for col in text_columns_tv:
                if col in df_top_voices.columns:
                    df_top_voices[col] = (
                        df_top_voices[col]
                        .astype(str)
                        .str.strip()
                        .str.title()
                        .replace('Nan', '')
                        .replace('None', '')
                    )
            
            # Adicionar coluna Month se houver Date
            if 'Date' in df_top_voices.columns:
                df_top_voices['Month'] = df_top_voices['Date'].dt.strftime('%Y-%m')
            
            # Armazenar em session_state para acesso fácil
            st.session_state['top_voices_data'] = df_top_voices
            
        except FileNotFoundError:
            st.warning(f"⚠️ Arquivo Top Voices não encontrado: {TOP_VOICES_PATH}")
            df_top_voices = pd.DataFrame()
            st.session_state['top_voices_data'] = pd.DataFrame()
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar Top Voices: {str(e)}")
            df_top_voices = pd.DataFrame()
            st.session_state['top_voices_data'] = pd.DataFrame()

        # =========================
        # 3. RETORNAR DADOS
        # =========================
        return df_main, KPIS, FILTERS, df_top_voices

    except Exception as e:
        st.error(f"❌ Erro crítico ao carregar dados: {str(e)}")
        # Retornar DataFrames vazios em caso de erro
        return pd.DataFrame(), KPIS, FILTERS, pd.DataFrame()


def load_top_voices_data():
    """
    Função auxiliar para carregar apenas dados do Top Voices.
    Útil se você quiser carregar separadamente.
    """
    if 'top_voices_data' in st.session_state:
        return st.session_state['top_voices_data']
    
    try:
        df_top_voices = pd.read_excel(TOP_VOICES_PATH)
        
        # Aplicar as mesmas normalizações
        df_top_voices.columns = (
            df_top_voices.columns.astype(str)
            .str.strip()
            .str.replace("\n", " ", regex=False)
            .str.replace("\r", "", regex=False)
        )
        
        # Normalizar data
        if 'Date' in df_top_voices.columns:
            df_top_voices['Date'] = pd.to_datetime(df_top_voices['Date'], errors='coerce')
        
        st.session_state['top_voices_data'] = df_top_voices
        return df_top_voices
        
    except Exception as e:
        st.error(f"Erro ao carregar Top Voices: {e}")
        return pd.DataFrame()


def get_top_voices_kpis():
    """
    Retorna lista de KPIs disponíveis na planilha Top Voices.
    """
    return [
        'Posts Developed',
        'Reach', 
        'Engagement',
        'Likes',
        'Comments',
        'Quantidade'
    ]


def get_top_voices_filters():
    """
    Retorna lista de filtros disponíveis na planilha Top Voices.
    """
    return [
        'País (LATAM/BR)',
        'Tipo de Dado',
        'Nome_tag_post',
        'Month'
    ]