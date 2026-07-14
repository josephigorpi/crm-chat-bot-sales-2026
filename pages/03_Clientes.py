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

st.set_page_config(page_title="Clientes", page_icon="👥", layout="wide")


import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar import sidebar_navigation

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("app.py")

# ✅ Mostrar el sidebar
sidebar_navigation()


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
        st.error(f"Error al cargar datos: {str(e)}")
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
    
    # Segmentación de clientes (use 'segmento' from data_generator if available)
    if 'segmento' in enriched_customers.columns:
        enriched_customers['segment'] = enriched_customers['segmento']
    else:
        def segment_customer(row):
            if row['order_count'] == 0:
                return 'Sin Compras'
            elif row['order_count'] >= 10 and row['total_spent'] >= 1000:
                return 'VIP'
            elif row['order_count'] >= 5 or row['total_spent'] >= 500:
                return 'Frecuente'
            elif row['days_since_last_order'] and row['days_since_last_order'] > 90:
                return 'Inactivo'
            else:
                return 'Regular'
        
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
        name='Valor Promedio (€)',
        x=segment_stats.index,
        y=segment_stats['total_spent'],
        marker_color='#3b82f6',
        hovertemplate='<b>%{x}</b><br>Valor Promedio: €%{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Valor Promedio por Segmento de Cliente',
        xaxis_title='Segmento',
        yaxis_title='Valor Promedio (€)',
        template='plotly_white',
        height=400
    )
    
    return fig

def create_customer_activity_heatmap(customers_df):
    """Crea mapa de calor de actividad de clientes"""
    # Simular actividad por día de la semana y hora
    import numpy as np
    
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    hours = list(range(24))
    
    # Generar datos simulados
    np.random.seed(42)
    activity_data = []
    
    for day in days:
        for hour in hours:
            # Simular más actividad en horas laborales y fines de semana
            if day in ['Sábado', 'Domingo']:
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
        hovertemplate='<b>%{y}</b><br>Hora: %{x}:00<br>Actividad: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Mapa de Calor - Actividad de Clientes por Día y Hora',
        xaxis_title='Hora del Día',
        yaxis_title='Día de la Semana',
        template='plotly_white',
        height=400
    )
    
    return fig

