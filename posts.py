import streamlit as st

def render_posts(df, kpis):

    metric = st.selectbox("Ordenar por", kpis, key="posts_metric")

    cols = ["Name", "Post", "Permalink", metric]
    cols = [c for c in cols if c in df.columns]

    ranking = df[cols].sort_values(metric, ascending=False).head(20)

    st.dataframe(
        ranking,
        use_container_width=True,
        column_config={
            "Permalink": st.column_config.LinkColumn("Link")
        }
    )
