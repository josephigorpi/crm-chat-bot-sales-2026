"""
Página de Carritos Abandonados
Análisis y estrategias de recuperación de carritos abandonados
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_generator import get_all_data, generate_test_abandoned_cart
import time
import json
from utils.theme import inject_theme_css, get_plotly_template, init_theme_state
from i18n.strings import get_string
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Carritos Abandonados", page_icon="🛒", layout="wide")

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
    .cart-header {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .abandoned-cart-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #f59e0b;
        color: #1f2937;
    }
    
    .recovery-action {
        background: #fef3c7;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #f59e0b;
        margin: 0.5rem 0;
        color: #1f2937;
    }
    
    .high-value-cart {
        border-left: 4px solid #dc2626;
        background: #fef2f2;
        color: #1f2937;
    }
    
    .medium-value-cart {
        border-left: 4px solid #f59e0b;
        background: #fffbeb;
        color: #1f2937;
    }
    
    .low-value-cart {
        border-left: 4px solid #65a30d;
        background: #f7fee7;
        color: #1f2937;
    }
    
    .metric-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #f59e0b;
        color: #1f2937;
    }
    
    .product-item {
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        font-size: 0.9rem;
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

def load_cart_data():
    """Carga y procesa los datos de carritos, usando session state para persistencia"""
    try:
        if 'app_data' not in st.session_state:
            st.session_state.app_data = get_all_data()
        return st.session_state.app_data
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None

def calculate_abandonment_metrics(carts_df, customers_df, products_df):
    """Calcula métricas de abandono de carritos"""
    # Enriquecer datos de carritos
    enriched_carts = carts_df.merge(customers_df[['id', 'first_name', 'last_name', 'email', 'country']], 
                                   left_on='customer_id', right_on='id', how='left', suffixes=('', '_customer'))
    
    # Eliminar la columna duplicada del customer
    enriched_carts = enriched_carts.drop('id_customer', axis=1)
    
    # Agregar columna total_value para compatibilidad
    enriched_carts['total_value'] = enriched_carts['total_amount']
    
    # Calcular tiempo desde abandono
    enriched_carts['created_at'] = pd.to_datetime(enriched_carts['created_at'])
    enriched_carts['abandoned_at'] = pd.to_datetime(enriched_carts['abandoned_at'])
    enriched_carts['hours_since_abandonment'] = (
        (datetime.now() - enriched_carts['abandoned_at']).dt.total_seconds() / 3600
    )
    
    # Categorizar por valor
    def categorize_cart_value(value):
        if value >= 200:
            return 'Alto Valor'
        elif value >= 100:
            return 'Valor Medio'
        else:
            return 'Bajo Valor'
    
    enriched_carts['value_category'] = enriched_carts['total_value'].apply(categorize_cart_value)
    
    # Categorizar por tiempo de abandono
    def categorize_abandonment_time(hours):
        if hours <= 1:
            return 'Reciente (< 1h)'
        elif hours <= 24:
            return 'Mismo día (< 24h)'
        elif hours <= 72:
            return 'Últimos 3 días'
        else:
            return 'Más de 3 días'
    
    enriched_carts['time_category'] = enriched_carts['hours_since_abandonment'].apply(categorize_abandonment_time)
    
    # Simular probabilidad de recuperación
    import numpy as np
    np.random.seed(42)
    
    def calculate_recovery_probability(row):
        base_prob = 0.3
        
        # Ajustar por valor del carrito
        if row['value_category'] == 'Alto Valor':
            base_prob += 0.2
        elif row['value_category'] == 'Valor Medio':
            base_prob += 0.1
        
        # Ajustar por tiempo de abandono
        if row['time_category'] == 'Reciente (< 1h)':
            base_prob += 0.3
        elif row['time_category'] == 'Mismo día (< 24h)':
            base_prob += 0.1
        elif row['time_category'] == 'Últimos 3 días':
            base_prob -= 0.1
        else:
            base_prob -= 0.2
        
        return max(0.05, min(0.95, base_prob))
    
    enriched_carts['recovery_probability'] = enriched_carts.apply(calculate_recovery_probability, axis=1)
    
    return enriched_carts

def check_and_send_reminders():
    """Verifica y envía recordatorios automáticos según la configuración"""
    # Obtener configuración
    if 'config_settings' not in st.session_state:
        return []
    
    config = st.session_state.config_settings.get('cart_reminders', {})
    if not config.get('enabled', False):
        return []
    
    # Obtener datos
    data = st.session_state.app_data
    carts_df = data['carts']
    customers_df = data['customers']
    
    # Calcular tiempo de espera
    delay_seconds = 10 if config.get('test_mode', False) else config.get('delay_seconds', 3600)
    
    # Filtrar carritos abandonados sin recordatorio
    abandoned_carts = carts_df[
        (carts_df['status'] == 'abandoned') & 
        (~carts_df['recordatorio_enviado'])
    ]
    
    sent_reminders = []
    for _, cart in abandoned_carts.iterrows():
        abandoned_at = pd.to_datetime(cart['abandoned_at'])
        time_since_abandoned = (datetime.now() - abandoned_at).total_seconds()
        
        if time_since_abandoned >= delay_seconds:
            # Enviar recordatorio
            customer = customers_df[customers_df['id'] == cart['customer_id']].iloc[0]
            
            # Crear mensaje usando la plantilla
            template = config.get('message_template', "¡Hola {nombre}! Te recordamos que tienes un carrito pendiente.")
            message = template.format(
                nombre=f"{customer['first_name']} {customer['last_name']}",
                email=customer['email'],
                valor=f"€{cart['total_amount']:.2f}",
                productos=str(len(json.loads(cart['cart_items'])))
            )
            
            # Marcar como enviado en el DataFrame
            carts_df.loc[carts_df['id'] == cart['id'], 'recordatorio_enviado'] = True
            
            # Agregar al historial
            reminder_data = {
                'cart_id': cart['id'],
                'cliente': f"{customer['first_name']} {customer['last_name']}",
                'email': customer['email'],
                'valor': cart['total_amount'],
                'mensaje': message,
                'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            
            st.session_state.sent_reminders.append(reminder_data)
            sent_reminders.append(reminder_data)
            
            # También actualizar el log en la página de configuración
            if 'cart_reminders_log' not in st.session_state:
                st.session_state.cart_reminders_log = []
            st.session_state.cart_reminders_log.append({
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'cliente': f"{customer['first_name']} {customer['last_name']}",
                'valor': f"€{cart['total_amount']:.2f}"
            })
    
    return sent_reminders

def create_abandonment_funnel(carts_df):
    """Crea embudo de abandono de carritos"""
    # Simular datos del embudo
    funnel_data = {
        'Visitantes': 50000,
        'Productos Vistos': 25000,
        'Añadido al Carrito': len(carts_df) + 5000,  # Incluir carritos completados
        'Carritos Abandonados': len(carts_df),
        'Recuperaciones': int(len(carts_df) * 0.15)  # 15% de recuperación
    }
    
    stages = list(funnel_data.keys())
    values = list(funnel_data.values())
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker=dict(
            color=["#3b82f6", "#06b6d4", "#f59e0b", "#ef4444", "#10b981"]
        )
    ))
    
    fig.update_layout(
        title="Embudo de Abandono de Carritos",
        template="plotly_white",
        height=400
    )
    
    return fig

def create_abandonment_reasons_chart():
    """Crea gráfico de razones de abandono"""
    # Datos simulados de razones de abandono
    reasons_data = {
        'Costos de envío altos': 35,
        'Proceso de checkout complejo': 25,
        'Falta de métodos de pago': 15,
        'Precios altos': 12,
        'Problemas técnicos': 8,
        'Falta de confianza': 5
    }
    
    fig = px.pie(
        values=list(reasons_data.values()),
        names=list(reasons_data.keys()),
        title="Principales Razones de Abandono",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{value}% de abandonos<extra></extra>'
    )
    
    fig.update_layout(
        template="plotly_white",
        height=400
    )
    
    return fig

def create_recovery_timeline():
    """Crea timeline de recuperación de carritos"""
    # Simular datos de recuperación por hora
    hours = list(range(0, 168, 6))  # Una semana en intervalos de 6 horas
    recovery_rates = [
        45, 35, 25, 20, 15, 12, 10, 8, 7, 6, 5, 4, 4, 3, 3, 2, 2, 2, 1, 1, 1, 1, 0.5, 0.5, 0.5, 0.3, 0.3, 0.2
    ]
    
    fig = px.line(
        x=hours,
        y=recovery_rates,
        title="Tasa de Recuperación por Tiempo Transcurrido",
        markers=True
    )
    
    fig.update_traces(
        line_color='#10b981',
        marker_color='#10b981',
        hovertemplate='<b>Horas: %{x}</b><br>Tasa de Recuperación: %{y}%<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title="Horas desde Abandono",
        yaxis_title="Tasa de Recuperación (%)",
        template="plotly_white",
        height=400
    )
    
    return fig

def display_recovery_strategies(cart_row):
    """Muestra estrategias de recuperación personalizadas"""
    strategies = []
    
    # Estrategias basadas en valor del carrito
    if cart_row['value_category'] == 'Alto Valor':
        strategies.extend([
            "🎯 Llamada telefónica personalizada",
            "💰 Descuento del 15-20%",
            "🚚 Envío gratuito premium"
        ])
    elif cart_row['value_category'] == 'Valor Medio':
        strategies.extend([
            "📧 Email personalizado con descuento del 10%",
            "🚚 Envío gratuito",
            "⏰ Recordatorio de stock limitado"
        ])
    else:
        strategies.extend([
            "📧 Email recordatorio simple",
            "💰 Descuento del 5%",
            "🎁 Regalo con compra"
        ])
    
    # Estrategias basadas en tiempo
    if cart_row['time_category'] == 'Reciente (< 1h)':
        strategies.append("⚡ Notificación push inmediata")
    elif cart_row['time_category'] == 'Mismo día (< 24h)':
        strategies.append("📱 SMS recordatorio")
    elif cart_row['time_category'] == 'Últimos 3 días':
        strategies.append("🔄 Campaña de retargeting")
    else:
        strategies.append("💌 Email de reactivación especial")
    
    return strategies

def main():
    # Header de la página
    st.markdown(f"""
    <div class="cart-header">
        <h1>{get_string('carts_title', st.session_state.language)}</h1>
        <p>{get_string('carts_subtitle', st.session_state.language)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for reminders
    if 'sent_reminders' not in st.session_state:
        st.session_state.sent_reminders = []
    
    # Initialize config settings if not present (for consistency with Config page)
    if 'config_settings' not in st.session_state:
        st.session_state.config_settings = {
            'cart_reminders': {
                'enabled': True,
                'delay_seconds': 3600,
                'test_mode': False,
                'message_template': "¡Hola {nombre}! Te recordamos que tienes un carrito pendiente de {valor}. ¡Completa tu compra ahora!"
            }
        }
    
    # Cargar datos
    data = load_cart_data()
    if data is None:
        return
    
    carts_df = data['carts']
    customers_df = data['customers']
    products_df = data['products']
    
    # Botón para generar carrito de prueba
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🧪 Generar Carrito de Prueba", type="primary"):
            test_cart = generate_test_abandoned_cart(customers_df, products_df)
            # Convertir el dict a una fila del DataFrame
            new_cart_row = pd.DataFrame([test_cart])
            # Concatenar con el DataFrame existente
            st.session_state.app_data['carts'] = pd.concat(
                [carts_df, new_cart_row],
                ignore_index=True
            )
            st.success(f"✅ Carrito de prueba generado: {test_cart['id']}")
            st.rerun()
    
    with col2:
        # Verificar y enviar recordatorios
        sent_reminders = check_and_send_reminders()
        if sent_reminders:
            for reminder in sent_reminders:
                st.toast(f"📨 Recordatorio enviado a {reminder['cliente']}!")
    
    # Calcular métricas de abandono
    enriched_carts = calculate_abandonment_metrics(carts_df, customers_df, products_df)
    
    # Filtros
    st.markdown("### 🔍 Filtros de Carritos Abandonados")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        value_categories = ['Todos'] + list(enriched_carts['value_category'].unique())
        selected_value = st.selectbox("Valor del Carrito", value_categories)
    
    with col2:
        time_categories = ['Todos'] + list(enriched_carts['time_category'].unique())
        selected_time = st.selectbox("Tiempo de Abandono", time_categories)
    
    with col3:
        countries = ['Todos'] + list(enriched_carts['country'].unique())
        selected_country = st.selectbox("País", countries)
    
    with col4:
        min_probability = st.slider("Probabilidad Mínima de Recuperación", 0.0, 1.0, 0.0, 0.05)
    
    # Aplicar filtros
    filtered_carts = enriched_carts.copy()
    
    if selected_value != 'Todos':
        filtered_carts = filtered_carts[filtered_carts['value_category'] == selected_value]
    
    if selected_time != 'Todos':
        filtered_carts = filtered_carts[filtered_carts['time_category'] == selected_time]
    
    if selected_country != 'Todos':
        filtered_carts = filtered_carts[filtered_carts['country'] == selected_country]
    
    filtered_carts = filtered_carts[filtered_carts['recovery_probability'] >= min_probability]
    
    # Métricas principales
    st.markdown("### 📊 Métricas de Abandono")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-box">
            <h3>{:,}</h3>
            <p>Carritos Abandonados</p>
        </div>
        """.format(len(filtered_carts)), unsafe_allow_html=True)
    
    with col2:
        total_value = filtered_carts['total_value'].sum()
        st.markdown("""
        <div class="metric-box">
            <h3>€{:,.2f}</h3>
            <p>Valor Total Perdido</p>
        </div>
        """.format(total_value), unsafe_allow_html=True)
    
    with col3:
        avg_recovery_prob = filtered_carts['recovery_probability'].mean()
        st.markdown("""
        <div class="metric-box">
            <h3>{:.1f}%</h3>
            <p>Prob. Recuperación Promedio</p>
        </div>
        """.format(avg_recovery_prob * 100), unsafe_allow_html=True)
    
    with col4:
        potential_recovery = (filtered_carts['total_value'] * filtered_carts['recovery_probability']).sum()
        st.markdown("""
        <div class="metric-box">
            <h3>€{:,.2f}</h3>
            <p>Recuperación Potencial</p>
        </div>
        """.format(potential_recovery), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizaciones principales
    st.markdown("### 📈 Análisis de Abandono")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Embudo de abandono
        funnel_chart = create_abandonment_funnel(enriched_carts)
        st.plotly_chart(funnel_chart, use_container_width=True)
    
    with col2:
        # Razones de abandono
        reasons_chart = create_abandonment_reasons_chart()
        st.plotly_chart(reasons_chart, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Timeline de recuperación
        recovery_timeline = create_recovery_timeline()
        st.plotly_chart(recovery_timeline, use_container_width=True)
    
    with col2:
        # Distribución por valor de carrito
        value_dist = filtered_carts['value_category'].value_counts()
        
        fig = px.bar(
            x=value_dist.index,
            y=value_dist.values,
            title="Distribución por Valor de Carrito",
            color=value_dist.values,
            color_continuous_scale='Reds'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Carritos: %{y}<extra></extra>'
        )
        
        fig.update_layout(
            xaxis_title="Categoría de Valor",
            yaxis_title="Número de Carritos",
            template="plotly_white",
            height=400,
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Análisis por tiempo de abandono
    st.markdown("### ⏰ Análisis Temporal")
    
    time_analysis = filtered_carts.groupby('time_category').agg({
        'id': 'count',
        'total_value': ['sum', 'mean'],
        'recovery_probability': 'mean'
    }).round(2)
    
    time_analysis.columns = ['count', 'total_value', 'avg_value', 'avg_recovery_prob']
    time_analysis = time_analysis.reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Número de Carritos',
        x=time_analysis['time_category'],
        y=time_analysis['count'],
        marker_color='#f59e0b',
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>Carritos: %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        name='Prob. Recuperación (%)',
        x=time_analysis['time_category'],
        y=time_analysis['avg_recovery_prob'] * 100,
        mode='lines+markers',
        line=dict(color='#10b981'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Probabilidad: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='Carritos Abandonados y Probabilidad de Recuperación por Tiempo',
        xaxis_title='Tiempo desde Abandono',
        yaxis=dict(title='Número de Carritos', side='left'),
        yaxis2=dict(title='Probabilidad de Recuperación (%)', side='right', overlaying='y'),
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Log de recordatorios enviados
    st.markdown("### 📨 Historial de Recordatorios Enviados")
    if st.session_state.sent_reminders:
        for reminder in reversed(st.session_state.sent_reminders):
            st.markdown(f"""
            <div class="recovery-action">
                ✅ **{reminder['cliente']}** - Carrito #{reminder['cart_id']} - {reminder['mensaje']} - {reminder['fecha']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No se han enviado recordatorios aún.")
    st.markdown("---")
    
    # Carritos prioritarios para recuperación
    st.markdown("### 🎯 Carritos Prioritarios para Recuperación")
    
    # Ordenar por probabilidad de recuperación y valor
    priority_carts = filtered_carts.copy()
    priority_carts['priority_score'] = (
        priority_carts['recovery_probability'] * 0.6 + 
        (priority_carts['total_value'] / priority_carts['total_value'].max()) * 0.4
    )
    priority_carts = priority_carts.sort_values('priority_score', ascending=False).head(10)
    
    for _, cart in priority_carts.iterrows():
        # Check if reminder was already sent from DataFrame
        reminder_sent = cart['recordatorio_enviado']
        
        # Determinar clase CSS basada en valor
        if cart['value_category'] == 'Alto Valor':
            card_class = 'high-value-cart'
        elif cart['value_category'] == 'Valor Medio':
            card_class = 'medium-value-cart'
        else:
            card_class = 'low-value-cart'
        
        with st.expander(f"🛒 Carrito #{cart['id']} - {cart['first_name']} {cart['last_name']} - €{cart['total_value']:.2f} - {'📨 Recordatorio Enviado' if reminder_sent else ''}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="abandoned-cart-card {card_class}">
                    <h4>👤 {cart['first_name']} {cart['last_name']}</h4>
                    <p><strong>📧 Email:</strong> {cart['email']}</p>
                    <p><strong>🌍 País:</strong> {cart['country']}</p>
                    <p><strong>💰 Valor del Carrito:</strong> €{cart['total_value']:.2f}</p>
                    <p><strong>⏰ Tiempo de Abandono:</strong> {cart['time_category']}</p>
                    <p><strong>📊 Probabilidad de Recuperación:</strong> {cart['recovery_probability']:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar productos en el carrito (simulado)
                st.markdown("**🛍️ Productos en el Carrito:**")
                import json
                try:
                    products_in_cart = json.loads(cart['cart_items'])
                    for product in products_in_cart[:3]:  # Mostrar solo los primeros 3
                        st.markdown(f"""
                        <div class="product-item">
                            • {product['product_name']} - Cantidad: {product['quantity']} - €{product['unit_price']:.2f}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if len(products_in_cart) > 3:
                        st.markdown(f"<div class='product-item'>... y {len(products_in_cart) - 3} productos más</div>", unsafe_allow_html=True)
                except:
                    st.markdown("*Productos no disponibles*")
            
            with col2:
                st.markdown("**🎯 Estrategias de Recuperación Recomendadas:**")
                strategies = display_recovery_strategies(cart)
                
                for strategy in strategies:
                    st.markdown(f"""
                    <div class="recovery-action">
                        {strategy}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botones de acción
                st.markdown("**⚡ Acciones Rápidas:**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button(f"📧 Enviar Email", key=f"email_{cart['id']}"):
                        st.success("Email de recuperación enviado!")
                
                with col_b:
                    if st.button(f"💰 Crear Descuento", key=f"discount_{cart['id']}"):
                        st.success("Descuento del 10% creado!")
                
                with col_c:
                    if st.button(f"📨 Enviar Recordatorio", key=f"reminder_{cart['id']}", disabled=reminder_sent):
                        # Add reminder to session state
                        st.session_state.sent_reminders.append({
                            'cart_id': cart['id'],
                            'cliente': f"{cart['first_name']} {cart['last_name']}",
                            'email': cart['email'],
                            'valor': cart['total_value'],
                            'mensaje': "¿Sigues interesado? Te dejamos 10% de descuento",
                            'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        })
                        st.success(f"Recordatorio enviado a {cart['first_name']} {cart['last_name']}!")
                        st.rerun()
    
    st.markdown("---")
    
    # Tabla completa de carritos abandonados
    st.markdown("### 📋 Todos los Carritos Abandonados")
    
    # Preparar datos para mostrar
    display_carts = filtered_carts.copy()
    display_carts['Cliente'] = display_carts['first_name'] + ' ' + display_carts['last_name']
    display_carts['Email'] = display_carts['email']
    display_carts['País'] = display_carts['country']
    display_carts['Valor'] = display_carts['total_value'].apply(lambda x: f"€{x:.2f}")
    display_carts['Categoría'] = display_carts['value_category']
    display_carts['Tiempo Abandono'] = display_carts['time_category']
    display_carts['Prob. Recuperación'] = display_carts['recovery_probability'].apply(lambda x: f"{x:.1%}")
    display_carts['Fecha Abandono'] = display_carts['created_at'].dt.strftime('%d/%m/%Y %H:%M')
    
    # Mostrar tabla
    st.dataframe(
        display_carts[['Cliente', 'Email', 'País', 'Valor', 'Categoría', 'Tiempo Abandono', 'Prob. Recuperación', 'Fecha Abandono']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cliente": st.column_config.TextColumn("Cliente", width="medium"),
            "Email": st.column_config.TextColumn("Email", width="large"),
            "País": st.column_config.TextColumn("País", width="small"),
            "Valor": st.column_config.TextColumn("Valor", width="small"),
            "Categoría": st.column_config.TextColumn("Categoría", width="medium"),
            "Tiempo Abandono": st.column_config.TextColumn("Tiempo Abandono", width="medium"),
            "Prob. Recuperación": st.column_config.TextColumn("Prob. Recuperación", width="small"),
            "Fecha Abandono": st.column_config.TextColumn("Fecha Abandono", width="medium")
        }
    )
    
    # Resumen y recomendaciones
    st.markdown("### 💡 Resumen y Recomendaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        high_value_carts = len(filtered_carts[filtered_carts['value_category'] == 'Alto Valor'])
        recent_carts = len(filtered_carts[filtered_carts['time_category'] == 'Reciente (< 1h)'])
        
        st.info(f"""
        **📊 Oportunidades Inmediatas:**
        - {high_value_carts} carritos de alto valor para recuperar
        - {recent_carts} carritos abandonados recientemente
        - €{potential_recovery:.2f} en recuperación potencial
        - Tasa de abandono actual: {(len(enriched_carts) / (len(enriched_carts) + 5000)) * 100:.1f}%
        """)
    
    with col2:
        avg_cart_value = filtered_carts['total_value'].mean()
        top_recovery_prob = filtered_carts['recovery_probability'].max()
        
        st.success(f"""
        **🎯 Estrategias Recomendadas:**
        - Implementar emails automáticos en la primera hora
        - Ofrecer descuentos progresivos según el tiempo
        - Simplificar el proceso de checkout
        - Valor promedio de carrito: €{avg_cart_value:.2f}
        """)

if __name__ == "__main__":
    main()
