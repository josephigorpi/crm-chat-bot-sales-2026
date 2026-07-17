"""
Página de Gestión de Clientes
Análisis completo de la base de clientes y segmentación
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_generator import get_all_data
from utils.chart_utils import create_customer_segments_chart, create_customer_conversion_funnel
from utils.theme import inject_theme_css, get_plotly_template, init_theme_state
from i18n.strings import get_string
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Clientes", page_icon="👥", layout="wide")


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
    .customer-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .segment-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #8b5cf6;
        color: #1f2937;
    }
    
    .customer-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.5rem;
        color: #1f2937;
    }
    
    .metric-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    
    .filter-section {
        background: #f1f5f9;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: #1f2937;
    }
    
    .add-customer-form {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin: 2rem 0;
        color: #1f2937;
    }
    
    .customer-form-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

def load_customers_data():
    """Carga y procesa los datos de clientes con session_state para persistencia"""
    try:
        # Inicializar session_state para clientes si no existe
        if 'customers_data' not in st.session_state:
            data = get_all_data()
            st.session_state.customers_data = data
            st.session_state.added_customers = []
        
        # Combinar clientes originales con clientes agregados
        original_customers = st.session_state.customers_data['customers'].copy()
        
        if st.session_state.added_customers:
            # Convertir clientes agregados a DataFrame
            added_df = pd.DataFrame(st.session_state.added_customers)
            # Combinar con clientes originales
            combined_customers = pd.concat([original_customers, added_df], ignore_index=True)
        else:
            combined_customers = original_customers
        
        # Actualizar los datos con la lista combinada
        updated_data = st.session_state.customers_data.copy()
        updated_data['customers'] = combined_customers
        
        return updated_data
    except Exception as e:
        st.error(f"{get_string('customers_load_error', st.session_state.language)} {str(e)}")
        return None

def calculate_customer_metrics(customers_df, orders_df):
    """Calcula métricas avanzadas de clientes"""
    # Verificar si hay órdenes disponibles
    if orders_df.empty or 'customer_id' not in orders_df.columns:
        # Si no hay órdenes, crear un DataFrame con valores por defecto
        enriched_customers = customers_df.copy()
        enriched_customers['total_spent'] = 0
        enriched_customers['order_count'] = 0
        enriched_customers['avg_order_value'] = 0
        enriched_customers['first_order'] = None
        enriched_customers['last_order'] = None
        enriched_customers['days_since_last_order'] = None
    else:
        # Calcular valor total por cliente
        customer_orders = orders_df.groupby('customer_id').agg({
            'total_amount': ['sum', 'count', 'mean'],
            'created_at': ['min', 'max']
        }).round(2)
        
        # Verificar si el groupby generó datos
        if customer_orders.empty:
            # Si no hay datos después del groupby, usar valores por defecto
            enriched_customers = customers_df.copy()
            enriched_customers['total_spent'] = 0
            enriched_customers['order_count'] = 0
            enriched_customers['avg_order_value'] = 0
            enriched_customers['first_order'] = None
            enriched_customers['last_order'] = None
            enriched_customers['days_since_last_order'] = None
        else:
            customer_orders.columns = ['total_spent', 'order_count', 'avg_order_value', 'first_order', 'last_order']
            customer_orders = customer_orders.reset_index()
            
            # Merge con datos de clientes
            enriched_customers = customers_df.merge(customer_orders, left_on='id', right_on='customer_id', how='left')
            
            # Asegurar que las columnas existan antes de rellenar valores nulos
            for col in ['total_spent', 'order_count', 'avg_order_value']:
                if col not in enriched_customers.columns:
                    enriched_customers[col] = 0
                else:
                    enriched_customers[col] = enriched_customers[col].fillna(0)
            
            # Manejar columnas de fechas
            for col in ['first_order', 'last_order']:
                if col not in enriched_customers.columns:
                    enriched_customers[col] = None
            
            # Calcular días desde última compra
            today = datetime.now()
            if 'last_order' in enriched_customers.columns:
                enriched_customers['days_since_last_order'] = enriched_customers['last_order'].apply(
                    lambda x: (today - x).days if pd.notna(x) else None
                )
            else:
                enriched_customers['days_since_last_order'] = None
    
    # Segmentación de clientes
    segment_map = {
        'Nuevo': get_string('customers_segment_new', st.session_state.language),
        'Regular': get_string('customers_segment_regular', st.session_state.language),
        'Frecuente': get_string('customers_segment_frequent', st.session_state.language),
        'VIP': get_string('customers_segment_vip', st.session_state.language),
        'Inactivo': get_string('customers_segment_inactive', st.session_state.language),
        'Sin Compras': get_string('customers_segment_no_purchases', st.session_state.language)
    }
    
    if 'segmento' in enriched_customers.columns:
        enriched_customers['segment'] = enriched_customers['segmento'].map(segment_map).fillna(enriched_customers['segmento'])
    else:
        def segment_customer(row):
            if row['order_count'] == 0:
                return get_string('customers_segment_no_purchases', st.session_state.language)
            elif row['order_count'] >= 10 and row['total_spent'] >= 1000:
                return get_string('customers_segment_vip', st.session_state.language)
            elif row['order_count'] >= 5 or row['total_spent'] >= 500:
                return get_string('customers_segment_frequent', st.session_state.language)
            elif row['days_since_last_order'] and row['days_since_last_order'] > 90:
                return get_string('customers_segment_inactive', st.session_state.language)
            else:
                return get_string('customers_segment_regular', st.session_state.language)
        
        enriched_customers['segment'] = enriched_customers.apply(segment_customer, axis=1)
    
    return enriched_customers

def create_customer_lifetime_value_chart(customers_df):
    """Crea gráfico de valor de vida del cliente"""
    # Agrupar por segmento
    segment_stats = customers_df.groupby('segment').agg({
        'total_spent': 'mean',
        'order_count': 'mean',
        'avg_order_value': 'mean'
    }).round(2)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=get_string('chart_customer_avg_value', st.session_state.language),
        x=segment_stats.index,
        y=segment_stats['total_spent'],
        marker_color='#3b82f6',
        hovertemplate='<b>%{x}</b><br>' + get_string('chart_customer_avg_value_hover', st.session_state.language) + ': €%{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title=get_string('chart_customer_lifetime_value', st.session_state.language),
        xaxis_title=get_string('chart_customer_segment', st.session_state.language),
        yaxis_title=get_string('chart_customer_avg_value_y', st.session_state.language),
        template='plotly_white',
        height=400
    )
    
    return fig

def create_customer_activity_heatmap(customers_df):
    """Crea mapa de calor de actividad de clientes"""
    # Simular actividad por día de la semana y hora
    import numpy as np
    
    days = [
        get_string('chart_day_monday', st.session_state.language),
        get_string('chart_day_tuesday', st.session_state.language),
        get_string('chart_day_wednesday', st.session_state.language),
        get_string('chart_day_thursday', st.session_state.language),
        get_string('chart_day_friday', st.session_state.language),
        get_string('chart_day_saturday', st.session_state.language),
        get_string('chart_day_sunday', st.session_state.language)
    ]
    hours = list(range(24))
    
    # Generar datos simulados
    np.random.seed(42)
    activity_data = []
    
    for day in days:
        for hour in hours:
            # Simular más actividad en horas laborales y fines de semana
            if day in [get_string('chart_day_saturday', st.session_state.language), get_string('chart_day_sunday', st.session_state.language)]:
                base_activity = np.random.poisson(15)
            elif 9 <= hour <= 18:
                base_activity = np.random.poisson(20)
            elif 19 <= hour <= 22:
                base_activity = np.random.poisson(25)
            else:
                base_activity = np.random.poisson(5)
            
            activity_data.append({
                'day': day,
                'hour': hour,
                'activity': base_activity
            })
    
    activity_df = pd.DataFrame(activity_data)
    
    # Crear matriz para heatmap
    heatmap_data = activity_df.pivot(index='day', columns='hour', values='activity')
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Blues',
        hovertemplate='<b>%{y}</b><br>' + get_string('chart_heatmap_hour_hover', st.session_state.language) + ': %{x}:00<br>' + get_string('chart_heatmap_activity_hover', st.session_state.language) + ': %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=get_string('chart_customer_activity_heatmap', st.session_state.language),
        xaxis_title=get_string('chart_heatmap_hour_x', st.session_state.language),
        yaxis_title=get_string('chart_heatmap_day_y', st.session_state.language),
        template='plotly_white',
        height=400
    )
    
    return fig

def main():
    # Header de la página
    st.markdown(f"""
    <div class="customer-header">
        <h1>{get_string('customers_title', st.session_state.language)}</h1>
        <p>{get_string('customers_subtitle', st.session_state.language)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    data = load_customers_data()
    if data is None:
        return
    
    customers_df = data['customers']
    orders_df = data['orders']
    
    # Calcular métricas enriquecidas
    enriched_customers = calculate_customer_metrics(customers_df, orders_df)
    
    # Filtros
    st.markdown(f"### {get_string('customers_filters', st.session_state.language)}")
    
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            segments = [get_string('customers_filter_segment_all', st.session_state.language)] + list(enriched_customers['segment'].unique())
            selected_segment = st.selectbox(
                get_string('customers_filter_segment', st.session_state.language),
                segments
            )
        
        with col2:
            countries = [get_string('customers_filter_country_all', st.session_state.language)] + list(enriched_customers['country'].unique())
            selected_country = st.selectbox(
                get_string('customers_filter_country', st.session_state.language),
                countries
            )
        
        with col3:
            min_spent = float(enriched_customers['total_spent'].min())
            max_spent = float(enriched_customers['total_spent'].max())
            spent_range = st.slider(
                get_string('customers_filter_spent', st.session_state.language),
                min_value=min_spent, 
                max_value=max_spent, 
                value=(min_spent, max_spent)
            )
        
        with col4:
            search_customer = st.text_input(
                get_string('customers_search', st.session_state.language),
                placeholder=get_string('customers_search_placeholder', st.session_state.language)
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección para agregar nuevos clientes
    st.markdown(f"### {get_string('customers_add_new', st.session_state.language)}")
    
    with st.expander(get_string('customers_add_form_title', st.session_state.language), expanded=True):
        st.markdown(f"""
        <div class="add-customer-form">
            <div class="customer-form-header">
                <h3>{get_string('customers_add_form_header', st.session_state.language)}</h3>
                <p>{get_string('customers_add_form_subtitle', st.session_state.language)}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_name = st.text_input(
                    get_string('customers_add_name', st.session_state.language),
                    placeholder=get_string('customers_add_name_placeholder', st.session_state.language)
                )
                customer_email = st.text_input(
                    get_string('customers_add_email', st.session_state.language),
                    placeholder=get_string('customers_add_email_placeholder', st.session_state.language)
                )
                customer_phone = st.text_input(
                    get_string('customers_add_phone', st.session_state.language),
                    placeholder=get_string('customers_add_phone_placeholder', st.session_state.language)
                )
                customer_country = st.selectbox(
                    get_string('customers_add_country', st.session_state.language),
                    options=['España', 'México', 'Argentina', 'Colombia', 'Chile', 'Perú', 'Venezuela', 'Ecuador', 'Uruguay', 'Bolivia']
                )
            
            with col2:
                customer_city = st.text_input(
                    get_string('customers_add_city', st.session_state.language),
                    placeholder=get_string('customers_add_city_placeholder', st.session_state.language)
                )
                customer_address = st.text_area(
                    get_string('customers_add_address', st.session_state.language),
                    placeholder=get_string('customers_add_address_placeholder', st.session_state.language)
                )
                customer_age = st.number_input(
                    get_string('customers_add_age', st.session_state.language),
                    min_value=18, max_value=100, value=30, step=1
                )
                customer_segment = st.selectbox(
                    get_string('customers_add_segment', st.session_state.language),
                    options=[
                        get_string('customers_segment_new', st.session_state.language),
                        get_string('customers_segment_regular', st.session_state.language),
                        get_string('customers_segment_frequent', st.session_state.language),
                        get_string('customers_segment_vip', st.session_state.language)
                    ],
                    index=0
                )
            
            # Información adicional
            st.markdown(f"**{get_string('customers_add_additional_info', st.session_state.language)}**")
            col3, col4 = st.columns(2)
            
            with col3:
                customer_gender = st.selectbox(
                    get_string('customers_add_gender', st.session_state.language),
                    options=[
                        get_string('customers_add_gender_male', st.session_state.language),
                        get_string('customers_add_gender_female', st.session_state.language),
                        get_string('customers_add_gender_other', st.session_state.language),
                        get_string('customers_add_gender_prefer_not', st.session_state.language)
                    ]
                )
                customer_marketing = st.checkbox(
                    get_string('customers_add_marketing', st.session_state.language),
                    value=True
                )
            
            with col4:
                customer_newsletter = st.checkbox(
                    get_string('customers_add_newsletter', st.session_state.language),
                    value=False
                )
                customer_notes = st.text_area(
                    get_string('customers_add_notes', st.session_state.language),
                    placeholder=get_string('customers_add_notes_placeholder', st.session_state.language)
                )
            
            submitted = st.form_submit_button(
                get_string('customers_add_button', st.session_state.language),
                use_container_width=True
            )
            
            if submitted:
                if customer_name and customer_email and customer_country:
                    # Validar formato de email básico
                    if '@' in customer_email and '.' in customer_email:
                        # Agregar cliente al session_state
                        new_customer = {
                            'id': len(st.session_state.customers_data['customers']) + len(st.session_state.added_customers) + 1,
                            'first_name': customer_name.split()[0] if customer_name else '',
                            'last_name': ' '.join(customer_name.split()[1:]) if len(customer_name.split()) > 1 else '',
                            'email': customer_email,
                            'phone': customer_phone,
                            'country': customer_country,
                            'city': customer_city,
                            'address': customer_address,
                            'age': customer_age,
                            'gender': customer_gender,
                            'segment': customer_segment,
                            'marketing_consent': customer_marketing,
                            'newsletter': customer_newsletter,
                            'notes': customer_notes,
                            'created_at': datetime.now(),
                            'total_spent': 0,
                            'order_count': 0
                        }
                        
                        # Agregar a la lista de clientes agregados
                        st.session_state.added_customers.append(new_customer)
                        
                        st.success(get_string('customers_add_success', st.session_state.language, name=customer_name))
                        st.info(get_string('customers_add_info', st.session_state.language))
                        
                        # Mostrar resumen del cliente agregado
                        st.markdown(f"**{get_string('customers_add_summary', st.session_state.language)}**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{get_string('customers_add_name_label', st.session_state.language)}** {customer_name}")
                            st.write(f"**{get_string('customers_add_email_label', st.session_state.language)}** {customer_email}")
                            st.write(f"**{get_string('customers_add_phone_label', st.session_state.language)}** {customer_phone if customer_phone else get_string('customers_add_not_provided', st.session_state.language)}")
                            st.write(f"**{get_string('customers_add_country_label', st.session_state.language)}** {customer_country}")
                            st.write(f"**{get_string('customers_add_city_label', st.session_state.language)}** {customer_city if customer_city else get_string('customers_add_not_provided_city', st.session_state.language)}")
                        with col2:
                            st.write(f"**{get_string('customers_add_age_label', st.session_state.language)}** {customer_age} {get_string('customers_add_years', st.session_state.language)}")
                            st.write(f"**{get_string('customers_add_gender_label', st.session_state.language)}** {customer_gender}")
                            st.write(f"**{get_string('customers_add_segment_label', st.session_state.language)}** {customer_segment}")
                            st.write(f"**{get_string('customers_add_marketing_label', st.session_state.language)}** {get_string('customers_add_yes', st.session_state.language) if customer_marketing else get_string('customers_add_no', st.session_state.language)}")
                            st.write(f"**{get_string('customers_add_newsletter_label', st.session_state.language)}** {get_string('customers_add_yes', st.session_state.language) if customer_newsletter else get_string('customers_add_no', st.session_state.language)}")
                        
                        if customer_notes:
                            st.write(f"**{get_string('customers_add_notes_label', st.session_state.language)}** {customer_notes}")
                        
                        # Forzar rerun para actualizar la página
                        st.rerun()
                    else:
                        st.error(get_string('customers_add_email_invalid', st.session_state.language))
                else:
                    st.error(get_string('customers_add_error', st.session_state.language))
    
    # Aplicar filtros
    filtered_customers = enriched_customers.copy()
    
    if selected_segment != get_string('customers_filter_segment_all', st.session_state.language):
        filtered_customers = filtered_customers[filtered_customers['segment'] == selected_segment]
    
    if selected_country != get_string('customers_filter_country_all', st.session_state.language):
        filtered_customers = filtered_customers[filtered_customers['country'] == selected_country]
    
    filtered_customers = filtered_customers[
        (filtered_customers['total_spent'] >= spent_range[0]) & 
        (filtered_customers['total_spent'] <= spent_range[1])
    ]
    
    if search_customer:
        filtered_customers = filtered_customers[
            (filtered_customers['first_name'].str.contains(search_customer, case=False, na=False)) |
            (filtered_customers['last_name'].str.contains(search_customer, case=False, na=False)) |
            (filtered_customers['email'].str.contains(search_customer, case=False, na=False))
        ]
    
    # Métricas principales
    st.markdown(f"### {get_string('customers_metrics', st.session_state.language)}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>{len(filtered_customers):,}</h3>
            <p>{get_string('customers_metric_total', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_customers = len(filtered_customers[filtered_customers['segment'] != get_string('customers_segment_no_purchases', st.session_state.language)])
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>{active_customers:,}</h3>
            <p>{get_string('customers_metric_active', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_clv = filtered_customers['total_spent'].mean()
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>€{avg_clv:.2f}</h3>
            <p>{get_string('customers_metric_avg_clv', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        vip_customers = len(filtered_customers[filtered_customers['segment'] == get_string('customers_segment_vip', st.session_state.language)])
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>{vip_customers:,}</h3>
            <p>{get_string('customers_metric_vip', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Segmentación de clientes
    st.markdown(f"### {get_string('customers_segmentation', st.session_state.language)}")
    
    segment_stats = filtered_customers.groupby('segment').agg({
        'id': 'count',
        'total_spent': ['mean', 'sum'],
        'order_count': 'mean',
        'avg_order_value': 'mean'
    }).round(2)
    
    segment_stats.columns = ['count', 'avg_spent', 'total_revenue', 'avg_orders', 'avg_order_value']
    segment_stats = segment_stats.reset_index()
    
    for _, segment in segment_stats.iterrows():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"""
            <div class="segment-card">
                <h4>{segment['segment']}</h4>
                <p><strong>{int(segment['count'])}</strong> {get_string('customers_segment_customers', st.session_state.language)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            **{get_string('customers_segment_metrics', st.session_state.language)}**
            - {get_string('customers_segment_avg_spent', st.session_state.language)} €{segment['avg_spent']:.2f}
            - {get_string('customers_segment_total_revenue', st.session_state.language)} €{segment['total_revenue']:.2f}
            - {get_string('customers_segment_avg_orders', st.session_state.language)} {segment['avg_orders']:.1f}
            - {get_string('customers_segment_avg_order_value', st.session_state.language)} €{segment['avg_order_value']:.2f}
            """)
    
    st.markdown("---")
    
    # Visualizaciones
    st.markdown(f"### {get_string('customers_analysis', st.session_state.language)}")
    
    # Obtener el template de plotly
    chart_template = get_plotly_template()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Segmentación de clientes
        segmentation_chart = create_customer_segments_chart(filtered_customers, data['orders'], chart_template, st.session_state.language)
        st.plotly_chart(segmentation_chart, use_container_width=True)
    
    with col2:
        # Valor de vida del cliente por segmento
        clv_chart = create_customer_lifetime_value_chart(filtered_customers)
        st.plotly_chart(clv_chart, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribución geográfica
        country_dist = filtered_customers['country'].value_counts().head(10)
        
        fig = px.bar(
            x=country_dist.values,
            y=country_dist.index,
            orientation='h',
            title=get_string('customers_geographic', st.session_state.language),
            color=country_dist.values,
            color_continuous_scale='Viridis'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>' + get_string('customers_geographic_x', st.session_state.language) + ': %{x}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            template=chart_template,
            xaxis_title=get_string('customers_geographic_x', st.session_state.language),
            yaxis_title=get_string('customers_geographic_y', st.session_state.language),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Mapa de calor de actividad
        activity_heatmap = create_customer_activity_heatmap(filtered_customers)
        st.plotly_chart(activity_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Embudo de conversión
    st.markdown(f"### {get_string('customers_conversion_funnel', st.session_state.language)}")
    
    conversion_data = {
        get_string('customers_conversion_visitors', st.session_state.language): 10000,
        get_string('customers_conversion_registered', st.session_state.language): len(enriched_customers),
        get_string('customers_conversion_first_purchase', st.session_state.language): len(enriched_customers[enriched_customers['order_count'] > 0]),
        get_string('customers_conversion_recurring', st.session_state.language): len(enriched_customers[enriched_customers['order_count'] > 1]),
        get_string('customers_conversion_vip', st.session_state.language): len(enriched_customers[enriched_customers['segment'] == get_string('customers_segment_vip', st.session_state.language)])
    }
    
    conversion_chart = create_customer_conversion_funnel(conversion_data, chart_template)
    st.plotly_chart(conversion_chart, use_container_width=True)
    
    # Mostrar tasas de conversión
    col1, col2, col3 = st.columns(3)
    
    visitors = conversion_data[get_string('customers_conversion_visitors', st.session_state.language)]
    registered = conversion_data[get_string('customers_conversion_registered', st.session_state.language)]
    first_purchase = conversion_data[get_string('customers_conversion_first_purchase', st.session_state.language)]
    recurring = conversion_data[get_string('customers_conversion_recurring', st.session_state.language)]
    
    with col1:
        reg_rate = (registered / visitors) * 100 if visitors > 0 else 0
        st.metric(get_string('customers_conversion_registration_rate', st.session_state.language), f"{reg_rate:.1f}%")
    
    with col2:
        purchase_rate = (first_purchase / registered) * 100 if registered > 0 else 0
        st.metric(get_string('customers_conversion_purchase_rate', st.session_state.language), f"{purchase_rate:.1f}%")
    
    with col3:
        retention_rate = (recurring / first_purchase) * 100 if first_purchase > 0 else 0
        st.metric(get_string('customers_conversion_retention_rate', st.session_state.language), f"{retention_rate:.1f}%")
    
    st.markdown("---")
    
    # Lista de clientes
    st.markdown(f"### {get_string('customers_list', st.session_state.language)}")
    
    # Opciones de visualización
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**{get_string('customers_list_showing', st.session_state.language, count=len(filtered_customers))}**")
    
    with col2:
        sort_by = st.selectbox(
            get_string('customers_list_sort_by', st.session_state.language),
            ["total_spent", "order_count", "last_order", "first_name"],
            format_func=lambda x: {
                "total_spent": get_string('customers_list_sort_total_spent', st.session_state.language),
                "order_count": get_string('customers_list_sort_order_count', st.session_state.language),
                "last_order": get_string('customers_list_sort_last_order', st.session_state.language),
                "first_name": get_string('customers_list_sort_name', st.session_state.language)
            }[x]
        )
    
    with col3:
        sort_options = [
            get_string('customers_list_sort_descending', st.session_state.language),
            get_string('customers_list_sort_ascending', st.session_state.language)
        ]
        sort_order = st.selectbox(
            get_string('customers_list_sort_order', st.session_state.language),
            sort_options
        )
    
    # Aplicar ordenamiento
    ascending = sort_order == get_string('customers_list_sort_ascending', st.session_state.language)
    sorted_customers = filtered_customers.sort_values(sort_by, ascending=ascending)
    
    # Preparar datos para mostrar
    display_customers = sorted_customers.copy()
    display_customers[get_string('customers_table_client', st.session_state.language)] = display_customers['first_name'] + ' ' + display_customers['last_name']
    display_customers[get_string('customers_table_email', st.session_state.language)] = display_customers['email']
    display_customers[get_string('customers_table_country', st.session_state.language)] = display_customers['country']
    display_customers[get_string('customers_table_segment', st.session_state.language)] = display_customers['segment']
    display_customers[get_string('customers_table_total_spent', st.session_state.language)] = display_customers['total_spent'].apply(lambda x: f"€{x:.2f}")
    display_customers[get_string('customers_table_orders', st.session_state.language)] = display_customers['order_count'].astype(int)
    display_customers[get_string('customers_table_last_purchase', st.session_state.language)] = display_customers['last_order'].apply(
        lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else get_string('customers_table_never', st.session_state.language)
    )
    
    # Function to color segment cells
    def color_segment(val):
        colors = {
            get_string('customers_segment_new', st.session_state.language): "background-color: #ff9800; color: white;",
            get_string('customers_segment_frequent', st.session_state.language): "background-color: #2196f3; color: white;",
            get_string('customers_segment_vip', st.session_state.language): "background-color: #9c27b0; color: white;",
            get_string('customers_segment_regular', st.session_state.language): "background-color: #4caf50; color: white;",
            get_string('customers_segment_inactive', st.session_state.language): "background-color: #9e9e9e; color: white;",
            get_string('customers_segment_no_purchases', st.session_state.language): "background-color: #f44336; color: white;"
        }
        return colors.get(val, "")
    
    # Create styled dataframe
    styled_df = display_customers[[
        get_string('customers_table_client', st.session_state.language),
        get_string('customers_table_email', st.session_state.language),
        get_string('customers_table_country', st.session_state.language),
        get_string('customers_table_segment', st.session_state.language),
        get_string('customers_table_total_spent', st.session_state.language),
        get_string('customers_table_orders', st.session_state.language),
        get_string('customers_table_last_purchase', st.session_state.language)
    ]].style.map(
        color_segment,
        subset=[get_string('customers_table_segment', st.session_state.language)]
    )
    
    # Mostrar tabla
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            get_string('customers_table_client', st.session_state.language): st.column_config.TextColumn(
                get_string('customers_table_client', st.session_state.language), width="large"
            ),
            get_string('customers_table_email', st.session_state.language): st.column_config.TextColumn(
                get_string('customers_table_email', st.session_state.language), width="large"
            ),
            get_string('customers_table_country', st.session_state.language): st.column_config.TextColumn(
                get_string('customers_table_country', st.session_state.language), width="medium"
            ),
            get_string('customers_table_segment', st.session_state.language): st.column_config.TextColumn(
                get_string('customers_table_segment', st.session_state.language), width="medium"
            ),
            get_string('customers_table_total_spent', st.session_state.language): st.column_config.TextColumn(
                get_string('customers_table_total_spent', st.session_state.language), width="small"
            ),
            get_string('customers_table_orders', st.session_state.language): st.column_config.NumberColumn(
                get_string('customers_table_orders', st.session_state.language), width="small"
            ),
            get_string('customers_table_last_purchase', st.session_state.language): st.column_config.TextColumn(
                get_string('customers_table_last_purchase', st.session_state.language), width="medium"
            )
        }
    )
    
    # Información adicional
    st.markdown(f"### {get_string('customers_insights', st.session_state.language)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_spender = sorted_customers.iloc[0] if len(sorted_customers) > 0 else None
        if top_spender is not None:
            st.success(f"""
            **{get_string('customers_insights_top', st.session_state.language)}**
            - {get_string('customers_insights_top_name', st.session_state.language)} {top_spender['first_name']} {top_spender['last_name']}
            - {get_string('customers_insights_top_spent', st.session_state.language)} €{top_spender['total_spent']:.2f}
            - {get_string('customers_insights_top_orders', st.session_state.language)} {int(top_spender['order_count'])}
            - {get_string('customers_insights_top_segment', st.session_state.language)} {top_spender['segment']}
            """)
    
    with col2:
        segment_distribution = filtered_customers['segment'].value_counts()
        largest_segment = segment_distribution.index[0] if len(segment_distribution) > 0 else "N/A"
        
        st.info(f"""
        **{get_string('customers_insights_distribution', st.session_state.language)}**
        - {get_string('customers_insights_main_segment', st.session_state.language)} {largest_segment}
        - {get_string('customers_insights_segment_count', st.session_state.language)} {segment_distribution.iloc[0] if len(segment_distribution) > 0 else 0}
        - {get_string('customers_insights_unique_countries', st.session_state.language)} {filtered_customers['country'].nunique()}
        """)

if __name__ == "__main__":
    main()
