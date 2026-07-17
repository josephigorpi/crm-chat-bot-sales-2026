"""
Página de Configuración
Ajustes del sistema, personalización y administración
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from utils.theme import inject_theme_css, get_plotly_template, init_theme_state
from i18n.strings import get_string
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")


# Importar el sidebar
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar import sidebar_navigation

# Inicializar estado de tema e idioma
init_theme_state()
if 'language' not in st.session_state:
    st.session_state.language = 'es'

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    switch_page("app")

# ✅ Mostrar el sidebar
sidebar_navigation()
inject_theme_css()


# CSS personalizado
st.markdown("""
<style>
    .config-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .config-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border-left: 4px solid #3b82f6;
        color: #1f2937;
    }
    
    .config-item {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
        color: #1f2937;
    }
    
    .setting-group {
        margin-bottom: 2rem;
    }
    
    .setting-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f2937;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    
    .setting-description {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-active {
        background-color: #10b981;
    }
    
    .status-inactive {
        background-color: #ef4444;
    }
    
    .status-warning {
        background-color: #f59e0b;
    }
    
    .alert-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .alert-success {
        background-color: #ecfdf5;
        border: 1px solid #10b981;
        color: #065f46;
    }
    
    .alert-warning {
        background-color: #fffbeb;
        border: 1px solid #f59e0b;
        color: #92400e;
    }
    
    .alert-error {
        background-color: #fef2f2;
        border: 1px solid #ef4444;
        color: #991b1b;
    }
    
    .user-profile {
        display: flex;
        align-items: center;
        padding: 1rem;
        background: #f0f9ff;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: #1f2937;
    }
    
    .user-avatar {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    .backup-info {
        background: #f0fdf4;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1f2937;
    }
    
    .system-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #3b82f6;
        color: #1f2937;
    }
    
    .stat-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #3b82f6;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        color: #6b7280;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializa el estado de la sesión para configuraciones"""
    
    # Configuración por defecto completa
    default_config = {
        'notifications': {
            'email_alerts': True,
            'push_notifications': False,
            'daily_reports': True,
            'low_stock_alerts': True,
            'new_customer_alerts': False
        },
        'dashboard': {
            'auto_refresh': True,
            'refresh_interval': 30,
            'default_date_range': 30,
            'show_animations': True,
            'compact_mode': False
        },
        'chatbot': {
            'auto_responses': True,
            'learning_mode': True,
            'escalation_threshold': 3,
            'response_delay': 1,
            'multilingual': False
        },
        'security': {
            'two_factor_auth': False,
            'session_timeout': 60,
            'password_expiry': 90,
            'login_attempts': 3,
            'audit_logging': True
        },
        'data': {
            'auto_backup': True,
            'backup_frequency': 'daily',
            'data_retention': 365,
            'export_format': 'CSV',
            'anonymize_exports': True
        },
        'cart_reminders': {
            'enabled': True,
            'delay_seconds': 3600,
            'test_mode': False,
            'message_template': "¡Hola {nombre}! Te recordamos que tienes un carrito pendiente de {valor}. ¡Completa tu compra ahora!"
        }
    }
    
    # Si no existe config_settings, crearlo con los valores por defecto
    if 'config_settings' not in st.session_state:
        st.session_state.config_settings = default_config
    else:
        # Verificar que todas las claves existan y agregar las que falten
        for key, default_value in default_config.items():
            if key not in st.session_state.config_settings:
                st.session_state.config_settings[key] = default_value
            elif isinstance(default_value, dict):
                # Verificar claves anidadas
                for sub_key, sub_default in default_value.items():
                    if sub_key not in st.session_state.config_settings[key]:
                        st.session_state.config_settings[key][sub_key] = sub_default
    
    # System info
    if 'system_info' not in st.session_state:
        st.session_state.system_info = {
            'version': '1.0.0',
            'last_backup': datetime.now() - timedelta(hours=6),
            'uptime': '15 días, 8 horas',
            'total_users': 25,
            'active_sessions': 8,
            'database_size': '2.3 GB',
            'api_calls_today': 1247,
            'errors_today': 3
        }
    
    # Log de recordatorios
    if 'cart_reminders_log' not in st.session_state:
        st.session_state.cart_reminders_log = []

def save_settings():
    """Simula el guardado de configuraciones"""
    st.success(get_string('config_save_success', st.session_state.language))
    st.balloons()

def reset_settings():
    """Resetea las configuraciones a valores por defecto"""
    if st.button(get_string('config_reset_button', st.session_state.language), type="secondary"):
        initialize_session_state()
        st.success(get_string('config_reset_success', st.session_state.language))
        st.rerun()

def export_settings():
    """Exporta las configuraciones actuales"""
    settings_json = json.dumps(st.session_state.config_settings, indent=2, default=str)
    st.download_button(
        label=get_string('config_export_download', st.session_state.language),
        data=settings_json,
        file_name=f"configuraciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def main():
    # Inicializar estado
    initialize_session_state()
    
    # Header de la página
    st.markdown(f"""
    <div class="config-header">
        <h1>{get_string('config_title', st.session_state.language)}</h1>
        <p>{get_string('config_subtitle', st.session_state.language)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Perfil de usuario
    st.markdown(f"### {get_string('config_user_profile', st.session_state.language)}")
    
    st.markdown(f"""
    <div class="user-profile">
        <div class="user-avatar">{get_string('config_user_avatar', st.session_state.language)}</div>
        <div>
            <h4>{get_string('config_user_name', st.session_state.language)}</h4>
            <p>{get_string('config_user_email', st.session_state.language)} • {get_string('config_user_last_access', st.session_state.language)}</p>
            <p><span class="status-indicator status-active"></span>{get_string('config_user_active', st.session_state.language)}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Estadísticas del sistema
    st.markdown(f"### {get_string('config_system_status', st.session_state.language)}")
    
    system_info = st.session_state.system_info
    
    st.markdown(f"""
    <div class="system-stats">
        <div class="stat-card">
            <div class="stat-value">{system_info['version']}</div>
            <div class="stat-label">{get_string('config_system_version', st.session_state.language)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['uptime']}</div>
            <div class="stat-label">{get_string('config_system_uptime', st.session_state.language)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['active_sessions']}</div>
            <div class="stat-label">{get_string('config_system_active_sessions', st.session_state.language)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['database_size']}</div>
            <div class="stat-label">{get_string('config_system_db_size', st.session_state.language)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['api_calls_today']:,}</div>
            <div class="stat-label">{get_string('config_system_api_calls', st.session_state.language)}</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['errors_today']}</div>
            <div class="stat-label">{get_string('config_system_errors', st.session_state.language)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Configuraciones principales
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Notificaciones
        st.markdown(f"""
        <div class="config-section">
            <div class="setting-title">{get_string('config_notifications', st.session_state.language)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Verificar que la clave existe antes de acceder
        if 'notifications' not in st.session_state.config_settings:
            st.session_state.config_settings['notifications'] = {
                'email_alerts': True,
                'push_notifications': False,
                'daily_reports': True,
                'low_stock_alerts': True,
                'new_customer_alerts': False
            }
        
        notifications = st.session_state.config_settings['notifications']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            notifications['email_alerts'] = st.checkbox(
                get_string('config_notifications_email', st.session_state.language),
                value=notifications['email_alerts'],
                help=get_string('config_notifications_email_help', st.session_state.language)
            )
            
            notifications['daily_reports'] = st.checkbox(
                get_string('config_notifications_daily', st.session_state.language),
                value=notifications['daily_reports'],
                help=get_string('config_notifications_daily_help', st.session_state.language)
            )
            
            notifications['low_stock_alerts'] = st.checkbox(
                get_string('config_notifications_stock', st.session_state.language),
                value=notifications['low_stock_alerts'],
                help=get_string('config_notifications_stock_help', st.session_state.language)
            )
        
        with col_b:
            notifications['push_notifications'] = st.checkbox(
                get_string('config_notifications_push', st.session_state.language),
                value=notifications['push_notifications'],
                help=get_string('config_notifications_push_help', st.session_state.language)
            )
            
            notifications['new_customer_alerts'] = st.checkbox(
                get_string('config_notifications_customers', st.session_state.language),
                value=notifications['new_customer_alerts'],
                help=get_string('config_notifications_customers_help', st.session_state.language)
            )
        
        # Dashboard
        st.markdown(f"""
        <div class="config-section">
            <div class="setting-title">{get_string('config_dashboard', st.session_state.language)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        dashboard = st.session_state.config_settings['dashboard']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            dashboard['auto_refresh'] = st.checkbox(
                get_string('config_dashboard_autorefresh', st.session_state.language),
                value=dashboard['auto_refresh'],
                help=get_string('config_dashboard_autorefresh_help', st.session_state.language)
            )
            
            if dashboard['auto_refresh']:
                dashboard['refresh_interval'] = st.slider(
                    get_string('config_dashboard_refresh_interval', st.session_state.language),
                    min_value=10,
                    max_value=300,
                    value=dashboard['refresh_interval'],
                    step=10
                )
            
            dashboard['default_date_range'] = st.selectbox(
                get_string('config_dashboard_date_range', st.session_state.language),
                options=[7, 30, 90, 365],
                index=[7, 30, 90, 365].index(dashboard['default_date_range']),
                format_func=lambda x: get_string('config_dashboard_date_range_last', st.session_state.language, days=x)
            )
        
        with col_b:
            dashboard['show_animations'] = st.checkbox(
                get_string('config_dashboard_animations', st.session_state.language),
                value=dashboard['show_animations'],
                help=get_string('config_dashboard_animations_help', st.session_state.language)
            )
            
            dashboard['compact_mode'] = st.checkbox(
                get_string('config_dashboard_compact', st.session_state.language),
                value=dashboard['compact_mode'],
                help=get_string('config_dashboard_compact_help', st.session_state.language)
            )
        
        # Chatbot
        st.markdown(f"""
        <div class="config-section">
            <div class="setting-title">{get_string('config_chatbot', st.session_state.language)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        chatbot = st.session_state.config_settings['chatbot']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            chatbot['auto_responses'] = st.checkbox(
                get_string('config_chatbot_auto', st.session_state.language),
                value=chatbot['auto_responses'],
                help=get_string('config_chatbot_auto_help', st.session_state.language)
            )
            
            chatbot['learning_mode'] = st.checkbox(
                get_string('config_chatbot_learning', st.session_state.language),
                value=chatbot['learning_mode'],
                help=get_string('config_chatbot_learning_help', st.session_state.language)
            )
            
            chatbot['multilingual'] = st.checkbox(
                get_string('config_chatbot_multilingual', st.session_state.language),
                value=chatbot['multilingual'],
                help=get_string('config_chatbot_multilingual_help', st.session_state.language)
            )
        
        with col_b:
            chatbot['escalation_threshold'] = st.slider(
                get_string('config_chatbot_escalation', st.session_state.language),
                min_value=1,
                max_value=10,
                value=chatbot['escalation_threshold'],
                help=get_string('config_chatbot_escalation_help', st.session_state.language)
            )
            
            chatbot['response_delay'] = st.slider(
                get_string('config_chatbot_delay', st.session_state.language),
                min_value=0,
                max_value=5,
                value=chatbot['response_delay'],
                help=get_string('config_chatbot_delay_help', st.session_state.language)
            )
        
        # Recordatorios de carritos abandonados
        st.markdown(f"""
        <div class="config-section">
            <div class="setting-title">{get_string('config_cart_reminders', st.session_state.language)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        cart_reminders = st.session_state.config_settings['cart_reminders']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            cart_reminders['enabled'] = st.checkbox(
                get_string('config_cart_reminders_enabled', st.session_state.language),
                value=cart_reminders['enabled'],
                help=get_string('config_cart_reminders_enabled_help', st.session_state.language)
            )
            
            cart_reminders['test_mode'] = st.checkbox(
                get_string('config_cart_reminders_test', st.session_state.language),
                value=cart_reminders['test_mode'],
                help=get_string('config_cart_reminders_test_help', st.session_state.language)
            )
        
        with col_b:
            if cart_reminders['test_mode']:
                st.info(get_string('config_cart_reminders_test_info', st.session_state.language))
            else:
                cart_reminders['delay_seconds'] = st.slider(
                    get_string('config_cart_reminders_delay', st.session_state.language),
                    min_value=60,  # 1 minuto
                    max_value=86400,  # 24 horas
                    value=cart_reminders['delay_seconds'],
                    step=60,
                    help=get_string('config_cart_reminders_delay_help', st.session_state.language)
                )
                # Convertir segundos a formato legible
                hours = cart_reminders['delay_seconds'] // 3600
                minutes = (cart_reminders['delay_seconds'] % 3600) // 60
                st.markdown(get_string('config_cart_reminders_delay_display', st.session_state.language, hours=hours, minutes=minutes))
        
        cart_reminders['message_template'] = st.text_area(
            get_string('config_cart_reminders_template', st.session_state.language),
            value=cart_reminders['message_template'],
            help=get_string('config_cart_reminders_template_help', st.session_state.language),
            height=100
        )
        
        # Log de recordatorios enviados
        st.markdown(f"### {get_string('config_cart_reminders_log', st.session_state.language)}")
        if st.session_state.cart_reminders_log:
            for reminder in reversed(st.session_state.cart_reminders_log):
                st.markdown(f"""
                <div style="padding: 0.5rem; margin: 0.25rem 0; border-left: 4px solid #10b981; background: #f0fdf4;">
                    <strong>[{reminder['timestamp']}]</strong> 
                    <span style="color: #10b981; font-weight: bold;">ENVIADO</span><br>
                    {get_string('config_cart_reminders_log_entry', st.session_state.language, client=reminder['cliente'], value=reminder['valor'])}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(get_string('config_cart_reminders_log_none', st.session_state.language))
        
        # Seguridad
        st.markdown(f"""
        <div class="config-section">
            <div class="setting-title">{get_string('config_security', st.session_state.language)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        security = st.session_state.config_settings['security']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            security['two_factor_auth'] = st.checkbox(
                get_string('config_security_2fa', st.session_state.language),
                value=security['two_factor_auth'],
                help=get_string('config_security_2fa_help', st.session_state.language)
            )
            
            security['audit_logging'] = st.checkbox(
                get_string('config_security_audit', st.session_state.language),
                value=security['audit_logging'],
                help=get_string('config_security_audit_help', st.session_state.language)
            )
            
            security['session_timeout'] = st.slider(
                get_string('config_security_timeout', st.session_state.language),
                min_value=15,
                max_value=480,
                value=security['session_timeout'],
                step=15
            )
        
        with col_b:
            security['password_expiry'] = st.slider(
                get_string('config_security_password_expiry', st.session_state.language),
                min_value=30,
                max_value=365,
                value=security['password_expiry'],
                step=30
            )
            
            security['login_attempts'] = st.slider(
                get_string('config_security_login_attempts', st.session_state.language),
                min_value=3,
                max_value=10,
                value=security['login_attempts']
            )
        
        # Datos y Backup
        st.markdown(f"""
        <div class="config-section">
            <div class="setting-title">{get_string('config_data', st.session_state.language)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        data_config = st.session_state.config_settings['data']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            data_config['auto_backup'] = st.checkbox(
                get_string('config_data_backup', st.session_state.language),
                value=data_config['auto_backup'],
                help=get_string('config_data_backup_help', st.session_state.language)
            )
            
            if data_config['auto_backup']:
                data_config['backup_frequency'] = st.selectbox(
                    get_string('config_data_backup_frequency', st.session_state.language),
                    options=['hourly', 'daily', 'weekly'],
                    index=['hourly', 'daily', 'weekly'].index(data_config['backup_frequency']),
                    format_func=lambda x: {
                        'hourly': get_string('config_data_backup_frequency_hourly', st.session_state.language),
                        'daily': get_string('config_data_backup_frequency_daily', st.session_state.language),
                        'weekly': get_string('config_data_backup_frequency_weekly', st.session_state.language)
                    }[x]
                )
            
            data_config['data_retention'] = st.slider(
                get_string('config_data_retention', st.session_state.language),
                min_value=30,
                max_value=2555,  # ~7 años
                value=data_config['data_retention'],
                step=30
            )
        
        with col_b:
            data_config['export_format'] = st.selectbox(
                get_string('config_data_export_format', st.session_state.language),
                options=['CSV', 'Excel', 'JSON', 'PDF'],
                index=['CSV', 'Excel', 'JSON', 'PDF'].index(data_config['export_format'])
            )
            
            data_config['anonymize_exports'] = st.checkbox(
                get_string('config_data_anonymize', st.session_state.language),
                value=data_config['anonymize_exports'],
                help=get_string('config_data_anonymize_help', st.session_state.language)
            )
    
    with col2:
        # Panel de acciones rápidas
        st.markdown(f"### {get_string('config_quick_actions', st.session_state.language)}")
        
        # Guardar configuraciones
        if st.button(get_string('config_save', st.session_state.language), type="primary", use_container_width=True):
            save_settings()
        
        # Exportar configuraciones
        st.markdown(f"**{get_string('config_export', st.session_state.language)}**")
        export_settings()
        
        uploaded_file = st.file_uploader(
            get_string('config_import', st.session_state.language),
            type=['json'],
            help=get_string('config_import_help', st.session_state.language)
        )
        
        if uploaded_file is not None:
            try:
                imported_config = json.load(uploaded_file)
                st.session_state.config_settings.update(imported_config)
                st.success(get_string('config_import_success', st.session_state.language))
                st.rerun()
            except Exception as e:
                st.error(get_string('config_import_error', st.session_state.language, error=str(e)))
        
        st.markdown("---")
        
        # Reset configuraciones
        st.markdown(f"**{get_string('config_reset', st.session_state.language)}**")
        if st.button(get_string('config_reset_button', st.session_state.language), use_container_width=True):
            reset_settings()
        
        st.markdown("---")
        
        # Información de backup
        st.markdown(f"**{get_string('config_backup_info', st.session_state.language)}**")
        
        last_backup = system_info['last_backup']
        hours_ago = (datetime.now() - last_backup).seconds // 3600
        st.markdown(f"""
        <div class="backup-info">
            <strong>{get_string('config_backup_last', st.session_state.language)}</strong><br>
            {last_backup.strftime('%d/%m/%Y %H:%M')}<br>
            <small>{get_string('config_backup_hours_ago', st.session_state.language, hours=hours_ago)}</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(get_string('config_backup_manual', st.session_state.language), use_container_width=True):
            with st.spinner(get_string('config_backup_creating', st.session_state.language)):
                import time
                time.sleep(2)  # Simular proceso
                st.success(get_string('config_backup_success', st.session_state.language))
        
        st.markdown("---")
        
        # Estado del sistema
        st.markdown(f"**{get_string('config_system_status_details', st.session_state.language)}**")
        
        # Indicadores de estado
        st.markdown(f"""
        <div class="config-item">
            <div><span class="status-indicator status-active"></span>{get_string('config_status_database', st.session_state.language)}</div>
            <div><span class="status-indicator status-active"></span>{get_string('config_status_api', st.session_state.language)}</div>
            <div><span class="status-indicator status-warning"></span>{get_string('config_status_cache', st.session_state.language, percent=78)}</div>
            <div><span class="status-indicator status-active"></span>{get_string('config_status_backup', st.session_state.language)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mantenimiento
        st.markdown(f"**{get_string('config_maintenance', st.session_state.language)}**")
        
        if st.button(get_string('config_maintenance_cache', st.session_state.language), use_container_width=True):
            st.success(get_string('config_maintenance_cache_success', st.session_state.language))
        
        if st.button(get_string('config_maintenance_restart', st.session_state.language), use_container_width=True):
            st.warning(get_string('config_maintenance_restart_warning', st.session_state.language))
        
        if st.button(get_string('config_maintenance_optimize', st.session_state.language), use_container_width=True):
            with st.spinner(get_string('config_maintenance_optimizing', st.session_state.language)):
                import time
                time.sleep(3)
                st.success(get_string('config_maintenance_optimize_success', st.session_state.language))
    
    st.markdown("---")
    
    # Configuraciones avanzadas
    with st.expander(get_string('config_advanced', st.session_state.language)):
        st.markdown(f"### {get_string('config_advanced_technical', st.session_state.language)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{get_string('config_advanced_api', st.session_state.language)}**")
            
            api_rate_limit = st.slider(get_string('config_advanced_rate_limit', st.session_state.language), 100, 10000, 1000, 100)
            api_timeout = st.slider(get_string('config_advanced_timeout', st.session_state.language), 5, 60, 30, 5)
            
            enable_webhooks = st.checkbox(get_string('config_advanced_webhooks', st.session_state.language), value=True)
            if enable_webhooks:
                webhook_url = st.text_input(
                    get_string('config_advanced_webhook_url', st.session_state.language),
                    placeholder=get_string('config_advanced_webhook_placeholder', st.session_state.language)
                )
            
            st.markdown(f"**{get_string('config_advanced_email', st.session_state.language)}**")
            smtp_server = st.text_input(get_string('config_advanced_smtp_server', st.session_state.language), value="smtp.gmail.com")
            smtp_port = st.number_input(get_string('config_advanced_smtp_port', st.session_state.language), value=587, min_value=1, max_value=65535)
            smtp_user = st.text_input(
                get_string('config_advanced_smtp_user', st.session_state.language),
                placeholder=get_string('config_advanced_smtp_placeholder', st.session_state.language)
            )
        
        with col2:
            st.markdown(f"**{get_string('config_advanced_logging', st.session_state.language)}**")
            
            log_level = st.selectbox(
                get_string('config_advanced_log_level', st.session_state.language),
                options=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                index=1,
                format_func=lambda x: {
                    'DEBUG': 'DEBUG',
                    'INFO': get_string('config_logs_level_info', st.session_state.language),
                    'WARNING': get_string('config_logs_level_warning', st.session_state.language),
                    'ERROR': get_string('config_logs_level_error', st.session_state.language),
                    'CRITICAL': get_string('config_logs_level_critical', st.session_state.language)
                }[x]
            )
            
            max_log_size = st.slider(get_string('config_advanced_max_log_size', st.session_state.language), 10, 1000, 100, 10)
            log_retention_days = st.slider(get_string('config_advanced_log_retention', st.session_state.language), 7, 365, 30, 7)
            
            enable_metrics = st.checkbox(get_string('config_advanced_metrics', st.session_state.language), value=True)
            enable_alerts = st.checkbox(get_string('config_advanced_alerts', st.session_state.language), value=True)
            
            st.markdown(f"**{get_string('config_advanced_ui', st.session_state.language)}**")
            
            theme_color = st.color_picker(get_string('config_advanced_theme_color', st.session_state.language), value="#3b82f6")
            custom_logo = st.file_uploader(
                get_string('config_advanced_logo', st.session_state.language),
                type=['png', 'jpg', 'svg']
            )
            
            if custom_logo:
                st.success(get_string('config_advanced_logo_upload', st.session_state.language))
    
    # Logs del sistema
    with st.expander(get_string('config_logs', st.session_state.language)):
        st.markdown(f"### {get_string('config_logs_recent', st.session_state.language)}")
        
        # Simular logs del sistema
        logs_data = [
            {"timestamp": "2024-01-15 14:30:25", "level": "INFO", "message": "Usuario admin@salesbot.com inició sesión", "source": "AUTH"},
            {"timestamp": "2024-01-15 14:25:12", "level": "INFO", "message": "Backup automático completado exitosamente", "source": "BACKUP"},
            {"timestamp": "2024-01-15 14:20:08", "level": "WARNING", "message": "Cache al 78% de capacidad", "source": "SYSTEM"},
            {"timestamp": "2024-01-15 14:15:33", "level": "INFO", "message": "Reporte de ventas generado", "source": "REPORTS"},
            {"timestamp": "2024-01-15 14:10:45", "level": "ERROR", "message": "Fallo temporal en conexión API externa", "source": "API"},
            {"timestamp": "2024-01-15 14:05:22", "level": "INFO", "message": "Nuevo cliente registrado: cliente@ejemplo.com", "source": "CRM"},
            {"timestamp": "2024-01-15 14:00:15", "level": "INFO", "message": "Chatbot procesó 15 conversaciones", "source": "CHATBOT"},
        ]
        
        logs_df = pd.DataFrame(logs_data)
        
        # Filtros para logs
        col1, col2, col3 = st.columns(3)
        
        level_names = {
            "Todos": get_string('config_logs_all', st.session_state.language),
            "INFO": get_string('config_logs_level_info', st.session_state.language),
            "WARNING": get_string('config_logs_level_warning', st.session_state.language),
            "ERROR": get_string('config_logs_level_error', st.session_state.language),
            "CRITICAL": get_string('config_logs_level_critical', st.session_state.language)
        }
        
        with col1:
            level_filter = st.selectbox(
                get_string('config_logs_filter_level', st.session_state.language),
                ["Todos", "INFO", "WARNING", "ERROR", "CRITICAL"],
                format_func=lambda x: level_names.get(x, x)
            )
        
        with col2:
            source_filter = st.selectbox(
                get_string('config_logs_filter_source', st.session_state.language),
                ["Todos", "AUTH", "BACKUP", "SYSTEM", "REPORTS", "API", "CRM", "CHATBOT"]
            )
        
        with col3:
            if st.button(get_string('config_logs_refresh', st.session_state.language)):
                st.success(get_string('config_logs_refresh_success', st.session_state.language))
        
        # Aplicar filtros
        filtered_logs = logs_df.copy()
        if level_filter != "Todos":
            filtered_logs = filtered_logs[filtered_logs['level'] == level_filter]
        if source_filter != "Todos":
            filtered_logs = filtered_logs[filtered_logs['source'] == source_filter]
        
        # Mostrar logs con colores
        for _, log in filtered_logs.iterrows():
            level_color = {
                'INFO': '#3b82f6',
                'WARNING': '#f59e0b',
                'ERROR': '#ef4444',
                'CRITICAL': '#dc2626'
            }.get(log['level'], '#6b7280')
            
            st.markdown(f"""
            <div style="padding: 0.5rem; margin: 0.25rem 0; border-left: 4px solid {level_color}; background: #f8fafc;">
                <strong>[{log['timestamp']}]</strong> 
                <span style="color: {level_color}; font-weight: bold;">{level_names.get(log['level'], log['level'])}</span> 
                <span style="color: #6b7280;">({log['source']})</span><br>
                {log['message']}
            </div>
            """, unsafe_allow_html=True)
    
    # Información del sistema
    st.markdown("---")
    st.markdown(f"### {get_string('config_system_info', st.session_state.language)}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **{get_string('config_system_info_system', st.session_state.language)}**
        - {get_string('config_system_info_version', st.session_state.language, version=system_info['version'])}
        - {get_string('config_system_info_uptime', st.session_state.language, uptime=system_info['uptime'])}
        - {get_string('config_system_info_users', st.session_state.language, users=system_info['total_users'])}
        """)
    
    with col2:
        st.info(f"""
        **{get_string('config_system_info_database', st.session_state.language)}**
        - {get_string('config_system_info_db_size', st.session_state.language, size=system_info['database_size'])}
        - {get_string('config_system_info_backup', st.session_state.language)}
        - {get_string('config_system_info_db_status', st.session_state.language)}
        """)
    
    with col3:
        st.info(f"""
        **{get_string('config_system_info_performance', st.session_state.language)}**
        - {get_string('config_system_info_api_calls', st.session_state.language, calls=system_info['api_calls_today'])}
        - {get_string('config_system_info_errors', st.session_state.language, errors=system_info['errors_today'])}
        - {get_string('config_system_info_sessions', st.session_state.language, sessions=system_info['active_sessions'])}
        """)

if __name__ == "__main__":
    main()
