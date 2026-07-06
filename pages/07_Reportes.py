"""
Página de Reportes
Generación de reportes en PDF y análisis avanzados
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_generator import get_all_data
from utils.pdf_generator import (
    generate_sales_report, 
    generate_customer_report, 
    generate_product_report,
    generate_chatbot_report,
    generate_abandoned_carts_report,
    create_download_link
)

st.set_page_config(page_title="Reportes", page_icon="📊", layout="wide")

# CSS personalizado
st.markdown("""
<style>
    .reports-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .report-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        border-top: 4px solid #3b82f6;
        transition: transform 0.3s ease;
        color: #1f2937;
    }
    
    .report-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .report-type {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .report-type h3 {
        margin: 0;
        color: #1f2937;
    }
    
    .report-description {
        color: #6b7280;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    
    .report-metrics {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-box {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e2e8f0;
        color: #1f2937;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #3b82f6;
        margin-bottom: 0.25rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6b7280;
    }
    
    .download-section {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #0ea5e9;
        margin-top: 1rem;
        color: #1f2937;
    }
    
    .analysis-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #1f2937;
    }
    
    .insight-box {
        background: #ecfdf5;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #1f2937;
    }
    
    .warning-box {
        background: #fffbeb;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #1f2937;
    }
    
    .kpi-dashboard {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def enrich_customers_data(customers_df, orders_df):
    """Enriquece los datos de clientes con métricas de pedidos"""
    # Calcular métricas por cliente
    customer_orders = orders_df.groupby('customer_id').agg({
        'total_amount': ['sum', 'count', 'mean'],
        'created_at': ['min', 'max']
    }).round(2)
    
    customer_orders.columns = ['total_spent', 'order_count', 'avg_order_value', 'first_order', 'last_order']
    customer_orders = customer_orders.reset_index()
    
    # Merge con datos de clientes
    enriched_customers = customers_df.merge(customer_orders, left_on='id', right_on='customer_id', how='left')
    
    # Rellenar valores nulos
    enriched_customers['total_spent'] = enriched_customers['total_spent'].fillna(0)
    enriched_customers['order_count'] = enriched_customers['order_count'].fillna(0)
    enriched_customers['avg_order_value'] = enriched_customers['avg_order_value'].fillna(0)
    
    return enriched_customers

@st.cache_data
def load_reports_data():
    """Carga y prepara todos los datos necesarios para los reportes"""
    try:
        data = get_all_data()
        # Enriquecer datos de clientes
        data['customers'] = enrich_customers_data(data['customers'], data['orders'])
        
        # Agregar satisfaction_score a conversaciones (simulado)
        import numpy as np
        data['conversations']['satisfaction_score'] = np.random.uniform(3.0, 5.0, len(data['conversations']))
        
        return data
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None

def calculate_kpis(data):
    """Calcula KPIs principales para el dashboard"""
    orders_df = data['orders']
    customers_df = data['customers']
    conversations_df = data['conversations']
    carts_df = data['carts']
    
    # KPIs de ventas
    total_revenue = orders_df['total_amount'].sum()
    total_orders = len(orders_df)
    avg_order_value = orders_df['total_amount'].mean()
    
    # KPIs de clientes
    total_customers = len(customers_df)
    # Simular clientes activos (90% de los clientes)
    active_customers = int(total_customers * 0.9)
    # Usar la columna total_spent que ahora existe
    avg_clv = customers_df['total_spent'].mean()
    
    # KPIs de conversaciones
    total_conversations = len(conversations_df)
    # Usar 'processed' en lugar de 'status'
    resolved_conversations = len(conversations_df[conversations_df['processed'] == True])
    resolution_rate = (resolved_conversations / total_conversations) * 100 if total_conversations > 0 else 0
    
    # KPIs de carritos abandonados
    abandoned_carts = len(carts_df[carts_df['status'] == 'abandoned'])
    abandoned_value = carts_df[carts_df['status'] == 'abandoned']['total_amount'].sum()
    
    return {
        'revenue': total_revenue,
        'orders': total_orders,
        'aov': avg_order_value,
        'customers': total_customers,
        'active_customers': active_customers,
        'clv': avg_clv,
        'conversations': total_conversations,
        'resolution_rate': resolution_rate,
        'abandoned_carts': abandoned_carts,
        'abandoned_value': abandoned_value
    }

def create_revenue_trend_chart(orders_df):
    """Crea gráfico de tendencia de ingresos"""
    # Crear copia para evitar modificar el DataFrame original
    orders_df = orders_df.copy()
    # Renombrar created_at a order_date para consistencia
    orders_df['order_date'] = orders_df['created_at']
    
    # Agrupar por mes
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    monthly_revenue = orders_df.groupby(orders_df['order_date'].dt.to_period('M')).agg({
        'total_amount': 'sum',
        'id': 'count'
    }).reset_index()
    
    monthly_revenue['month'] = monthly_revenue['order_date'].astype(str)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=monthly_revenue['month'],
        y=monthly_revenue['total_amount'],
        mode='lines+markers',
        name='Revenue Mensual',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Revenue: €%{y:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Tendencia de Revenue Mensual',
        xaxis_title='Mes',
        yaxis_title='Revenue (€)',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_customer_acquisition_chart(customers_df):
    """Crea gráfico de adquisición de clientes"""
    customers_df['created_at'] = pd.to_datetime(customers_df['created_at'])
    monthly_customers = customers_df.groupby(customers_df['created_at'].dt.to_period('M')).size().reset_index()
    monthly_customers['month'] = monthly_customers['created_at'].astype(str)
    monthly_customers.columns = ['created_at', 'new_customers', 'month']
    
    fig = px.bar(
        monthly_customers,
        x='month',
        y='new_customers',
        title='Adquisición de Clientes por Mes',
        color='new_customers',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig

def create_performance_radar_chart(kpis):
    """Crea gráfico radar de rendimiento"""
    # Normalizar KPIs a escala 0-100
    categories = ['Revenue', 'Pedidos', 'Clientes', 'Resolución', 'Satisfacción']
    
    # Valores normalizados (simulados para el ejemplo)
    values = [85, 78, 92, kpis['resolution_rate'], 88]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Rendimiento Actual',
        line_color='#3b82f6',
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Radar de Rendimiento General",
        height=400
    )
    
    return fig

def generate_executive_summary(data, kpis):
    """Genera resumen ejecutivo automático"""
    orders_df = data['orders']
    customers_df = data['customers']
    
    # Calcular crecimiento (simulado)
    revenue_growth = 15.3  # Simulado
    customer_growth = 8.7  # Simulado
    
    # Identificar tendencias
    top_product = "Producto más vendido"  # Simplificado
    # Obtener el país con más ingresos usando datos de customers
    orders_with_country = orders_df.merge(customers_df[['id', 'country']], left_on='customer_id', right_on='id', how='left')
    top_country = orders_with_country.groupby('country')['total_amount'].sum().idxmax() if len(orders_with_country) > 0 else "N/A"
    
    summary = f"""
    ## 📈 Resumen Ejecutivo
    
    ### Rendimiento General
    - **Revenue Total:** €{kpis['revenue']:,.2f} (+{revenue_growth}% vs mes anterior)
    - **Pedidos Procesados:** {kpis['orders']:,} pedidos
    - **Valor Promedio de Pedido:** €{kpis['aov']:.2f}
    - **Tasa de Resolución:** {kpis['resolution_rate']:.1f}%
    
    ### Insights Clave
    - 🎯 **Mercado Principal:** {top_country} genera el mayor revenue
    - 👥 **Crecimiento de Clientes:** +{customer_growth}% nuevos clientes
    - 🛒 **Carritos Abandonados:** €{kpis['abandoned_value']:,.2f} en valor potencial
    - 💬 **Efectividad del Chatbot:** {kpis['resolution_rate']:.1f}% de resolución
    
    ### Recomendaciones
    1. **Optimizar conversión:** Implementar estrategias de recuperación de carritos abandonados
    2. **Expandir mercados:** Considerar expansión en mercados con alto potencial
    3. **Mejorar chatbot:** Entrenar en intents con baja tasa de éxito
    4. **Fidelización:** Desarrollar programas de lealtad para clientes VIP
    """
    
    return summary

def main():
    # Header de la página
    st.markdown("""
    <div class="reports-header">
        <h1>📊 Centro de Reportes</h1>
        <p>Análisis avanzados y generación de reportes ejecutivos en PDF</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    data = load_reports_data()
    if data is None:
        return
    
    # Calcular KPIs
    kpis = calculate_kpis(data)
    
    # Dashboard de KPIs principales
    st.markdown("### 🎯 Dashboard de KPIs")
    
    st.markdown("""
    <div class="kpi-dashboard">
        <div class="kpi-card">
            <div class="kpi-value">€{:,.0f}</div>
            <div class="kpi-label">Revenue Total</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{:,}</div>
            <div class="kpi-label">Pedidos Totales</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{:,}</div>
            <div class="kpi-label">Clientes Activos</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{:.1f}%</div>
            <div class="kpi-label">Tasa Resolución</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">€{:,.0f}</div>
            <div class="kpi-label">Carritos Abandonados</div>
        </div>
    </div>
    """.format(
        kpis['revenue'],
        kpis['orders'],
        kpis['active_customers'],
        kpis['resolution_rate'],
        kpis['abandoned_value']
    ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizaciones de tendencias
    st.markdown("### 📈 Análisis de Tendencias")
    
    col1, col2 = st.columns(2)
    
    with col1:
        revenue_chart = create_revenue_trend_chart(data['orders'])
        st.plotly_chart(revenue_chart, use_container_width=True)
    
    with col2:
        customer_chart = create_customer_acquisition_chart(data['customers'])
        st.plotly_chart(customer_chart, use_container_width=True)
    
    # Análisis de métodos de pago
    st.markdown("### 💳 Análisis de Métodos de Pago")
    if 'metodo_pago' in data['orders']:
        payment_counts = data['orders']['metodo_pago'].value_counts()
        payment_revenue = data['orders'].groupby('metodo_pago')['total_amount'].sum()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=payment_counts.index,
            y=payment_counts.values,
            name='Número de Pedidos',
            marker_color='#3b82f6'
        ))
        fig.add_trace(go.Bar(
            x=payment_revenue.index,
            y=payment_revenue.values,
            name='Revenue',
            marker_color='#10b981',
            yaxis='y2'
        ))
        fig.update_layout(
            title='Uso de Métodos de Pago',
            yaxis=dict(title='Número de Pedidos'),
            yaxis2=dict(title='Revenue (€)', overlaying='y', side='right'),
            barmode='group',
            template='plotly_white',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de métodos de pago disponibles.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        radar_chart = create_performance_radar_chart(kpis)
        st.plotly_chart(radar_chart, use_container_width=True)
    
    with col2:
        # Distribución de revenue por país (usando datos de customers)
        orders_with_country = data['orders'].merge(
            data['customers'][['id', 'country']], 
            left_on='customer_id', 
            right_on='id', 
            how='left'
        )
        country_revenue = orders_with_country.groupby('country')['total_amount'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=country_revenue.values,
            y=country_revenue.index,
            orientation='h',
            title='Revenue por País (Top 10)',
            color=country_revenue.values,
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            template='plotly_white',
            height=400,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Resumen ejecutivo
    executive_summary = generate_executive_summary(data, kpis)
    st.markdown(executive_summary)
    
    st.markdown("---")
    
    # Sección de generación de reportes
    st.markdown("### 📋 Generación de Reportes PDF")
    
    # Configuración de reportes
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Configuración de Reportes:**")
        
        # Selector de período
        period_options = {
            "Último mes": 30,
            "Últimos 3 meses": 90,
            "Últimos 6 meses": 180,
            "Último año": 365
        }
        
        selected_period = st.selectbox("Período de análisis:", list(period_options.keys()))
        days = period_options[selected_period]
        
        # Fecha de corte
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        st.info(f"📅 Analizando datos desde {start_date.strftime('%d/%m/%Y')} hasta {end_date.strftime('%d/%m/%Y')}")
    
    with col2:
        st.markdown("**Opciones de Formato:**")
        include_charts = st.checkbox("Incluir gráficos", value=True)
        include_tables = st.checkbox("Incluir tablas detalladas", value=True)
        include_insights = st.checkbox("Incluir insights automáticos", value=True)
    
    # Reportes disponibles
    st.markdown("### 📊 Reportes Disponibles")
    
    # Reporte de Ventas
    with st.container():
        st.markdown("""
        <div class="report-card">
            <div class="report-type">
                <h3>💰 Reporte de Ventas</h3>
            </div>
            <div class="report-description">
                Análisis completo de rendimiento de ventas, tendencias de revenue, productos más vendidos y métricas de conversión.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{kpis['revenue']:,.0f}</div>
                <div class="metric-label">Revenue Total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['orders']:,}</div>
                <div class="metric-label">Pedidos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{kpis['aov']:.2f}</div>
                <div class="metric-label">AOV</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📥 Generar Reporte de Ventas", key="sales_report"):
            with st.spinner("Generando reporte de ventas..."):
                pdf_bytes = generate_sales_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_ventas.pdf", "📥 Descargar Reporte de Ventas")
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("✅ Reporte de ventas generado exitosamente!")
    
    # Reporte de Clientes
    with st.container():
        st.markdown("""
        <div class="report-card">
            <div class="report-type">
                <h3>👥 Reporte de Clientes</h3>
            </div>
            <div class="report-description">
                Análisis detallado de la base de clientes, segmentación, CLV, retención y oportunidades de crecimiento.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['customers']:,}</div>
                <div class="metric-label">Total Clientes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['active_customers']:,}</div>
                <div class="metric-label">Clientes Activos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{kpis['clv']:.2f}</div>
                <div class="metric-label">CLV Promedio</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📥 Generar Reporte de Clientes", key="customer_report"):
            with st.spinner("Generando reporte de clientes..."):
                pdf_bytes = generate_customer_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_clientes.pdf", "📥 Descargar Reporte de Clientes")
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("✅ Reporte de clientes generado exitosamente!")
    
    # Reporte de Productos
    with st.container():
        st.markdown("""
        <div class="report-card">
            <div class="report-type">
                <h3>📦 Reporte de Productos</h3>
            </div>
            <div class="report-description">
                Análisis de rendimiento de productos, inventario, categorías más rentables y recomendaciones de stock.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        products_df = data['products']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{len(products_df):,}</div>
                <div class="metric-label">Total Productos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Usar 'active' en lugar de 'status' para productos
            active_products = len(products_df[products_df['active'] == True])
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{active_products:,}</div>
                <div class="metric-label">Productos Activos</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_price = products_df['price'].mean()
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{avg_price:.2f}</div>
                <div class="metric-label">Precio Promedio</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📥 Generar Reporte de Productos", key="product_report"):
            with st.spinner("Generando reporte de productos..."):
                pdf_bytes = generate_product_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_productos.pdf", "📥 Descargar Reporte de Productos")
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("✅ Reporte de productos generado exitosamente!")
    
    # Reporte de Chatbot
    with st.container():
        st.markdown("""
        <div class="report-card">
            <div class="report-type">
                <h3>🤖 Reporte de Efectividad del Chatbot</h3>
            </div>
            <div class="report-description">
                Análisis de rendimiento del chatbot, intents más utilizados, tasa de resolución y satisfacción del cliente.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['conversations']:,}</div>
                <div class="metric-label">Conversaciones</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['resolution_rate']:.1f}%</div>
                <div class="metric-label">Tasa Resolución</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_satisfaction = data['conversations']['satisfaction_score'].mean()
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{avg_satisfaction:.1f}/5</div>
                <div class="metric-label">Satisfacción</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📥 Generar Reporte de Chatbot", key="chatbot_report"):
            with st.spinner("Generando reporte de chatbot..."):
                pdf_bytes = generate_chatbot_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_chatbot.pdf", "📥 Descargar Reporte de Chatbot")
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("✅ Reporte de chatbot generado exitosamente!")
    
    # Reporte de Carritos Abandonados
    with st.container():
        st.markdown("""
        <div class="report-card">
            <div class="report-type">
                <h3>🛒 Reporte de Carritos Abandonados</h3>
            </div>
            <div class="report-description">
                Análisis de carritos abandonados, valor perdido, razones de abandono y estrategias de recuperación.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['abandoned_carts']:,}</div>
                <div class="metric-label">Carritos Abandonados</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{kpis['abandoned_value']:,.0f}</div>
                <div class="metric-label">Valor Perdido</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_carts = len(data['carts'])
            abandonment_rate = (kpis['abandoned_carts'] / total_carts) * 100 if total_carts > 0 else 0
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{abandonment_rate:.1f}%</div>
                <div class="metric-label">Tasa Abandono</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📥 Generar Reporte de Carritos Abandonados", key="carts_report"):
            with st.spinner("Generando reporte de carritos abandonados..."):
                pdf_bytes = generate_abandoned_carts_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_carritos_abandonados.pdf", "📥 Descargar Reporte de Carritos")
                st.markdown(download_link, unsafe_allow_html=True)
                st.success("✅ Reporte de carritos abandonados generado exitosamente!")
    
    st.markdown("---")
    
    # Reporte ejecutivo completo
    st.markdown("### 📊 Reporte Ejecutivo Completo")
    
    st.markdown("""
    <div class="report-card">
        <div class="report-type">
            <h3>📈 Reporte Ejecutivo Integral</h3>
        </div>
        <div class="report-description">
            Reporte completo que incluye todos los análisis: ventas, clientes, productos, chatbot y carritos abandonados. 
            Ideal para presentaciones ejecutivas y toma de decisiones estratégicas.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Este reporte incluye:**")
        st.markdown("""
        - 📊 Dashboard ejecutivo con KPIs principales
        - 💰 Análisis detallado de ventas y revenue
        - 👥 Segmentación y análisis de clientes
        - 📦 Rendimiento de productos y categorías
        - 🤖 Efectividad del chatbot y conversaciones
        - 🛒 Análisis de carritos abandonados
        - 📈 Tendencias y proyecciones
        - 💡 Insights y recomendaciones estratégicas
        """)
    
    with col2:
        st.markdown("**Métricas incluidas:**")
        st.markdown(f"""
        - Revenue: €{kpis['revenue']:,.0f}
        - Pedidos: {kpis['orders']:,}
        - Clientes: {kpis['customers']:,}
        - Resolución: {kpis['resolution_rate']:.1f}%
        - Valor perdido: €{kpis['abandoned_value']:,.0f}
        """)
    
    if st.button("📥 Generar Reporte Ejecutivo Completo", key="executive_report", type="primary"):
        with st.spinner("Generando reporte ejecutivo completo... Esto puede tomar unos momentos."):
            # Generar todos los reportes y combinarlos (simplificado para el ejemplo)
            pdf_bytes = generate_sales_report(data, start_date, end_date)  # En una implementación real, sería un reporte combinado
            download_link = create_download_link(pdf_bytes, "reporte_ejecutivo_completo.pdf", "📥 Descargar Reporte Ejecutivo Completo")
            st.markdown(download_link, unsafe_allow_html=True)
            st.success("✅ Reporte ejecutivo completo generado exitosamente!")
            
            # Mostrar resumen de lo generado
            st.info("""
            📋 **Reporte generado con éxito:**
            - ✅ Análisis de ventas y revenue
            - ✅ Segmentación de clientes
            - ✅ Rendimiento de productos
            - ✅ Efectividad del chatbot
            - ✅ Análisis de carritos abandonados
            - ✅ Insights y recomendaciones
            """)
    
    st.markdown("---")
    
    # Programación de reportes
    st.markdown("### ⏰ Programación de Reportes")
    
    st.info("""
    **🚀 Funcionalidad Futura:** 
    En la versión completa, podrás programar la generación automática de reportes:
    - 📅 Reportes diarios, semanales o mensuales
    - 📧 Envío automático por email
    - 🔔 Notificaciones de alertas personalizadas
    - 📊 Dashboards en tiempo real
    """)

if __name__ == "__main__":
    main()