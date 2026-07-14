"""
Utilidades para crear gráficos con Plotly
Funciones auxiliares para visualizaciones del dashboard con soporte para tema e idioma
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from i18n.strings import get_string

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

def create_metric_card_chart(value, title, delta=None, delta_color="normal", template="plotly_white"):
    """
    Crea un gráfico simple para cards de métricas.
    
    Args:
        value: Valor a mostrar
        title: Título de la métrica
        delta: Valor delta (opcional)
        delta_color: Color del delta
        template: Template de Plotly (plotly_white o plotly_dark)
    
    Returns:
        Figure de Plotly
    """
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
        template=template
    )
    
    return fig

def create_conversation_heatmap(conversations_df, language='es', template="plotly_white"):
    """
    Crea mapa de calor de conversaciones por día y hora.
    
    Args:
        conversations_df: DataFrame con conversaciones
        language: Idioma para labels ('es' o 'en')
        template: Template de Plotly
    
    Returns:
        Figure de Plotly
    """
    if len(conversations_df) == 0:
        # Crear gráfico vacío si no hay datos
        fig = go.Figure()
        fig.add_annotation(
            text=get_string('chart_heatmap_no_data', language),
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font=dict(size=16)
        )
        fig.update_layout(
            title=get_string('chart_heatmap', language),
            height=400,
            template=template
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
    day_order_en = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Mapear nombres de días según idioma
    day_labels = day_order_es if language == 'es' else day_order_en
    day_mapping = dict(zip(day_order, day_labels))
    heatmap_pivot.index = heatmap_pivot.index.map(day_mapping)
    heatmap_pivot = heatmap_pivot.reindex(day_labels)
    
    fig = px.imshow(
        heatmap_pivot,
        title=get_string('chart_heatmap', language),
        color_continuous_scale='Blues',
        aspect='auto',
        labels={
            'x': get_string('chart_heatmap_hour', language),
            'y': get_string('chart_heatmap_day', language),
            'color': get_string('chart_heatmap_conversations', language)
        }
    )
    
    fig.update_layout(
        height=400,
        template=template,
        xaxis_title=get_string('chart_heatmap_hour', language),
        yaxis_title=get_string('chart_heatmap_day', language)
    )
    
    return fig

def create_sales_timeline(orders_df, template="plotly_white", language='es'):
    """
    Crea gráfico de línea temporal de ventas.
    
    Args:
        orders_df: DataFrame con órdenes
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    # Agrupar ventas por día
    orders_df = orders_df.copy()
    orders_df['date'] = pd.to_datetime(orders_df['created_at']).dt.date
    daily_sales = orders_df.groupby('date')['total_amount'].sum().reset_index()
    
    fig = px.line(
        daily_sales, 
        x='date', 
        y='total_amount',
        title=get_string('chart_sales_timeline', language),
        color_discrete_sequence=[COLORS['primary']]
    )
    
    fig.update_traces(
        line=dict(width=3),
        hovertemplate='<b>%{x}</b><br>' + get_string('chart_sales_amount', language) + ': USD %{y:,.2f}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=template,
        xaxis_title=get_string('chart_sales_date', language),
        yaxis_title=get_string('chart_sales_amount', language),
        hovermode='x unified'
    )
    
    return fig

def create_order_status_donut(orders_df, template="plotly_white", language='es'):
    """
    Crea gráfico de dona con distribución de estados de pedidos.
    
    Args:
        orders_df: DataFrame con órdenes
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    status_counts = orders_df['status'].value_counts()
    
    # Mapear estados según idioma
    if language == 'es':
        status_labels = {
            'pending': get_string('order_status_pending', language),
            'processing': get_string('order_status_processing', language),
            'shipped': get_string('order_status_shipped', language),
            'delivered': get_string('order_status_delivered', language),
            'cancelled': get_string('order_status_cancelled', language),
        }
    else:
        status_labels = {
            'pending': get_string('order_status_pending', language),
            'processing': get_string('order_status_processing', language),
            'shipped': get_string('order_status_shipped', language),
            'delivered': get_string('order_status_delivered', language),
            'cancelled': get_string('order_status_cancelled', language),
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
        hovertemplate='<b>%{label}</b><br>' + get_string('chart_intents_conversations', language) + ': %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        title=get_string('chart_order_status', language),
        height=400,
        template=template,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
    )
    
    return fig

def create_messages_by_hour(conversations_df, template="plotly_white", language='es'):
    """
    Crea gráfico de barras de mensajes por hora del día.
    
    Args:
        conversations_df: DataFrame con conversaciones
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    conversations_df = conversations_df.copy()
    conversations_df['hour'] = pd.to_datetime(conversations_df['created_at']).dt.hour
    hourly_messages = conversations_df.groupby('hour').size().reset_index(name='count')
    
    # Asegurar que tenemos todas las horas (0-23)
    all_hours = pd.DataFrame({'hour': range(24)})
    hourly_messages = all_hours.merge(hourly_messages, on='hour', how='left').fillna(0)
    
    fig = px.bar(
        hourly_messages,
        x='hour',
        y='count',
        title=get_string('chart_messages_by_hour', language),
        color_discrete_sequence=[COLORS['secondary']]
    )
    
    fig.update_traces(
        hovertemplate='<b>' + get_string('chart_messages_hour', language) + ': %{x}:00</b><br>' + 
                      get_string('chart_messages_count', language) + ': %{y}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=template,
        xaxis_title=get_string('chart_messages_hour', language),
        yaxis_title=get_string('chart_messages_count', language),
        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
    )
    
    return fig

