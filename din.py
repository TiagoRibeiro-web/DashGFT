import streamlit as st
import pandas as pd
import plotly.express as px

def render_din(df):

    st.subheader("📘 DIN — Eficiência Temática")

    st.caption(
        "Avalia o interesse real por tema (Tag), cruzando volume de exposição "
        "com eficiência de consumo."
    )
    st.markdown(
    """
    **DIN (Data Interest Network)** analisa a eficiência dos temas (Tags) considerando
    o volume de exposição e o interesse real gerado.

    - **Impressions** indicam o quanto o tema foi exibido  
    - **Consumptions** representam interesse efetivo  
    - **CTR** mostra a eficiência do tema  

    Esta aba ajuda a identificar:
    - Temas estratégicos que escalam bem  
    - Oportunidades com alto interesse e baixa exposição  
    - Conteúdos com alto alcance, mas baixo engajamento  
    """
)

    # =========================
    # AGREGAÇÃO POR TAG
    # =========================
    required_cols = ["Tag", "Impressions", "Consumptions"]

    for col in required_cols:
        if col not in df.columns:
            st.warning(f"Coluna '{col}' não encontrada na base.")
            return

    agg = (
        df.groupby("Tag", dropna=False)[
            ["Impressions", "Consumptions"]
        ]
        .sum()
        .reset_index()
    )

    # =========================
    # CTR
    # =========================
    agg["CTR"] = agg.apply(
        lambda r: r["Consumptions"] / r["Impressions"]
        if r["Impressions"] > 0 else 0,
        axis=1
    )

    # =========================
    # CLASSIFICAÇÃO (DIN)
    # =========================
    impressions_median = agg["Impressions"].median()
    ctr_median = agg["CTR"].median()

    def classify(row):
        if row["Impressions"] >= impressions_median and row["CTR"] >= ctr_median:
            return "Estratégico"
        if row["Impressions"] < impressions_median and row["CTR"] >= ctr_median:
            return "Oportunidade"
        if row["Impressions"] >= impressions_median and row["CTR"] < ctr_median:
            return "Desperdício"
        return "Baixo impacto"

    agg["Classificação"] = agg.apply(classify, axis=1)

    # =========================
    # TABELA
    # =========================
    st.dataframe(
        agg.sort_values("CTR", ascending=False),
        use_container_width=True,
        column_config={
            "Impressions": st.column_config.NumberColumn("Impressions", format="%,d"),
            "Consumptions": st.column_config.NumberColumn("Consumptions", format="%,d"),
            "CTR": st.column_config.NumberColumn("CTR", format="%.2%"),
        }
    )

    # =========================
    # GRÁFICO — TOP 10 CTR
    # =========================
    st.markdown("### 🔝 Top 10 Tags por CTR")

    top10 = agg.sort_values("CTR", ascending=False).head(10)

    fig = px.bar(
        top10,
        x="CTR",
        y="Tag",
        orientation="h",
        text=top10["CTR"].apply(lambda x: f"{x:.2%}"),
    )

    fig.update_layout(yaxis=dict(autorange="reversed"))

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="din_top10_ctr_chart"
    )
