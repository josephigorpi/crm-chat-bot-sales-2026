"""
Generador de reportes PDF para el Dashboard del Chatbot de Ventas
Utiliza FPDF para crear reportes profesionales
"""

from fpdf import FPDF
import pandas as pd
from datetime import datetime
import json
import io
import base64

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """Encabezado del PDF"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Dashboard Chatbot de Ventas - Reporte', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Generado el: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        """Pie de página del PDF"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def add_title(self, title):
        """Añade un título de sección"""
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
        
    def add_subtitle(self, subtitle):
        """Añade un subtítulo"""
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, subtitle, 0, 1, 'L')
        self.ln(3)
        
    def add_metric_box(self, label, value, x_pos=None):
        """Añade una caja de métrica"""
        if x_pos:
            self.set_x(x_pos)
        
        y_position = self.get_y()
        box_width = 50
        box_height = 25
    
        # Dibujar el rectángulo
        self.set_fill_color(240, 240, 240)
        self.rect(x_position, y_position, box_width, box_height, 'F')
        
        # Dibujar borde
        self.set_draw_color(200, 200, 200)
        self.rect(x_position, y_position, box_width, box_height, 'D')
        
        # Texto de la etiqueta (más pequeño)
        self.set_font('Arial', 'B', 8)
        self.set_xy(x_position + 2, y_position + 2)
        self.cell(box_width - 4, 6, label, 0, 1, 'C')
        
        # Texto del valor (más grande)
        self.set_font('Arial', 'B', 12)
        self.set_xy(x_position + 2, y_position + 10)
        self.cell(box_width - 4, 10, str(value), 0, 1, 'C')
        
        # Restaurar posición Y
        self.set_y(y_position + box_height)
        
        return x_position + box_width  # Retornar la siguiente posición X
        
    def add_table(self, headers, data, col_widths=None):
        """Añade una tabla al PDF"""
        if not col_widths:
            col_widths = [190 / len(headers)] * len(headers)
        
        # Encabezados
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(230, 230, 230)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, str(header), 1, 0, 'C', True)
        self.ln()
        
        # Datos
        self.set_font('Arial', '', 9)
        self.set_fill_color(255, 255, 255)
        
        for row in data:
            for i, cell in enumerate(row):
                # Truncar texto si es muy largo
                cell_text = str(cell)
                if len(cell_text) > 25:
                    cell_text = cell_text[:22] + "..."
                    
                self.cell(col_widths[i], 6, cell_text, 1, 0, 'C')
            self.ln()

def generate_sales_report(data, start_date=None, end_date=None):
    """Genera reporte de ventas completo"""
    pdf = ReportPDF()
    pdf.add_page()
    
    # Título del reporte
    pdf.add_title("REPORTE DE VENTAS COMPLETO")
    
    if start_date and end_date:
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, f"Período: {start_date} - {end_date}", 0, 1, 'L')
        pdf.ln(5)
    
    # Métricas principales
    pdf.add_subtitle("Métricas Principales")
    
    orders_df = data['orders']
    total_sales = orders_df['total_amount'].sum()
    total_orders = len(orders_df)
    avg_order = orders_df['total_amount'].mean()
    
    # Añadir métricas en cajas
    y_pos = pdf.get_y()
    pdf.add_metric_box("Total Ventas", f"USD {total_sales:,.2f}", 10)
    pdf.set_xy(65, y_pos)
    pdf.add_metric_box("Total Pedidos", f"{total_orders}", 65)
    pdf.set_xy(120, y_pos)
    pdf.add_metric_box("Promedio", f"USD {avg_order:.2f}", 120)
    
    pdf.ln(25)
    
    # Ventas por estado
    pdf.add_subtitle("Distribución por Estado")
    status_counts = orders_df['status'].value_counts()
    
    status_data = []
    for status, count in status_counts.items():
        percentage = (count / total_orders * 100)
        status_data.append([status.title(), count, f"{percentage:.1f}%"])
    
    pdf.add_table(
        ["Estado", "Cantidad", "Porcentaje"],
        status_data,
        [60, 40, 40]
    )
    
    pdf.ln(10)
    
    # Top productos (simulado)
    pdf.add_subtitle("Top 10 Productos")
    products_df = data['products']
    top_products = products_df.head(10)
    
    product_data = []
    for _, product in top_products.iterrows():
        product_data.append([
            product['name'][:30],
            product['category'].title(),
            f"USD {product['price']:.2f}"
        ])
    
    pdf.add_table(
        ["Producto", "Categoría", "Precio"],
        product_data,
        [100, 50, 40]
    )
    
    return pdf

