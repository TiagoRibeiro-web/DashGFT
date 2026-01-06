import streamlit as st
import plotly.express as px


def render_dashboard(data):

    st.title("📊 GFT Technology – NEW DASH")

    sheet = st.sidebar.selectbox(
        "Fonte de dados",
        list(data.keys())
    )

    df = data[sheet]

    # =========================
    # Identificação dinâmica
    # =========================
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(exclude="number").columns.tolist()

    if not numeric_cols:
        st.error("Nenhuma coluna numérica encontrada nesta aba.")
        st.dataframe(df)
        return

    # =========================
    # KPIs
    # =========================
    st.subheader("Visão Geral")

    kpi_cols = st.columns(min(4, len(numeric_cols)))

    for col, metric in zip(kpi_cols, numeric_cols[:4]):
        col.metric(
            label=metric,
            value=f"{df[metric].sum():,.0f}"
        )

    st.markdown("---")

    # =========================
    # Gráfico principal
    # =========================
    st.subheader("Análise")

    dimension = st.selectbox(
        "Dimensão",
        categorical_cols if categorical_cols else df.columns
    )

    metric = st.selectbox(
        "Métrica",
        numeric_cols
    )

    agg_df = (
        df.groupby(dimension, dropna=False)[metric]
        .sum()
        .reset_index()
        .sort_values(metric, ascending=False)
        .head(10)
    )

    fig = px.bar(
        agg_df,
        x=dimension,
        y=metric,
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    with st.expander("Ver dados brutos"):
        st.dataframe(df, use_container_width=True)
