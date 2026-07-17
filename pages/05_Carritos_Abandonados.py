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
        st.error(f"{get_string('carts_load_error', st.session_state.language)} {str(e)}")
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
            return get_string('carts_filter_value_high', st.session_state.language)
        elif value >= 100:
            return get_string('carts_filter_value_medium', st.session_state.language)
        else:
            return get_string('carts_filter_value_low', st.session_state.language)
    
    enriched_carts['value_category'] = enriched_carts['total_value'].apply(categorize_cart_value)
    
    # Categorizar por tiempo de abandono
    def categorize_abandonment_time(hours):
        if hours <= 1:
            return get_string('carts_filter_time_recent', st.session_state.language)
        elif hours <= 24:
            return get_string('carts_filter_time_same_day', st.session_state.language)
        elif hours <= 72:
            return get_string('carts_filter_time_last_3days', st.session_state.language)
        else:
            return get_string('carts_filter_time_older', st.session_state.language)
    
    enriched_carts['time_category'] = enriched_carts['hours_since_abandonment'].apply(categorize_abandonment_time)
    
    # Simular probabilidad de recuperación
    import numpy as np
    np.random.seed(42)
    
    def calculate_recovery_probability(row):
        base_prob = 0.3
        
        # Ajustar por valor del carrito
        if row['value_category'] == get_string('carts_filter_value_high', st.session_state.language):
            base_prob += 0.2
        elif row['value_category'] == get_string('carts_filter_value_medium', st.session_state.language):
            base_prob += 0.1
        
        # Ajustar por tiempo de abandono
        if row['time_category'] == get_string('carts_filter_time_recent', st.session_state.language):
            base_prob += 0.3
        elif row['time_category'] == get_string('carts_filter_time_same_day', st.session_state.language):
            base_prob += 0.1
        elif row['time_category'] == get_string('carts_filter_time_last_3days', st.session_state.language):
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
        get_string('carts_funnel_visitors', st.session_state.language): 50000,
        get_string('carts_funnel_products_viewed', st.session_state.language): 25000,
        get_string('carts_funnel_added_to_cart', st.session_state.language): len(carts_df) + 5000,
        get_string('carts_funnel_abandoned', st.session_state.language): len(carts_df),
        get_string('carts_funnel_recovered', st.session_state.language): int(len(carts_df) * 0.15)
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
        title=get_string('carts_funnel', st.session_state.language),
        template="plotly_white",
        height=400
    )
    
    return fig

def create_abandonment_reasons_chart():
    """Crea gráfico de razones de abandono"""
    # Datos simulados de razones de abandono
    reasons_data = {
        get_string('carts_reasons_shipping', st.session_state.language): 35,
        get_string('carts_reasons_checkout', st.session_state.language): 25,
        get_string('carts_reasons_payment', st.session_state.language): 15,
        get_string('carts_reasons_price', st.session_state.language): 12,
        get_string('carts_reasons_technical', st.session_state.language): 8,
        get_string('carts_reasons_trust', st.session_state.language): 5
    }
    
    fig = px.pie(
        values=list(reasons_data.values()),
        names=list(reasons_data.keys()),
        title=get_string('carts_reasons', st.session_state.language),
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
        title=get_string('carts_recovery_timeline', st.session_state.language),
        markers=True
    )
    
    fig.update_traces(
        line_color='#10b981',
        marker_color='#10b981',
        hovertemplate='<b>' + get_string('carts_recovery_timeline_hover', st.session_state.language) + '</b><br>' + get_string('carts_recovery_timeline_value', st.session_state.language) + '<extra></extra>'
    )
    
    fig.update_layout(
        xaxis_title=get_string('carts_recovery_timeline_hours', st.session_state.language),
        yaxis_title=get_string('carts_recovery_timeline_rate', st.session_state.language),
        template="plotly_white",
        height=400
    )
    
    return fig

