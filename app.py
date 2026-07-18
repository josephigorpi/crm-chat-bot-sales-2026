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
from utils.theme import inject_theme_css, get_theme, init_theme_state, get_plotly_template
from i18n.strings import get_string

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Chatbot Ventas",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✅ Inyectar CSS dinámico del tema
inject_theme_css()

# Inicializar estado de tema e idioma
init_theme_state()
if 'language' not in st.session_state:
    st.session_state.language = 'es'

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
    """Página de login con soporte para i18n"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Header del login
    st.markdown(f"""
    <div class="login-header">
        <div class="login-title">{get_string('login_title', st.session_state.language)}</div>
        <div class="login-subtitle">{get_string('login_subtitle', st.session_state.language)}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulario de login
    with st.form("login_form"):
        email = st.text_input(
            get_string('login_email', st.session_state.language),
            placeholder=get_string('login_email_placeholder', st.session_state.language)
        )
        password = st.text_input(
            get_string('login_password', st.session_state.language),
            type="password",
            placeholder=get_string('login_password_placeholder', st.session_state.language)
        )
        remember_me = st.checkbox(get_string('login_remember_me', st.session_state.language))
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.form_submit_button(
                get_string('login_button', st.session_state.language),
                use_container_width=True
            )
    
    # Validación de credenciales
    if login_button:
        if email == "admin@chatbot.com" and password == "admin123":
            st.session_state.authenticated = True
            st.session_state.username = "Administrador"
            st.session_state.remember_me = remember_me
            st.success(get_string('login_success', st.session_state.language))
            st.rerun()
        else:
            st.error(get_string('login_error', st.session_state.language))
    
    # Información de credenciales de prueba
    st.markdown("---")
    st.info(f"""
    **{get_string('login_credentials_title', st.session_state.language)}**
    - {get_string('login_credentials_email', st.session_state.language)}
    - {get_string('login_credentials_password', st.session_state.language)}
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)


def dashboard_page():
    """Página principal del dashboard con soporte para i18n y temas dinámicos"""
    st.markdown(f'<h1 class="main-header">{get_string("dashboard_title", st.session_state.language)}</h1>', unsafe_allow_html=True)
    
    # Mensaje de bienvenida
    st.markdown(f"""
    <div class="welcome-message">
        <h3>{get_string('dashboard_welcome', st.session_state.language, username=st.session_state.username)}</h3>
        <p>{get_string('dashboard_subtitle', st.session_state.language)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    try:
        with st.spinner(get_string('dashboard_load_error', st.session_state.language)):
            data = get_all_data()
            metrics = get_calculated_metrics()
        
        # Obtener template de gráficos según tema
        chart_template = get_plotly_template()
        
        # Métricas principales en cards
        st.markdown(f"### {get_string('dashboard_metrics', st.session_state.language)}")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label=get_string('dashboard_total_sales', st.session_state.language),
                value=f"€{metrics['total_sales']:,.2f}",
                delta=f"+12.5%"
            )
        
        with col2:
            st.metric(
                label=get_string('dashboard_total_customers', st.session_state.language),
                value=f"{metrics['total_customers']:,}",
                delta=f"+{len(data['customers'][pd.to_datetime(data['customers']['created_at']) >= datetime.now() - pd.Timedelta(days=30)])}"
            )
        
        with col3:
            st.metric(
                label=get_string('dashboard_total_orders', st.session_state.language),
                value=f"{metrics['total_orders']:,}",
                delta=f"{get_string('dashboard_analysis', st.session_state.language)}: {metrics['total_orders']/30:.1f}/día"
            )
        
        with col4:
            st.metric(
                label=get_string('dashboard_conversion_rate', st.session_state.language),
                value=f"{metrics['conversion_rate']:.1f}%",
                delta=f"+2.3%"
            )
        
        st.markdown("---")
        
        # Gráficos principales
        st.markdown(f"### {get_string('dashboard_analysis', st.session_state.language)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de ventas en el tiempo
            sales_chart = create_sales_timeline(data['orders'], chart_template, st.session_state.language)
            st.plotly_chart(sales_chart, use_container_width=True)
        
        with col2:
            # Gráfico de estados de pedidos
            status_chart = create_order_status_donut(data['orders'], chart_template, st.session_state.language)
            st.plotly_chart(status_chart, use_container_width=True)
        
        # Segunda fila de gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            # Mensajes por hora
            messages_chart = create_messages_by_hour(data['conversations'], chart_template, st.session_state.language)
            st.plotly_chart(messages_chart, use_container_width=True)
        
        with col2:
            # Distribución de intenciones
            intent_chart = create_intent_distribution(data['conversations'], chart_template, st.session_state.language)
            st.plotly_chart(intent_chart, use_container_width=True)
        
        st.markdown("---")
        
        # Tabla de últimos pedidos
        st.markdown(f"### {get_string('dashboard_last_orders', st.session_state.language)}")

        st.write("Orders")
        st.write(data['orders'].columns.tolist())
        
        st.write("Customers")
        st.write(data['customers'].columns.tolist())

        
        recent_orders = data['orders'].merge(
            data['customers'][['id', 'first_name', 'last_name']], 
            left_on='customer_id', 
            right_on='id'
        ).sort_values('created_at', ascending=False).head(10)


        st.write("Recent Orders")
        st.write(recent_orders.columns.tolist())
        
        # Formatear datos para mostrar
        display_orders = recent_orders[['id', 'first_name', 'last_name', 'total_amount', 'status', 'created_at']].copy()
        display_orders['Cliente'] = display_orders['first_name'] + ' ' + display_orders['last_name']
        display_orders['Monto'] = display_orders['total_amount'].apply(lambda x: f"€{x:.2f}")
        
        # Traducir estado de órdenes
        status_map = {
            'pending': get_string('order_status_pending', st.session_state.language),
            'processing': get_string('order_status_processing', st.session_state.language),
            'shipped': get_string('order_status_shipped', st.session_state.language),
            'delivered': get_string('order_status_delivered', st.session_state.language),
            'cancelled': get_string('order_status_cancelled', st.session_state.language),
        }
        display_orders['Estado'] = display_orders['status'].map(status_map)
        display_orders['Fecha'] = pd.to_datetime(display_orders['created_at']).dt.strftime('%d/%m/%Y %H:%M')
        display_orders['ID'] = display_orders['id'].str[:8] + "..."
        
        st.dataframe(
            display_orders[['ID', 'Cliente', 'Monto', 'Estado', 'Fecha']],
            use_container_width=True,
            hide_index=True
        )
        
        # Información adicional
        st.markdown(f"### {get_string('dashboard_system_info', st.session_state.language)}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"""
            **{get_string('dashboard_last_update', st.session_state.language)}**  
            {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
            """)
        
        with col2:
            st.info(f"""
            **{get_string('dashboard_data_loaded', st.session_state.language)}**  
            {len(data['customers'])} {get_string('dashboard_customers_loaded', st.session_state.language)}, {len(data['products'])} {get_string('dashboard_products_loaded', st.session_state.language)}
            """)
        
        with col3:
            st.info(f"""
            **{get_string('dashboard_conversations', st.session_state.language)}**  
            {len(data['conversations'])} {get_string('dashboard_messages_processed', st.session_state.language)}
            """)
    
    except Exception as e:
        st.error(f"{get_string('dashboard_load_error', st.session_state.language)} {str(e)}")
        st.info(get_string('dashboard_load_error_info', st.session_state.language))

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
