# sidebar.py
import streamlit as st
from datetime import datetime
from i18n.strings import get_string
from utils.theme import toggle_theme, get_theme, init_theme_state

def sidebar_navigation():
    """Navegación en la barra lateral con soporte para tema e idioma"""
    with st.sidebar:
        # Inicializar estado de idioma si no existe
        if 'language' not in st.session_state:
            st.session_state.language = 'es'
        
        # Inicializar tema
        init_theme_state()
        
        # Logo y título
        st.markdown(f"""
        <div class="sidebar-logo">
            <h2>{get_string('sidebar_title', st.session_state.language)}</h2>
            <p style="color: #6b7280; font-size: 0.9rem;">{get_string('sidebar_version', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Información del usuario
        if 'username' in st.session_state and st.session_state.username:
            st.markdown(f"""
            <div class="user-info">
                <strong>👤 {st.session_state.username}</strong><br>
                <small>{get_string('sidebar_connected_from', st.session_state.language)}: {datetime.now().strftime('%H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Menú de navegación
        st.markdown(f"### {get_string('sidebar_pages', st.session_state.language)}")
        st.markdown(f"""
        {get_string('sidebar_pages_info', st.session_state.language)}
        
        - {get_string('sidebar_page_dashboard', st.session_state.language)}
        - {get_string('sidebar_page_products', st.session_state.language)}
        - {get_string('sidebar_page_customers', st.session_state.language)}
        - {get_string('sidebar_page_conversations', st.session_state.language)}
        - {get_string('sidebar_page_abandoned_carts', st.session_state.language)}
        - {get_string('sidebar_page_orders', st.session_state.language)}
        - {get_string('sidebar_page_reports', st.session_state.language)}
        - {get_string('sidebar_page_settings', st.session_state.language)}
        """)
        
        st.markdown("---")
        
        # ✅ Selector de Idioma
        st.markdown(f"### {get_string('sidebar_language', st.session_state.language)}")
        
        language_options = {'Español': 'es', 'English': 'en'}
        selected_language = st.selectbox(
            "Seleccionar idioma / Select language",
            options=list(language_options.keys()),
            index=0 if st.session_state.language == 'es' else 1,
            key="language_selector"
        )
        
        if language_options[selected_language] != st.session_state.language:
            st.session_state.language = language_options[selected_language]
            st.rerun()
        
        st.markdown("---")
        
        # ✅ Botón de modo oscuro/claro mejorado
        st.markdown(f"### {get_string('sidebar_theme', st.session_state.language)}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            pass  # Espacio para alineación
        with col2:
            # Botón toggle con ícono dinámico
            current_theme = get_theme()
            if current_theme == 'light':
                icon = "🌙"
                label = get_string('sidebar_theme_dark', st.session_state.language)
            else:
                icon = "☀️"
                label = get_string('sidebar_theme_light', st.session_state.language)
            
            if st.button(f"{icon} {label}", use_container_width=True, key="theme_toggle"):
                toggle_theme()
                st.rerun()
        
        st.markdown("---")
        
        # Botón de cerrar sesión
        if st.button(f"🚪 {get_string('sidebar_logout', st.session_state.language)}", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()
