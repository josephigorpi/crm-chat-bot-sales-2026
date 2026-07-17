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
from utils.theme import inject_theme_css, get_plotly_template, init_theme_state
from i18n.strings import get_string
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Reportes", page_icon="📊", layout="wide")

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
        st.error(f"{get_string('reports_load_error', st.session_state.language)} {str(e)}")
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

def create_revenue_trend_chart(orders_df, chart_template):
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
        name=get_string('reports_trends_revenue', st.session_state.language),
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>' + get_string('reports_trends_revenue_hover', st.session_state.language, y='%{y}') + '<extra></extra>'
    ))
    
    fig.update_layout(
        title=get_string('reports_trends_revenue', st.session_state.language),
        xaxis_title=get_string('reports_trends_revenue_month', st.session_state.language),
        yaxis_title=get_string('reports_trends_revenue_amount', st.session_state.language),
        template=chart_template,
        height=400
    )
    
    return fig

def create_customer_acquisition_chart(customers_df, chart_template):
    """Crea gráfico de adquisición de clientes"""
    customers_df['created_at'] = pd.to_datetime(customers_df['created_at'])
    monthly_customers = customers_df.groupby(customers_df['created_at'].dt.to_period('M')).size().reset_index()
    monthly_customers['month'] = monthly_customers['created_at'].astype(str)
    monthly_customers.columns = ['created_at', 'new_customers', 'month']
    
    fig = px.bar(
        monthly_customers,
        x='month',
        y='new_customers',
        title=get_string('reports_trends_customers', st.session_state.language),
        color='new_customers',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        template=chart_template,
        height=400,
        showlegend=False,
        xaxis_title=get_string('reports_trends_revenue_month', st.session_state.language),
        yaxis_title=get_string('reports_trends_customers_count', st.session_state.language)
    )
    
    return fig

def create_performance_radar_chart(kpis, chart_template):
    """Crea gráfico radar de rendimiento"""
    # Normalizar KPIs a escala 0-100
    categories = [
        get_string('reports_radar_categories', st.session_state.language).split(', ')
    ][0]
    
    # Valores normalizados (simulados para el ejemplo)
    values = [85, 78, 92, kpis['resolution_rate'], 88]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=get_string('reports_radar_performance', st.session_state.language),
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
        title=get_string('reports_radar', st.session_state.language),
        height=400,
        template=chart_template
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
    # Obtener el país con más ingresos usando datos de customers
    orders_with_country = orders_df.merge(customers_df[['id', 'country']], left_on='customer_id', right_on='id', how='left')
    top_country = orders_with_country.groupby('country')['total_amount'].sum().idxmax() if len(orders_with_country) > 0 else "N/A"
    
    summary = f"""
    ## {get_string('reports_executive_summary', st.session_state.language)}
    
    ### {get_string('reports_summary_general', st.session_state.language)}
    - {get_string('reports_summary_revenue', st.session_state.language, value=kpis['revenue'], growth=revenue_growth)}
    - {get_string('reports_summary_orders', st.session_state.language, value=kpis['orders'])}
    - {get_string('reports_summary_aov', st.session_state.language, value=kpis['aov'])}
    - {get_string('reports_summary_resolution', st.session_state.language, value=kpis['resolution_rate'])}
    
    ### {get_string('reports_summary_insights', st.session_state.language)}
    - {get_string('reports_summary_top_market', st.session_state.language, country=top_country)}
    - {get_string('reports_summary_customer_growth', st.session_state.language, growth=customer_growth)}
    - {get_string('reports_summary_abandoned_value', st.session_state.language, value=kpis['abandoned_value'])}
    - {get_string('reports_summary_chatbot_rate', st.session_state.language, rate=kpis['resolution_rate'])}
    
    ### {get_string('reports_summary_recommendations', st.session_state.language)}
    {get_string('reports_summary_rec_optimize', st.session_state.language)}
    {get_string('reports_summary_rec_expand', st.session_state.language)}
    {get_string('reports_summary_rec_chatbot', st.session_state.language)}
    {get_string('reports_summary_rec_loyalty', st.session_state.language)}
    """
    
    return summary

