"""
Generador de datos falsos para el Dashboard del Chatbot de Ventas con IA
Genera datos realistas para todas las tablas del sistema
"""

import pandas as pd
import numpy as np
from faker import Faker
import uuid
import json
import random
from datetime import datetime, timedelta
import streamlit as st

# Configurar Faker en español
fake = Faker('es_ES')
Faker.seed(42)  # Para datos consistentes
np.random.seed(42)
random.seed(42)

@st.cache_data
def generate_customers(n=50):
    """Genera datos falsos para la tabla CUSTOMERS"""
    customers = []
    
    for _ in range(n):
        customer_id = str(uuid.uuid4())
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Generar número de pedidos para segmentación
        total_orders = random.randint(0, 15)
        
        # Segmentación automática
        if total_orders == 0:
            segmento = "Nuevo"
        elif 1 <= total_orders <= 4:
            segmento = "Frecuente"
        else:
            segmento = "VIP"
        
        # Generar metadata realista
        metadata = {
            "preferences": {
                "categories": random.sample(["electrónica", "ropa", "hogar", "deportes", "belleza"], 
                                          random.randint(1, 3)),
                "price_range": random.choice(["bajo", "medio", "alto"]),
                "communication_channel": random.choice(["whatsapp", "email", "sms"])
            },
            "purchase_history": {
                "total_orders": total_orders,
                "avg_order_value": round(random.uniform(25, 500), 2),
                "last_purchase_days_ago": random.randint(1, 365)
            },
            "behavior": {
                "cart_abandonment_rate": round(random.uniform(0.1, 0.8), 2),
                "response_time_hours": random.randint(1, 48),
                "satisfaction_score": round(random.uniform(3.0, 5.0), 1)
            }
        }
        
        customers.append({
            'id': customer_id,
            'phone_number': f"+34{fake.random_number(digits=9, fix_len=True)}",
            'email': f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}",
            'first_name': first_name,
            'last_name': last_name,
            'country': random.choice(['España', 'Francia', 'Italia', 'Portugal', 'Alemania', 'Reino Unido']),
            'created_at': fake.date_time_between(start_date='-2y', end_date='now'),
            'segmento': segmento,
            'metadata': json.dumps(metadata)
        })
    
    return pd.DataFrame(customers)

@st.cache_data
def generate_products(n=40):
    """Genera datos falsos para la tabla PRODUCTS"""
    products = []
    
    categories = {
        "electrónica": ["smartphone", "laptop", "tablet", "auriculares", "smartwatch", "cámara"],
        "ropa": ["camiseta", "pantalón", "vestido", "chaqueta", "zapatos", "bolso"],
        "hogar": ["sofá", "mesa", "lámpara", "alfombra", "cojín", "espejo"],
        "deportes": ["zapatillas", "ropa deportiva", "pelota", "raqueta", "pesas", "bicicleta"],
        "belleza": ["crema facial", "perfume", "maquillaje", "champú", "mascarilla", "sérum"]
    }
    
    for _ in range(n):
        category = random.choice(list(categories.keys()))
        product_type = random.choice(categories[category])
        brand = fake.company()
        
        # Generar precio según categoría
        price_ranges = {
            "electrónica": (50, 1500),
            "ropa": (15, 200),
            "hogar": (25, 800),
            "deportes": (20, 300),
            "belleza": (10, 150)
        }
        
        min_price, max_price = price_ranges[category]
        price = round(random.uniform(min_price, max_price), 2)
        
        products.append({
            'id': str(uuid.uuid4()),
            'shopify_product_id': f"shopify_{fake.random_number(digits=8)}",
            'name': f"{brand} {product_type.title()}",
            'description': fake.text(max_nb_chars=200),
            'price': price,
            'category': category,
            'tags': json.dumps(random.sample([
                "nuevo", "oferta", "bestseller", "premium", "eco-friendly", 
                "limitado", "trending", "descuento"
            ], random.randint(1, 4))),
            'inventory_count': random.randint(0, 100),
            'image_url': f"https://picsum.photos/300/300?random={random.randint(1, 1000)}",
            'active': random.choice([True, True, True, False])  # 75% activos
        })
    
    return pd.DataFrame(products)

