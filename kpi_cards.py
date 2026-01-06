import streamlit as st

def kpi_card(title, value):

    st.markdown("""
    <style>
        .kpi-card {
            background: #FFFFFF;
            padding: 18px;
            border-radius: 16px;
            box-shadow: 0px 8px 25px rgba(0,0,0,0.08);
            border-left: 6px solid #0D3B66;
        }
        .kpi-title {
            font-size: 14px;
            color: #6c757d;
            font-weight: 600;
        }
        .kpi-value {
            font-size: 28px;
            font-weight: 700;
            color: #0D3B66;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)
