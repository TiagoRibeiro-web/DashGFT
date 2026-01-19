# auth.py - ATUALIZADO para usar secrets.toml
import streamlit as st
import bcrypt

def verify_login(username, password):
    """Verifica se usuário e senha são válidos usando secrets.toml"""
    try:
        # Verifica se o usuário existe no secrets
        if "auth" in st.secrets and username in st.secrets["auth"]:
            stored_hash = st.secrets["auth"][username]
            # Verifica o hash bcrypt
            return bcrypt.checkpw(password.encode(), stored_hash.encode())
    except Exception as e:
        st.error(f"Erro na verificação: {e}")
    return False

def login_screen():
    """Tela de login usando secrets.toml"""
    
    st.markdown(
        """
        <style>
        .login-container {
            max-width: 400px;
            margin: 150px auto;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            background-color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.title("🔐 GFT Dashboard")
        
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        
        if st.button("Entrar", use_container_width=True):
            if verify_login(username, password):
                st.session_state.auth = True
                st.session_state.current_user = username
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos!")
        
        st.markdown('</div>', unsafe_allow_html=True)