import streamlit as st
import plotly.express as px
from kpi_cards import kpi_card


def render_new_dash(df, kpis):

    # =========================
    # KPIs (CARDS ESTILOSOS)
    # =========================
    st.subheader("📊 Visão Geral")

    kpi_cols = st.columns(5)
    for i, kpi in enumerate(kpis):
        df_kpi = df.copy()
        value = int(df_kpi[kpi].sum())
        with kpi_cols[i % 5]:
            kpi_card(kpi, f"{value:,}")

    st.markdown("---")

    # =========================
    # TOP 10 POR DIMENSÃO
    # =========================
    st.subheader("📈 Top 10 por Dimensão")

    dim = st.selectbox(
        "Dimensão",
        [c for c in df.columns if c not in kpis],
        key="nd_dim"
    )

    metric = st.selectbox(
        "Métrica",
        kpis,
        key="nd_metric"
    )

    df_top = df.copy()

    top = (
        df_top
        .groupby(dim, dropna=False)[metric]
        .sum()
        .reset_index()
        .sort_values(metric, ascending=False)
        .head(10)
    )

    fig_top = px.bar(
        top,
        x=dim,
        y=metric,
        text_auto=True
    )

    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")

    # =========================
    # COMPARATIVO MONTH vs MONTH
    # =========================
    st.subheader("📊 Comparativo Month vs Month")

    df_cmp = df.copy()

    months = (
        df_cmp["Month"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )
    months = sorted(months)

    col1, col2, col3 = st.columns(3)

    with col1:
        cmp_metric = st.selectbox(
            "Métrica",
            kpis,
            key="cmp_metric"
        )

    with col2:
        month_a = st.selectbox(
            "Mês A",
            months,
            key="cmp_month_a"
        )

    with col3:
        month_b = st.selectbox(
            "Mês B",
            months,
            index=1 if len(months) > 1 else 0,
            key="cmp_month_b"
        )

    val_a = df_cmp[df_cmp["Month"].astype(str) == month_a][cmp_metric].sum()
    val_b = df_cmp[df_cmp["Month"].astype(str) == month_b][cmp_metric].sum()

    delta = ((val_b - val_a) / val_a * 100) if val_a else 0

    st.metric(
        label=f"{cmp_metric}: {month_b} vs {month_a}",
        value=f"{int(val_b):,}",
        delta=f"{delta:.2f}%"
    )

    st.markdown("---")

    # =========================
    # EVOLUÇÃO TEMPORAL
    # =========================
    st.subheader("📉 Evolução Temporal")

    time_metric = st.selectbox(
        "Métrica para evolução",
        kpis,
        key="time_metric"
    )

    df_time = df.copy()

    trend = (
        df_time
        .groupby("Month", dropna=False)[time_metric]
        .sum()
        .reset_index()
        .sort_values("Month")
    )

    fig_line = px.line(
        trend,
        x="Month",
        y=time_metric,
        markers=True
    )

    st.plotly_chart(fig_line, use_container_width=True)
