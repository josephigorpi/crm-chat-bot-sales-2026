# sidebar.py
import streamlit as st
from datetime import datetime

def sidebar_navigation():
    """Navegación en la barra lateral"""
    with st.sidebar:
        # Logo y título
        st.markdown("""
        <div class="sidebar-logo">
            <h2>🤖 Chatbot Ventas</h2>
            <p style="color: #6b7280; font-size: 0.9rem;">Dashboard v1.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Información del usuario
        if 'username' in st.session_state and st.session_state.username:
            st.markdown(f"""
            <div class="user-info">
                <strong>👤 {st.session_state.username}</strong><br>
                <small>Conectado desde: {datetime.now().strftime('%H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Menú de navegación
        st.markdown("### 📋 Páginas Disponibles")
        st.markdown("""
        Usa el selector de páginas arriba para navegar:
        
        - 🏠 **app**: Dashboard Principal
        - 📦 **02_Productos**: Análisis de productos
        - 👥 **03_Clientes**: Gestión de clientes  
        - 💬 **04_Conversaciones**: Análisis del chatbot
        - 🛒 **05_Carritos_Abandonados**: Recuperación de ventas
        - 📦 **06_Pedidos_y_Envios**: Gestión de órdenes
        - 📊 **07_Reportes**: Generación de informes
        - ⚙️ **08_Configuracion**: Ajustes del sistema
        """)
        
        st.markdown("---")
        
        # ✅ NUEVO: Botón de modo oscuro/claro
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 🌓 Tema")
        with col2:
            # Inicializar estado del tema si no existe
            if 'dark_mode' not in st.session_state:
                st.session_state.dark_mode = False
            
            # Botón toggle con ícono dinámico
            icon = "🌙" if not st.session_state.dark_mode else "☀️"
            label = "Oscuro" if not st.session_state.dark_mode else "Claro"
            
            if st.button(f"{icon} {label}", use_container_width=True, key="theme_toggle"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
        
        
        st.markdown("---")
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()
