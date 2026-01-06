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
        value = int(df[kpi].sum())
        with kpi_cols[i % 5]:
            kpi_card(kpi, f"{value:,}")

    st.markdown("---")

    # =========================
    # TOP 10 POR DIMENSÃO
    # =========================
    st.subheader("📈 Top 10 por Dimensão")

    dims = [
        c for c in df.columns
        if c not in kpis
        and df[c].dtype == "object"
        and c not in ["Date", "Date_norm", "Month", "YearMonth"]
    ]

    dim = st.selectbox(
        "Dimensão",
        dims,
        key="top10_dim"
    )

    metric = st.selectbox(
        "Métrica",
        kpis,
        key="top10_metric"
    )

    df_top = df.copy()

    # Garante numérico
    df_top[metric] = pd.to_numeric(
        df_top[metric],
        errors="coerce"
    ).fillna(0)

    top10 = (
        df_top
        .groupby(dim, dropna=False)[metric]
        .sum()
        .reset_index()
        .sort_values(metric, ascending=False)
        .head(10)
    )

    fig_bar = px.bar(
        top10,
        x=dim,
        y=metric,
        text=metric,
        labels={
            dim: dim,
            metric: metric
        }
    )

    fig_bar.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="inside"
    )

    fig_bar.update_layout(
        xaxis=dict(
            categoryorder="total descending"
        )
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # =========================
    # COMPARATIVO MONTH vs MONTH
    # =========================
    st.subheader("📊 Comparativo Month vs Month")

    months = (
        df["Month"]
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

    val_a = df[df["Month"].astype(str) == month_a][cmp_metric].sum()
    val_b = df[df["Month"].astype(str) == month_b][cmp_metric].sum()

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

    trend = (
        df.groupby("Month", dropna=False)[time_metric]
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
