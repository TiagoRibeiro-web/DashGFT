# app.py - VERSÃO COMPLETA ATUALIZADA COM TOP VOICES
import streamlit as st
import pandas as pd
import zipfile
import tempfile
import os
from datetime import datetime
from PIL import Image
from din import render_din
from tv_din import render_tv_din

# =========================
# Imports internos
# =========================
from auth import login_screen
from data_loader import load_data, load_top_voices_data
from filters import apply_filters
from new_dash import render_new_dash
from posts import render_posts
from tags import render_tags
from exports import export_multi_excel, export_full_excel
from topvoices import render_top_voices_dashboard

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="GFT Technology | Social Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Funções auxiliares
# =========================
def export_all_data(df_main_filtered, df_top_voices):
    """
    Exporta todos os dados do sistema (principal + top voices).
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"gft_dashboard_completo_{timestamp}.zip"
        
        # Criar arquivo temporário ZIP
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                # 1. Adicionar dados principais
                if not df_main_filtered.empty:
                    main_csv_path = os.path.join(tmpdir, 'dados_principais.csv')
                    df_main_filtered.to_csv(main_csv_path, index=False, encoding='utf-8-sig')
                    zipf.write(main_csv_path, 'dados_principais.csv')
                
                # 2. Adicionar dados Top Voices completos
                if not df_top_voices.empty:
                    tv_csv_path = os.path.join(tmpdir, 'top_voices_completo.csv')
                    df_top_voices.to_csv(tv_csv_path, index=False, encoding='utf-8-sig')
                    zipf.write(tv_csv_path, 'top_voices_completo.csv')
                
                # 3. Adicionar relatório resumido
                summary_path = os.path.join(tmpdir, 'resumo.txt')
                with open(summary_path, 'w', encoding='utf-8') as f:
                    f.write(f"Relatório GFT Dashboard - {timestamp}\n")
                    f.write("="*50 + "\n\n")
                    f.write(f"Dados principais: {len(df_main_filtered)} registros\n")
                    f.write(f"Top Voices: {len(df_top_voices)} registros\n")
                    
                    # Estatísticas principais
                    if not df_main_filtered.empty:
                        if 'Reach' in df_main_filtered.columns:
                            total_reach = df_main_filtered['Reach'].sum()
                            f.write(f"Alcance total principal: {int(total_reach):,}\n")
                    
                    if not df_top_voices.empty:
                        if 'Reach' in df_top_voices.columns:
                            total_reach_tv = df_top_voices['Reach'].sum()
                            f.write(f"Alcance total Top Voices: {int(total_reach_tv):,}\n")
                    
                    f.write(f"\nGerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                zipf.write(summary_path, 'resumo.txt')
            
            # Ler o arquivo ZIP para download
            with open(zip_path, 'rb') as f:
                st.sidebar.download_button(
                    label="📥 Baixar ZIP completo",
                    data=f,
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True
                )
        
        st.sidebar.success(f"✅ ZIP '{zip_filename}' pronto para download!")
        
    except Exception as e:
        st.sidebar.error(f"❌ Erro ao criar export global: {str(e)}")

# =========================
# Controle de sessão
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

# =========================
# Login
# =========================
if not st.session_state.auth:
    login_screen()
    st.stop()

# ======================================================
# USUÁRIO AUTENTICADO
# ======================================================

# =========================
# Carregar dados - AGORA COM TOP VOICES
# =========================
try:
    # Carrega dados principais e Top Voices
    df_main, KPIS, FILTERS, df_top_voices = load_data()
    
    # Armazenar em session_state para acesso em outros módulos
    st.session_state['df_main'] = df_main
    st.session_state['df_top_voices'] = df_top_voices
    
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {str(e)}")
    # Criar DataFrames vazios em caso de erro
    df_main = pd.DataFrame()
    df_top_voices = pd.DataFrame()
    st.stop()

# =========================
# Aplicar filtros globais apenas ao df_main
# =========================
df_main_filtered = apply_filters(df_main.copy(), FILTERS)

# =========================
# Header com logo
# =========================
try:
    logo = Image.open("assets/gft_logo.jpg")
    
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        st.image(logo, width=120)
    with col_title:
        st.markdown("## Social Media Dashboard")
        st.markdown("Visão consolidada de performance de mídias sociais")
    
    st.markdown("---")
except Exception as e:
    st.warning(f"⚠️ Logo não encontrada: {e}")
    st.markdown("## Social Media Dashboard")
    st.markdown("---")

# =========================
# DATAFRAMES PARA EXPORT - APENAS DO MAIN
# =========================

# -------- NEW DASH (base filtrada)
df_new_dash = df_main_filtered.copy()

# -------- POSTS (FORMATO IGUAL AO EXCEL ORIGINAL)
# Verificar colunas disponíveis para evitar erros
available_columns = df_main_filtered.columns.tolist()

# Mapear nomes de colunas possíveis
column_mapping = {
    'description': ['description', 'Description', 'Descrição', 'Post Description'],
    'Permalink': ['Permalink', 'Link', 'URL', 'Post URL', 'Link do Post']
}

# Encontrar nomes reais das colunas
desc_column = None
link_column = None

for key, possible_names in column_mapping.items():
    for name in possible_names:
        if name in available_columns:
            if key == 'description':
                desc_column = name
            elif key == 'Permalink':
                link_column = name
            break

# Criar DataFrame para export de posts
df_posts_export = df_main_filtered.copy()

# Renomear colunas se encontradas
if desc_column:
    df_posts_export = df_posts_export.rename(columns={desc_column: "Description"})
if link_column:
    df_posts_export = df_posts_export.rename(columns={link_column: "Link"})

# Definir colunas para export
posts_columns = [
    "Channel",
    "Name",
    "Date",
    "Reach",
    "Impressions",
    "Engagement",
    "CTR",
    "Video Views",
    "Description",
    "Link",
    "Score"
]

# Mantém apenas colunas existentes
posts_columns = [c for c in posts_columns if c in df_posts_export.columns]

# =========================
# NORMALIZAÇÃO DEFINITIVA DA DATA
# =========================
if "Date" in df_posts_export.columns:
    df_posts_export["Date_norm"] = pd.to_datetime(
        df_posts_export["Date"].astype(str).str.strip(),
        errors="coerce",
        dayfirst=True
    )
else:
    df_posts_export["Date_norm"] = pd.NaT

# Ordenação segura
if not df_posts_export.empty:
    df_posts_export = (
        df_posts_export
        .sort_values("Date_norm", ascending=False)
        .loc[:, posts_columns]   # remove Date_norm antes do export
    )

# -------- TAGS (AGREGADO)
if not df_main_filtered.empty and "Tag" in df_main_filtered.columns:
    numeric_cols = ["Impressions", "Reach", "Interactions", "Video Views"]
    available_numeric = [col for col in numeric_cols if col in df_main_filtered.columns]
    
    if available_numeric:
        df_tags_export = (
            df_main_filtered.groupby("Tag", dropna=False)[available_numeric]
            .sum()
            .reset_index()
        )
    else:
        df_tags_export = pd.DataFrame(columns=["Tag"])
else:
    df_tags_export = pd.DataFrame(columns=["Tag"])

# =========================
# EXPORT EXCEL MULTI-ABA
# =========================
if not df_new_dash.empty:
    try:
        export_multi_excel(
            df_base=df_new_dash,
            df_posts=df_posts_export,
            df_tags=df_tags_export
        )
    except Exception as e:
        st.sidebar.warning(f"⚠️ Erro ao criar export multi-aba: {e}")

# =========================
# EXPORT FULL (BASE COMPLETA)
# =========================
if not df_main_filtered.empty:
    try:
        export_full_excel(df_main_filtered)
    except Exception as e:
        st.sidebar.warning(f"⚠️ Erro ao criar export completo: {e}")

# =========================
# Abas do dashboard - ATUALIZADO COM TOP VOICES
# =========================
tab1, tab2, tab3, tab6 = st.tabs([
    "📊 NEW DASH",
    "📝 POSTS",
    "🏷️ TAGS",
    
    "🎤 TOP VOICES"
])

with tab1:
    if not df_main_filtered.empty:
        render_new_dash(df_main_filtered.copy(), KPIS)
    else:
        st.warning("⚠️ Nenhum dado disponível para análise.")
        st.info("Verifique se o arquivo 'banco_de_posts_gft.xlsx' está na pasta correta.")

with tab2:
    if not df_main_filtered.empty:
        render_posts(df_main_filtered.copy(), KPIS)
    else:
        st.warning("⚠️ Nenhum dado disponível para análise.")
        st.info("Verifique se o arquivo 'banco_de_posts_gft.xlsx' está na pasta correta.")

with tab3:
    if not df_main_filtered.empty:
        render_tags(df_main_filtered.copy(), KPIS)
    else:
        st.warning("⚠️ Nenhum dado disponível para análise.")
        st.info("Verifique se o arquivo 'banco_de_posts_gft.xlsx' está na pasta correta.")

# with tab4:
#     if not df_main_filtered.empty:
#         render_din(df_main_filtered.copy())
#     else:
#         st.warning("⚠️ Nenhum dado disponível para análise.")
#         st.info("Verifique se o arquivo 'banco_de_posts_gft.xlsx' está na pasta correta.")

# with tab5:
#     if not df_main_filtered.empty:
#         render_tv_din(df_main_filtered.copy())
#     else:
#         st.warning("⚠️ Nenhum dado disponível para análise.")
#         st.info("Verifique se o arquivo 'banco_de_posts_gft.xlsx' está na pasta correta.")

with tab6:
    # Usar dados específicos do Top Voices
    if not df_top_voices.empty:
        render_top_voices_dashboard(df_top_voices.copy())
    else:
        st.warning("⚠️ Dados da planilha Top Voices não disponíveis.")
        st.info("""
        Para usar a funcionalidade Top Voices:
        1. Certifique-se de que o arquivo 'topvoices.xlsx' está na mesma pasta do aplicativo
        2. O arquivo deve ter as colunas conforme o template:
           - Date, País (LATAM/BR), Tipo de Dado, Nome_tag_post, Link
           - Posts Developed, Reach, Engagement, Likes, Comments, Quantidade
        3. Recarregue a página após adicionar o arquivo
        """)
        
        # Opção para carregar manualmente
        if st.button("🔄 Tentar carregar dados do Top Voices novamente"):
            try:
                df_top_voices = load_top_voices_data()
                if not df_top_voices.empty:
                    st.success("✅ Dados carregados com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Ainda não foi possível carregar os dados.")
            except Exception as e:
                st.error(f"❌ Erro ao carregar: {e}")

# =========================
# Sidebar com estatísticas e controles
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Estatísticas")

if not df_main_filtered.empty:
    st.sidebar.metric("📋 Registros Principais", f"{len(df_main_filtered):,}")
    
    if 'Channel' in df_main_filtered.columns:
        channels = df_main_filtered['Channel'].nunique()
        st.sidebar.metric("📺 Canais", channels)
    
    if 'Date' in df_main_filtered.columns:
        try:
            min_date = pd.to_datetime(df_main_filtered['Date']).min()
            max_date = pd.to_datetime(df_main_filtered['Date']).max()
           # st.sidebar.metric("📅 Período", f"{min_date.strftime('%d/%m/%Y')} a {max_date.strftime('%d/%m/%Y')}")
        except:
            pass

if not df_top_voices.empty:
    st.sidebar.metric("🎤 Registros Top Voices", f"{len(df_top_voices):,}")

# =========================
# Exportação Global
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("### 📤 Exportação Global")

if st.sidebar.button("📁 Exportar TODOS os dados (ZIP)", 
                    use_container_width=True,
                    help="Exporta todos os dados em um único arquivo ZIP"):
    export_all_data(df_main_filtered, df_top_voices)

# =========================
# Logout
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Controle de Acesso")

if st.sidebar.button("🚪 Sair do sistema", 
                    use_container_width=True,
                    type="primary"):
    # Limpar session_state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# =========================
# Informações de versão
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ Informações")
st.sidebar.caption("**Dashboard v2.0**")
st.sidebar.caption("Inclui módulo Top Voices")
st.sidebar.caption(f"Dados carregados: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}")

# =========================
# Debug informações (opcional)
# =========================
if st.sidebar.checkbox("🔍 Mostrar informações de debug", False):
    st.sidebar.markdown("### Debug Info")
    
    st.sidebar.write("**Dados principais:**")
    st.sidebar.write(f"- Shape: {df_main.shape}")
    st.sidebar.write(f"- Colunas: {len(df_main.columns)}")
    
    st.sidebar.write("**Top Voices:**")
    st.sidebar.write(f"- Shape: {df_top_voices.shape}")
    st.sidebar.write(f"- Colunas: {len(df_top_voices.columns)}")
    
    if not df_top_voices.empty:
        st.sidebar.write("**Amostra Top Voices:**")
        st.sidebar.dataframe(df_top_voices.head(3))
    
    st.sidebar.write("**Session State:**")
    st.sidebar.write(list(st.session_state.keys()))

# =========================
# Rodapé
# =========================
st.markdown("---")
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    st.caption("GFT Technology Social Dashboard | Versão 2.0 | Desenvolvido para análise de mídias sociais")
    st.caption("© 2026 GFT Technology. Todos os direitos reservados.")