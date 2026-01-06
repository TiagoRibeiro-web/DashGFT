import streamlit as st
import pandas as pd


def render_tags(df, kpis):

    st.subheader("🏷️ Performance por Tag")

    # =========================
    # MAPEAMENTO DE COLUNAS (ROBUSTO)
    # =========================
    consumption_col = None
    for c in ["Consumption", "Consumptions"]:
        if c in df.columns:
            consumption_col = c
            break

    if consumption_col is None:
        st.error("Coluna de Consumption(s) não encontrada na base.")
        return

    required_cols = {
        "Reach": "sum",
        "Impressions": "sum",
        consumption_col: "sum",
        "Score": "sum"
    }

    required_cols = {
        col: agg for col, agg in required_cols.items() if col in df.columns
    }

    # =========================
    # AGREGAÇÃO POR TAG
    # =========================
    agg = (
        df.groupby("Tag", dropna=False)
        .agg(required_cols)
        .reset_index()
    )

    # =========================
    # CTR = Consumptions / Impressions
    # (AJUSTE: nunca retorna None)
    # =========================
    agg["CTR"] = agg.apply(
        lambda r: (r[consumption_col] / r["Impressions"])
        if r["Impressions"] > 0 else 0,
        axis=1
    )

    # =========================
    # AJUSTE: manter CTR numérico
    # (formatação fica no column_config)
    # =========================
    agg["CTR_pct"] = agg["CTR"].fillna(0)

    # =========================
    # CONTROLES
    # =========================
    order_by = st.selectbox(
        "Ordenar por",
        ["Impressions", "Reach", consumption_col, "CTR", "Score"],
        index=0
    )

    ascending = st.checkbox("Ordem crescente", value=False)

    agg = agg.sort_values(order_by, ascending=ascending)

    # =========================
    # TABELA ESTILO EXCEL (DIN)
    # =========================
    st.dataframe(
        agg[[
            "Tag",
            "Reach",
            "Impressions",
            consumption_col,
            "CTR_pct",
            "Score"
        ]],
        use_container_width=True,
        column_config={
            "Reach": st.column_config.NumberColumn("Reach", format="%,d"),
            "Impressions": st.column_config.NumberColumn("Impressions", format="%,d"),
            consumption_col: st.column_config.NumberColumn(
                "Consumptions", format="%,d"
            ),
            "CTR_pct": st.column_config.ProgressColumn(
                "CTR",
                min_value=0,
                max_value=0.5,   # 50% visual
                format="%.2f%%"
            ),
            "Score": st.column_config.NumberColumn("Score", format="%,d"),
        }
    )
