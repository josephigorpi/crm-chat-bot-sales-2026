"""
Página de Pedidos y Envíos
Gestión completa de pedidos y seguimiento de envíos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_generator import get_all_data
from utils.chart_utils import create_delivery_time_chart
from utils.theme import inject_theme_css, get_plotly_template, init_theme_state
from i18n.strings import get_string
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Pedidos y Envíos", page_icon="📦", layout="wide")


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
    .orders-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .order-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
        color: #1f2937;
    }
    
    .status-pending {
        border-left: 4px solid #f59e0b;
        background: #fffbeb;
        color: #1f2937;
    }
    
    .status-processing {
        border-left: 4px solid #06b6d4;
        background: #f0f9ff;
        color: #1f2937;
    }
    
    .status-shipped {
        border-left: 4px solid #8b5cf6;
        background: #faf5ff;
        color: #1f2937;
    }
    
    .status-delivered {
        border-left: 4px solid #10b981;
        background: #f0fdf4;
        color: #1f2937;
    }
    
    .status-cancelled {
        border-left: 4px solid #ef4444;
        background: #fef2f2;
        color: #1f2937;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #3b82f6;
        color: #1f2937;
    }
    
    .tracking-timeline {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: #1f2937;
    }
    
    .timeline-step {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
    }
    
    .timeline-step.completed {
        color: #10b981;
    }
    
    .timeline-step.current {
        color: #3b82f6;
        font-weight: bold;
    }
    
    .timeline-step.pending {
        color: #9ca3af;
    }
    
    .shipment-info {
        background: #e0f2fe;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #0ea5e9;
        margin: 1rem 0;
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

def load_orders_data():
    """Carga y procesa los datos de pedidos y envíos"""
    try:
        data = get_all_data()
        return data
    except Exception as e:
        st.error(f"{get_string('orders_load_error', st.session_state.language)} {str(e)}")
        return None

def enrich_orders_data(orders_df, customers_df, shipments_df):
    """Enriquece los datos de pedidos con información adicional"""
    # Merge con datos de clientes
    enriched_orders = orders_df.merge(
        customers_df[['id', 'first_name', 'last_name', 'email', 'country']], 
        left_on='customer_id', right_on='id', how='left', suffixes=('', '_customer')
    )
    
    # Merge con datos de envíos usando el id original del pedido
    enriched_orders = enriched_orders.merge(
        shipments_df, left_on='id', right_on='order_id', how='left', suffixes=('', '_shipment')
    )
    
    # Crear columna delivery_status basada en status_shipment
    enriched_orders['delivery_status'] = enriched_orders['status_shipment'].fillna('no_shipment')
    
    # Crear columna delivered_at basada en actual_delivery
    enriched_orders['delivered_at'] = enriched_orders['actual_delivery']
    
    # Crear columna shipping_method basada en carrier
    enriched_orders['shipping_method'] = enriched_orders['carrier'].fillna(get_string('orders_shipping_unassigned', st.session_state.language))
    
    # Renombrar created_at a order_date para consistencia
    enriched_orders['order_date'] = enriched_orders['created_at']
    
    # Calcular días desde el pedido
    enriched_orders['order_date'] = pd.to_datetime(enriched_orders['order_date'])
    enriched_orders['days_since_order'] = (
        datetime.now() - enriched_orders['order_date']
    ).dt.days
    
    # Calcular tiempo de entrega (si está entregado)
    enriched_orders['delivery_time_days'] = None
    delivered_mask = enriched_orders['delivery_status'] == 'delivered'
    if delivered_mask.any():
        enriched_orders.loc[delivered_mask, 'delivery_time_days'] = (
            pd.to_datetime(enriched_orders.loc[delivered_mask, 'delivered_at']) - 
            enriched_orders.loc[delivered_mask, 'order_date']
        ).dt.days
    
    return enriched_orders

def get_status_color(status):
    """Retorna el color asociado a cada estado"""
    colors = {
        'pending': '#f59e0b',
        'processing': '#06b6d4',
        'shipped': '#8b5cf6',
        'delivered': '#10b981',
        'cancelled': '#ef4444'
    }
    return colors.get(status, '#6b7280')

def get_status_emoji(status):
    """Retorna el emoji asociado a cada estado"""
    emojis = {
        'pending': '⏳',
        'processing': '🔄',
        'shipped': '🚚',
        'delivered': '✅',
        'cancelled': '❌'
    }
    return emojis.get(status, '❓')

def get_payment_status_label(status):
    """Retorna la etiqueta traducida para el estado de pago"""
    labels = {
        'pending': get_string('orders_payment_pending', st.session_state.language),
        'paid': get_string('orders_payment_paid', st.session_state.language),
        'failed': get_string('orders_payment_failed', st.session_state.language),
        'refunded': get_string('orders_payment_refunded', st.session_state.language)
    }
    return labels.get(status, status)

def get_status_label(status):
    """Retorna la etiqueta traducida para el estado del pedido"""
    labels = {
        'pending': get_string('orders_filter_status_pending', st.session_state.language),
        'processing': get_string('orders_filter_status_processing', st.session_state.language),
        'shipped': get_string('orders_filter_status_shipped', st.session_state.language),
        'delivered': get_string('orders_filter_status_delivered', st.session_state.language),
        'cancelled': get_string('orders_filter_status_cancelled', st.session_state.language)
    }
    return labels.get(status, status)

def create_order_status_timeline():
    """Crea timeline de estados de pedidos"""
    # Simular datos de timeline
    timeline_data = []
    statuses = ['pending', 'processing', 'shipped', 'delivered']
    
    status_names = {
        'pending': get_string('orders_timeline_pending', st.session_state.language),
        'processing': get_string('orders_timeline_processing', st.session_state.language),
        'shipped': get_string('orders_timeline_shipped', st.session_state.language),
        'delivered': get_string('orders_timeline_delivered', st.session_state.language)
    }
    
    for i, status in enumerate(statuses):
        timeline_data.append({
            'step': i + 1,
            'status': status_names[status],
            'avg_time': [0, 1, 3, 7][i]  # Días promedio
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=timeline_df['avg_time'],
        y=timeline_df['status'],
        mode='markers+lines',
        marker=dict(size=15, color='#3b82f6'),
        line=dict(color='#3b82f6', width=3),
        hovertemplate='<b>%{y}</b><br>' + get_string('orders_timeline_step', st.session_state.language, days='%{x}') + '<extra></extra>',
        text=[status_names[s] for s in statuses]
    ))
    
    fig.update_layout(
        title=get_string('orders_timeline', st.session_state.language),
        xaxis_title=get_string('orders_timeline_x', st.session_state.language),
        yaxis_title=get_string('orders_timeline_y', st.session_state.language),
        template='plotly_white',
        height=400,
        xaxis=dict(range=[-0.5, 8])
    )
    
    return fig

def create_shipping_performance_chart(orders_df):
    """Crea gráfico de rendimiento de envíos"""
    # Agrupar por método de envío
    shipping_stats = orders_df.groupby('shipping_method').agg({
        'id': 'count',
        'delivery_time_days': 'mean',
        'total_amount': 'mean'
    }).round(2)
    
    shipping_stats.columns = ['order_count', 'avg_delivery_days', 'avg_order_value']
    shipping_stats = shipping_stats.reset_index()
    
    fig = go.Figure()
    
    # Barras para número de pedidos
    fig.add_trace(go.Bar(
        name=get_string('orders_shipping_performance_orders', st.session_state.language),
        x=shipping_stats['shipping_method'],
        y=shipping_stats['order_count'],
        marker_color='#3b82f6',
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>' + get_string('orders_shipping_performance_orders_hover', st.session_state.language, count='%{y}') + '<extra></extra>'
    ))
    
    # Línea para tiempo promedio de entrega
    fig.add_trace(go.Scatter(
        name=get_string('orders_shipping_performance_days', st.session_state.language),
        x=shipping_stats['shipping_method'],
        y=shipping_stats['avg_delivery_days'],
        mode='lines+markers',
        line=dict(color='#ef4444'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>' + get_string('orders_shipping_performance_days_hover', st.session_state.language, days='%{y:.1f}') + '<extra></extra>'
    ))
    
    fig.update_layout(
        title=get_string('orders_shipping_performance', st.session_state.language),
        xaxis_title=get_string('orders_shipping_performance_x', st.session_state.language),
        yaxis=dict(title=get_string('orders_shipping_performance_orders', st.session_state.language), side='left'),
        yaxis2=dict(title=get_string('orders_shipping_performance_days', st.session_state.language), side='right', overlaying='y'),
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    return fig

def display_order_tracking(order_row):
    """Muestra el seguimiento detallado de un pedido"""
    current_status = order_row['status']
    
    # Definir los pasos del timeline
    steps = [
        ('pending', get_string('orders_tracking_confirmado', st.session_state.language), get_string('orders_tracking_confirmado_desc', st.session_state.language)),
        ('processing', get_string('orders_tracking_preparando', st.session_state.language), get_string('orders_tracking_preparando_desc', st.session_state.language)),
        ('shipped', get_string('orders_tracking_enviado', st.session_state.language), get_string('orders_tracking_enviado_desc', st.session_state.language)),
        ('delivered', get_string('orders_tracking_entregado', st.session_state.language), get_string('orders_tracking_entregado_desc', st.session_state.language))
    ]
    
    st.markdown(f"**{get_string('orders_tracking', st.session_state.language)}**")
    
    for step_status, step_title, step_desc in steps:
        if step_status == current_status:
            step_class = "current"
            icon = "🔵"
        elif steps.index((step_status, step_title, step_desc)) < steps.index(next(s for s in steps if s[0] == current_status)):
            step_class = "completed"
            icon = "✅"
        else:
            step_class = "pending"
            icon = "⚪"
        
        st.markdown(f"""
        <div class="timeline-step {step_class}">
            {icon} <strong>{step_title}</strong> - {step_desc}
        </div>
        """, unsafe_allow_html=True)
    
    # Información de envío si está disponible
    if pd.notna(order_row.get('tracking_number')):
        estimated_date = order_row.get('estimated_delivery')
        estimated_str = estimated_date.strftime('%d/%m/%Y') if pd.notna(estimated_date) else get_string('orders_shipment_not_available', st.session_state.language)
        
        st.markdown(f"""
        <div class="shipment-info">
            <strong>{get_string('orders_shipment_info', st.session_state.language)}</strong><br>
            • {get_string('orders_shipment_tracking', st.session_state.language)} {order_row['tracking_number']}<br>
            • {get_string('orders_shipment_carrier', st.session_state.language)} {order_row.get('carrier', get_string('orders_shipment_not_available', st.session_state.language))}<br>
            • {get_string('orders_shipment_method', st.session_state.language)} {order_row.get('shipping_method', get_string('orders_shipment_not_available', st.session_state.language))}<br>
            • {get_string('orders_shipment_estimated', st.session_state.language)} {estimated_str}
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header de la página
    st.markdown(f"""
    <div class="orders-header">
        <h1>{get_string('orders_title', st.session_state.language)}</h1>
        <p>{get_string('orders_subtitle', st.session_state.language)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    data = load_orders_data()
    if data is None:
        return
    
    orders_df = data['orders']
    customers_df = data['customers']
    shipments_df = data['shipments']
    
    # Enriquecer datos de pedidos
    enriched_orders = enrich_orders_data(orders_df, customers_df, shipments_df)
    
    # Filtros
    st.markdown(f"### {get_string('orders_filters', st.session_state.language)}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        statuses = [get_string('orders_filter_status_all', st.session_state.language)] + list(enriched_orders['status'].unique())
        selected_status = st.selectbox(
            get_string('orders_filter_status', st.session_state.language),
            statuses
        )
    
    with col2:
        shipping_methods = [get_string('orders_filter_shipping_all', st.session_state.language)] + list(enriched_orders['shipping_method'].unique())
        selected_shipping = st.selectbox(
            get_string('orders_filter_shipping', st.session_state.language),
            shipping_methods
        )
    
    with col3:
        countries = [get_string('orders_filter_country_all', st.session_state.language)] + list(enriched_orders['country'].unique())
        selected_country = st.selectbox(
            get_string('orders_filter_country', st.session_state.language),
            countries
        )
    
    with col4:
        date_range = st.date_input(
            get_string('orders_filter_date', st.session_state.language),
            value=(
                enriched_orders['order_date'].min().date(),
                enriched_orders['order_date'].max().date()
            ),
            min_value=enriched_orders['order_date'].min().date(),
            max_value=enriched_orders['order_date'].max().date()
        )
    
    # Aplicar filtros
    filtered_orders = enriched_orders.copy()
    
    if selected_status != get_string('orders_filter_status_all', st.session_state.language):
        filtered_orders = filtered_orders[filtered_orders['status'] == selected_status]
    
    if selected_shipping != get_string('orders_filter_shipping_all', st.session_state.language):
        filtered_orders = filtered_orders[filtered_orders['shipping_method'] == selected_shipping]
    
    if selected_country != get_string('orders_filter_country_all', st.session_state.language):
        filtered_orders = filtered_orders[filtered_orders['country'] == selected_country]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_orders = filtered_orders[
            (filtered_orders['order_date'].dt.date >= start_date) &
            (filtered_orders['order_date'].dt.date <= end_date)
        ]
    
    # Métricas principales
    st.markdown(f"### {get_string('orders_metrics', st.session_state.language)}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(filtered_orders):,}</h3>
            <p>{get_string('orders_metric_total', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_revenue = filtered_orders['total_amount'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>€{total_revenue:,.2f}</h3>
            <p>{get_string('orders_metric_revenue', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_order_value = filtered_orders['total_amount'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>€{avg_order_value:.2f}</h3>
            <p>{get_string('orders_metric_avg_value', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        delivered_orders = len(filtered_orders[filtered_orders['status'] == 'delivered'])
        delivery_rate = (delivered_orders / len(filtered_orders)) * 100 if len(filtered_orders) > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{delivery_rate:.1f}%</h3>
            <p>{get_string('orders_metric_delivery_rate', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizaciones principales
    st.markdown(f"### {get_string('orders_analysis', st.session_state.language)}")
    
    # Obtener el template de plotly
    chart_template = get_plotly_template()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución por estado
        status_counts = filtered_orders['status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=[f"{get_status_emoji(status)} {get_status_label(status)}" for status in status_counts.index],
            title=get_string('orders_status_distribution', st.session_state.language),
            color_discrete_sequence=[get_status_color(status) for status in status_counts.index]
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>' + get_string('orders_status_distribution_hover', st.session_state.language, value='%{value}', percent='%{percent}') + '<extra></extra>'
        )
        
        fig.update_layout(template=chart_template, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Timeline de estados
        timeline_chart = create_order_status_timeline()
        st.plotly_chart(timeline_chart, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rendimiento de envíos
        shipping_performance = create_shipping_performance_chart(filtered_orders)
        st.plotly_chart(shipping_performance, use_container_width=True)
    
    with col2:
        # Tiempo de entrega
        delivery_chart = create_delivery_time_chart(filtered_orders, chart_template, st.session_state.language)
        st.plotly_chart(delivery_chart, use_container_width=True)
    
    st.markdown("---")
    
    # Análisis temporal
    st.markdown(f"### {get_string('orders_trends', st.session_state.language)}")
    
    # Pedidos por día
    daily_orders = filtered_orders.groupby(filtered_orders['order_date'].dt.date).agg({
        'id': 'count',
        'total_amount': 'sum'
    }).reset_index()
    
    daily_orders.columns = ['date', 'order_count', 'daily_revenue']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_orders['date'],
        y=daily_orders['order_count'],
        mode='lines+markers',
        name=get_string('orders_trends_count', st.session_state.language),
        line=dict(color='#3b82f6'),
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_orders['date'],
        y=daily_orders['daily_revenue'],
        mode='lines+markers',
        name=get_string('orders_trends_revenue', st.session_state.language),
        line=dict(color='#10b981'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=get_string('orders_trends_title', st.session_state.language),
        xaxis_title=get_string('orders_trends_date', st.session_state.language),
        yaxis=dict(title=get_string('orders_trends_count', st.session_state.language), side='left'),
        yaxis2=dict(title=get_string('orders_trends_revenue', st.session_state.language), side='right', overlaying='y'),
        template=chart_template,
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Pedidos recientes con seguimiento
    st.markdown(f"### {get_string('orders_recent', st.session_state.language)}")
    
    recent_orders = filtered_orders.nlargest(10, 'order_date')
    
    for _, order in recent_orders.iterrows():
        status_class = f"status-{order['status']}"
        
        expander_label = get_string('orders_recent_expander', st.session_state.language,
            emoji=get_status_emoji(order['status']),
            id=order['id'],
            name=f"{order['first_name']} {order['last_name']}",
            amount=order['total_amount']
        )
        
        with st.expander(expander_label):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                payment_method = order.get('metodo_pago', get_string('orders_details_not_available', st.session_state.language))
                payment_status = order.get('estado_pago', get_string('orders_details_not_available', st.session_state.language))
                
                st.markdown(f"""
                <div class="order-card {status_class}">
                    <h4>{get_string('orders_details', st.session_state.language)}</h4>
                    <p><strong>{get_string('orders_details_client', st.session_state.language)}</strong> {order['first_name']} {order['last_name']}</p>
                    <p><strong>{get_string('orders_details_email', st.session_state.language)}</strong> {order['email']}</p>
                    <p><strong>{get_string('orders_details_country', st.session_state.language)}</strong> {order['country']}</p>
                    <p><strong>{get_string('orders_details_total', st.session_state.language)}</strong> €{order['total_amount']:.2f}</p>
                    <p><strong>{get_string('orders_details_payment_method', st.session_state.language)}</strong> {payment_method}</p>
                    <p><strong>{get_string('orders_details_payment_status', st.session_state.language)}</strong> {get_payment_status_label(payment_status)}</p>
                    <p><strong>{get_string('orders_details_date', st.session_state.language)}</strong> {order['order_date'].strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>{get_string('orders_details_shipping', st.session_state.language)}</strong> {order['shipping_method']}</p>
                    <p><strong>{get_string('orders_details_status', st.session_state.language)}</strong> {get_status_emoji(order['status'])} {get_status_label(order['status'])}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                display_order_tracking(order)
                
                # Acciones rápidas
                st.markdown(f"**{get_string('orders_actions', st.session_state.language)}**")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(get_string('orders_action_notify', st.session_state.language), key=f"notify_{order['id']}"):
                        st.success(get_string('orders_action_notify_sent', st.session_state.language))
                
                with col_b:
                    if st.button(get_string('orders_action_details', st.session_state.language), key=f"details_{order['id']}"):
                        st.info(get_string('orders_action_details_info', st.session_state.language))
    
    st.markdown("---")
    
    # Tabla completa de pedidos
    st.markdown(f"### {get_string('orders_list', st.session_state.language)}")
    
    # Opciones de ordenamiento
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**{get_string('orders_list_showing', st.session_state.language, count=len(filtered_orders))}**")
    
    with col2:
        sort_by = st.selectbox(
            get_string('orders_list_sort_by', st.session_state.language),
            ["order_date", "total_amount", "status", "customer_id"],
            format_func=lambda x: {
                "order_date": get_string('orders_list_sort_date', st.session_state.language),
                "total_amount": get_string('orders_list_sort_amount', st.session_state.language),
                "status": get_string('orders_list_sort_status', st.session_state.language),
                "customer_id": get_string('orders_list_sort_customer', st.session_state.language)
            }[x]
        )
    
    with col3:
        sort_options = [
            get_string('orders_list_sort_descending', st.session_state.language),
            get_string('orders_list_sort_ascending', st.session_state.language)
        ]
        sort_order = st.selectbox(
            get_string('orders_list_sort_order', st.session_state.language),
            sort_options
        )
    
    # Aplicar ordenamiento
    ascending = sort_order == get_string('orders_list_sort_ascending', st.session_state.language)
    sorted_orders = filtered_orders.sort_values(sort_by, ascending=ascending)
    
    # Preparar datos para mostrar
    display_orders = sorted_orders.copy()
    display_orders[get_string('orders_table_id', st.session_state.language)] = display_orders['id']
    display_orders[get_string('orders_table_client', st.session_state.language)] = display_orders['first_name'] + ' ' + display_orders['last_name']
    display_orders[get_string('orders_table_email', st.session_state.language)] = display_orders['email']
    display_orders[get_string('orders_table_country', st.session_state.language)] = display_orders['country']
    display_orders[get_string('orders_table_total', st.session_state.language)] = display_orders['total_amount'].apply(lambda x: f"€{x:.2f}")
    
    payment_method_col = order.get('metodo_pago', get_string('orders_details_not_available', st.session_state.language))
    display_orders[get_string('orders_table_payment_method', st.session_state.language)] = display_orders.apply(lambda x: x.get('metodo_pago', get_string('orders_details_not_available', st.session_state.language)), axis=1)
    display_orders[get_string('orders_table_payment_status', st.session_state.language)] = display_orders.apply(lambda x: get_payment_status_label(x.get('estado_pago', get_string('orders_details_not_available', st.session_state.language))), axis=1)
    
    display_orders[get_string('orders_table_status', st.session_state.language)] = display_orders['status'].apply(lambda x: f"{get_status_emoji(x)} {get_status_label(x)}")
    display_orders[get_string('orders_table_date', st.session_state.language)] = display_orders['order_date'].dt.strftime('%d/%m/%Y')
    display_orders[get_string('orders_table_shipping', st.session_state.language)] = display_orders['shipping_method']
    
    # Mostrar tabla
    st.dataframe(
        display_orders[[
            get_string('orders_table_id', st.session_state.language),
            get_string('orders_table_client', st.session_state.language),
            get_string('orders_table_email', st.session_state.language),
            get_string('orders_table_country', st.session_state.language),
            get_string('orders_table_total', st.session_state.language),
            get_string('orders_table_payment_method', st.session_state.language),
            get_string('orders_table_payment_status', st.session_state.language),
            get_string('orders_table_status', st.session_state.language),
            get_string('orders_table_date', st.session_state.language),
            get_string('orders_table_shipping', st.session_state.language)
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            get_string('orders_table_id', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_id', st.session_state.language), width="small"
            ),
            get_string('orders_table_client', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_client', st.session_state.language), width="medium"
            ),
            get_string('orders_table_email', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_email', st.session_state.language), width="large"
            ),
            get_string('orders_table_country', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_country', st.session_state.language), width="small"
            ),
            get_string('orders_table_total', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_total', st.session_state.language), width="small"
            ),
            get_string('orders_table_payment_method', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_payment_method', st.session_state.language), width="medium"
            ),
            get_string('orders_table_payment_status', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_payment_status', st.session_state.language), width="medium"
            ),
            get_string('orders_table_status', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_status', st.session_state.language), width="medium"
            ),
            get_string('orders_table_date', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_date', st.session_state.language), width="small"
            ),
            get_string('orders_table_shipping', st.session_state.language): st.column_config.TextColumn(
                get_string('orders_table_shipping', st.session_state.language), width="medium"
            )
        }
    )
    
    # Resumen y estadísticas
    st.markdown(f"### {get_string('orders_executive_summary', st.session_state.language)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estadísticas de rendimiento
        avg_delivery_time = filtered_orders['delivery_time_days'].mean() if not filtered_orders['delivery_time_days'].isna().all() else 0
        pending_orders = len(filtered_orders[filtered_orders['status'] == 'pending'])
        top_shipping = filtered_orders['shipping_method'].mode().iloc[0] if len(filtered_orders) > 0 else 'N/A'
        
        st.info(f"""
        **{get_string('orders_summary_shipping', st.session_state.language)}**
        - {get_string('orders_summary_avg_delivery', st.session_state.language, days=avg_delivery_time)}
        - {get_string('orders_summary_pending', st.session_state.language, count=pending_orders)}
        - {get_string('orders_summary_delivery_rate', st.session_state.language, rate=delivery_rate)}
        - {get_string('orders_summary_top_shipping', st.session_state.language, method=top_shipping)}
        """)
    
    with col2:
        # Análisis de países
        country_stats = filtered_orders.groupby('country').agg({
            'id': 'count',
            'total_amount': 'sum'
        }).sort_values('total_amount', ascending=False)
        
        top_country = country_stats.index[0] if len(country_stats) > 0 else "N/A"
        top_country_revenue = country_stats.iloc[0]['total_amount'] if len(country_stats) > 0 else 0
        international_orders = len(filtered_orders[filtered_orders['country'] != 'Spain'])
        
        st.success(f"""
        **{get_string('orders_summary_geographic', st.session_state.language)}**
        - {get_string('orders_summary_top_country', st.session_state.language, country=top_country)}
        - {get_string('orders_summary_top_revenue', st.session_state.language, revenue=top_country_revenue)}
        - {get_string('orders_summary_unique_countries', st.session_state.language, count=filtered_orders['country'].nunique())}
        - {get_string('orders_summary_international', st.session_state.language, count=international_orders)}
        """)

if __name__ == "__main__":
    main()
