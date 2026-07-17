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
    st.success("✅ Configuraciones guardadas exitosamente!")
    st.balloons()

def reset_settings():
    """Resetea las configuraciones a valores por defecto"""
    if st.button("🔄 Confirmar Reset", type="secondary"):
        initialize_session_state()
        st.success("✅ Configuraciones restablecidas a valores por defecto!")
        st.experimental_rerun()

def export_settings():
    """Exporta las configuraciones actuales"""
    settings_json = json.dumps(st.session_state.config_settings, indent=2, default=str)
    st.download_button(
        label="📥 Descargar Configuraciones",
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
    st.markdown("### 👤 Perfil de Usuario")
    
    st.markdown("""
    <div class="user-profile">
        <div class="user-avatar">AD</div>
        <div>
            <h4>Administrador Demo</h4>
            <p>admin@salesbot.com • Último acceso: Hoy, 14:30</p>
            <p><span class="status-indicator status-active"></span>Sesión activa</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Estadísticas del sistema
    st.markdown("### 📊 Estado del Sistema")
    
    system_info = st.session_state.system_info
    
    st.markdown(f"""
    <div class="system-stats">
        <div class="stat-card">
            <div class="stat-value">{system_info['version']}</div>
            <div class="stat-label">Versión del Sistema</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['uptime']}</div>
            <div class="stat-label">Tiempo Activo</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['active_sessions']}</div>
            <div class="stat-label">Sesiones Activas</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['database_size']}</div>
            <div class="stat-label">Tamaño de BD</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['api_calls_today']:,}</div>
            <div class="stat-label">Llamadas API Hoy</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{system_info['errors_today']}</div>
            <div class="stat-label">Errores Hoy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Configuraciones principales
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Notificaciones
        st.markdown("""
        <div class="config-section">
            <div class="setting-title">🔔 Configuración de Notificaciones</div>
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
                "Alertas por Email",
                value=notifications['email_alerts'],
                help="Recibir notificaciones importantes por email"
            )
            
            notifications['daily_reports'] = st.checkbox(
                "Reportes Diarios",
                value=notifications['daily_reports'],
                help="Recibir resumen diario de métricas"
            )
            
            notifications['low_stock_alerts'] = st.checkbox(
                "Alertas de Stock Bajo",
                value=notifications['low_stock_alerts'],
                help="Notificar cuando el inventario esté bajo"
            )
        
        with col_b:
            notifications['push_notifications'] = st.checkbox(
                "Notificaciones Push",
                value=notifications['push_notifications'],
                help="Notificaciones en tiempo real en el navegador"
            )
            
            notifications['new_customer_alerts'] = st.checkbox(
                "Alertas de Nuevos Clientes",
                value=notifications['new_customer_alerts'],
                help="Notificar cuando se registre un nuevo cliente"
            )
        
        # Dashboard
        st.markdown("""
        <div class="config-section">
            <div class="setting-title">📊 Configuración del Dashboard</div>
        </div>
        """, unsafe_allow_html=True)
        
        dashboard = st.session_state.config_settings['dashboard']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            dashboard['auto_refresh'] = st.checkbox(
                "Actualización Automática",
                value=dashboard['auto_refresh'],
                help="Actualizar datos automáticamente"
            )
            
            if dashboard['auto_refresh']:
                dashboard['refresh_interval'] = st.slider(
                    "Intervalo de Actualización (segundos)",
                    min_value=10,
                    max_value=300,
                    value=dashboard['refresh_interval'],
                    step=10
                )
            
            dashboard['default_date_range'] = st.selectbox(
                "Rango de Fechas por Defecto",
                options=[7, 30, 90, 365],
                index=[7, 30, 90, 365].index(dashboard['default_date_range']),
                format_func=lambda x: f"Últimos {x} días"
            )
        
        with col_b:
            dashboard['show_animations'] = st.checkbox(
                "Mostrar Animaciones",
                value=dashboard['show_animations'],
                help="Habilitar animaciones en gráficos"
            )
            
            dashboard['compact_mode'] = st.checkbox(
                "Modo Compacto",
                value=dashboard['compact_mode'],
                help="Mostrar más información en menos espacio"
            )
        
        # Chatbot
        st.markdown("""
        <div class="config-section">
            <div class="setting-title">🤖 Configuración del Chatbot</div>
        </div>
        """, unsafe_allow_html=True)
        
        chatbot = st.session_state.config_settings['chatbot']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            chatbot['auto_responses'] = st.checkbox(
                "Respuestas Automáticas",
                value=chatbot['auto_responses'],
                help="Habilitar respuestas automáticas del chatbot"
            )
            
            chatbot['learning_mode'] = st.checkbox(
                "Modo Aprendizaje",
                value=chatbot['learning_mode'],
                help="Permitir que el chatbot aprenda de las conversaciones"
            )
            
            chatbot['multilingual'] = st.checkbox(
                "Soporte Multiidioma",
                value=chatbot['multilingual'],
                help="Detectar y responder en múltiples idiomas"
            )
        
        with col_b:
            chatbot['escalation_threshold'] = st.slider(
                "Umbral de Escalación",
                min_value=1,
                max_value=10,
                value=chatbot['escalation_threshold'],
                help="Número de intentos antes de escalar a humano"
            )
            
            chatbot['response_delay'] = st.slider(
                "Retraso de Respuesta (segundos)",
                min_value=0,
                max_value=5,
                value=chatbot['response_delay'],
                help="Simular tiempo de pensamiento humano"
            )
        
        # Recordatorios de carritos abandonados
        st.markdown("""
        <div class="config-section">
            <div class="setting-title">🛒 Recordatorios de Carritos Abandonados</div>
        </div>
        """, unsafe_allow_html=True)
        
        cart_reminders = st.session_state.config_settings['cart_reminders']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            cart_reminders['enabled'] = st.checkbox(
                "Habilitar Recordatorios Automáticos",
                value=cart_reminders['enabled'],
                help="Enviar recordatorios automáticos para carritos abandonados"
            )
            
            cart_reminders['test_mode'] = st.checkbox(
                "Modo Prueba (10 segundos de espera)",
                value=cart_reminders['test_mode'],
                help="Modo de prueba con espera muy corta para comprobar el funcionamiento"
            )
        
        with col_b:
            if cart_reminders['test_mode']:
                st.info(f"ℹ️ Modo Prueba activado: Espera de 10 segundos")
            else:
                cart_reminders['delay_seconds'] = st.slider(
                    "Tiempo de Espera para Recordatorio",
                    min_value=60,  # 1 minuto
                    max_value=86400,  # 24 horas
                    value=cart_reminders['delay_seconds'],
                    step=60,
                    help="Tiempo que debe transcurrir desde el abandono para enviar el recordatorio"
                )
                # Convertir segundos a formato legible
                hours = cart_reminders['delay_seconds'] // 3600
                minutes = (cart_reminders['delay_seconds'] % 3600) // 60
                st.markdown(f"**Tiempo configurado:** {hours}h {minutes}m")
        
        cart_reminders['message_template'] = st.text_area(
            "Plantilla de Mensaje",
            value=cart_reminders['message_template'],
            help="Variables disponibles: {nombre}, {email}, {valor}, {productos}",
            height=100
        )
        
        # Log de recordatorios enviados
        st.markdown("### 📋 Log de Recordatorios")
        if st.session_state.cart_reminders_log:
            for reminder in reversed(st.session_state.cart_reminders_log):
                st.markdown(f"""
                <div style="padding: 0.5rem; margin: 0.25rem 0; border-left: 4px solid #10b981; background: #f0fdf4;">
                    <strong>[{reminder['timestamp']}]</strong> 
                    <span style="color: #10b981; font-weight: bold;">ENVIADO</span><br>
                    Cliente: {reminder['cliente']}<br>
                    Valor: {reminder['valor']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aún no se han enviado recordatorios automáticos.")
        
        # Seguridad
        st.markdown("""
        <div class="config-section">
            <div class="setting-title">🔒 Configuración de Seguridad</div>
        </div>
        """, unsafe_allow_html=True)
        
        security = st.session_state.config_settings['security']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            security['two_factor_auth'] = st.checkbox(
                "Autenticación de Dos Factores",
                value=security['two_factor_auth'],
                help="Requerir 2FA para mayor seguridad"
            )
            
            security['audit_logging'] = st.checkbox(
                "Registro de Auditoría",
                value=security['audit_logging'],
                help="Registrar todas las acciones del usuario"
            )
            
            security['session_timeout'] = st.slider(
                "Timeout de Sesión (minutos)",
                min_value=15,
                max_value=480,
                value=security['session_timeout'],
                step=15
            )
        
        with col_b:
            security['password_expiry'] = st.slider(
                "Expiración de Contraseña (días)",
                min_value=30,
                max_value=365,
                value=security['password_expiry'],
                step=30
            )
            
            security['login_attempts'] = st.slider(
                "Intentos de Login Máximos",
                min_value=3,
                max_value=10,
                value=security['login_attempts']
            )
        
        # Datos y Backup
        st.markdown("""
        <div class="config-section">
            <div class="setting-title">💾 Configuración de Datos y Backup</div>
        </div>
        """, unsafe_allow_html=True)
        
        data_config = st.session_state.config_settings['data']
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            data_config['auto_backup'] = st.checkbox(
                "Backup Automático",
                value=data_config['auto_backup'],
                help="Realizar backups automáticos de los datos"
            )
            
            if data_config['auto_backup']:
                data_config['backup_frequency'] = st.selectbox(
                    "Frecuencia de Backup",
                    options=['hourly', 'daily', 'weekly'],
                    index=['hourly', 'daily', 'weekly'].index(data_config['backup_frequency']),
                    format_func=lambda x: {
                        'hourly': 'Cada hora',
                        'daily': 'Diario',
                        'weekly': 'Semanal'
                    }[x]
                )
            
            data_config['data_retention'] = st.slider(
                "Retención de Datos (días)",
                min_value=30,
                max_value=2555,  # ~7 años
                value=data_config['data_retention'],
                step=30
            )
        
        with col_b:
            data_config['export_format'] = st.selectbox(
                "Formato de Exportación",
                options=['CSV', 'Excel', 'JSON', 'PDF'],
                index=['CSV', 'Excel', 'JSON', 'PDF'].index(data_config['export_format'])
            )
            
            data_config['anonymize_exports'] = st.checkbox(
                "Anonimizar Exportaciones",
                value=data_config['anonymize_exports'],
                help="Remover información personal de las exportaciones"
            )
    
    with col2:
        # Panel de acciones rápidas
        st.markdown("### ⚡ Acciones Rápidas")
        
        # Guardar configuraciones
        if st.button("💾 Guardar Configuraciones", type="primary", use_container_width=True):
            save_settings()
        
        # Exportar configuraciones
        st.markdown("**📤 Exportar/Importar:**")
        export_settings()
        
        uploaded_file = st.file_uploader(
            "📥 Importar Configuraciones",
            type=['json'],
            help="Cargar configuraciones desde archivo JSON"
        )
        
        if uploaded_file is not None:
            try:
                imported_config = json.load(uploaded_file)
                st.session_state.config_settings.update(imported_config)
                st.success("✅ Configuraciones importadas!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"❌ Error al importar: {str(e)}")
        
        st.markdown("---")
        
        # Reset configuraciones
        st.markdown("**🔄 Restablecer:**")
        if st.button("⚠️ Reset a Valores por Defecto", use_container_width=True):
            reset_settings()
        
        st.markdown("---")
        
        # Información de backup
        st.markdown("**💾 Información de Backup:**")
        
        last_backup = system_info['last_backup']
        st.markdown(f"""
        <div class="backup-info">
            <strong>Último Backup:</strong><br>
            {last_backup.strftime('%d/%m/%Y %H:%M')}<br>
            <small>Hace {(datetime.now() - last_backup).seconds // 3600} horas</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Crear Backup Manual", use_container_width=True):
            with st.spinner("Creando backup..."):
                import time
                time.sleep(2)  # Simular proceso
                st.success("✅ Backup creado exitosamente!")
        
        st.markdown("---")
        
        # Estado del sistema
        st.markdown("**📊 Estado del Sistema:**")
        
        # Indicadores de estado
        st.markdown("""
        <div class="config-item">
            <div><span class="status-indicator status-active"></span>Base de Datos: Conectada</div>
            <div><span class="status-indicator status-active"></span>API: Funcionando</div>
            <div><span class="status-indicator status-warning"></span>Cache: 78% utilizado</div>
            <div><span class="status-indicator status-active"></span>Backup: Actualizado</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mantenimiento
        st.markdown("**🔧 Mantenimiento:**")
        
        if st.button("🧹 Limpiar Cache", use_container_width=True):
            st.success("✅ Cache limpiado!")
        
        if st.button("🔄 Reiniciar Servicios", use_container_width=True):
            st.warning("⚠️ Los servicios se reiniciarán en 30 segundos")
        
        if st.button("📊 Optimizar Base de Datos", use_container_width=True):
            with st.spinner("Optimizando..."):
                import time
                time.sleep(3)
                st.success("✅ Base de datos optimizada!")
    
    st.markdown("---")
    
    # Configuraciones avanzadas
    with st.expander("🔧 Configuraciones Avanzadas"):
        st.markdown("### ⚙️ Configuraciones Técnicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🌐 API y Integraciones:**")
            
            api_rate_limit = st.slider("Límite de Rate API (req/min)", 100, 10000, 1000, 100)
            api_timeout = st.slider("Timeout API (segundos)", 5, 60, 30, 5)
            
            enable_webhooks = st.checkbox("Habilitar Webhooks", value=True)
            if enable_webhooks:
                webhook_url = st.text_input("URL de Webhook", placeholder="https://api.ejemplo.com/webhook")
            
            st.markdown("**📧 Configuración de Email:**")
            smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
            smtp_port = st.number_input("Puerto SMTP", value=587, min_value=1, max_value=65535)
            smtp_user = st.text_input("Usuario SMTP", placeholder="usuario@ejemplo.com")
        
        with col2:
            st.markdown("**🔍 Logging y Monitoreo:**")
            
            log_level = st.selectbox(
                "Nivel de Log",
                options=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                index=1
            )
            
            max_log_size = st.slider("Tamaño Máximo de Log (MB)", 10, 1000, 100, 10)
            log_retention_days = st.slider("Retención de Logs (días)", 7, 365, 30, 7)
            
            enable_metrics = st.checkbox("Habilitar Métricas", value=True)
            enable_alerts = st.checkbox("Habilitar Alertas", value=True)
            
            st.markdown("**🎨 Personalización UI:**")
            
            theme_color = st.color_picker("Color Principal", value="#3b82f6")
            custom_logo = st.file_uploader("Logo Personalizado", type=['png', 'jpg', 'svg'])
            
            if custom_logo:
                st.success("✅ Logo cargado (funcionalidad en desarrollo)")
    
    # Logs del sistema
    with st.expander("📋 Logs del Sistema"):
        st.markdown("### 📊 Actividad Reciente")
        
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
        
        with col1:
            level_filter = st.selectbox("Filtrar por Nivel:", ["Todos", "INFO", "WARNING", "ERROR", "CRITICAL"])
        
        with col2:
            source_filter = st.selectbox("Filtrar por Fuente:", ["Todos", "AUTH", "BACKUP", "SYSTEM", "REPORTS", "API", "CRM", "CHATBOT"])
        
        with col3:
            if st.button("🔄 Actualizar Logs"):
                st.success("Logs actualizados!")
        
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
                <span style="color: {level_color}; font-weight: bold;">{log['level']}</span> 
                <span style="color: #6b7280;">({log['source']})</span><br>
                {log['message']}
            </div>
            """, unsafe_allow_html=True)
    
    # Información del sistema
    st.markdown("---")
    st.markdown("### ℹ️ Información del Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **🖥️ Sistema:**
        - Versión: {system_info['version']}
        - Uptime: {system_info['uptime']}
        - Usuarios totales: {system_info['total_users']}
        """)
    
    with col2:
        st.info(f"""
        **💾 Base de Datos:**
        - Tamaño: {system_info['database_size']}
        - Último backup: Hace 6 horas
        - Estado: Saludable ✅
        """)
    
    with col3:
        st.info(f"""
        **📊 Rendimiento:**
        - API calls hoy: {system_info['api_calls_today']:,}
        - Errores hoy: {system_info['errors_today']}
        - Sesiones activas: {system_info['active_sessions']}
        """)

if __name__ == "__main__":
    main()
