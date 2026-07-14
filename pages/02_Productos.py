"""
Página de Análisis de Productos
Gestión y análisis completo de productos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_generator import get_all_data
from utils.chart_utils import create_top_products_chart, create_price_distribution, create_category_donut

st.set_page_config(page_title="Productos", page_icon="📦", layout="wide")

# Verificar autenticación
st.page_link("app.py", label="Volver a dash")

# CSS personalizado
st.markdown("""
<style>
    .product-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .filter-container {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        color: #1f2937;
    }
    
    .metric-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #3b82f6;
        color: #1f2937;
    }
    
    .alert-box {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1f2937;
    }
    
    .success-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #1f2937;
    }
    
    .add-product-form {
        background: #f8fafc;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin: 2rem 0;
        color: #1f2937;
    }
    
    .form-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

def load_products_data():
    """Carga y procesa los datos de productos con session_state para persistencia"""
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
            st.info(f"🔍 Debug: Se encontraron {len(st.session_state.added_products)} productos agregados en session_state")
            # Convertir productos agregados a DataFrame
            added_df = pd.DataFrame(st.session_state.added_products)
            # Combinar con productos originales
            combined_products = pd.concat([original_products, added_df], ignore_index=True)
        else:
            combined_products = original_products
        
        # Debug: mostrar total de productos
        st.info(f"🔍 Debug: Total de productos (originales + agregados): {len(combined_products)}")
        
        # Actualizar los datos con la lista combinada
        updated_data = st.session_state.products_data.copy()
        updated_data['products'] = combined_products
        
        return updated_data
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None

