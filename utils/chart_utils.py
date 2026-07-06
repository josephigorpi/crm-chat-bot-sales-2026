"""
Utilidades para crear gráficos con Plotly
Funciones auxiliares para visualizaciones del dashboard
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Paleta de colores moderna
COLORS = {
    'primary': '#3B82F6',      # Azul
    'secondary': '#10B981',    # Verde
    'accent': '#F59E0B',       # Amarillo
    'danger': '#EF4444',       # Rojo
    'warning': '#F97316',      # Naranja
    'info': '#06B6D4',         # Cian
    'success': '#22C55E',      # Verde claro
    'purple': '#8B5CF6',       # Púrpura
    'pink': '#EC4899',         # Rosa
    'gray': '#6B7280'          # Gris
}

CHART_TEMPLATE = "plotly_white"

def create_metric_card_chart(value, title, delta=None, delta_color="normal"):
    """Crea un gráfico simple para cards de métricas"""
    fig = go.Figure()
    
    # Añadir el valor principal
    fig.add_trace(go.Indicator(
        mode = "number+delta" if delta else "number",
        value = value,
        delta = {'reference': delta, 'relative': True} if delta else None,
        title = {"text": title},
        number = {'font': {'size': 40}},
        domain = {'x': [0, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(
        height=150,
        margin=dict(l=20, r=20, t=40, b=20),
        template=CHART_TEMPLATE
    )
    
    return fig

def create_conversation_heatmap(conversations_df):
    """Crea mapa de calor de conversaciones por día y hora"""
    if len(conversations_df) == 0:
        # Crear gráfico vacío si no hay datos
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de conversaciones disponibles",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title='Mapa de Calor: Conversaciones por Día y Hora',
            height=400,
            template=CHART_TEMPLATE
        )
        return fig
    
    # Convertir created_at a datetime si no lo está
    conversations_df = conversations_df.copy()
    conversations_df['created_at'] = pd.to_datetime(conversations_df['created_at'])
    conversations_df['hour'] = conversations_df['created_at'].dt.hour
    conversations_df['day_name'] = conversations_df['created_at'].dt.day_name()
    
    # Crear matriz de conversaciones
    heatmap_data = conversations_df.groupby(['day_name', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='day_name', columns='hour', values='count').fillna(0)
    
    # Ordenar días de la semana
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_order_es = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    # Mapear nombres de días al español
    day_mapping = dict(zip(day_order, day_order_es))
    heatmap_pivot.index = heatmap_pivot.index.map(day_mapping)
    heatmap_pivot = heatmap_pivot.reindex(day_order_es)
    
    fig = px.imshow(
        heatmap_pivot,
        title='Mapa de Calor: Conversaciones por Día y Hora',
        color_continuous_scale='Blues',
        aspect='auto',
        labels={'x': 'Hora del Día', 'y': 'Día de la Semana', 'color': 'Número de Conversaciones'}
    )
    
    fig.update_layout(
        height=400,
        template=CHART_TEMPLATE,
        xaxis_title="Hora del Día",
        yaxis_title="Día de la Semana"
    )
    
    return fig

def create_sales_timeline(orders_df):
    """Crea gráfico de línea temporal de ventas"""
    # Agrupar ventas por día
    orders_df['date'] = pd.to_datetime(orders_df['created_at']).dt.date
    daily_sales = orders_df.groupby('date')['total_amount'].sum().reset_index()
    
    fig = px.line(
        daily_sales, 
        x='date', 
        y='total_amount',
        title='Ventas Diarias (Últimos 30 días)',
        color_discrete_sequence=[COLORS['primary']]
    )
    
    fig.update_traces(
        line=dict(width=3),
        hovertemplate='<b>%{x}</b><br>Ventas: USD %{y:,.2f}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=CHART_TEMPLATE,
        xaxis_title="Fecha",
        yaxis_title="Ventas (USD)",
        hovermode='x unified'
    )
    
    return fig

def create_order_status_donut(orders_df):
    """Crea gráfico de dona con distribución de estados de pedidos"""
    status_counts = orders_df['status'].value_counts()
    
    # Mapear estados a español
    status_labels = {
        'pending': 'Pendiente',
        'processing': 'Procesando',
        'shipped': 'Enviado',
        'delivered': 'Entregado',
        'cancelled': 'Cancelado'
    }
    
    labels = [status_labels.get(status, status) for status in status_counts.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=status_counts.values,
        hole=.4,
        marker_colors=[COLORS['warning'], COLORS['info'], COLORS['accent'], 
                      COLORS['success'], COLORS['danger']]
    )])
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        title="Distribución de Estados de Pedidos",
        height=400,
        template=CHART_TEMPLATE,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
    )
    
    return fig

def create_messages_by_hour(conversations_df):
    """Crea gráfico de barras de mensajes por hora del día"""
    conversations_df['hour'] = pd.to_datetime(conversations_df['created_at']).dt.hour
    hourly_messages = conversations_df.groupby('hour').size().reset_index(name='count')
    
    # Asegurar que tenemos todas las horas (0-23)
    all_hours = pd.DataFrame({'hour': range(24)})
    hourly_messages = all_hours.merge(hourly_messages, on='hour', how='left').fillna(0)
    
    fig = px.bar(
        hourly_messages,
        x='hour',
        y='count',
        title='Mensajes por Hora del Día',
        color_discrete_sequence=[COLORS['secondary']]
    )
    
    fig.update_traces(
        hovertemplate='<b>Hora: %{x}:00</b><br>Mensajes: %{y}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=CHART_TEMPLATE,
        xaxis_title="Hora del Día",
        yaxis_title="Número de Mensajes",
        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
    )
    
    return fig

def create_intent_distribution(conversations_df):
    """Crea gráfico de barras horizontales de intenciones"""
    intent_counts = conversations_df['intent'].value_counts()
    
    # Mapear intents a español
    intent_labels = {
        'consulta-producto': 'Consulta Producto',
        'seguimiento-pedido': 'Seguimiento Pedido',
        'procesar-pago': 'Procesar Pago',
        'carrito-abandonado': 'Carrito Abandonado'
    }
    
    labels = [intent_labels.get(intent, intent) for intent in intent_counts.index]
    
    fig = px.bar(
        x=intent_counts.values,
        y=labels,
        orientation='h',
        title='Intenciones Más Comunes',
        color_discrete_sequence=[COLORS['purple']]
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Cantidad: %{x}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=CHART_TEMPLATE,
        xaxis_title="Número de Conversaciones",
        yaxis_title="Intención"
    )
    
    return fig

def create_top_products_chart(products_df, orders_df):
    """Crea gráfico de top 10 productos más vendidos"""
    # Simular ventas por producto (en datos reales vendría de order_items)
    product_sales = products_df.copy()
    product_sales['sales_count'] = np.random.randint(0, 50, len(products_df))
    
    top_products = product_sales.nlargest(10, 'sales_count')
    
    fig = px.bar(
        top_products,
        x='sales_count',
        y='name',
        orientation='h',
        title='Top 10 Productos Más Vendidos',
        color='sales_count',
        color_continuous_scale='Blues'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Ventas: %{x}<extra></extra>'
    )
    
    fig.update_layout(
        height=500,
        template=CHART_TEMPLATE,
        xaxis_title="Número de Ventas",
        yaxis_title="Producto",
        coloraxis_showscale=False
    )
    
    return fig

def create_price_distribution(products_df):
    """Crea histograma de distribución de precios"""
    fig = px.histogram(
        products_df,
        x='price',
        nbins=20,
        title='Distribución de Precios de Productos',
        color_discrete_sequence=[COLORS['accent']]
    )
    
    fig.update_traces(
        hovertemplate='<b>Rango: USD %{x}</b><br>Productos: %{y}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=CHART_TEMPLATE,
        xaxis_title="Precio (USD)",
        yaxis_title="Número de Productos"
    )
    
    return fig

def create_category_donut(products_df):
    """Crea gráfico de dona de productos por categoría"""
    category_counts = products_df['category'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=category_counts.index.str.title(),
        values=category_counts.values,
        hole=.4,
        marker_colors=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], 
                      COLORS['purple'], COLORS['pink']]
    )])
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Productos: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        title="Productos por Categoría",
        height=400,
        template=CHART_TEMPLATE,
        showlegend=True
    )
    
    return fig

def create_customer_segments_chart(customers_df, orders_df):
    """Crea gráfico de segmentación de clientes por valor de compra"""
    # Calcular valor total por cliente
    customer_values = orders_df.groupby('customer_id')['total_amount'].sum().reset_index()
    
    # Crear segmentos
    def categorize_customer(value):
        if value >= 500:
            return 'Premium (USD 500+)'
        elif value >= 200:
            return 'Medio (USD 200-499)'
        elif value >= 50:
            return 'Básico (USD 50-199)'
        else:
            return 'Nuevo (< USD 50)'
    
    customer_values['segment'] = customer_values['total_amount'].apply(categorize_customer)
    segment_counts = customer_values['segment'].value_counts()
    
    fig = px.bar(
        x=segment_counts.index,
        y=segment_counts.values,
        title='Segmentación de Clientes por Valor de Compra',
        color=segment_counts.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Clientes: %{y}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=CHART_TEMPLATE,
        xaxis_title="Segmento",
        yaxis_title="Número de Clientes",
        coloraxis_showscale=False
    )
    
    return fig

def create_conversion_funnel(carts_df):
    """Crea embudo de conversión para carritos"""
    total_carts = len(carts_df)
    abandoned_carts = len(carts_df[carts_df['status'] == 'abandoned'])
    completed_carts = len(carts_df[carts_df['status'] == 'completed'])
    
    stages = ['Carritos Creados', 'Carritos Completados']
    values = [total_carts, completed_carts]
    
    fig = go.Figure(go.Funnel(
        y = stages,
        x = values,
        textinfo = "value+percent initial",
        marker_color = [COLORS['info'], COLORS['success']]
    ))
    
    fig.update_layout(
        title="Embudo de Conversión",
        height=400,
        template=CHART_TEMPLATE
    )
    
    return fig

def create_customer_conversion_funnel(conversion_data):
    """Crea embudo de conversión para clientes"""
    stages = list(conversion_data.keys())
    values = list(conversion_data.values())
    
    # Verificar si todos los valores son 0 para evitar RangeError
    if all(v == 0 for v in values):
        # Crear un gráfico vacío con mensaje
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos disponibles para mostrar el embudo de conversión",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title="Embudo de Conversión de Clientes",
            height=400,
            template=CHART_TEMPLATE,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Asegurar que hay al menos un valor positivo para evitar problemas de rango
    min_value = max(1, min(v for v in values if v > 0)) if any(v > 0 for v in values) else 1
    adjusted_values = [max(v, min_value) if v == 0 else v for v in values]
    
    fig = go.Figure(go.Funnel(
        y = stages,
        x = adjusted_values,
        textinfo = "value+percent initial",
        marker_color = [COLORS['info'], COLORS['primary'], COLORS['secondary'], COLORS['purple'], COLORS['accent']][:len(stages)]
    ))
    
    fig.update_layout(
        title="Embudo de Conversión de Clientes",
        height=400,
        template=CHART_TEMPLATE
    )
    
    return fig

def create_heatmap_conversations(conversations_df):
    """Crea mapa de calor de conversaciones por día y hora"""
    conversations_df['hour'] = pd.to_datetime(conversations_df['created_at']).dt.hour
    conversations_df['day_name'] = pd.to_datetime(conversations_df['created_at']).dt.day_name()
    
    # Crear matriz de conversaciones
    heatmap_data = conversations_df.groupby(['day_name', 'hour']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='day_name', columns='hour', values='count').fillna(0)
    
    # Ordenar días de la semana
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(day_order)
    
    fig = px.imshow(
        heatmap_pivot,
        title='Mapa de Calor: Conversaciones por Día y Hora',
        color_continuous_scale='Blues',
        aspect='auto'
    )
    
    fig.update_layout(
        height=400,
        template=CHART_TEMPLATE,
        xaxis_title="Hora del Día",
        yaxis_title="Día de la Semana"
    )
    
    return fig

def create_delivery_time_chart(shipments_df):
    """Crea gráfico de tiempo promedio de entrega por transportista"""
    # Calcular tiempo de entrega para envíos completados
    delivered_shipments = shipments_df[shipments_df['status'] == 'delivered'].copy()
    
    if len(delivered_shipments) > 0:
        delivered_shipments['delivery_days'] = (
            pd.to_datetime(delivered_shipments['actual_delivery']) - 
            pd.to_datetime(delivered_shipments['estimated_delivery'])
        ).dt.days
        
        avg_delivery = delivered_shipments.groupby('carrier')['delivery_days'].mean().reset_index()
        
        fig = px.bar(
            avg_delivery,
            x='carrier',
            y='delivery_days',
            title='Tiempo Promedio de Entrega por Transportista',
            color='delivery_days',
            color_continuous_scale='RdYlGn_r'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Días promedio: %{y:.1f}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            template=CHART_TEMPLATE,
            xaxis_title="Transportista",
            yaxis_title="Días de Diferencia",
            coloraxis_showscale=False
        )
    else:
        # Gráfico vacío si no hay datos
        fig = go.Figure()
        fig.add_annotation(
            text="No hay datos de entregas completadas",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        fig.update_layout(height=400, template=CHART_TEMPLATE)
    
    return fig