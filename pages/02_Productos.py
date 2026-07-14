"""
Página de Análisis de Productos
Gestión y análisis completo de productos con soporte para tema e idioma
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_all_data
from utils.chart_utils import create_top_products_chart, create_price_distribution, create_category_donut
from utils.theme import inject_theme_css, get_plotly_template, init_theme_state
from i18n.strings import get_string

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sidebar import sidebar_navigation


st.set_page_config(page_title="Productos", page_icon="📦", layout="wide")

# ✅ Inyectar CSS dinámico del tema
inject_theme_css()

# Inicializar estado de tema e idioma
init_theme_state()
if 'language' not in st.session_state:
    st.session_state.language = 'es'

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("app.py")

# ✅ Mostrar el sidebar
sidebar_navigation()

def load_products_data():
    """
    Carga y procesa los datos de productos con session_state para persistencia.
    
    Returns:
        Dict con datos de productos o None si hay error
    """
    try:
        # Inicializar session_state para productos si no existe
        if 'products_data' not in st.session_state:
            data = get_all_data()
            st.session_state.products_data = data
            st.session_state.added_products = []
        
        # Combinar productos originales con productos agregados
        original_products = st.session_state.products_data['products'].copy()
        
        # Debug: mostrar información sobre productos agregados
        if st.session_state.added_products:
            st.info(f"🔍 Debug: {get_string('products_debug_added', st.session_state.language, count=len(st.session_state.added_products))}")
            # Convertir productos agregados a DataFrame
            added_df = pd.DataFrame(st.session_state.added_products)
            # Combinar con productos originales
            combined_products = pd.concat([original_products, added_df], ignore_index=True)
        else:
            combined_products = original_products
        
        # Debug: mostrar total de productos
        st.info(f"🔍 {get_string('products_debug_total', st.session_state.language, count=len(combined_products))}")
        
        # Actualizar los datos con la lista combinada
        updated_data = st.session_state.products_data.copy()
        updated_data['products'] = combined_products
        
        return updated_data
    except Exception as e:
        st.error(f"{get_string('products_load_error', st.session_state.language)} {str(e)}")
        return None

def create_low_inventory_alert(products_df, threshold=10):
    """
    Crea alerta de productos con bajo inventario.
    
    Args:
        products_df: DataFrame con productos
        threshold: Umbral de inventario bajo
    """
    low_stock = products_df[products_df['inventory_count'] < threshold]
    
    if len(low_stock) > 0:
        st.markdown(f"""
        <div class="alert-box">
            <h4>{get_string('products_low_inventory_alert', st.session_state.language)}</h4>
            <p><strong>{len(low_stock)} {get_string('products_low_inventory_text', st.session_state.language, count=len(low_stock), threshold=threshold)}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar productos con bajo stock
        with st.expander(get_string('products_low_inventory_show', st.session_state.language, count=len(low_stock))):
            display_low_stock = low_stock[['name', 'category', 'inventory_count', 'price']].copy()
            display_low_stock[get_string('products_table_product', st.session_state.language)] = display_low_stock['name']
            display_low_stock[get_string('products_table_category', st.session_state.language)] = display_low_stock['category'].str.title()
            display_low_stock[get_string('products_table_inventory', st.session_state.language)] = display_low_stock['inventory_count']
            display_low_stock[get_string('products_table_price', st.session_state.language)] = display_low_stock['price'].apply(lambda x: f"€{x:.2f}")
            
            st.dataframe(
                display_low_stock[[
                    get_string('products_table_product', st.session_state.language),
                    get_string('products_table_category', st.session_state.language),
                    get_string('products_table_inventory', st.session_state.language),
                    get_string('products_table_price', st.session_state.language)
                ]],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.markdown(f"""
        <div class="success-box">
            <h4>{get_string('products_inventory_healthy', st.session_state.language)}</h4>
            <p>{get_string('products_inventory_healthy_text', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header de la página
    st.markdown(f"""
    <div class="product-header">
        <h1>{get_string('products_title', st.session_state.language)}</h1>
        <p>{get_string('products_subtitle', st.session_state.language)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    data = load_products_data()
    if data is None:
        return
    
    products_df = data['products']
    chart_template = get_plotly_template()
    
    # Sección de filtros
    st.markdown(f"### {get_string('products_filters', st.session_state.language)}")
    
    with st.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filtro por categoría
            categories = [get_string('products_filter_category_all', st.session_state.language)] + list(products_df['category'].unique())
            selected_category = st.selectbox(
                get_string('products_filter_category', st.session_state.language),
                categories
            )
        
        with col2:
            # Filtro por rango de precio
            min_price = float(products_df['price'].min())
            max_price = float(products_df['price'].max())
            price_range = st.slider(
                get_string('products_filter_price', st.session_state.language),
                min_value=min_price, 
                max_value=max_price, 
                value=(min_price, max_price)
            )
        
        with col3:
            # Filtro por estado
            status_options = [
                get_string('products_filter_status_all', st.session_state.language),
                get_string('products_filter_status_active', st.session_state.language),
                get_string('products_filter_status_inactive', st.session_state.language)
            ]
            selected_status = st.selectbox(
                get_string('products_filter_status', st.session_state.language),
                status_options
            )
        
        with col4:
            # Buscador
            search_term = st.text_input(
                get_string('products_search', st.session_state.language),
                placeholder=get_string('products_search_placeholder', st.session_state.language)
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección para agregar nuevos productos
    st.markdown(f"### {get_string('products_add_new', st.session_state.language)}")
    
    with st.expander(get_string('products_add_form_title', st.session_state.language), expanded=True):
        st.markdown(f"""
        <div class="add-product-form">
            <div class="form-header">
                <h3>{get_string('products_add_form_header', st.session_state.language)}</h3>
                <p>{get_string('products_add_form_subtitle', st.session_state.language)}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input(
                    get_string('products_add_name', st.session_state.language),
                    placeholder=get_string('products_add_name_placeholder', st.session_state.language)
                )
                product_category = st.selectbox(
                    get_string('products_add_category', st.session_state.language),
                    options=['electronics', 'clothing', 'books', 'home', 'sports', 'beauty']
                )
                product_price = st.number_input(
                    get_string('products_add_price', st.session_state.language),
                    min_value=0.01,
                    value=100.00,
                    step=0.01
                )
            
            with col2:
                product_inventory = st.number_input(
                    get_string('products_add_inventory', st.session_state.language),
                    min_value=0,
                    value=50,
                    step=1
                )
                product_active = st.checkbox(get_string('products_add_active', st.session_state.language), value=True)
                product_description = st.text_area(
                    get_string('products_add_description', st.session_state.language),
                    placeholder=get_string('products_add_description_placeholder', st.session_state.language)
                )
            
            submitted = st.form_submit_button(
                get_string('products_add_button', st.session_state.language),
                use_container_width=True
            )
            
            if submitted:
                if product_name and product_category and product_price > 0:
                    # Agregar producto al session_state
                    new_product = {
                        'id': len(st.session_state.products_data['products']) + len(st.session_state.added_products) + 1,
                        'name': product_name,
                        'category': product_category,
                        'price': product_price,
                        'inventory_count': product_inventory,
                        'active': product_active,
                        'description': product_description
                    }
                    
                    # Agregar a la lista de productos agregados
                    st.session_state.added_products.append(new_product)
                    
                    st.success(get_string('products_add_success', st.session_state.language, name=product_name))
                    st.info(get_string('products_add_info', st.session_state.language))
                    
                    # Mostrar resumen del producto agregado
                    st.markdown(get_string('products_add_summary', st.session_state.language))
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{get_string('products_add_name_label', st.session_state.language)}** {product_name}")
                        st.write(f"**{get_string('products_add_category_label', st.session_state.language)}** {product_category.title()}")
                        st.write(f"**{get_string('products_add_price_label', st.session_state.language)}** USD {product_price:.2f}")
                    with col2:
                        st.write(f"**{get_string('products_add_inventory_label', st.session_state.language)}** {product_inventory} {get_string('products_add_units', st.session_state.language)}")
                        status_text = get_string('products_add_status_active', st.session_state.language) if product_active else get_string('products_add_status_inactive', st.session_state.language)
                        st.write(f"**{get_string('products_add_status_label', st.session_state.language)}** {status_text}")
                        st.write(f"**{get_string('products_add_description_label', st.session_state.language)}** {product_description if product_description else get_string('products_add_no_description', st.session_state.language)}")
                    
                    # Forzar rerun para actualizar la página
                    st.rerun()
                else:
                    st.error(get_string('products_add_error', st.session_state.language))
    
    # Aplicar filtros
    filtered_df = products_df.copy()
    
    if selected_category != get_string('products_filter_category_all', st.session_state.language):
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= price_range[0]) & 
        (filtered_df['price'] <= price_range[1])
    ]
    
    if selected_status == get_string('products_filter_status_active', st.session_state.language):
        filtered_df = filtered_df[filtered_df['active'] == True]
    elif selected_status == get_string('products_filter_status_inactive', st.session_state.language):
        filtered_df = filtered_df[filtered_df['active'] == False]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False, na=False)
        ]
    
    # Métricas de productos
    st.markdown(f"### {get_string('products_metrics', st.session_state.language)}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h3>{len(filtered_df)}</h3>
            <p>{get_string('products_metric_total', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_products = len(filtered_df[filtered_df['active'] == True])
        st.markdown(f"""
        <div class="metric-box">
            <h3>{active_products}</h3>
            <p>{get_string('products_metric_active', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_price = filtered_df['price'].mean()
        st.markdown(f"""
        <div class="metric-box">
            <h3>€{avg_price:.2f}</h3>
            <p>{get_string('products_metric_avg_price', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_inventory = filtered_df['inventory_count'].sum()
        st.markdown(f"""
        <div class="metric-box">
            <h3>{total_inventory:,}</h3>
            <p>{get_string('products_metric_total_inventory', st.session_state.language)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Alerta de inventario bajo
    create_low_inventory_alert(filtered_df)
    
    # Visualizaciones
    st.markdown(f"### {get_string('products_analysis', st.session_state.language)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top productos más vendidos (simulado)
        top_products_chart = create_top_products_chart(filtered_df, data['orders'], chart_template, st.session_state.language)
        st.plotly_chart(top_products_chart, use_container_width=True)
    
    with col2:
        # Distribución de precios
        price_dist_chart = create_price_distribution(filtered_df, chart_template, st.session_state.language)
        st.plotly_chart(price_dist_chart, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Productos por categoría
        category_chart = create_category_donut(filtered_df, chart_template, st.session_state.language)
        st.plotly_chart(category_chart, use_container_width=True)
    
    with col2:
        # Gráfico de inventario por categoría
        inventory_by_category = filtered_df.groupby('category')['inventory_count'].sum().reset_index()
        
        fig = px.bar(
            inventory_by_category,
            x='category',
            y='inventory_count',
            title=get_string('chart_inventory_by_category', st.session_state.language),
            color='inventory_count',
            color_continuous_scale='Blues'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>' + get_string('chart_inventory_stock', st.session_state.language) + ': %{y}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            template=chart_template,
            xaxis_title=get_string('chart_inventory_category', st.session_state.language),
            yaxis_title=get_string('chart_inventory_stock', st.session_state.language),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla de productos
    st.markdown(f"### {get_string('products_catalog', st.session_state.language)}")
    
    # Opciones de ordenamiento
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**{get_string('products_table_showing', st.session_state.language, count=len(filtered_df))}**")
    
    with col2:
        sort_by = st.selectbox(
            get_string('products_table_sort_by', st.session_state.language),
            ["name", "price", "inventory_count", "category"],
            format_func=lambda x: {
                "name": get_string('products_table_sort_name', st.session_state.language),
                "price": get_string('products_table_sort_price', st.session_state.language),
                "inventory_count": get_string('products_table_sort_inventory', st.session_state.language),
                "category": get_string('products_table_sort_category', st.session_state.language)
            }[x]
        )
    
    with col3:
        sort_options = [
            get_string('products_table_sort_ascending', st.session_state.language),
            get_string('products_table_sort_descending', st.session_state.language)
        ]
        sort_order = st.selectbox(
            get_string('products_table_sort_order', st.session_state.language),
            sort_options
        )
    
    # Aplicar ordenamiento
    ascending = sort_order == get_string('products_table_sort_ascending', st.session_state.language)
    sorted_df = filtered_df.sort_values(sort_by, ascending=ascending)
    
    # Preparar datos para mostrar
    display_df = sorted_df.copy()
    display_df[get_string('products_table_product', st.session_state.language)] = display_df['name']
    display_df[get_string('products_table_category', st.session_state.language)] = display_df['category'].str.title()
    display_df[get_string('products_table_price', st.session_state.language)] = display_df['price'].apply(lambda x: f"${x:.2f}")
    display_df[get_string('products_table_inventory', st.session_state.language)] = display_df['inventory_count']
    display_df[get_string('products_table_status', st.session_state.language)] = display_df['active'].apply(
        lambda x: get_string('products_table_status_active', st.session_state.language) if x else get_string('products_table_status_inactive', st.session_state.language)
    )
    
    # Simular ventas
    import numpy as np
    np.random.seed(42)
    display_df[get_string('products_table_sales', st.session_state.language)] = np.random.randint(0, 100, len(display_df))
    
    # Mostrar tabla
    st.dataframe(
        display_df[[
            get_string('products_table_product', st.session_state.language),
            get_string('products_table_category', st.session_state.language),
            get_string('products_table_price', st.session_state.language),
            get_string('products_table_inventory', st.session_state.language),
            get_string('products_table_sales', st.session_state.language),
            get_string('products_table_status', st.session_state.language)
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            get_string('products_table_product', st.session_state.language): st.column_config.TextColumn(
                get_string('products_table_product', st.session_state.language), width="large"
            ),
            get_string('products_table_category', st.session_state.language): st.column_config.TextColumn(
                get_string('products_table_category', st.session_state.language), width="medium"
            ),
            get_string('products_table_price', st.session_state.language): st.column_config.TextColumn(
                get_string('products_table_price', st.session_state.language), width="small"
            ),
            get_string('products_table_inventory', st.session_state.language): st.column_config.NumberColumn(
                get_string('products_table_inventory', st.session_state.language), width="small"
            ),
            get_string('products_table_sales', st.session_state.language): st.column_config.NumberColumn(
                get_string('products_table_sales', st.session_state.language), width="small"
            ),
            get_string('products_table_status', st.session_state.language): st.column_config.TextColumn(
                get_string('products_table_status', st.session_state.language), width="medium"
            )
        }
    )
    
    # Información adicional
    st.markdown(f"### {get_string('products_info', st.session_state.language)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **{get_string('products_info_statistics', st.session_state.language)}**
        - {get_string('products_info_showing', st.session_state.language)}: {len(filtered_df)}
        - {get_string('products_info_total', st.session_state.language)}: {len(products_df)}
        - {get_string('products_info_filters_applied', st.session_state.language)}: {4 - [selected_category, selected_status, search_term, price_range].count(None)}
        """)
    
    with col2:
        categories_count = filtered_df['category'].value_counts()
        most_common_category = categories_count.index[0] if len(categories_count) > 0 else "N/A"
        
        st.info(f"""
        **{get_string('products_info_categories', st.session_state.language)}**
        - {get_string('products_info_common_category', st.session_state.language)}: {most_common_category.title()}
        - {get_string('products_info_unique_categories', st.session_state.language)}: {filtered_df['category'].nunique()}
        - {get_string('products_info_highest_price', st.session_state.language)}: €{filtered_df['price'].max():.2f}
        """)

if __name__ == "__main__":
    main()
