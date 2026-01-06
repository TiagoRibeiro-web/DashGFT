import streamlit as st
import pandas as pd

def apply_filters(df, filters):
    """
    Aplica filtros globais no sidebar com normalização de valores
    para evitar duplicidade (ex: 'Instagram', 'Instagram ', 'Instagram\\n').
    """

    st.sidebar.markdown("### 🎛️ Filtros")

    # Inicializa filtros na sessão
    if "filters" not in st.session_state:
        st.session_state.filters = {}

    # =========================
    # CRIAÇÃO DOS FILTROS
    # =========================
    for col in filters:
        if col not in df.columns:
            continue

        # 🔥 NORMALIZAÇÃO DOS VALORES (CORREÇÃO PRINCIPAL)
        values = (
            df[col]
            .dropna()
            .astype(str)
            .str.strip()                      # remove espaços
            .str.replace("\n", "", regex=False)
            .str.replace("\r", "", regex=False)
            .replace("nan", None)
            .dropna()
            .unique()
            .tolist()
        )

        values = sorted(values)

        selected = st.sidebar.multiselect(
            col,
            values,
            default=st.session_state.filters.get(col, []),
            key=f"filter_{col}"
        )

        st.session_state.filters[col] = selected

    # =========================
    # APLICAÇÃO DOS FILTROS
    # =========================
    for col, selected in st.session_state.filters.items():
        if selected and col in df.columns:
            df = df[
                df[col]
                .astype(str)
                .str.strip()
                .str.replace("\n", "", regex=False)
                .str.replace("\r", "", regex=False)
                .isin(selected)
            ]

    return df