def main():
    # Header de la página
    st.markdown("""
    <div class="customer-header">
        <h1>👥 Gestión de Clientes</h1>
        <p>Análisis completo de la base de clientes y segmentación inteligente</p>
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
    st.markdown("### 🔍 Filtros de Clientes")
    
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            segments = ['Todos'] + list(enriched_customers['segment'].unique())
            selected_segment = st.selectbox("Segmento", segments)
        
        with col2:
            countries = ['Todos'] + list(enriched_customers['country'].unique())
            selected_country = st.selectbox("País", countries)
        
        with col3:
            min_spent = float(enriched_customers['total_spent'].min())
            max_spent = float(enriched_customers['total_spent'].max())
            spent_range = st.slider(
                "Gasto Total (€)", 
                min_value=min_spent, 
                max_value=max_spent, 
                value=(min_spent, max_spent)
            )
        
        with col4:
            search_customer = st.text_input("🔍 Buscar cliente", placeholder="Nombre o email...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección para agregar nuevos clientes
    st.markdown("### ➕ Agregar Nuevo Cliente")
    
    with st.expander("🆕 Formulario para Agregar Cliente", expanded=True):
        st.markdown("""
        <div class="add-customer-form">
            <div class="customer-form-header">
                <h3>👥 Nuevo Cliente</h3>
                <p>Complete la información del cliente</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_name = st.text_input("Nombre Completo *", placeholder="Ej: Juan Pérez")
                customer_email = st.text_input("Email *", placeholder="juan.perez@email.com")
                customer_phone = st.text_input("Teléfono", placeholder="+1 234 567 8900")
                customer_country = st.selectbox(
                    "País *", 
                    options=['España', 'México', 'Argentina', 'Colombia', 'Chile', 'Perú', 'Venezuela', 'Ecuador', 'Uruguay', 'Bolivia']
                )
            
            with col2:
                customer_city = st.text_input("Ciudad", placeholder="Madrid")
                customer_address = st.text_area("Dirección", placeholder="Calle Principal 123")
                customer_age = st.number_input("Edad", min_value=18, max_value=100, value=30, step=1)
                customer_segment = st.selectbox(
                    "Segmento Inicial", 
                    options=['Nuevo', 'Regular', 'Frecuente', 'VIP'],
                    index=0
                )
            
            # Información adicional
            st.markdown("**📋 Información Adicional**")
            col3, col4 = st.columns(2)
            
            with col3:
                customer_gender = st.selectbox("Género", options=['Masculino', 'Femenino', 'Otro', 'Prefiero no decir'])
                customer_marketing = st.checkbox("Acepta marketing por email", value=True)
            
            with col4:
                customer_newsletter = st.checkbox("Suscrito al newsletter", value=False)
                customer_notes = st.text_area("Notas adicionales", placeholder="Información relevante del cliente...")
            
            submitted = st.form_submit_button("✅ Agregar Cliente", use_container_width=True)
            
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
                        
                        st.success(f"✅ Cliente '{customer_name}' agregado exitosamente!")
                        st.info("💡 El cliente se ha agregado a la lista y será visible inmediatamente.")
                        
                        # Mostrar resumen del cliente agregado
                        st.markdown("**📋 Resumen del Cliente Agregado:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Nombre:** {customer_name}")
                            st.write(f"**Email:** {customer_email}")
                            st.write(f"**Teléfono:** {customer_phone if customer_phone else 'No proporcionado'}")
                            st.write(f"**País:** {customer_country}")
                            st.write(f"**Ciudad:** {customer_city if customer_city else 'No proporcionada'}")
                        with col2:
                            st.write(f"**Edad:** {customer_age} años")
                            st.write(f"**Género:** {customer_gender}")
                            st.write(f"**Segmento:** {customer_segment}")
                            st.write(f"**Marketing:** {'Sí' if customer_marketing else 'No'}")
                            st.write(f"**Newsletter:** {'Sí' if customer_newsletter else 'No'}")
                        
                        if customer_notes:
                            st.write(f"**Notas:** {customer_notes}")
                        
                        # Forzar rerun para actualizar la página
                        st.rerun()
                    else:
                        st.error("❌ Por favor ingrese un email válido")
                else:
                    st.error("❌ Por favor complete todos los campos obligatorios (*)")
    
    # Aplicar filtros
    filtered_customers = enriched_customers.copy()
    
    if selected_segment != 'Todos':
        filtered_customers = filtered_customers[filtered_customers['segment'] == selected_segment]
    
    if selected_country != 'Todos':
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
    st.markdown("### 📊 Métricas de Clientes")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-highlight">
            <h3>{:,}</h3>
            <p>Total Clientes</p>
        </div>
        """.format(len(filtered_customers)), unsafe_allow_html=True)
    
    with col2:
        active_customers = len(filtered_customers[filtered_customers['segment'] != 'Sin Compras'])
        st.markdown("""
        <div class="metric-highlight">
            <h3>{:,}</h3>
            <p>Clientes Activos</p>
        </div>
        """.format(active_customers), unsafe_allow_html=True)
    
    with col3:
        avg_clv = filtered_customers['total_spent'].mean()
        st.markdown("""
        <div class="metric-highlight">
            <h3>€{:.2f}</h3>
            <p>CLV Promedio</p>
        </div>
        """.format(avg_clv), unsafe_allow_html=True)
    
    with col4:
        vip_customers = len(filtered_customers[filtered_customers['segment'] == 'VIP'])
        st.markdown("""
        <div class="metric-highlight">
            <h3>{:,}</h3>
            <p>Clientes VIP</p>
        </div>
        """.format(vip_customers), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Segmentación de clientes
    st.markdown("### 🎯 Segmentación de Clientes")
    
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
                <p><strong>{int(segment['count'])}</strong> clientes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            **Métricas del Segmento:**
            - 💰 Gasto promedio: €{segment['avg_spent']:.2f}
            - 📈 Revenue total: €{segment['total_revenue']:.2f}
            - 🛒 Pedidos promedio: {segment['avg_orders']:.1f}
            - 💳 Valor promedio por pedido: €{segment['avg_order_value']:.2f}
            """)
    
    st.markdown("---")
    
    # Visualizaciones
    st.markdown("### 📈 Análisis Visual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Segmentación de clientes
        segmentation_chart = create_customer_segments_chart(filtered_customers, data['orders'])
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
            title='Top 10 Países por Número de Clientes',
            color=country_dist.values,
            color_continuous_scale='Viridis'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Clientes: %{x}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            template="plotly_white",
            xaxis_title="Número de Clientes",
            yaxis_title="País",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Mapa de calor de actividad
        activity_heatmap = create_customer_activity_heatmap(filtered_customers)
        st.plotly_chart(activity_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Embudo de conversión
    st.markdown("### 🎯 Embudo de Conversión")
    
    conversion_data = {
        'Visitantes': 10000,
        'Registrados': len(enriched_customers),
        'Primera Compra': len(enriched_customers[enriched_customers['order_count'] > 0]),
        'Clientes Recurrentes': len(enriched_customers[enriched_customers['order_count'] > 1]),
        'Clientes VIP': len(enriched_customers[enriched_customers['segment'] == 'VIP'])
    }
    
    conversion_chart = create_customer_conversion_funnel(conversion_data)
    st.plotly_chart(conversion_chart, use_container_width=True)
    
    # Mostrar tasas de conversión
    col1, col2, col3 = st.columns(3)
    
    with col1:
        reg_rate = (conversion_data['Registrados'] / conversion_data['Visitantes']) * 100 if conversion_data['Visitantes'] > 0 else 0
        st.metric("Tasa de Registro", f"{reg_rate:.1f}%")
    
    with col2:
        purchase_rate = (conversion_data['Primera Compra'] / conversion_data['Registrados']) * 100 if conversion_data['Registrados'] > 0 else 0
        st.metric("Tasa de Primera Compra", f"{purchase_rate:.1f}%")
    
    with col3:
        retention_rate = (conversion_data['Clientes Recurrentes'] / conversion_data['Primera Compra']) * 100 if conversion_data['Primera Compra'] > 0 else 0
        st.metric("Tasa de Retención", f"{retention_rate:.1f}%")
    
    st.markdown("---")
    
    # Lista de clientes
    st.markdown("### 📋 Lista de Clientes")
    
    # Opciones de visualización
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Mostrando {len(filtered_customers)} clientes**")
    
    with col2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["total_spent", "order_count", "last_order", "first_name"],
            format_func=lambda x: {
                "total_spent": "Gasto Total",
                "order_count": "Número de Pedidos",
                "last_order": "Última Compra",
                "first_name": "Nombre"
            }[x]
        )
    
    with col3:
        sort_order = st.selectbox("Orden:", ["Descendente", "Ascendente"])
    
    # Aplicar ordenamiento
    ascending = sort_order == "Ascendente"
    sorted_customers = filtered_customers.sort_values(sort_by, ascending=ascending)
    
    # Preparar datos para mostrar
    display_customers = sorted_customers.copy()
    display_customers['Cliente'] = display_customers['first_name'] + ' ' + display_customers['last_name']
    display_customers['Email'] = display_customers['email']
    display_customers['País'] = display_customers['country']
    display_customers['Segmento'] = display_customers['segment']
    display_customers['Gasto Total'] = display_customers['total_spent'].apply(lambda x: f"€{x:.2f}")
    display_customers['Pedidos'] = display_customers['order_count'].astype(int)
    display_customers['Última Compra'] = display_customers['last_order'].apply(
        lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else 'Nunca'
    )
    
    # Function to color segment cells
    def color_segment(val):
        colors = {
            "Nuevo": "background-color: #ff9800; color: white;",
            "Frecuente": "background-color: #2196f3; color: white;",
            "VIP": "background-color: #9c27b0; color: white;",
            "Regular": "background-color: #4caf50; color: white;",
            "Inactivo": "background-color: #9e9e9e; color: white;",
            "Sin Compras": "background-color: #f44336; color: white;"
        }
        return colors.get(val, "")
    
    # Create styled dataframe (use .map instead of deprecated .applymap)
    styled_df = display_customers[['Cliente', 'Email', 'País', 'Segmento', 'Gasto Total', 'Pedidos', 'Última Compra']].style.map(
        color_segment,
        subset=['Segmento']
    )
    
    # Mostrar tabla
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cliente": st.column_config.TextColumn("Cliente", width="large"),
            "Email": st.column_config.TextColumn("Email", width="large"),
            "País": st.column_config.TextColumn("País", width="medium"),
            "Segmento": st.column_config.TextColumn("Segmento", width="medium"),
            "Gasto Total": st.column_config.TextColumn("Gasto Total", width="small"),
            "Pedidos": st.column_config.NumberColumn("Pedidos", width="small"),
            "Última Compra": st.column_config.TextColumn("Última Compra", width="medium")
        }
    )
    
    # Información adicional
    st.markdown("### ℹ️ Insights de Clientes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        top_spender = sorted_customers.iloc[0] if len(sorted_customers) > 0 else None
        if top_spender is not None:
            st.success(f"""
            **🏆 Cliente Top:**
            - {top_spender['first_name']} {top_spender['last_name']}
            - Gasto total: €{top_spender['total_spent']:.2f}
            - Pedidos: {int(top_spender['order_count'])}
            - Segmento: {top_spender['segment']}
            """)
    
    with col2:
        segment_distribution = filtered_customers['segment'].value_counts()
        largest_segment = segment_distribution.index[0] if len(segment_distribution) > 0 else "N/A"
        
        st.info(f"""
        **📊 Distribución de Segmentos:**
        - Segmento principal: {largest_segment}
        - Clientes en segmento: {segment_distribution.iloc[0] if len(segment_distribution) > 0 else 0}
        - Países únicos: {filtered_customers['country'].nunique()}
        """)

if __name__ == "__main__":
    main()