def generate_customer_report(data, start_date=None, end_date=None):
    """Genera reporte de análisis de clientes"""
    pdf = ReportPDF()
    pdf.add_page()
    
    pdf.add_title("ANÁLISIS DE COMPORTAMIENTO DEL CLIENTE")
    
    customers_df = data['customers']
    orders_df = data['orders']
    
    # Métricas de clientes
    pdf.add_subtitle("Métricas de Clientes")
    
    total_customers = len(customers_df)
    active_customers = len(orders_df['customer_id'].unique())
    new_customers = len(customers_df[
        pd.to_datetime(customers_df['created_at']) >= 
        datetime.now() - pd.Timedelta(days=30)
    ])
    
    y_pos = pdf.get_y()
    pdf.add_metric_box("Total Clientes", f"{total_customers}", 10)
    pdf.set_xy(65, y_pos)
    pdf.add_metric_box("Activos", f"{active_customers}", 65)
    pdf.set_xy(120, y_pos)
    pdf.add_metric_box("Nuevos (30d)", f"{new_customers}", 120)
    
    pdf.ln(25)
    
    # Top clientes por valor
    pdf.add_subtitle("Top 10 Clientes por Valor")
    customer_values = orders_df.groupby('customer_id')['total_amount'].sum().reset_index()
    customer_values = customer_values.merge(
        customers_df[['id', 'first_name', 'last_name', 'email']], 
        left_on='customer_id', 
        right_on='id'
    )
    top_customers = customer_values.nlargest(10, 'total_amount')
    
    customer_data = []
    for _, customer in top_customers.iterrows():
        customer_data.append([
            f"{customer['first_name']} {customer['last_name']}",
            customer['email'][:25],
            f"USD {customer['total_amount']:.2f}"
        ])
    
    pdf.add_table(
        ["Cliente", "Email", "Total Compras"],
        customer_data,
        [70, 70, 50]
    )
    
    return pdf

def generate_product_report(data, start_date=None, end_date=None):
    """Genera reporte de performance de productos"""
    pdf = ReportPDF()
    pdf.add_page()
    
    pdf.add_title("PERFORMANCE DE PRODUCTOS")
    
    products_df = data['products']
    
    # Métricas de productos
    pdf.add_subtitle("Métricas Generales")
    
    total_products = len(products_df)
    active_products = len(products_df[products_df['active'] == True])
    low_inventory = len(products_df[products_df['inventory_count'] < 10])
    
    y_pos = pdf.get_y()
    pdf.add_metric_box("Total Productos", f"{total_products}", 10)
    pdf.set_xy(65, y_pos)
    pdf.add_metric_box("Activos", f"{active_products}", 65)
    pdf.set_xy(120, y_pos)
    pdf.add_metric_box("Bajo Stock", f"{low_inventory}", 120)
    
    pdf.ln(25)
    
    # Productos por categoría
    pdf.add_subtitle("Distribución por Categoría")
    category_counts = products_df['category'].value_counts()
    
    category_data = []
    for category, count in category_counts.items():
        avg_price = products_df[products_df['category'] == category]['price'].mean()
        category_data.append([
            category.title(),
            count,
            f"USD {avg_price:.2f}"
        ])
    
    pdf.add_table(
        ["Categoría", "Cantidad", "Precio Promedio"],
        category_data,
        [70, 40, 50]
    )
    
    pdf.ln(10)
    
    # Productos con bajo inventario
    pdf.add_subtitle("Productos con Bajo Inventario (< 10 unidades)")
    low_stock = products_df[products_df['inventory_count'] < 10].head(10)
    
    if len(low_stock) > 0:
        stock_data = []
        for _, product in low_stock.iterrows():
            stock_data.append([
                product['name'][:35],
                product['inventory_count'],
                f"USD {product['price']:.2f}"
            ])
        
        pdf.add_table(
            ["Producto", "Stock", "Precio"],
            stock_data,
            [120, 35, 35]
        )
    else:
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, "No hay productos con bajo inventario", 0, 1, 'C')
    
    return pdf