def create_intent_distribution(conversations_df, template="plotly_white", language='es'):
    """
    Crea gráfico de barras horizontales de intenciones.
    
    Args:
        conversations_df: DataFrame con conversaciones
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    intent_counts = conversations_df['intent'].value_counts()
    
    # Mapear intents según idioma
    if language == 'es':
        intent_labels = {
            'consulta-producto': 'Consulta Producto',
            'seguimiento-pedido': 'Seguimiento Pedido',
            'procesar-pago': 'Procesar Pago',
            'carrito-abandonado': 'Carrito Abandonado'
        }
    else:
        intent_labels = {
            'consulta-producto': 'Product Inquiry',
            'seguimiento-pedido': 'Order Tracking',
            'procesar-pago': 'Process Payment',
            'carrito-abandonado': 'Abandoned Cart'
        }
    
    labels = [intent_labels.get(intent, intent) for intent in intent_counts.index]
    
    fig = px.bar(
        x=intent_counts.values,
        y=labels,
        orientation='h',
        title=get_string('chart_intents', language),
        color_discrete_sequence=[COLORS['purple']]
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>' + get_string('chart_intents_conversations', language) + ': %{x}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=template,
        xaxis_title=get_string('chart_intents_conversations', language),
        yaxis_title=get_string('chart_intents_intent', language)
    )
    
    return fig

def create_top_products_chart(products_df, orders_df, template="plotly_white", language='es'):
    """
    Crea gráfico de top 10 productos más vendidos.
    
    Args:
        products_df: DataFrame con productos
        orders_df: DataFrame con órdenes
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    # Simular ventas por producto (en datos reales vendría de order_items)
    product_sales = products_df.copy()
    product_sales['sales_count'] = np.random.randint(0, 50, len(products_df))
    
    top_products = product_sales.nlargest(10, 'sales_count')
    
    fig = px.bar(
        top_products,
        x='sales_count',
        y='name',
        orientation='h',
        title=get_string('chart_top_products', language),
        color='sales_count',
        color_continuous_scale='Blues'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>' + get_string('chart_top_products_sales', language) + ': %{x}<extra></extra>'
    )
    
    fig.update_layout(
        height=500,
        template=template,
        xaxis_title=get_string('chart_top_products_sales', language),
        yaxis_title=get_string('chart_top_products_product', language),
        coloraxis_showscale=False
    )
    
    return fig

def create_price_distribution(products_df, template="plotly_white", language='es'):
    """
    Crea histograma de distribución de precios.
    
    Args:
        products_df: DataFrame con productos
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    fig = px.histogram(
        products_df,
        x='price',
        nbins=20,
        title=get_string('chart_price_distribution', language),
        color_discrete_sequence=[COLORS['accent']]
    )
    
    fig.update_traces(
        hovertemplate='<b>' + get_string('chart_price_range', language) + ' %{x}</b><br>' + 
                      get_string('chart_price_products', language) + ' %{y}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=template,
        xaxis_title=get_string('chart_price_x', language),
        yaxis_title=get_string('chart_price_y', language)
    )
    
    return fig

def create_category_donut(products_df, template="plotly_white", language='es'):
    """
    Crea gráfico de dona de productos por categoría.
    
    Args:
        products_df: DataFrame con productos
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
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
        hovertemplate='<b>%{label}</b><br>' + get_string('chart_category_products', language) + ': %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        title=get_string('chart_category_donut', language),
        height=400,
        template=template,
        showlegend=True
    )
    
    return fig

