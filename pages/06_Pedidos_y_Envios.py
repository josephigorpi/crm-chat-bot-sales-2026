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
        st.error(f"Error al cargar datos: {str(e)}")
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
    enriched_orders['shipping_method'] = enriched_orders['carrier'].fillna('Sin asignar')
    
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

def create_order_status_timeline():
    """Crea timeline de estados de pedidos"""
    # Simular datos de timeline
    timeline_data = []
    statuses = ['pending', 'processing', 'shipped', 'delivered']
    
    for i, status in enumerate(statuses):
        timeline_data.append({
            'step': i + 1,
            'status': status.title(),
            'description': {
                'pending': 'Pedido recibido y confirmado',
                'processing': 'Preparando el pedido',
                'shipped': 'Pedido enviado',
                'delivered': 'Pedido entregado'
            }[status],
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
        hovertemplate='<b>%{y}</b><br>Día promedio: %{x}<br>%{text}<extra></extra>',
        text=timeline_df['description']
    ))
    
    fig.update_layout(
        title='Timeline Promedio de Estados de Pedido',
        xaxis_title='Días desde el Pedido',
        yaxis_title='Estado del Pedido',
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
        name='Número de Pedidos',
        x=shipping_stats['shipping_method'],
        y=shipping_stats['order_count'],
        marker_color='#3b82f6',
        yaxis='y',
        hovertemplate='<b>%{x}</b><br>Pedidos: %{y}<extra></extra>'
    ))
    
    # Línea para tiempo promedio de entrega
    fig.add_trace(go.Scatter(
        name='Tiempo Promedio (días)',
        x=shipping_stats['shipping_method'],
        y=shipping_stats['avg_delivery_days'],
        mode='lines+markers',
        line=dict(color='#ef4444'),
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Días promedio: %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Rendimiento por Método de Envío',
        xaxis_title='Método de Envío',
        yaxis=dict(title='Número de Pedidos', side='left'),
        yaxis2=dict(title='Días Promedio de Entrega', side='right', overlaying='y'),
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
        ('pending', 'Pedido Confirmado', 'Hemos recibido tu pedido'),
        ('processing', 'Preparando Pedido', 'Empaquetando tus productos'),
        ('shipped', 'Enviado', 'Tu pedido está en camino'),
        ('delivered', 'Entregado', 'Pedido entregado exitosamente')
    ]
    
    st.markdown("**📍 Seguimiento del Pedido:**")
    
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
    if pd.notna(order_row['tracking_number']):
        st.markdown(f"""
        <div class="shipment-info">
            <strong>📦 Información de Envío:</strong><br>
            • Número de seguimiento: {order_row['tracking_number']}<br>
            • Transportista: {order_row['carrier']}<br>
            • Método: {order_row['shipping_method']}<br>
            • Fecha estimada: {order_row['estimated_delivery'].strftime('%d/%m/%Y') if pd.notna(order_row['estimated_delivery']) else 'No disponible'}
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
    st.markdown("### 🔍 Filtros de Pedidos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        statuses = ['Todos'] + list(enriched_orders['status'].unique())
        selected_status = st.selectbox("Estado del Pedido", statuses)
    
    with col2:
        shipping_methods = ['Todos'] + list(enriched_orders['shipping_method'].unique())
        selected_shipping = st.selectbox("Método de Envío", shipping_methods)
    
    with col3:
        countries = ['Todos'] + list(enriched_orders['country'].unique())
        selected_country = st.selectbox("País", countries)
    
    with col4:
        date_range = st.date_input(
            "Rango de Fechas",
            value=(
                enriched_orders['order_date'].min().date(),
                enriched_orders['order_date'].max().date()
            ),
            min_value=enriched_orders['order_date'].min().date(),
            max_value=enriched_orders['order_date'].max().date()
        )
    
    # Aplicar filtros
    filtered_orders = enriched_orders.copy()
    
    if selected_status != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['status'] == selected_status]
    
    if selected_shipping != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['shipping_method'] == selected_shipping]
    
    if selected_country != 'Todos':
        filtered_orders = filtered_orders[filtered_orders['country'] == selected_country]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_orders = filtered_orders[
            (filtered_orders['order_date'].dt.date >= start_date) &
            (filtered_orders['order_date'].dt.date <= end_date)
        ]
    
    # Métricas principales
    st.markdown("### 📊 Métricas de Pedidos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>{:,}</h3>
            <p>Total Pedidos</p>
        </div>
        """.format(len(filtered_orders)), unsafe_allow_html=True)
    
    with col2:
        total_revenue = filtered_orders['total_amount'].sum()
        st.markdown("""
        <div class="metric-card">
            <h3>€{:,.2f}</h3>
            <p>Revenue Total</p>
        </div>
        """.format(total_revenue), unsafe_allow_html=True)
    
    with col3:
        avg_order_value = filtered_orders['total_amount'].mean()
        st.markdown("""
        <div class="metric-card">
            <h3>€{:.2f}</h3>
            <p>Valor Promedio</p>
        </div>
        """.format(avg_order_value), unsafe_allow_html=True)
    
    with col4:
        delivered_orders = len(filtered_orders[filtered_orders['status'] == 'delivered'])
        delivery_rate = (delivered_orders / len(filtered_orders)) * 100 if len(filtered_orders) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h3>{:.1f}%</h3>
            <p>Tasa de Entrega</p>
        </div>
        """.format(delivery_rate), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizaciones principales
    st.markdown("### 📈 Análisis de Pedidos y Envíos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución por estado
        status_counts = filtered_orders['status'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=[f"{get_status_emoji(status)} {status.title()}" for status in status_counts.index],
            title="Distribución por Estado de Pedido",
            color_discrete_sequence=[get_status_color(status) for status in status_counts.index]
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>%{value} pedidos (%{percent})<extra></extra>'
        )
        
        fig.update_layout(template="plotly_white", height=400)
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
        delivery_chart = create_delivery_time_chart(filtered_orders)
        st.plotly_chart(delivery_chart, use_container_width=True)
    
    st.markdown("---")
    
    # Análisis temporal
    st.markdown("### 📊 Tendencias Temporales")
    
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
        name='Número de Pedidos',
        line=dict(color='#3b82f6'),
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_orders['date'],
        y=daily_orders['daily_revenue'],
        mode='lines+markers',
        name='Revenue Diario (€)',
        line=dict(color='#10b981'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Tendencia de Pedidos y Revenue',
        xaxis_title='Fecha',
        yaxis=dict(title='Número de Pedidos', side='left'),
        yaxis2=dict(title='Revenue Diario (€)', side='right', overlaying='y'),
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Pedidos recientes con seguimiento
    st.markdown("### 🔍 Pedidos Recientes con Seguimiento")
    
    recent_orders = filtered_orders.nlargest(10, 'order_date')
    
    for _, order in recent_orders.iterrows():
        status_class = f"status-{order['status']}"
        
        with st.expander(f"{get_status_emoji(order['status'])} Pedido #{order['id']} - {order['first_name']} {order['last_name']} - €{order['total_amount']:.2f}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="order-card {status_class}">
                    <h4>📋 Detalles del Pedido</h4>
                    <p><strong>👤 Cliente:</strong> {order['first_name']} {order['last_name']}</p>
                    <p><strong>📧 Email:</strong> {order['email']}</p>
                    <p><strong>🌍 País:</strong> {order['country']}</p>
                    <p><strong>💰 Total:</strong> €{order['total_amount']:.2f}</p>
                    <p><strong>💳 Método de Pago:</strong> {order['metodo_pago'] if 'metodo_pago' in order else 'No disponible'}</p>
                    <p><strong>💵 Estado de Pago:</strong> {order['estado_pago'] if 'estado_pago' in order else 'No disponible'}</p>
                    <p><strong>📅 Fecha:</strong> {order['order_date'].strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>🚚 Método de Envío:</strong> {order['shipping_method']}</p>
                    <p><strong>📊 Estado:</strong> {get_status_emoji(order['status'])} {order['status'].title()}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                display_order_tracking(order)
                
                # Acciones rápidas
                st.markdown("**⚡ Acciones Rápidas:**")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"📧 Notificar Cliente", key=f"notify_{order['id']}"):
                        st.success("Notificación enviada!")
                
                with col_b:
                    if st.button(f"📋 Ver Detalles", key=f"details_{order['id']}"):
                        st.info("Redirigiendo a detalles...")
    
    st.markdown("---")
    
    # Tabla completa de pedidos
    st.markdown("### 📋 Lista Completa de Pedidos")
    
    # Opciones de ordenamiento
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Mostrando {len(filtered_orders)} pedidos**")
    
    with col2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["order_date", "total_amount", "status", "customer_id"],
            format_func=lambda x: {
                "order_date": "Fecha",
                "total_amount": "Monto Total",
                "status": "Estado",
                "customer_id": "Cliente"
            }[x]
        )
    
    with col3:
        sort_order = st.selectbox("Orden:", ["Descendente", "Ascendente"])
    
    # Aplicar ordenamiento
    ascending = sort_order == "Ascendente"
    sorted_orders = filtered_orders.sort_values(sort_by, ascending=ascending)
    
    # Preparar datos para mostrar
    display_orders = sorted_orders.copy()
    display_orders['ID'] = display_orders['id']
    display_orders['Cliente'] = display_orders['first_name'] + ' ' + display_orders['last_name']
    display_orders['Email'] = display_orders['email']
    display_orders['País'] = display_orders['country']
    display_orders['Total'] = display_orders['total_amount'].apply(lambda x: f"€{x:.2f}")
    display_orders['Método Pago'] = display_orders['metodo_pago'] if 'metodo_pago' in display_orders else 'No disponible'
    display_orders['Estado Pago'] = display_orders['estado_pago'] if 'estado_pago' in display_orders else 'No disponible'
    display_orders['Estado'] = display_orders['status'].apply(lambda x: f"{get_status_emoji(x)} {x.title()}")
    display_orders['Fecha'] = display_orders['order_date'].dt.strftime('%d/%m/%Y')
    display_orders['Envío'] = display_orders['shipping_method']
    
    # Mostrar tabla
    st.dataframe(
        display_orders[['ID', 'Cliente', 'Email', 'País', 'Total', 'Método Pago', 'Estado Pago', 'Estado', 'Fecha', 'Envío']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Cliente": st.column_config.TextColumn("Cliente", width="medium"),
            "Email": st.column_config.TextColumn("Email", width="large"),
            "País": st.column_config.TextColumn("País", width="small"),
            "Total": st.column_config.TextColumn("Total", width="small"),
            "Método Pago": st.column_config.TextColumn("Método Pago", width="medium"),
            "Estado Pago": st.column_config.TextColumn("Estado Pago", width="medium"),
            "Estado": st.column_config.TextColumn("Estado", width="medium"),
            "Fecha": st.column_config.TextColumn("Fecha", width="small"),
            "Envío": st.column_config.TextColumn("Método de Envío", width="medium")
        }
    )
    
    # Resumen y estadísticas
    st.markdown("### 📊 Resumen Ejecutivo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Estadísticas de rendimiento
        avg_delivery_time = filtered_orders['delivery_time_days'].mean()
        pending_orders = len(filtered_orders[filtered_orders['status'] == 'pending'])
        
        st.info(f"""
        **⚡ Rendimiento de Envíos:**
        - Tiempo promedio de entrega: {avg_delivery_time:.1f} días
        - Pedidos pendientes: {pending_orders}
        - Tasa de entrega exitosa: {delivery_rate:.1f}%
        - Método de envío más usado: {filtered_orders['shipping_method'].mode().iloc[0] if len(filtered_orders) > 0 else 'N/A'}
        """)
    
    with col2:
        # Análisis de países
        country_stats = filtered_orders.groupby('country').agg({
            'id': 'count',
            'total_amount': 'sum'
        }).sort_values('total_amount', ascending=False)
        
        top_country = country_stats.index[0] if len(country_stats) > 0 else "N/A"
        top_country_revenue = country_stats.iloc[0]['total_amount'] if len(country_stats) > 0 else 0
        
        st.success(f"""
        **🌍 Análisis Geográfico:**
        - País con más pedidos: {top_country}
        - Revenue del país top: €{top_country_revenue:.2f}
        - Países únicos: {filtered_orders['country'].nunique()}
        - Pedidos internacionales: {len(filtered_orders[filtered_orders['country'] != 'Spain'])}
        """)

if __name__ == "__main__":
    main()
