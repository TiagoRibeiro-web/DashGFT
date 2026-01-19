# top_voices.py (versão atualizada)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

def render_top_voices_dashboard(df):
    """
    Renderiza o dashboard da aba Top Voices.
    """
    if df.empty:
        st.warning("Nenhum dado disponível para análise.")
        return
    
    st.markdown("## 🎤 Top Voices Dashboard")
    st.markdown("Análise de performance dos principais influenciadores e tags")
    
    # Exibir informações sobre os dados
    with st.expander("ℹ️ Informações sobre os dados"):
        st.write(f"**Total de registros:** {len(df):,}")
        st.write(f"**Período:** {df['Date'].min().strftime('%d/%m/%Y') if 'Date' in df.columns and not df['Date'].isna().all() else 'N/A'} a {df['Date'].max().strftime('%d/%m/%Y') if 'Date' in df.columns and not df['Date'].isna().all() else 'N/A'}")
        st.write(f"**Colunas disponíveis:** {', '.join(df.columns.tolist())}")
    
    # Filtros específicos para Top Voices
    st.markdown("### 🔍 Filtros")
    
    col1, col2, col3 = st.columns(3)
    
    filter_applied = False
    
    with col1:
        # Filtro por país/região
        if 'País (LATAM/BR)' in df.columns:
            paises = sorted([str(p) for p in df['País (LATAM/BR)'].dropna().unique()])
            paises_selecionados = st.multiselect(
                "País/Região",
                options=paises,
                default=paises[:min(3, len(paises))] if paises else []
            )
            if paises_selecionados:
                df = df[df['País (LATAM/BR)'].isin(paises_selecionados)]
                filter_applied = True
    
    with col2:
        # Filtro por tipo de dado
        if 'Tipo de Dado' in df.columns:
            tipos = sorted([str(t) for t in df['Tipo de Dado'].dropna().unique()])
            tipos_selecionados = st.multiselect(
                "Tipo de Dado",
                options=tipos,
                default=tipos[:min(3, len(tipos))] if tipos else []
            )
            if tipos_selecionados:
                df = df[df['Tipo de Dado'].isin(tipos_selecionados)]
                filter_applied = True
    
    with col3:
        # Filtro por nome/tag
        if 'Nome_tag_post' in df.columns:
            nomes = sorted([str(n) for n in df['Nome_tag_post'].dropna().unique()])
            nomes_selecionados = st.multiselect(
                "Nome/Tag",
                options=nomes,
                default=nomes[:min(5, len(nomes))] if nomes else []
            )
            if nomes_selecionados:
                df = df[df['Nome_tag_post'].isin(nomes_selecionados)]
                filter_applied = True
    
    if filter_applied:
        st.success(f"✅ {len(df)} registros após filtros")
    
    # Métricas principais
    st.markdown("### 📈 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Posts Developed' in df.columns:
            total_posts = df['Posts Developed'].sum()
            st.metric("Total de Posts", f"{int(total_posts):,}")
        else:
            st.metric("Total de Registros", f"{len(df):,}")
    
    with col2:
        if 'Reach' in df.columns:
            total_reach = df['Reach'].sum()
            st.metric("Total de Alcance", f"{int(total_reach):,}")
    
    with col3:
        if 'Engagement' in df.columns:
            total_engagement = df['Engagement'].sum()
            st.metric("Engajamento Total", f"{int(total_engagement):,}")
    
    with col4:
        if 'Likes' in df.columns:
            total_likes = df['Likes'].sum()
            st.metric("Likes Totais", f"{int(total_likes):,}")
    
    st.markdown("---")
    
    # Análise por Perfil
    if 'Tipo de Dado' in df.columns and 'Nome_tag_post' in df.columns:
        perfis_df = df[df['Tipo de Dado'] == 'Perfil'].copy()
        
        if not perfis_df.empty:
            st.markdown("### 👥 Análise por Perfil")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top perfis por alcance
                if 'Reach' in perfis_df.columns:
                    perfis_df['Reach'] = pd.to_numeric(perfis_df['Reach'], errors='coerce')
                    top_perfis_reach = perfis_df.groupby('Nome_tag_post')['Reach'].sum().nlargest(10).reset_index()
                    
                    if not top_perfis_reach.empty:
                        fig = px.bar(
                            top_perfis_reach,
                            x='Reach',
                            y='Nome_tag_post',
                            orientation='h',
                            title='Top 10 Perfis por Alcance',
                            color='Reach',
                            color_continuous_scale='Blues'
                        )
                        fig.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top perfis por engajamento
                if 'Engagement' in perfis_df.columns:
                    perfis_df['Engagement'] = pd.to_numeric(perfis_df['Engagement'], errors='coerce')
                    top_perfis_eng = perfis_df.groupby('Nome_tag_post')['Engagement'].sum().nlargest(10).reset_index()
                    
                    if not top_perfis_eng.empty:
                        fig = px.bar(
                            top_perfis_eng,
                            x='Engagement',
                            y='Nome_tag_post',
                            orientation='h',
                            title='Top 10 Perfis por Engajamento',
                            color='Engagement',
                            color_continuous_scale='Greens'
                        )
                        fig.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    # Análise por Tag
    if 'Tipo de Dado' in df.columns and 'Nome_tag_post' in df.columns:
        tags_df = df[df['Tipo de Dado'] == 'Tag'].copy()
        
        if not tags_df.empty:
            st.markdown("### 🏷️ Análise por Tag")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top tags por engajamento
                if 'Engagement' in tags_df.columns:
                    tags_df['Engagement'] = pd.to_numeric(tags_df['Engagement'], errors='coerce')
                    top_tags_eng = tags_df.groupby('Nome_tag_post')['Engagement'].sum().nlargest(10).reset_index()
                    
                    if not top_tags_eng.empty:
                        fig = px.bar(
                            top_tags_eng,
                            x='Engagement',
                            y='Nome_tag_post',
                            orientation='h',
                            title='Top 10 Tags por Engajamento',
                            color='Engagement',
                            color_continuous_scale='Purples'
                        )
                        fig.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top tags por likes
                if 'Likes' in tags_df.columns:
                    tags_df['Likes'] = pd.to_numeric(tags_df['Likes'], errors='coerce')
                    top_tags_likes = tags_df.groupby('Nome_tag_post')['Likes'].sum().nlargest(10).reset_index()
                    
                    if not top_tags_likes.empty:
                        fig = px.bar(
                            top_tags_likes,
                            x='Likes',
                            y='Nome_tag_post',
                            orientation='h',
                            title='Top 10 Tags por Likes',
                            color='Likes',
                            color_continuous_scale='Oranges'
                        )
                        fig.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    # Análise por Post
    if 'Tipo de Dado' in df.columns and 'Nome_tag_post' in df.columns:
        posts_df = df[df['Tipo de Dado'] == 'Post'].copy()
        
        if not posts_df.empty:
            st.markdown("### 📝 Análise por Post")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top posts por alcance
                if 'Reach' in posts_df.columns:
                    posts_df['Reach'] = pd.to_numeric(posts_df['Reach'], errors='coerce')
                    top_posts_reach = posts_df.nlargest(10, 'Reach')[['Nome_tag_post', 'Reach', 'Link']]
                    
                    if not top_posts_reach.empty:
                        fig = px.bar(
                            top_posts_reach,
                            x='Reach',
                            y='Nome_tag_post',
                            orientation='h',
                            title='Top 10 Posts por Alcance',
                            color='Reach',
                            color_continuous_scale='Reds'
                        )
                        fig.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top posts por engajamento
                if 'Engagement' in posts_df.columns:
                    posts_df['Engagement'] = pd.to_numeric(posts_df['Engagement'], errors='coerce')
                    top_posts_eng = posts_df.nlargest(10, 'Engagement')[['Nome_tag_post', 'Engagement', 'Link']]
                    
                    if not top_posts_eng.empty:
                        fig = px.bar(
                            top_posts_eng,
                            x='Engagement',
                            y='Nome_tag_post',
                            orientation='h',
                            title='Top 10 Posts por Engajamento',
                            color='Engagement',
                            color_continuous_scale='Viridis'
                        )
                        fig.update_layout(
                            yaxis={'categoryorder': 'total ascending'},
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    # Análise temporal
    if 'Date' in df.columns:
        st.markdown("### 📅 Análise Temporal")
        
        try:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
            # Remover datas inválidas
            df_temp = df.dropna(subset=['Date'])
            
            if not df_temp.empty:
                # Agrupar por mês
                df_temp['Month'] = df_temp['Date'].dt.strftime('%Y-%m')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'Engagement' in df_temp.columns:
                        df_temp['Engagement'] = pd.to_numeric(df_temp['Engagement'], errors='coerce')
                        monthly_engagement = df_temp.groupby('Month')['Engagement'].sum().reset_index()
                        
                        if not monthly_engagement.empty:
                            fig = px.line(
                                monthly_engagement,
                                x='Month',
                                y='Engagement',
                                title='Engajamento Mensal',
                                markers=True,
                                line_shape='spline'
                            )
                            fig.update_layout(
                                xaxis_title='Mês',
                                yaxis_title='Engajamento',
                                height=300
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'Reach' in df_temp.columns:
                        df_temp['Reach'] = pd.to_numeric(df_temp['Reach'], errors='coerce')
                        monthly_reach = df_temp.groupby('Month')['Reach'].sum().reset_index()
                        
                        if not monthly_reach.empty:
                            fig = px.line(
                                monthly_reach,
                                x='Month',
                                y='Reach',
                                title='Alcance Mensal',
                                markers=True,
                                line_shape='spline',
                                color_discrete_sequence=['#FF6B6B']
                            )
                            fig.update_layout(
                                xaxis_title='Mês',
                                yaxis_title='Alcance',
                                height=300
                            )
                            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Não foi possível gerar análise temporal: {e}")
    
    # Tabela de dados
    st.markdown("### 📋 Dados Detalhados")
    
    # Selecionar colunas para exibição
    display_cols = []
    preferred_cols = ['Date', 'País (LATAM/BR)', 'Tipo de Dado', 'Nome_tag_post', 
                     'Reach', 'Engagement', 'Likes', 'Comments', 'Link']
    
    for col in preferred_cols:
        if col in df.columns:
            display_cols.append(col)
    
    # Adicionar outras colunas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        if col not in display_cols and col != 'Quantidade':
            display_cols.append(col)
    
    if display_cols:
        # Ordenar por data se disponível
        if 'Date' in df.columns:
            df_display = df[display_cols].sort_values('Date', ascending=False)
        else:
            df_display = df[display_cols]
        
        # Configurar colunas para exibição
        column_config = {}
        if 'Link' in df_display.columns:
            column_config['Link'] = st.column_config.LinkColumn("Link", display_text="🔗")
        
        # Configurar colunas numéricas
        for col in df_display.select_dtypes(include=[np.number]).columns:
            column_config[col] = st.column_config.NumberColumn(format="%d")
        
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config=column_config,
            height=400
        )
    
    # Exportar dados
    st.markdown("---")
    st.markdown("### 📤 Exportar Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exportar Top Voices (CSV)", use_container_width=True):
            csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="Baixar CSV",
                data=csv,
                file_name=f"top_voices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("📊 Exportar Relatório (Excel)", use_container_width=True):
            # Criar Excel com múltiplas abas
            with pd.ExcelWriter('top_voices_report.xlsx', engine='openpyxl') as writer:
                # Dados completos
                df.to_excel(writer, sheet_name='Dados Completos', index=False)
                
                # Resumo por perfil
                if 'Tipo de Dado' in df.columns and 'Nome_tag_post' in df.columns:
                    perfis_df = df[df['Tipo de Dado'] == 'Perfil'].copy()
                    if not perfis_df.empty:
                        perfis_summary = perfis_df.groupby('Nome_tag_post').agg({
                            'Reach': 'sum',
                            'Engagement': 'sum',
                            'Likes': 'sum'
                        }).reset_index()
                        perfis_summary.to_excel(writer, sheet_name='Resumo Perfis', index=False)
                
                # Resumo por tag
                if 'Tipo de Dado' in df.columns and 'Nome_tag_post' in df.columns:
                    tags_df = df[df['Tipo de Dado'] == 'Tag'].copy()
                    if not tags_df.empty:
                        tags_summary = tags_df.groupby('Nome_tag_post').agg({
                            'Engagement': 'sum',
                            'Likes': 'sum',
                            'Comments': 'sum'
                        }).reset_index()
                        tags_summary.to_excel(writer, sheet_name='Resumo Tags', index=False)
            
            with open('top_voices_report.xlsx', 'rb') as f:
                st.download_button(
                    label="Baixar Excel",
                    data=f,
                    file_name=f"top_voices_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )