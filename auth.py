import streamlit as st
from PIL import Image
import bcrypt

def login_screen():

    # =========================
    # ESTILO
    # =========================
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp {
        background: linear-gradient(135deg, #0D3B66, #145DA0);
    }
    h1, h2, h3, label {
        color: white !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #145DA0, #0D3B66);
        color: white;
        border-radius: 10px;
        height: 45px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown("<br><br><br>", unsafe_allow_html=True)

        logo = Image.open("assets/gft_logo.jpg")
        st.image(logo, width=220)

        st.markdown("### Social Media Dashboard")

        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar"):

            try:
                secret_user = st.secrets["auth"]["username"]
                secret_hash = st.secrets["auth"]["password_hash"]
            except KeyError:
                st.error("Configuração de autenticação não encontrada.")
                return

            if username == secret_user and bcrypt.checkpw(
                password.encode("utf-8"),
                secret_hash.encode("utf-8")
            ):
                st.session_state.auth = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")
