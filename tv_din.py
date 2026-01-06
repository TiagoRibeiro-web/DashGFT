import streamlit as st
import pandas as pd
import plotly.express as px

def render_tv_din(df):

    st.subheader("📺 TV-DIN — Eficiência Temática em Vídeo")

    st.caption(
        "Avalia quais temas funcionam melhor quando apresentados em formato de vídeo."
    )
    st.markdown(
    """
    **TV-DIN** é uma especialização da análise temática focada em conteúdos de vídeo.

    Aqui, o foco não é apenas visualização, mas **consumo real**:
    - **Video Views** indicam atenção inicial  
    - **Consumptions** indicam retenção/interesse  
    - **CTR** mostra a eficiência do tema em vídeo  

    Esta aba ajuda a responder:
    - Quais temas funcionam melhor em vídeo  
    - Quais temas não se beneficiam do formato audiovisual  
    - Onde investir esforços em Reels, Shorts ou Lives  
    """
)


    required_cols = [
        "Tag",
        "Impressions",
        "Consumptions",
        "Video Views"
    ]

    for col in required_cols:
        if col not in df.columns:
            st.warning(f"Coluna '{col}' não encontrada na base.")
            return

    # =========================
    # AGREGAÇÃO POR TAG
    # =========================
    agg = (
        df.groupby("Tag", dropna=False)[
            ["Impressions", "Consumptions", "Video Views"]
        ]
        .sum()
        .reset_index()
    )

    # =========================
    # CTR (vídeo)
    # =========================
    agg["CTR"] = agg.apply(
        lambda r: r["Consumptions"] / r["Impressions"]
        if r["Impressions"] > 0 else 0,
        axis=1
    )

    # =========================
    # CLASSIFICAÇÃO (TV-DIN)
    # =========================
    ctr_median = agg["CTR"].median()

    def classify_video(row):
        if row["CTR"] >= ctr_median:
            return "Forte em vídeo"
        if row["CTR"] >= ctr_median * 0.7:
            return "Neutro"
        return "Fraco em vídeo"

    agg["Classificação"] = agg.apply(classify_video, axis=1)

    # =========================
    # TABELA
    # =========================
    st.dataframe(
        agg.sort_values("CTR", ascending=False),
        use_container_width=True,
        column_config={
            "Video Views": st.column_config.NumberColumn("Video Views", format="%,d"),
            "Impressions": st.column_config.NumberColumn("Impressions", format="%,d"),
            "Consumptions": st.column_config.NumberColumn("Consumptions", format="%,d"),
            "CTR": st.column_config.NumberColumn("CTR", format="%.2%"),
        }
    )

    # =========================
    # GRÁFICO — TOP 10 CTR VÍDEO
    # =========================
    st.markdown("### 🎬 Top 10 Tags por CTR em Vídeo")

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
        key="tv_din_top10_ctr_chart"
    )