def generate_chatbot_report(data, start_date=None, end_date=None):
    """Genera reporte de efectividad del chatbot"""
    pdf = ReportPDF()
    pdf.add_page()
    
    pdf.add_title("EFECTIVIDAD DEL CHATBOT")
    
    conversations_df = data['conversations']
    
    # Métricas del chatbot
    pdf.add_subtitle("Métricas de Conversaciones")
    
    total_conversations = len(conversations_df)
    avg_confidence = conversations_df['confidence_score'].mean()
    processed_rate = (conversations_df['processed'].sum() / total_conversations * 100)
    
    y_pos = pdf.get_y()
    pdf.add_metric_box("Total Conversaciones", f"{total_conversations}", 10)
    pdf.set_xy(65, y_pos)
    pdf.add_metric_box("Confianza Promedio", f"{avg_confidence:.2f}", 65)
    pdf.set_xy(120, y_pos)
    pdf.add_metric_box("Procesadas", f"{processed_rate:.1f}%", 120)
    
    pdf.ln(25)
    
    # Distribución por intención
    pdf.add_subtitle("Distribución por Intención")
    intent_counts = conversations_df['intent'].value_counts()
    
    intent_labels = {
        'consulta-producto': 'Consulta Producto',
        'seguimiento-pedido': 'Seguimiento Pedido',
        'procesar-pago': 'Procesar Pago',
        'carrito-abandonado': 'Carrito Abandonado'
    }
    
    intent_data = []
    for intent, count in intent_counts.items():
        label = intent_labels.get(intent, intent)
        percentage = (count / total_conversations * 100)
        avg_conf = conversations_df[conversations_df['intent'] == intent]['confidence_score'].mean()
        intent_data.append([
            label,
            count,
            f"{percentage:.1f}%",
            f"{avg_conf:.2f}"
        ])
    
    pdf.add_table(
        ["Intención", "Cantidad", "%", "Confianza"],
        intent_data,
        [70, 40, 30, 40]
    )
    
    return pdf

def generate_abandoned_carts_report(data, start_date=None, end_date=None):
    """Genera reporte de carritos abandonados"""
    pdf = ReportPDF()
    pdf.add_page()
    
    pdf.add_title("CARRITOS ABANDONADOS Y RECUPERACIÓN")
    
    carts_df = data['carts']
    
    # Métricas de carritos abandonados
    pdf.add_subtitle("Métricas de Abandono")
    
    total_carts = len(carts_df)
    abandoned_carts = len(carts_df[carts_df['status'] == 'abandoned'])
    abandoned_value = carts_df[carts_df['status'] == 'abandoned']['total_amount'].sum()
    abandonment_rate = (abandoned_carts / total_carts * 100) if total_carts > 0 else 0
    
    y_pos = pdf.get_y()
    pdf.add_metric_box("Carritos Abandonados", f"{abandoned_carts}", 10)
    pdf.set_xy(65, y_pos)
    pdf.add_metric_box("Valor Perdido", f"USD {abandoned_value:,.0f}", 65)
    pdf.set_xy(120, y_pos)
    pdf.add_metric_box("Tasa Abandono", f"{abandonment_rate:.1f}%", 120)
    
    pdf.ln(25)
    
    # Top carritos abandonados por valor
    pdf.add_subtitle("Top 10 Carritos Abandonados por Valor")
    abandoned = carts_df[carts_df['status'] == 'abandoned'].nlargest(10, 'total_amount')
    
    if len(abandoned) > 0:
        customers_df = data['customers']
        abandoned_with_customer = abandoned.merge(
            customers_df[['id', 'first_name', 'last_name']], 
            left_on='customer_id', 
            right_on='id'
        )
        
        abandoned_data = []
        for _, cart in abandoned_with_customer.iterrows():
            days_ago = (datetime.now() - pd.to_datetime(cart['created_at'])).days
            abandoned_data.append([
                f"{cart['first_name']} {cart['last_name']}",
                f"USD {cart['total_amount']:.2f}",
                f"{days_ago} días"
            ])
        
        pdf.add_table(
            ["Cliente", "Valor", "Hace"],
            abandoned_data,
            [80, 50, 50]
        )
    else:
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, "No hay carritos abandonados registrados", 0, 1, 'C')
    
    return pdf

def pdf_to_bytes(pdf):
    """Convierte PDF a bytes para descarga"""
    return bytes(pdf.output())

def create_download_link(pdf, filename, link_text=None):
    """Crea un enlace de descarga para el PDF"""
    pdf_bytes = pdf_to_bytes(pdf)
    b64 = base64.b64encode(pdf_bytes).decode()
    if link_text is None:
        link_text = f"📄 Descargar {filename}"
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">{link_text}</a>'
    return href