@st.cache_data
def generate_conversations(customers_df, n=200):
    """Genera datos falsos para la tabla CONVERSATIONS"""
    conversations = []
    
    intents = ["consulta-producto", "seguimiento-pedido", "procesar-pago", "carrito-abandonado"]
    message_types = ["user", "bot", "system"]
    
    # Mensajes de ejemplo por intent
    messages_by_intent = {
        "consulta-producto": [
            "¿Tienen smartphones en oferta?",
            "Me interesa una laptop para trabajo",
            "¿Qué colores tienen en camisetas?",
            "Busco zapatos deportivos talla 42"
        ],
        "seguimiento-pedido": [
            "¿Dónde está mi pedido?",
            "¿Cuándo llega mi compra?",
            "No he recibido el tracking",
            "Mi pedido está retrasado"
        ],
        "procesar-pago": [
            "¿Aceptan tarjeta de crédito?",
            "Problema con el pago",
            "¿Puedo pagar a plazos?",
            "Error en la transacción"
        ],
        "carrito-abandonado": [
            "Se me olvidó completar la compra",
            "¿Siguen disponibles los productos?",
            "Quiero finalizar mi pedido",
            "Problemas técnicos al pagar"
        ]
    }
    
    for _ in range(n):
        customer_id = random.choice(customers_df['id'].tolist())
        intent = random.choice(intents)
        message_type = random.choice(message_types)
        
        if message_type == "user":
            message_text = random.choice(messages_by_intent[intent])
        elif message_type == "bot":
            message_text = "¡Hola! Te ayudo con tu consulta. ¿En qué puedo asistirte?"
        else:
            message_text = "Sistema: Conversación iniciada"
        
        conversations.append({
            'id': str(uuid.uuid4()),
            'customer_id': customer_id,
            'session_id': f"session_{fake.random_number(digits=10)}",
            'message_text': message_text,
            'message_type': message_type,
            'intent': intent,
            'confidence_score': round(random.uniform(0.6, 1.0), 2),
            'created_at': fake.date_time_between(start_date='-30d', end_date='now'),
            'processed': random.choice([True, False])
        })
    
    return pd.DataFrame(conversations)

@st.cache_data
def generate_shopping_carts(customers_df, products_df, n=80):
    """Genera datos falsos para la tabla SHOPPING_CARTS"""
    carts = []
    
    for _ in range(n):
        customer_id = random.choice(customers_df['id'].tolist())
        
        # Generar items del carrito
        num_items = random.randint(1, 5)
        cart_items = []
        total_amount = 0
        
        selected_products = random.sample(products_df.to_dict('records'), num_items)
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            item_total = product['price'] * quantity
            total_amount += item_total
            
            cart_items.append({
                'product_id': product['id'],
                'product_name': product['name'],
                'quantity': quantity,
                'unit_price': product['price'],
                'total_price': item_total
            })
        
        # 60% completados, 40% abandonados
        status = random.choices(
            ["completed", "abandoned", "active"], 
            weights=[60, 35, 5]
        )[0]
        
        created_at = fake.date_time_between(start_date='-60d', end_date='now')
        abandoned_at = None
        
        if status == "abandoned":
            abandoned_at = created_at + timedelta(
                minutes=random.randint(5, 1440)  # Entre 5 minutos y 24 horas
            )
        
        carts.append({
            'id': str(uuid.uuid4()),
            'customer_id': customer_id,
            'session_id': f"session_{fake.random_number(digits=10)}",
            'cart_items': json.dumps(cart_items),
            'total_amount': round(total_amount, 2),
            'status': status,
            'created_at': created_at,
            'abandoned_at': abandoned_at,
            'recordatorio_enviado': False  # New field for reminder status
        })
    
    return pd.DataFrame(carts)

@st.cache_data
def generate_orders(customers_df, carts_df, n=60):
    """Genera datos falsos para la tabla ORDERS"""
    orders = []
    
    # Filtrar solo carritos completados
    completed_carts = carts_df[carts_df['status'] == 'completed']
    
    if len(completed_carts) < n:
        # Si no hay suficientes carritos completados, usar algunos abandonados
        additional_carts = carts_df[carts_df['status'] == 'abandoned'].head(n - len(completed_carts))
        selected_carts = pd.concat([completed_carts, additional_carts])
    else:
        selected_carts = completed_carts.head(n)
    
    statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    metodos_pago = ["Yape/Plin", "Tarjeta", "Contraentrega"]
    
    for _, cart in selected_carts.iterrows():
        status = random.choices(
            statuses,
            weights=[10, 15, 25, 45, 5]  # Mayoría entregados
        )[0]
        
        metodo_pago = random.choice(metodos_pago)
        
        # Asignar estado_pago según método y estado del pedido
        if metodo_pago == "Contraentrega":
            estado_pago = "Pago pendiente"
        else:
            estado_pago = "Pago confirmado" if status in ["shipped", "delivered"] else "Pago pendiente"
        
        created_at = cart['created_at'] + timedelta(minutes=random.randint(1, 30))
        completed_at = None
        
        if status in ["delivered", "cancelled"]:
            completed_at = created_at + timedelta(
                days=random.randint(1, 14)
            )
        
        # Generar dirección de envío
        shipping_address = {
            "street": fake.street_address(),
            "city": fake.city(),
            "postal_code": fake.postcode(),
            "country": "España"
        }
        
        orders.append({
            'id': str(uuid.uuid4()),
            'customer_id': cart['customer_id'],
            'cart_id': cart['id'],
            'stripe_payment_id': f"pi_{fake.random_number(digits=24)}",
            'shopify_order_id': f"order_{fake.random_number(digits=8)}",
            'total_amount': cart['total_amount'],
            'status': status,
            'metodo_pago': metodo_pago,
            'estado_pago': estado_pago,
            'shipping_address': json.dumps(shipping_address),
            'created_at': created_at,
            'completed_at': completed_at
        })
    
    return pd.DataFrame(orders)