def create_customer_segments_chart(customers_df, orders_df, template="plotly_white", language='es'):
    """
    Crea gráfico de segmentación de clientes por valor de compra.
    
    Args:
        customers_df: DataFrame con clientes
        orders_df: DataFrame con órdenes
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    # Calcular valor total por cliente
    customer_values = orders_df.groupby('customer_id')['total_amount'].sum().reset_index()
    
    # Crear segmentos
    def categorize_customer(value, lang='es'):
        if value >= 500:
            return get_string('chart_customer_segment_premium', lang)
        elif value >= 200:
            return get_string('chart_customer_segment_medium', lang)
        elif value >= 50:
            return get_string('chart_customer_segment_basic', lang)
        else:
            return get_string('chart_customer_segment_new', lang)
    
    customer_values['segment'] = customer_values['total_amount'].apply(
        lambda x: categorize_customer(x, language)
    )
    segment_counts = customer_values['segment'].value_counts()
    
    fig = px.bar(
        x=segment_counts.index,
        y=segment_counts.values,
        title=get_string('chart_customer_segments', language),
        color=segment_counts.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>' + get_string('chart_customer_segments_y', language) + ': %{y}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template=template,
        xaxis_title=get_string('chart_customer_segments_x', language),
        yaxis_title=get_string('chart_customer_segments_y', language),
        coloraxis_showscale=False
    )
    
    return fig

def create_conversion_funnel(carts_df, template="plotly_white", language='es'):
    """
    Crea embudo de conversión para carritos.
    
    Args:
        carts_df: DataFrame con carritos
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    total_carts = len(carts_df)
    abandoned_carts = len(carts_df[carts_df['status'] == 'abandoned'])
    completed_carts = len(carts_df[carts_df['status'] == 'completed'])
    
    if language == 'es':
        stages = [get_string('chart_conversion_carts_created', language), 
                  get_string('chart_conversion_carts_completed', language)]
    else:
        stages = [get_string('chart_conversion_carts_created', language),
                  get_string('chart_conversion_carts_completed', language)]
    
    values = [total_carts, completed_carts]
    
    fig = go.Figure(go.Funnel(
        y = stages,
        x = values,
        textinfo = "value+percent initial",
        marker_color = [COLORS['info'], COLORS['success']]
    ))
    
    fig.update_layout(
        title=get_string('chart_conversion_funnel', language),
        height=400,
        template=template
    )
    
    return fig

def create_customer_conversion_funnel(conversion_data, template="plotly_white", language='es'):
    """
    Crea embudo de conversión para clientes.
    
    Args:
        conversion_data: Dict con datos de conversión
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    stages = list(conversion_data.keys())
    values = list(conversion_data.values())
    
    # Verificar si todos los valores son 0 para evitar RangeError
    if all(v == 0 for v in values):
        # Crear un gráfico vacío con mensaje
        fig = go.Figure()
        fig.add_annotation(
            text=get_string('chart_conversion_funnel_no_data', language),
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=get_string('chart_conversion_funnel_customer', language),
            height=400,
            template=template,
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
        title=get_string('chart_conversion_funnel_customer', language),
        height=400,
        template=template
    )
    
    return fig

def create_heatmap_conversations(conversations_df, template="plotly_white", language='es'):
    """
    Crea mapa de calor de conversaciones por día y hora.
    
    Args:
        conversations_df: DataFrame con conversaciones
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
    conversations_df = conversations_df.copy()
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
        title=get_string('chart_heatmap', language),
        color_continuous_scale='Blues',
        aspect='auto'
    )
    
    fig.update_layout(
        height=400,
        template=template,
        xaxis_title=get_string('chart_heatmap_hour', language),
        yaxis_title=get_string('chart_heatmap_day', language)
    )
    
    return fig

def create_delivery_time_chart(shipments_df, template="plotly_white", language='es'):
    """
    Crea gráfico de tiempo promedio de entrega por transportista.
    
    Args:
        shipments_df: DataFrame con envíos
        template: Template de Plotly
        language: Idioma para labels
    
    Returns:
        Figure de Plotly
    """
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
            title=get_string('chart_delivery_time', language),
            color='delivery_days',
            color_continuous_scale='RdYlGn_r'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>' + get_string('chart_delivery_time_days', language) + ': %{y:.1f}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            template=template,
            xaxis_title=get_string('chart_delivery_time_carrier', language),
            yaxis_title=get_string('chart_delivery_time_days', language),
            coloraxis_showscale=False
        )
    else:
        # Gráfico vacío si no hay datos
        fig = go.Figure()
        fig.add_annotation(
            text=get_string('chart_delivery_time_no_data', language),
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
        fig.update_layout(height=400, template=template)
    
    return fig