def main():
    # Header de la página
    st.markdown(f"""
    <div class="reports-header">
        <h1>{get_string('reports_title', st.session_state.language)}</h1>
        <p>{get_string('reports_subtitle', st.session_state.language)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    data = load_reports_data()
    if data is None:
        return
    
    # Obtener template de plotly
    chart_template = get_plotly_template()
    
    # Calcular KPIs
    kpis = calculate_kpis(data)
    
    # Dashboard de KPIs principales
    st.markdown(f"### {get_string('reports_kpi_dashboard', st.session_state.language)}")
    
    st.markdown("""
    <div class="kpi-dashboard">
        <div class="kpi-card">
            <div class="kpi-value">€{:,.0f}</div>
            <div class="kpi-label">{}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{:,}</div>
            <div class="kpi-label">{}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{:,}</div>
            <div class="kpi-label">{}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{:.1f}%</div>
            <div class="kpi-label">{}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">€{:,.0f}</div>
            <div class="kpi-label">{}</div>
        </div>
    </div>
    """.format(
        kpis['revenue'],
        get_string('reports_kpi_revenue', st.session_state.language),
        kpis['orders'],
        get_string('reports_kpi_orders', st.session_state.language),
        kpis['active_customers'],
        get_string('reports_kpi_active_customers', st.session_state.language),
        kpis['resolution_rate'],
        get_string('reports_kpi_resolution_rate', st.session_state.language),
        kpis['abandoned_value'],
        get_string('reports_kpi_abandoned_value', st.session_state.language)
    ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizaciones de tendencias
    st.markdown(f"### {get_string('reports_trends', st.session_state.language)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        revenue_chart = create_revenue_trend_chart(data['orders'], chart_template)
        st.plotly_chart(revenue_chart, use_container_width=True)
    
    with col2:
        customer_chart = create_customer_acquisition_chart(data['customers'], chart_template)
        st.plotly_chart(customer_chart, use_container_width=True)
    
    # Análisis de métodos de pago
    st.markdown(f"### {get_string('reports_payment_analysis', st.session_state.language)}")
    if 'metodo_pago' in data['orders'].columns:
        payment_counts = data['orders']['metodo_pago'].value_counts()
        payment_revenue = data['orders'].groupby('metodo_pago')['total_amount'].sum()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=payment_counts.index,
            y=payment_counts.values,
            name=get_string('reports_payment_orders', st.session_state.language),
            marker_color='#3b82f6'
        ))
        fig.add_trace(go.Bar(
            x=payment_revenue.index,
            y=payment_revenue.values,
            name=get_string('reports_payment_revenue', st.session_state.language),
            marker_color='#10b981',
            yaxis='y2'
        ))
        fig.update_layout(
            title=get_string('reports_payment_title', st.session_state.language),
            yaxis=dict(title=get_string('reports_payment_orders', st.session_state.language)),
            yaxis2=dict(title=get_string('reports_payment_revenue', st.session_state.language), overlaying='y', side='right'),
            barmode='group',
            template=chart_template,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(get_string('reports_no_payment_data', st.session_state.language))
    
    col1, col2 = st.columns(2)
    
    with col1:
        radar_chart = create_performance_radar_chart(kpis, chart_template)
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
            title=get_string('reports_country_revenue', st.session_state.language),
            color=country_revenue.values,
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            template=chart_template,
            height=400,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title=get_string('reports_payment_revenue', st.session_state.language),
            yaxis_title=get_string('orders_filter_country', st.session_state.language)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Resumen ejecutivo
    executive_summary = generate_executive_summary(data, kpis)
    st.markdown(executive_summary)
    
    st.markdown("---")
    
    # Sección de generación de reportes
    st.markdown(f"### {get_string('reports_generation', st.session_state.language)}")
    
    # Configuración de reportes
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**{get_string('reports_config', st.session_state.language)}**")
        
        # Selector de período
        period_options = {
            get_string('reports_period_last_month', st.session_state.language): 30,
            get_string('reports_period_last_3months', st.session_state.language): 90,
            get_string('reports_period_last_6months', st.session_state.language): 180,
            get_string('reports_period_last_year', st.session_state.language): 365
        }
        
        selected_period = st.selectbox(
            get_string('reports_period', st.session_state.language),
            list(period_options.keys())
        )
        days = period_options[selected_period]
        
        # Fecha de corte
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        st.info(
            get_string('reports_date_range', st.session_state.language,
                start=start_date.strftime('%d/%m/%Y'),
                end=end_date.strftime('%d/%m/%Y')
            )
        )
    
    with col2:
        st.markdown(f"**{get_string('reports_format_options', st.session_state.language)}**")
        include_charts = st.checkbox(get_string('reports_include_charts', st.session_state.language), value=True)
        include_tables = st.checkbox(get_string('reports_include_tables', st.session_state.language), value=True)
        include_insights = st.checkbox(get_string('reports_include_insights', st.session_state.language), value=True)
    
    # Reportes disponibles
    st.markdown(f"### {get_string('reports_available', st.session_state.language)}")
    
    # Reporte de Ventas
    with st.container():
        st.markdown(f"""
        <div class="report-card">
            <div class="report-type">
                <h3>{get_string('reports_sales_title', st.session_state.language)}</h3>
            </div>
            <div class="report-description">
                {get_string('reports_sales_description', st.session_state.language)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{kpis['revenue']:,.0f}</div>
                <div class="metric-label">{get_string('reports_kpi_revenue', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['orders']:,}</div>
                <div class="metric-label">{get_string('reports_kpi_orders', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{kpis['aov']:.2f}</div>
                <div class="metric-label">{get_string('orders_metric_avg_value', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button(get_string('reports_sales_generate', st.session_state.language), key="sales_report"):
            with st.spinner(get_string('reports_sales_generating', st.session_state.language)):
                pdf_bytes = generate_sales_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_ventas.pdf", get_string('reports_download', st.session_state.language, name=get_string('reports_sales_title', st.session_state.language)))
                st.markdown(download_link, unsafe_allow_html=True)
                st.success(get_string('reports_sales_success', st.session_state.language))
    
    # Reporte de Clientes
    with st.container():
        st.markdown(f"""
        <div class="report-card">
            <div class="report-type">
                <h3>{get_string('reports_customers_title', st.session_state.language)}</h3>
            </div>
            <div class="report-description">
                {get_string('reports_customers_description', st.session_state.language)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['customers']:,}</div>
                <div class="metric-label">{get_string('customers_metric_total', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['active_customers']:,}</div>
                <div class="metric-label">{get_string('customers_metric_active', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{kpis['clv']:.2f}</div>
                <div class="metric-label">{get_string('customers_metric_avg_clv', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button(get_string('reports_customers_generate', st.session_state.language), key="customer_report"):
            with st.spinner(get_string('reports_customers_generating', st.session_state.language)):
                pdf_bytes = generate_customer_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_clientes.pdf", get_string('reports_download', st.session_state.language, name=get_string('reports_customers_title', st.session_state.language)))
                st.markdown(download_link, unsafe_allow_html=True)
                st.success(get_string('reports_customers_success', st.session_state.language))
    
    # Reporte de Productos
    with st.container():
        st.markdown(f"""
        <div class="report-card">
            <div class="report-type">
                <h3>{get_string('reports_products_title', st.session_state.language)}</h3>
            </div>
            <div class="report-description">
                {get_string('reports_products_description', st.session_state.language)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        products_df = data['products']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{len(products_df):,}</div>
                <div class="metric-label">{get_string('reports_products_metric_total', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            active_products = len(products_df[products_df['active'] == True])
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{active_products:,}</div>
                <div class="metric-label">{get_string('reports_products_metric_active', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_price = products_df['price'].mean()
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{avg_price:.2f}</div>
                <div class="metric-label">{get_string('reports_products_metric_avg_price', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button(get_string('reports_products_generate', st.session_state.language), key="product_report"):
            with st.spinner(get_string('reports_products_generating', st.session_state.language)):
                pdf_bytes = generate_product_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_productos.pdf", get_string('reports_download', st.session_state.language, name=get_string('reports_products_title', st.session_state.language)))
                st.markdown(download_link, unsafe_allow_html=True)
                st.success(get_string('reports_products_success', st.session_state.language))
    
    # Reporte de Chatbot
    with st.container():
        st.markdown(f"""
        <div class="report-card">
            <div class="report-type">
                <h3>{get_string('reports_chatbot_title', st.session_state.language)}</h3>
            </div>
            <div class="report-description">
                {get_string('reports_chatbot_description', st.session_state.language)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['conversations']:,}</div>
                <div class="metric-label">{get_string('reports_chatbot_metric_conversations', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['resolution_rate']:.1f}%</div>
                <div class="metric-label">{get_string('reports_chatbot_metric_resolution', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_satisfaction = data['conversations']['satisfaction_score'].mean()
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{avg_satisfaction:.1f}/5</div>
                <div class="metric-label">{get_string('reports_chatbot_metric_satisfaction', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button(get_string('reports_chatbot_generate', st.session_state.language), key="chatbot_report"):
            with st.spinner(get_string('reports_chatbot_generating', st.session_state.language)):
                pdf_bytes = generate_chatbot_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_chatbot.pdf", get_string('reports_download', st.session_state.language, name=get_string('reports_chatbot_title', st.session_state.language)))
                st.markdown(download_link, unsafe_allow_html=True)
                st.success(get_string('reports_chatbot_success', st.session_state.language))
    
    # Reporte de Carritos Abandonados
    with st.container():
        st.markdown(f"""
        <div class="report-card">
            <div class="report-type">
                <h3>{get_string('reports_carts_title', st.session_state.language)}</h3>
            </div>
            <div class="report-description">
                {get_string('reports_carts_description', st.session_state.language)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{kpis['abandoned_carts']:,}</div>
                <div class="metric-label">{get_string('reports_carts_metric_abandoned', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">€{kpis['abandoned_value']:,.0f}</div>
                <div class="metric-label">{get_string('reports_carts_metric_lost_value', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_carts = len(data['carts'])
            abandonment_rate = (kpis['abandoned_carts'] / total_carts) * 100 if total_carts > 0 else 0
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-value">{abandonment_rate:.1f}%</div>
                <div class="metric-label">{get_string('reports_carts_metric_rate', st.session_state.language)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button(get_string('reports_carts_generate', st.session_state.language), key="carts_report"):
            with st.spinner(get_string('reports_carts_generating', st.session_state.language)):
                pdf_bytes = generate_abandoned_carts_report(data, start_date, end_date)
                download_link = create_download_link(pdf_bytes, "reporte_carritos_abandonados.pdf", get_string('reports_download', st.session_state.language, name=get_string('reports_carts_title', st.session_state.language)))
                st.markdown(download_link, unsafe_allow_html=True)
                st.success(get_string('reports_carts_success', st.session_state.language))
    
    st.markdown("---")
    
    # Reporte ejecutivo completo
    st.markdown(f"### {get_string('reports_executive_title', st.session_state.language)}")
    
    st.markdown(f"""
    <div class="report-card">
        <div class="report-type">
            <h3>{get_string('reports_executive_title', st.session_state.language)}</h3>
        </div>
        <div class="report-description">
            {get_string('reports_executive_description', st.session_state.language)}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**{get_string('reports_executive_includes', st.session_state.language)}**")
        st.markdown(get_string('reports_executive_includes_list', st.session_state.language))
    
    with col2:
        st.markdown(f"**{get_string('reports_executive_metrics', st.session_state.language)}**")
        st.markdown(f"""
        - {get_string('reports_kpi_revenue', st.session_state.language)}: €{kpis['revenue']:,.0f}
        - {get_string('reports_kpi_orders', st.session_state.language)}: {kpis['orders']:,}
        - {get_string('reports_kpi_active_customers', st.session_state.language)}: {kpis['customers']:,}
        - {get_string('reports_kpi_resolution_rate', st.session_state.language)}: {kpis['resolution_rate']:.1f}%
        - {get_string('reports_kpi_abandoned_value', st.session_state.language)}: €{kpis['abandoned_value']:,.0f}
        """)
    
    if st.button(get_string('reports_executive_generate', st.session_state.language), key="executive_report", type="primary"):
        with st.spinner(get_string('reports_executive_generating', st.session_state.language)):
            pdf_bytes = generate_sales_report(data, start_date, end_date)
            download_link = create_download_link(pdf_bytes, "reporte_ejecutivo_completo.pdf", get_string('reports_download', st.session_state.language, name=get_string('reports_executive_title', st.session_state.language)))
            st.markdown(download_link, unsafe_allow_html=True)
            st.success(get_string('reports_executive_success', st.session_state.language))
            
            st.info(f"""
            {get_string('reports_executive_summary_generated', st.session_state.language)}
            {get_string('reports_executive_summary_items', st.session_state.language)}
            """)
    
    st.markdown("---")
    
    # Programación de reportes
    st.markdown(f"### {get_string('reports_scheduling', st.session_state.language)}")
    
    st.info(get_string('reports_scheduling_future', st.session_state.language))

if __name__ == "__main__":
    main()