def create_low_inventory_alert(products_df, threshold=10):
    """Crea alerta de productos con bajo inventario"""
    low_stock = products_df[products_df['inventory_count'] < threshold]
    
    if len(low_stock) > 0:
        st.markdown(f"""
        <div class="alert-box">
            <h4>⚠️ Alerta de Inventario Bajo</h4>
            <p><strong>{len(low_stock)} productos</strong> tienen menos de {threshold} unidades en stock.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar productos con bajo stock
        with st.expander(f"Ver {len(low_stock)} productos con bajo inventario"):
            display_low_stock = low_stock[['name', 'category', 'inventory_count', 'price']].copy()
            display_low_stock['Producto'] = display_low_stock['name']
            display_low_stock['Categoría'] = display_low_stock['category'].str.title()
            display_low_stock['Stock'] = display_low_stock['inventory_count']
            display_low_stock['Precio'] = display_low_stock['price'].apply(lambda x: f"€{x:.2f}")
            
            st.dataframe(
                display_low_stock[['Producto', 'Categoría', 'Stock', 'Precio']],
                use_container_width=True,
                hide_index=True
            )
    else:
        st.markdown("""
        <div class="success-box">
            <h4>✅ Inventario Saludable</h4>
            <p>Todos los productos tienen stock suficiente.</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Header de la página
    st.markdown("""
    <div class="product-header">
        <h1>📦 Análisis de Productos</h1>
        <p>Gestión completa del catálogo de productos y análisis de performance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    data = load_products_data()
    if data is None:
        return
    
    products_df = data['products']
    
    # Sección de filtros
    st.markdown("### 🔍 Filtros y Búsqueda")
    
    with st.container():
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Filtro por categoría
            categories = ['Todas'] + list(products_df['category'].unique())
            selected_category = st.selectbox("Categoría", categories)
        
        with col2:
            # Filtro por rango de precio
            min_price = float(products_df['price'].min())
            max_price = float(products_df['price'].max())
            price_range = st.slider(
                "Rango de Precio (€)", 
                min_value=min_price, 
                max_value=max_price, 
                value=(min_price, max_price)
            )
        
        with col3:
            # Filtro por estado
            status_options = ['Todos', 'Activos', 'Inactivos']
            selected_status = st.selectbox("Estado", status_options)
        
        with col4:
            # Buscador
            search_term = st.text_input("🔍 Buscar producto", placeholder="Nombre del producto...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Sección para agregar nuevos productos
    st.markdown("### ➕ Agregar Nuevo Producto")
    
    with st.expander("🆕 Formulario para Agregar Producto", expanded=True):
        st.markdown("""
        <div class="add-product-form">
            <div class="form-header">
                <h3>📦 Nuevo Producto</h3>
                <p>Complete la información del producto</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input("Nombre del Producto *", placeholder="Ej: iPhone 15 Pro")
                product_category = st.selectbox(
                    "Categoría *", 
                    options=['electronics', 'clothing', 'books', 'home', 'sports', 'beauty']
                )
                product_price = st.number_input("Precio (USD) *", min_value=0.01, value=100.00, step=0.01)
            
            with col2:
                product_inventory = st.number_input("Cantidad en Inventario *", min_value=0, value=50, step=1)
                product_active = st.checkbox("Producto Activo", value=True)
                product_description = st.text_area("Descripción", placeholder="Descripción del producto...")
            
            submitted = st.form_submit_button("✅ Agregar Producto", use_container_width=True)
            
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
                    
                    st.success(f"✅ Producto '{product_name}' agregado exitosamente!")
                    st.info("💡 El producto se ha agregado a la lista y será visible inmediatamente.")
                    
                    # Mostrar resumen del producto agregado
                    st.markdown("**📋 Resumen del Producto Agregado:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Nombre:** {product_name}")
                        st.write(f"**Categoría:** {product_category.title()}")
                        st.write(f"**Precio:** USD {product_price:.2f}")
                    with col2:
                        st.write(f"**Inventario:** {product_inventory} unidades")
                        st.write(f"**Estado:** {'Activo' if product_active else 'Inactivo'}")
                        st.write(f"**Descripción:** {product_description if product_description else 'Sin descripción'}")
                    
                    # Forzar rerun para actualizar la página
                    st.rerun()
                else:
                    st.error("❌ Por favor complete todos los campos obligatorios (*)")
    
    # Aplicar filtros
    filtered_df = products_df.copy()
    
    if selected_category != 'Todas':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= price_range[0]) & 
        (filtered_df['price'] <= price_range[1])
    ]
    
    if selected_status == 'Activos':
        filtered_df = filtered_df[filtered_df['active'] == True]
    elif selected_status == 'Inactivos':
        filtered_df = filtered_df[filtered_df['active'] == False]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False, na=False)
        ]
    
    # Métricas de productos
    st.markdown("### 📊 Métricas de Productos")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-box">
            <h3>{}</h3>
            <p>Total Productos</p>
        </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    
    with col2:
        active_products = len(filtered_df[filtered_df['active'] == True])
        st.markdown("""
        <div class="metric-box">
            <h3>{}</h3>
            <p>Productos Activos</p>
        </div>
        """.format(active_products), unsafe_allow_html=True)
    
    with col3:
        avg_price = filtered_df['price'].mean()
        st.markdown("""
        <div class="metric-box">
            <h3>€{:.2f}</h3>
            <p>Precio Promedio</p>
        </div>
        """.format(avg_price), unsafe_allow_html=True)
    
    with col4:
        total_inventory = filtered_df['inventory_count'].sum()
        st.markdown("""
        <div class="metric-box">
            <h3>{:,}</h3>
            <p>Total Inventario</p>
        </div>
        """.format(total_inventory), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Alerta de inventario bajo
    create_low_inventory_alert(filtered_df)
    
    # Visualizaciones
    st.markdown("### 📈 Análisis Visual")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top productos más vendidos (simulado)
        top_products_chart = create_top_products_chart(filtered_df, data['orders'])
        st.plotly_chart(top_products_chart, use_container_width=True)
    
    with col2:
        # Distribución de precios
        price_dist_chart = create_price_distribution(filtered_df)
        st.plotly_chart(price_dist_chart, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Productos por categoría
        category_chart = create_category_donut(filtered_df)
        st.plotly_chart(category_chart, use_container_width=True)
    
    with col2:
        # Gráfico de inventario por categoría
        inventory_by_category = filtered_df.groupby('category')['inventory_count'].sum().reset_index()
        
        fig = px.bar(
            inventory_by_category,
            x='category',
            y='inventory_count',
            title='Inventario Total por Categoría',
            color='inventory_count',
            color_continuous_scale='Blues'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Inventario: %{y}<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            template="plotly_white",
            xaxis_title="Categoría",
            yaxis_title="Unidades en Stock",
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla de productos
    st.markdown("### 📋 Catálogo de Productos")
    
    # Opciones de ordenamiento
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Mostrando {len(filtered_df)} productos**")
    
    with col2:
        sort_by = st.selectbox(
            "Ordenar por:",
            ["name", "price", "inventory_count", "category"],
            format_func=lambda x: {
                "name": "Nombre",
                "price": "Precio", 
                "inventory_count": "Inventario",
                "category": "Categoría"
            }[x]
        )
    
    with col3:
        sort_order = st.selectbox("Orden:", ["Ascendente", "Descendente"])
    
    # Aplicar ordenamiento
    ascending = sort_order == "Ascendente"
    sorted_df = filtered_df.sort_values(sort_by, ascending=ascending)
    
    # Preparar datos para mostrar
    display_df = sorted_df.copy()
    display_df['Producto'] = display_df['name']
    display_df['Categoría'] = display_df['category'].str.title()
    display_df['Precio'] = display_df['price'].apply(lambda x: f"${x:.2f}")
    display_df['Inventario'] = display_df['inventory_count']
    display_df['Estado'] = display_df['active'].apply(lambda x: "✅ Activo" if x else "❌ Inactivo")
    
    # Simular ventas
    import numpy as np
    np.random.seed(42)
    display_df['Ventas'] = np.random.randint(0, 100, len(display_df))
    
    # Mostrar tabla
    st.dataframe(
        display_df[['Producto', 'Categoría', 'Precio', 'Inventario', 'Ventas', 'Estado']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Producto": st.column_config.TextColumn("Producto", width="large"),
            "Categoría": st.column_config.TextColumn("Categoría", width="medium"),
            "Precio": st.column_config.TextColumn("Precio", width="small"),
            "Inventario": st.column_config.NumberColumn("Inventario", width="small"),
            "Ventas": st.column_config.NumberColumn("Ventas", width="small"),
            "Estado": st.column_config.TextColumn("Estado", width="medium")
        }
    )
    
    # Información adicional
    st.markdown("### ℹ️ Información Adicional")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **📊 Estadísticas de Filtrado:**
        - Productos mostrados: {len(filtered_df)}
        - Productos totales: {len(products_df)}
        - Filtros aplicados: {4 - [selected_category, selected_status, search_term, price_range].count(None)}
        """)
    
    with col2:
        categories_count = filtered_df['category'].value_counts()
        most_common_category = categories_count.index[0] if len(categories_count) > 0 else "N/A"
        
        st.info(f"""
        **🏷️ Análisis de Categorías:**
        - Categoría más común: {most_common_category.title()}
        - Categorías únicas: {filtered_df['category'].nunique()}
        - Precio más alto: €{filtered_df['price'].max():.2f}
        """)

if __name__ == "__main__":
    main()
