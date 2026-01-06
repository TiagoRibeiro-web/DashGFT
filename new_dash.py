import streamlit as st
import pandas as pd
import plotly.express as px


def render_new_dash(df: pd.DataFrame, kpis: list):
    st.header("📊 Visão Geral")

    # =========================
    # KPIs (cards simples)
    # =========================
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            value = pd.to_numeric(df[kpi], errors="coerce").sum()
            st.metric(kpi, f"{value:,.0f}")

    st.markdown("---")

    # =========================
    # EVOLUÇÃO TEMPORAL (CORRETA)
    # =========================
    st.subheader("📉 Evolução Temporal")

    time_metric = st.selectbox(
        "Métrica para evolução",
        kpis,
        key="time_metric"
    )

    df_time = df.copy()

    # Garante datetime
    df_time["Date_norm"] = pd.to_datetime(
        df_time["Date_norm"],
        errors="coerce"
    )

    # Cria período mensal REAL
    df_time["YearMonth"] = (
        df_time["Date_norm"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    trend = (
        df_time
        .groupby("YearMonth", as_index=False)[time_metric]
        .sum()
        .sort_values("YearMonth")
    )

    fig_line = px.line(
        trend,
        x="YearMonth",
        y=time_metric,
        markers=True,
        labels={
            "YearMonth": "Mês",
            time_metric: time_metric
        }
    )

    fig_line.update_layout(
        xaxis=dict(
            tickformat="%b/%Y",
            tickangle=-45
        )
    )

    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    # =========================
    # TOP 10 POR DIMENSÃO (CORRIGIDO)
    # =========================
    st.subheader("📊 Top 10 por Dimensão")

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