def display_recovery_strategies(cart_row):
    """Muestra estrategias de recuperación personalizadas"""
    strategies = []
    
    # Estrategias basadas en valor del carrito
    if cart_row['value_category'] == get_string('carts_filter_value_high', st.session_state.language):
        strategies.extend([
            get_string('carts_strategy_call', st.session_state.language),
            get_string('carts_strategy_discount_20', st.session_state.language),
            get_string('carts_strategy_free_shipping_premium', st.session_state.language)
        ])
    elif cart_row['value_category'] == get_string('carts_filter_value_medium', st.session_state.language):
        strategies.extend([
            get_string('carts_strategy_discount_10', st.session_state.language),
            get_string('carts_strategy_free_shipping', st.session_state.language),
            get_string('carts_strategy_stock_alert', st.session_state.language)
        ])
    else:
        strategies.extend([
            get_string('carts_strategy_simple_email', st.session_state.language),
            get_string('carts_strategy_discount_5', st.session_state.language),
            get_string('carts_strategy_free_gift', st.session_state.language)
        ])
    
    # Estrategias basadas en tiempo
    if cart_row['time_category'] == get_string('carts_filter_time_recent', st.session_state.language):
        strategies.append(get_string('carts_strategy_push_notification', st.session_state.language))
    elif cart_row['time_category'] == get_string('carts_filter_time_same_day', st.session_state.language):
        strategies.append(get_string('carts_strategy_sms', st.session_state.language))
    elif cart_row['time_category'] == get_string('carts_filter_time_last_3days', st.session_state.language):
        strategies.append(get_string('carts_strategy_retargeting', st.session_state.language))
    else:
        strategies.append(get_string('carts_strategy_reactivation', st.session_state.language))
    
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
        if st.button(get_string('carts_generate_test', st.session_state.language), type="primary"):
            test_cart = generate_test_abandoned_cart(customers_df, products_df)
            # Convertir el dict a una fila del DataFrame
            new_cart_row = pd.DataFrame([test_cart])
            # Concatenar con el DataFrame existente
            st.session_state.app_data['carts'] = pd.concat(
                [carts_df, new_cart_row],
                ignore_index=True
            )
            st.success(get_string('carts_generate_success', st.session_state.language, id=test_cart['id']))
            st.rerun()
    
    with col2:
        # Verificar y enviar recordatorios
        sent_reminders = check_and_send_reminders()
        if sent_reminders:
            for reminder in sent_reminders:
                st.toast(get_string('carts_reminder_sent', st.session_state.language, name=reminder['cliente']))
    
    # Calcular métricas de abandono
    enriched_carts = calculate_abandonment_metrics(carts_df, customers_df, products_df)
    
    # Filtros
    st.markdown(f"### {get_string('carts_filters', st.session_state.language)}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        value_categories = [get_string('carts_filter_value_all', st.session_state.language)] + list(enriched_carts['value_category'].unique())
        selected_value = st.selectbox(
            get_string('carts_filter_value', st.session_state.language),
            value_categories
        )
    
    with col2:
        time_categories = [get_string('carts_filter_time_all', st.session_state.language)] + list(enriched_carts['time_category'].unique())
        selected_time = st.selectbox(
            get_string('carts_filter_time', st.session_state.language),
            time_categories
        )
    
    with col3:
        countries = [get_string('carts_filter_country_all', st.session_state.language)] + list(enriched_carts['country'].unique())
        selected_country = st.selectbox(
            get_string('carts_filter_country', st.session_state.language),
            countries
        )
    
    with col4:
        min_probability = st.slider(
            get_string('carts_filter_probability', st.session_state.language),
            0.0, 1.0, 0.0, 0.05
        )
    
    # Aplicar filtros
    filtered_carts = enriched_carts.copy()
    
    if selected_value != get_string('carts_filter_value_all', st.session_state.language):
        filtered_carts = filtered_carts[filtered_carts['value_category'] == selected_value]
    
    if selected_time != get_string('carts_filter_time_all', st.session_state.language):
        filtered_carts = filtered_carts[filtered_carts['time_category'] == selected_time]
    
    if selected_country != get_string('carts_filter_country_all', st.session_state.language):
        filtered_carts = filtered_carts[filtered_carts['country'] == selected_country]
    
    filtered_carts = filtered_carts[filtered_carts['recovery_probability'] >= min_probability]
    
    # Métricas principales
    st.markdown(f"### {get_string('carts_metrics', st.session_state.language)}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{len(filtered_carts):,}</h3>
            <p>{get_string('carts_metric_total', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_value = filtered_carts['total_value'].sum()
        st.markdown(f"""
        <div class="metric-box">
            <h3>€{total_value:,.2f}</h3>
            <p>{get_string('carts_metric_lost_value', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_recovery_prob = filtered_carts['recovery_probability'].mean()
        st.markdown(f"""
        <div class="metric-box">
            <h3>{avg_recovery_prob * 100:.1f}%</h3>
            <p>{get_string('carts_metric_avg_recovery', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        potential_recovery = (filtered_carts['total_value'] * filtered_carts['recovery_probability']).sum()
        st.markdown(f"""
        <div class="metric-box">
            <h3>€{potential_recovery:,.2f}</h3>
            <p>{get_string('carts_metric_potential_recovery', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizaciones principales
    st.markdown(f"### {get_string('carts_analysis', st.session_state.language)}")
    
    # Obtener el template de plotly
    chart_template = get_plotly_template()
    
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
            title=get_string('carts_distribution', st.session_state.language),
            color=value_dist.values,
            color_continuous_scale='Reds'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>' + get_string('carts_distribution_y', st.session_state.language) + ': %{y}<extra></extra>'
        )
        
        fig.update_layout(
            xaxis_title=get_string('carts_distribution_x', st.session_state.language),
            yaxis_title=get_string('carts_distribution_y', st.session_state.language),
            template=chart_template,
            height=400,
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Análisis por tiempo de abandono
    st.markdown(f"### {get_string('carts_temporal_analysis', st.session_state.language)}")
    
    time_analysis = filtered_carts.groupby('time_category').agg({
        'id': 'count',
        'total_value': ['sum', 'mean'],
        'recovery_probability': 'mean'
    }).round(2)
    
    time_analysis.columns = ['count', 'total_value', 'avg_value', 'avg_recovery_prob']
    time_analysis = time_analysis.reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=get_string('carts_temporal_count', st.session_state.language),
        x=time_analysis['time_category'],
        y=time_analysis['count'],
        marker_color='#f59e0b',
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>' + get_string('carts_temporal_count', st.session_state.language) + ': %{y}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        name=get_string('carts_temporal_probability', st.session_state.language),
        x=time_analysis['time_category'],
        y=time_analysis['avg_recovery_prob'] * 100,
        mode='lines+markers',
        line=dict(color='#10b981'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>' + get_string('carts_temporal_probability', st.session_state.language) + ': %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title=get_string('carts_temporal_title', st.session_state.language),
        xaxis_title=get_string('carts_filter_time', st.session_state.language),
        yaxis=dict(title=get_string('carts_temporal_count', st.session_state.language), side='left'),
        yaxis2=dict(title=get_string('carts_temporal_probability', st.session_state.language), side='right', overlaying='y'),
        template=chart_template,
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Log de recordatorios enviados
    st.markdown(f"### {get_string('carts_reminder_history', st.session_state.language)}")
    if st.session_state.sent_reminders:
        for reminder in reversed(st.session_state.sent_reminders):
            st.markdown(f"""
            <div class="recovery-action">
                ✅ **{reminder['cliente']}** - Carrito #{reminder['cart_id']} - {reminder['mensaje']} - {reminder['fecha']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(get_string('carts_reminder_none', st.session_state.language))
    st.markdown("---")
    
    # Carritos prioritarios para recuperación
    st.markdown(f"### {get_string('carts_priority', st.session_state.language)}")
    
    # Ordenar por probabilidad de recuperación y valor
    priority_carts = filtered_carts.copy()
    priority_carts['priority_score'] = (
        priority_carts['recovery_probability'] * 0.6 + 
        (priority_carts['total_value'] / priority_carts['total_value'].max()) * 0.4
    )
    priority_carts = priority_carts.sort_values('priority_score', ascending=False).head(10)
    
    for _, cart in priority_carts.iterrows():
        # Check if reminder was already sent from DataFrame
        reminder_sent = cart.get('recordatorio_enviado', False)
        reminder_status = get_string('carts_priority_reminder_sent', st.session_state.language) if reminder_sent else ''
        
        # Determinar clase CSS basada en valor
        if cart['value_category'] == get_string('carts_filter_value_high', st.session_state.language):
            card_class = 'high-value-cart'
        elif cart['value_category'] == get_string('carts_filter_value_medium', st.session_state.language):
            card_class = 'medium-value-cart'
        else:
            card_class = 'low-value-cart'
        
        expander_label = get_string('carts_priority_expander', st.session_state.language,
            id=cart['id'],
            name=f"{cart['first_name']} {cart['last_name']}",
            value=cart['total_value'],
            reminder_status=reminder_status
        )
        
        with st.expander(expander_label):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="abandoned-cart-card {card_class}">
                    <h4>👤 {cart['first_name']} {cart['last_name']}</h4>
                    <p><strong>{get_string('carts_priority_email_label', st.session_state.language)}</strong> {cart['email']}</p>
                    <p><strong>{get_string('carts_priority_country_label', st.session_state.language)}</strong> {cart['country']}</p>
                    <p><strong>{get_string('carts_priority_value_label', st.session_state.language)}</strong> €{cart['total_value']:.2f}</p>
                    <p><strong>{get_string('carts_priority_time_label', st.session_state.language)}</strong> {cart['time_category']}</p>
                    <p><strong>{get_string('carts_priority_probability_label', st.session_state.language)}</strong> {cart['recovery_probability']:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar productos en el carrito (simulado)
                st.markdown(f"**{get_string('carts_priority_products', st.session_state.language)}**")
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
                        st.markdown(f"<div class='product-item'>{get_string('carts_priority_products_more', st.session_state.language, count=len(products_in_cart) - 3)}</div>", unsafe_allow_html=True)
                except:
                    st.markdown(f"*{get_string('carts_priority_products_unavailable', st.session_state.language)}*")
            
            with col2:
                st.markdown(f"**{get_string('carts_priority_strategies', st.session_state.language)}**")
                strategies = display_recovery_strategies(cart)
                
                for strategy in strategies:
                    st.markdown(f"""
                    <div class="recovery-action">
                        {strategy}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botones de acción
                st.markdown(f"**{get_string('carts_priority_actions', st.session_state.language)}**")
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button(get_string('carts_priority_action_email', st.session_state.language), key=f"email_{cart['id']}"):
                        st.success(get_string('carts_priority_action_email_sent', st.session_state.language))
                
                with col_b:
                    if st.button(get_string('carts_priority_action_discount', st.session_state.language), key=f"discount_{cart['id']}"):
                        st.success(get_string('carts_priority_action_discount_created', st.session_state.language))
                
                with col_c:
                    if st.button(get_string('carts_priority_action_reminder', st.session_state.language), key=f"reminder_{cart['id']}", disabled=reminder_sent):
                        # Add reminder to session state
                        st.session_state.sent_reminders.append({
                            'cart_id': cart['id'],
                            'cliente': f"{cart['first_name']} {cart['last_name']}",
                            'email': cart['email'],
                            'valor': cart['total_value'],
                            'mensaje': get_string('carts_priority_reminder_message', st.session_state.language),
                            'fecha': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                        })
                        st.success(get_string('carts_priority_action_reminder_sent', st.session_state.language, name=f"{cart['first_name']} {cart['last_name']}"))
                        st.rerun()
    
    st.markdown("---")
    
    # Tabla completa de carritos abandonados
    st.markdown(f"### {get_string('carts_list', st.session_state.language)}")
    
    # Preparar datos para mostrar
    display_carts = filtered_carts.copy()
    display_carts[get_string('carts_table_client', st.session_state.language)] = display_carts['first_name'] + ' ' + display_carts['last_name']
    display_carts[get_string('carts_table_email', st.session_state.language)] = display_carts['email']
    display_carts[get_string('carts_table_country', st.session_state.language)] = display_carts['country']
    display_carts[get_string('carts_table_value', st.session_state.language)] = display_carts['total_value'].apply(lambda x: f"€{x:.2f}")
    display_carts[get_string('carts_table_category', st.session_state.language)] = display_carts['value_category']
    display_carts[get_string('carts_table_time', st.session_state.language)] = display_carts['time_category']
    display_carts[get_string('carts_table_probability', st.session_state.language)] = display_carts['recovery_probability'].apply(lambda x: f"{x:.1%}")
    display_carts[get_string('carts_table_date', st.session_state.language)] = display_carts['created_at'].dt.strftime('%d/%m/%Y %H:%M')
    
    # Mostrar tabla
    st.dataframe(
        display_carts[[
            get_string('carts_table_client', st.session_state.language),
            get_string('carts_table_email', st.session_state.language),
            get_string('carts_table_country', st.session_state.language),
            get_string('carts_table_value', st.session_state.language),
            get_string('carts_table_category', st.session_state.language),
            get_string('carts_table_time', st.session_state.language),
            get_string('carts_table_probability', st.session_state.language),
            get_string('carts_table_date', st.session_state.language)
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            get_string('carts_table_client', st.session_state.language): st.column_config.TextColumn(
                get_string('carts_table_client', st.session_state.language), width="medium"
            ),
            get_string('carts_table_email', st.session_state.language): st.column_config.TextColumn(
                get_string('carts_table_email', st.session_state.language), width="large"
            ),
            get_string('carts_table_country', st.session_state.language): st.column_config.TextColumn(
                get_string('carts_table_country', st.session_state.language), width="small"
            ),
            get_string('carts_table_value', st.session_state.language): st.column_config.TextColumn(
                get_string('carts_table_value', st.session_state.language), width="small"
            ),
            get_string('carts_table_category', st.session_state.language): st.column_config.TextColumn(
                get_string('carts_table_category', st.session_state.language), width="medium"
            ),
            get_string('carts_table_time', st.session_state.language): st.column_config.TextColumn(
                get_string('carts_table_time', st.session_state.language), width="medium"
            ),
            get_string('carts_table_probability', st.session_state.language): st.column_config.TextColumn(
                get_string('carts_table_probability', st.session_state.language), width="small"
            ),
            get_string('carts_table_date', st.session_state.language): st.column_config.TextColumn(
                get_string('carts_table_date', st.session_state.language), width="medium"
            )
        }
    )
    
    # Resumen y recomendaciones
    st.markdown(f"### {get_string('carts_insights', st.session_state.language)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        high_value_carts = len(filtered_carts[filtered_carts['value_category'] == get_string('carts_filter_value_high', st.session_state.language)])
        recent_carts = len(filtered_carts[filtered_carts['time_category'] == get_string('carts_filter_time_recent', st.session_state.language)])
        
        st.info(f"""
        **{get_string('carts_insights_opportunities', st.session_state.language)}**
        - {get_string('carts_insights_high_value', st.session_state.language, count=high_value_carts)}
        - {get_string('carts_insights_recent', st.session_state.language, count=recent_carts)}
        - {get_string('carts_insights_potential', st.session_state.language, value=potential_recovery)}
        - {get_string('carts_insights_abandonment_rate', st.session_state.language, rate=(len(enriched_carts) / (len(enriched_carts) + 5000)) * 100)}
        """)
    
    with col2:
        avg_cart_value = filtered_carts['total_value'].mean()
        
        st.success(f"""
        **{get_string('carts_insights_strategies', st.session_state.language)}**
        - {get_string('carts_insights_strategy_auto_emails', st.session_state.language)}
        - {get_string('carts_insights_strategy_discounts', st.session_state.language)}
        - {get_string('carts_insights_strategy_checkout', st.session_state.language)}
        - {get_string('carts_insights_avg_value', st.session_state.language, value=avg_cart_value)}
        """)

if __name__ == "__main__":
    main()
