"""
Dashboard Frontend para Chatbot de Ventas con IA
Aplicación principal con sistema de autenticación y navegación
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Importar utilidades locales
from utils.data_generator import get_all_data, get_calculated_metrics
from utils.chart_utils import (
    create_sales_timeline, create_order_status_donut, 
    create_messages_by_hour, create_intent_distribution
)

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Chatbot Ventas",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .sidebar-logo {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    .user-info {
        background: #f3f4f6;
        padding: 0.8rem;
        border-radius: 8px;
        margin: 1rem 0;
        text-align: center;
        color: #1f2937;
    }
    
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        color: #1f2937;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-title {
        font-size: 2rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        color: #6b7280;
        font-size: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .welcome-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    
    .table-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

from sidebar import sidebar_navigation


def init_session_state():
    """Inicializa el estado de la sesión"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'remember_me' not in st.session_state:
        st.session_state.remember_me = False

def login_page():
    """Página de login"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Header del login
    st.markdown("""
    <div class="login-header">
        <div class="login-title">🤖 Chatbot Ventas</div>
        <div class="login-subtitle">Dashboard de Administración</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="admin@chatbot.com")
        password = st.text_input("🔒 Contraseña", type="password", placeholder="admin123")
        remember_me = st.checkbox("🔄 Recordar sesión")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.form_submit_button("🚀 Iniciar Sesión")
    
    # Validación de credenciales
    if login_button:
        if email == "admin@chatbot.com" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.username = "Administrador"
            st.session_state.remember_me = remember_me
            st.success("✅ ¡Bienvenido! Redirigiendo al dashboard...")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas. Usa: admin@chatbot.com / admin123")
    
    # Información de credenciales de prueba
    st.markdown("---")
    st.info("""
    **Credenciales de prueba:**
    - Email: admin@chatbot.com
    - Contraseña: admin123
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)



def dashboard_page():
    """Página principal del dashboard"""
    st.markdown('<h1 class="main-header">📊 Dashboard Principal</h1>', unsafe_allow_html=True)
    
    # Mensaje de bienvenida
    st.markdown(f"""
    <div class="welcome-message">
        <h3>¡Bienvenido, {st.session_state.username}! 👋</h3>
        <p>Aquí tienes un resumen completo de tu negocio actualizado en tiempo real.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    try:
        with st.spinner("Cargando datos del dashboard..."):
            data = get_all_data()
            metrics = get_calculated_metrics()
        
        # Métricas principales en cards
        st.markdown("### 📈 Métricas Principales")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Total Ventas",
                value=f"€{metrics['total_sales']:,.2f}",
                delta=f"+12.5%"
            )
        
        with col2:
            st.metric(
                label="👥 Total Clientes", 
                value=f"{metrics['total_customers']:,}",
                delta=f"+{len(data['customers'][pd.to_datetime(data['customers']['created_at']) >= datetime.now() - pd.Timedelta(days=30)])}"
            )
        
        with col3:
            st.metric(
                label="📦 Total Pedidos",
                value=f"{metrics['total_orders']:,}",
                delta=f"Promedio: {metrics['total_orders']/30:.1f}/día"
            )
        
        with col4:
            st.metric(
                label="📊 Tasa Conversión",
                value=f"{metrics['conversion_rate']:.1f}%",
                delta=f"+2.3%"
            )
        
        st.markdown("---")
        
        # Gráficos principales
        st.markdown("### 📊 Análisis Visual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de ventas en el tiempo
            sales_chart = create_sales_timeline(data['orders'])
            st.plotly_chart(sales_chart, use_container_width=True)
        
        with col2:
            # Gráfico de estados de pedidos
            status_chart = create_order_status_donut(data['orders'])
            st.plotly_chart(status_chart, use_container_width=True)
        
        # Segunda fila de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Mensajes por hora
            messages_chart = create_messages_by_hour(data['conversations'])
            st.plotly_chart(messages_chart, use_container_width=True)
        
        with col2:
            # Distribución de intenciones
            intent_chart = create_intent_distribution(data['conversations'])
            st.plotly_chart(intent_chart, use_container_width=True)
        
        st.markdown("---")
        
        # Tabla de últimos pedidos
        st.markdown("### 📋 Últimos 10 Pedidos")
        
        recent_orders = data['orders'].merge(
            data['customers'][['id', 'first_name', 'last_name']], 
            left_on='customer_id', 
            right_on='id'
        ).sort_values('created_at', ascending=False).head(10)
        
        # Formatear datos para mostrar
        display_orders = recent_orders[['id', 'first_name', 'last_name', 'total_amount', 'status', 'created_at']].copy()
        display_orders['Cliente'] = display_orders['first_name'] + ' ' + display_orders['last_name']
        display_orders['Monto'] = display_orders['total_amount'].apply(lambda x: f"€{x:.2f}")
        display_orders['Estado'] = display_orders['status'].str.title()
        display_orders['Fecha'] = pd.to_datetime(display_orders['created_at']).dt.strftime('%d/%m/%Y %H:%M')
        display_orders['ID'] = display_orders['id'].str[:8] + "..."
        
        st.dataframe(
            display_orders[['ID', 'Cliente', 'Monto', 'Estado', 'Fecha']],
            use_container_width=True,
            hide_index=True
        )
        
        # Información adicional
        st.markdown("### ℹ️ Información del Sistema")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **🔄 Última actualización:**  
            {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            """)
        
        with col2:
            st.info(f"""
            **📊 Datos cargados:**  
            {len(data['customers'])} clientes, {len(data['products'])} productos
            """)
        
        with col3:
            st.info(f"""
            **💬 Conversaciones:**  
            {len(data['conversations'])} mensajes procesados
            """)
    
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        st.info("Verifica que todos los archivos de utilidades estén correctamente configurados.")

def main():
    """Función principal de la aplicación"""
    init_session_state()
    
    # Verificar autenticación
    if not st.session_state.authenticated:
        login_page()
    else:
        # Mostrar navegación
        sidebar_navigation()
        
        # Mostrar dashboard principal
        dashboard_page()

if __name__ == "__main__":
    main()