@st.cache_data
def generate_shipments(orders_df, n=40):
    """Genera datos falsos para la tabla SHIPMENTS"""
    shipments = []
    
    # Solo pedidos que han sido enviados o entregados
    shipped_orders = orders_df[orders_df['status'].isin(['shipped', 'delivered'])].head(n)
    
    carriers = ["DHL", "FedEx", "UPS", "Correo Nacional"]
    
    for _, order in shipped_orders.iterrows():
        carrier = random.choice(carriers)
        
        # Generar número de tracking realista
        tracking_prefixes = {
            "DHL": "DHL",
            "FedEx": "FX",
            "UPS": "1Z",
            "Correo Nacional": "CN"
        }
        
        tracking_number = f"{tracking_prefixes[carrier]}{fake.random_number(digits=12)}"
        
        status = "delivered" if order['status'] == 'delivered' else random.choice(["pending", "in_transit", "delivered"])
        
        estimated_delivery = order['created_at'] + timedelta(days=random.randint(2, 7))
        actual_delivery = None
        
        if status == "delivered":
            actual_delivery = estimated_delivery + timedelta(days=random.randint(-1, 2))
        
        shipments.append({
            'id': str(uuid.uuid4()),
            'order_id': order['id'],
            'tracking_number': tracking_number,
            'carrier': carrier,
            'status': status,
            'estimated_delivery': estimated_delivery,
            'actual_delivery': actual_delivery
        })
    
    return pd.DataFrame(shipments)

@st.cache_data
def generate_recommendations(customers_df, products_df, n=100):
    """Genera datos falsos para la tabla RECOMMENDATIONS"""
    recommendations = []
    
    reasons = [
        "Basado en compras anteriores",
        "Productos populares en tu categoría",
        "Oferta especial para ti",
        "Complementa tu última compra",
        "Tendencia en tu ciudad",
        "Recomendado por otros clientes"
    ]
    
    for _ in range(n):
        customer_id = random.choice(customers_df['id'].tolist())
        product_id = random.choice(products_df['id'].tolist())
        
        recommendations.append({
            'id': str(uuid.uuid4()),
            'customer_id': customer_id,
            'product_id': product_id,
            'recommendation_score': round(random.uniform(0.5, 1.0), 2),
            'reason': random.choice(reasons),
            'shown_at': fake.date_time_between(start_date='-30d', end_date='now'),
            'clicked': random.choice([True, False])
        })
    
    return pd.DataFrame(recommendations)

@st.cache_data
def get_all_data():
    """Genera y retorna todos los datasets"""
    print("Generando datos falsos...")
    
    # Generar datos en orden de dependencias
    customers = generate_customers(50)
    products = generate_products(40)
    conversations = generate_conversations(customers, 200)
    carts = generate_shopping_carts(customers, products, 80)
    orders = generate_orders(customers, carts, 60)
    shipments = generate_shipments(orders, 40)
    recommendations = generate_recommendations(customers, products, 100)
    
    return {
        'customers': customers,
        'products': products,
        'conversations': conversations,
        'carts': carts,
        'orders': orders,
        'shipments': shipments,
        'recommendations': recommendations
    }

# Función auxiliar para obtener métricas calculadas
@st.cache_data
def get_calculated_metrics():
    """Calcula métricas derivadas de los datos"""
    data = get_all_data()
    
    # Métricas básicas
    total_sales = data['orders']['total_amount'].sum()
    total_customers = len(data['customers'])
    total_orders = len(data['orders'])
    
    # Tasa de conversión (pedidos completados / carritos totales)
    completed_orders = len(data['orders'][data['orders']['status'] == 'delivered'])
    total_carts = len(data['carts'])
    conversion_rate = (completed_orders / total_carts * 100) if total_carts > 0 else 0
    
    # Carritos abandonados
    abandoned_carts = len(data['carts'][data['carts']['status'] == 'abandoned'])
    abandoned_value = data['carts'][data['carts']['status'] == 'abandoned']['total_amount'].sum()
    
    # Valor promedio por pedido
    avg_order_value = data['orders']['total_amount'].mean() if len(data['orders']) > 0 else 0
    
    return {
        'total_sales': total_sales,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'conversion_rate': conversion_rate,
        'abandoned_carts': abandoned_carts,
        'abandoned_value': abandoned_value,
        'avg_order_value': avg_order_value
    }