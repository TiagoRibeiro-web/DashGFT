import streamlit as st
import pandas as pd
from io import BytesIO

def export_multi_excel(df_base, df_posts, df_tags):
    """
    Export analítico (multi-aba)
    """
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_base.to_excel(writer, sheet_name="NEW_DASH", index=False)
        df_posts.to_excel(writer, sheet_name="POSTS", index=False)
        df_tags.to_excel(writer, sheet_name="TAGS", index=False)

    st.download_button(
        "⬇️ Download Excel (Analítico)",
        buffer.getvalue(),
        file_name="gft_dashboard_analitico.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def export_full_excel(df_full):
    """
    Export FULL (base completa, sem agregação)
    """
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_full.to_excel(writer, sheet_name="BASE_COMPLETA", index=False)

    st.download_button(
        "⬇️ Download Excel (Base Completa)",
        buffer.getvalue(),
        file_name="gft_dashboard_base_completa.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
