"""
Página de Conversaciones y Chatbot
Análisis de efectividad del chatbot y gestión de conversaciones
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_generator import get_all_data
from utils.chart_utils import create_messages_by_hour, create_intent_distribution, create_conversation_heatmap
import qrcode
from io import BytesIO
from gtts import gTTS

st.set_page_config(page_title="Conversaciones", page_icon="💬", layout="wide")

# CSS personalizado
st.markdown("""
<style>
    .conversation-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-bubble {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #3b82f6;
        color: #1f2937;
    }
    
    .bot-bubble {
        background: #e0f2fe;
        border-left: 4px solid #0ea5e9;
        color: #1f2937;
    }
    
    .user-bubble {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        color: #1f2937;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #06b6d4;
        color: #1f2937;
    }
    
    .conversation-stats {
        background: #fafafa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: #1f2937;
    }
    
    .intent-tag {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

def load_conversation_data():
    """Carga y procesa los datos de conversaciones"""
    try:
        data = get_all_data()
        return data
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None

def calculate_chatbot_metrics(conversations_df):
    """Calcula métricas de efectividad del chatbot"""
    metrics = {}
    
    # Métricas básicas
    metrics['total_conversations'] = len(conversations_df)
    metrics['total_messages'] = len(conversations_df)  # Cada fila es un mensaje
    
    # Calcular mensajes por sesión
    messages_per_session = conversations_df.groupby('session_id').size()
    metrics['avg_messages_per_conversation'] = messages_per_session.mean()
    
    # Tasa de resolución (simulada)
    import numpy as np
    np.random.seed(42)
    conversations_df['resolved'] = np.random.choice([True, False], size=len(conversations_df), p=[0.75, 0.25])
    metrics['resolution_rate'] = (conversations_df['resolved'].sum() / len(conversations_df)) * 100
    
    # Satisfacción del cliente (simulada)
    conversations_df['satisfaction_score'] = np.random.uniform(3.0, 5.0, len(conversations_df))
    metrics['avg_satisfaction'] = conversations_df['satisfaction_score'].mean()
    
    # Tiempo promedio de respuesta (simulado en segundos)
    conversations_df['avg_response_time'] = np.random.uniform(30, 300, len(conversations_df))
    metrics['avg_response_time'] = conversations_df['avg_response_time'].mean()
    
    # Agregar columnas faltantes para compatibilidad
    conversations_df['start_time'] = pd.to_datetime(conversations_df['created_at'])
    conversations_df['message_count'] = conversations_df.groupby('session_id')['session_id'].transform('count')
    
    # Conversaciones por día
    conversations_df['date'] = conversations_df['start_time'].dt.date
    metrics['conversations_per_day'] = conversations_df.groupby('date').size().mean()
    
    return metrics, conversations_df

def create_satisfaction_gauge(satisfaction_score):
    """Crea un gauge de satisfacción del cliente"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = satisfaction_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Satisfacción Promedio"},
        delta = {'reference': 4.0},
        gauge = {
            'axis': {'range': [None, 5]},
            'bar': {'color': "#3b82f6"},
            'steps': [
                {'range': [0, 2], 'color': "#fecaca"},
                {'range': [2, 3], 'color': "#fed7aa"},
                {'range': [3, 4], 'color': "#fde68a"},
                {'range': [4, 5], 'color': "#bbf7d0"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 4.5
            }
        }
    ))
    
    fig.update_layout(height=300, template="plotly_white")
    return fig

def create_response_time_chart(conversations_df):
    """Crea gráfico de tiempo de respuesta"""
    # Agrupar por hora del día
    conversations_df['hour'] = pd.to_datetime(conversations_df['start_time']).dt.hour
    hourly_response = conversations_df.groupby('hour')['avg_response_time'].mean().reset_index()
    
    fig = px.line(
        hourly_response,
        x='hour',
        y='avg_response_time',
        title='Tiempo Promedio de Respuesta por Hora',
        markers=True
    )
    
    fig.update_traces(
        line_color='#8b5cf6',
        marker_color='#8b5cf6',
        hovertemplate='<b>Hora: %{x}:00</b><br>Tiempo: %{y:.1f}s<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template="plotly_white",
        xaxis_title="Hora del Día",
        yaxis_title="Tiempo de Respuesta (segundos)",
        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
    )
    
    return fig

def create_intent_success_rate(conversations_df):
    """Crea gráfico de tasa de éxito por intención"""
    # Simular tasas de éxito por intención
    import numpy as np
    np.random.seed(42)
    
    intent_success = conversations_df.groupby('intent').agg({
        'resolved': ['count', 'sum']
    }).round(2)
    
    intent_success.columns = ['total', 'resolved']
    intent_success['success_rate'] = (intent_success['resolved'] / intent_success['total']) * 100
    intent_success = intent_success.reset_index()
    
    fig = px.bar(
        intent_success,
        x='intent',
        y='success_rate',
        title='Tasa de Éxito por Tipo de Consulta',
        color='success_rate',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Tasa de Éxito: %{y:.1f}%<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        template="plotly_white",
        xaxis_title="Tipo de Consulta",
        yaxis_title="Tasa de Éxito (%)",
        coloraxis_showscale=False
    )
    
    return fig

def display_conversation_sample(conversations_df):
    """Muestra una muestra de conversaciones"""
    st.markdown("### 💬 Muestra de Conversaciones Recientes")
    
    # Seleccionar conversaciones recientes
    recent_conversations = conversations_df.nlargest(5, 'start_time')
    
    for _, conv in recent_conversations.iterrows():
        with st.expander(f"Conversación #{conv['id']} - {conv['intent'].title()} - {conv['start_time'].strftime('%d/%m/%Y %H:%M')}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Simular mensajes de la conversación
                st.markdown(f"""
                <div class="user-bubble">
                    <strong>👤 Cliente:</strong> Hola, tengo una consulta sobre {conv['intent']}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="bot-bubble">
                    <strong>🤖 Chatbot:</strong> ¡Hola! Estaré encantado de ayudarte con tu consulta sobre {conv['intent']}. ¿Podrías darme más detalles?
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="user-bubble">
                    <strong>👤 Cliente:</strong> Necesito información específica sobre este tema.
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="bot-bubble">
                    <strong>🤖 Chatbot:</strong> Perfecto, aquí tienes la información que necesitas...
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="conversation-stats">
                    <strong>📊 Estadísticas:</strong><br>
                    • Mensajes: {int(conv['message_count'])}<br>
                    • Duración: {int(conv['avg_response_time']//60)}m {int(conv['avg_response_time']%60)}s<br>
                    • Satisfacción: {conv['satisfaction_score']:.1f}/5<br>
                    • Estado: {'✅ Resuelto' if conv['resolved'] else '❌ No resuelto'}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<span class="intent-tag">{conv["intent"].title()}</span>', unsafe_allow_html=True)

def main():
    # Header de la página
    st.markdown("""
    <div class="conversation-header">
        <h1>💬 Conversaciones y Chatbot</h1>
        <p>Análisis de efectividad del chatbot y gestión de conversaciones con clientes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Cargar datos
    data = load_conversation_data()
    if data is None:
        return
    
    conversations_df = data['conversations']
    
    # Calcular métricas del chatbot
    metrics, enriched_conversations = calculate_chatbot_metrics(conversations_df)
    
    # Filtros
    st.markdown("### 🔍 Filtros de Conversaciones")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        intents = ['Todos'] + list(enriched_conversations['intent'].unique())
        selected_intent = st.selectbox("Tipo de Consulta", intents)
    
    with col2:
        status_options = ['Todos', 'Resueltos', 'No Resueltos']
        selected_status = st.selectbox("Estado", status_options)
    
    with col3:
        date_range = st.date_input(
            "Rango de Fechas",
            value=(
                enriched_conversations['start_time'].min().date(),
                enriched_conversations['start_time'].max().date()
            ),
            min_value=enriched_conversations['start_time'].min().date(),
            max_value=enriched_conversations['start_time'].max().date()
        )
    
    with col4:
        min_satisfaction = st.slider("Satisfacción Mínima", 1.0, 5.0, 1.0, 0.1)
    
    # Aplicar filtros
    filtered_conversations = enriched_conversations.copy()
    
    if selected_intent != 'Todos':
        filtered_conversations = filtered_conversations[filtered_conversations['intent'] == selected_intent]
    
    if selected_status == 'Resueltos':
        filtered_conversations = filtered_conversations[filtered_conversations['resolved'] == True]
    elif selected_status == 'No Resueltos':
        filtered_conversations = filtered_conversations[filtered_conversations['resolved'] == False]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_conversations = filtered_conversations[
            (filtered_conversations['start_time'].dt.date >= start_date) &
            (filtered_conversations['start_time'].dt.date <= end_date)
        ]
    
    filtered_conversations = filtered_conversations[
        filtered_conversations['satisfaction_score'] >= min_satisfaction
    ]
    
    # Métricas principales
    st.markdown("### 📊 Métricas del Chatbot")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>{:,}</h3>
            <p>Conversaciones Totales</p>
        </div>
        """.format(len(filtered_conversations)), unsafe_allow_html=True)
    
    with col2:
        resolved_count = len(filtered_conversations[filtered_conversations['resolved'] == True])
        resolution_rate = (resolved_count / len(filtered_conversations)) * 100 if len(filtered_conversations) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h3>{:.1f}%</h3>
            <p>Tasa de Resolución</p>
        </div>
        """.format(resolution_rate), unsafe_allow_html=True)
    
    with col3:
        avg_satisfaction = filtered_conversations['satisfaction_score'].mean() if len(filtered_conversations) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h3>{:.1f}/5</h3>
            <p>Satisfacción Promedio</p>
        </div>
        """.format(avg_satisfaction), unsafe_allow_html=True)
    
    with col4:
        avg_response = filtered_conversations['avg_response_time'].mean() if len(filtered_conversations) > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <h3>{:.0f}s</h3>
            <p>Tiempo Respuesta</p>
        </div>
        """.format(avg_response), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Visualizaciones principales
    st.markdown("### 📈 Análisis de Conversaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Mensajes por hora
        messages_chart = create_messages_by_hour(filtered_conversations)
        st.plotly_chart(messages_chart, use_container_width=True)
    
    with col2:
        # Distribución de intenciones
        intent_chart = create_intent_distribution(filtered_conversations)
        st.plotly_chart(intent_chart, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gauge de satisfacción
        satisfaction_gauge = create_satisfaction_gauge(avg_satisfaction)
        st.plotly_chart(satisfaction_gauge, use_container_width=True)
    
    with col2:
        # Tiempo de respuesta por hora
        response_time_chart = create_response_time_chart(filtered_conversations)
        st.plotly_chart(response_time_chart, use_container_width=True)
    
    # Análisis adicional
    col1, col2 = st.columns(2)
    
    with col1:
        # Tasa de éxito por intención
        intent_success_chart = create_intent_success_rate(filtered_conversations)
        st.plotly_chart(intent_success_chart, use_container_width=True)
    
    with col2:
        # Mapa de calor de conversaciones
        conversation_heatmap = create_conversation_heatmap(filtered_conversations)
        st.plotly_chart(conversation_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Análisis de tendencias
    st.markdown("### 📊 Tendencias Temporales")
    
    # Conversaciones por día
    daily_conversations = filtered_conversations.groupby(
        filtered_conversations['start_time'].dt.date
    ).agg({
        'id': 'count',
        'resolved': 'sum',
        'satisfaction_score': 'mean'
    }).reset_index()
    
    daily_conversations.columns = ['date', 'total_conversations', 'resolved_conversations', 'avg_satisfaction']
    daily_conversations['resolution_rate'] = (daily_conversations['resolved_conversations'] / daily_conversations['total_conversations']) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_conversations['date'],
        y=daily_conversations['total_conversations'],
        mode='lines+markers',
        name='Conversaciones Totales',
        line=dict(color='#3b82f6'),
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=daily_conversations['date'],
        y=daily_conversations['resolution_rate'],
        mode='lines+markers',
        name='Tasa de Resolución (%)',
        line=dict(color='#10b981'),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Tendencia de Conversaciones y Tasa de Resolución',
        xaxis_title='Fecha',
        yaxis=dict(title='Número de Conversaciones', side='left'),
        yaxis2=dict(title='Tasa de Resolución (%)', side='right', overlaying='y'),
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Muestra de conversaciones
    display_conversation_sample(filtered_conversations)
    
    st.markdown("---")
    
    # Chatbot interactivo con flujo de pago
    st.markdown("### 🤖 Chatbot Interactivo (Demo Pago)")
    
    # Inicializar estado del chat
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "bot", "text": "¡Hola! Soy tu asistente de ventas. ¿En qué puedo ayudarte? Si quieres simular un pago, escribe 'quiero pagar'."}
        ]
    if "payment_step" not in st.session_state:
        st.session_state.payment_step = 0  # 0: inicio, 1: seleccionar método, 2: mostrar QR/confirmar
    if "selected_payment" not in st.session_state:
        st.session_state.selected_payment = None
    
    # Mostrar mensajes del chat
    for msg in st.session_state.chat_messages:
        bubble_class = "bot-bubble" if msg["role"] == "bot" else "user-bubble"
        st.markdown(f"""
        <div class="{bubble_class}">
            <strong>{"🤖 Chatbot:" if msg["role"] == "bot" else "👤 Cliente:"}</strong> {msg["text"]}
        </div>
        """, unsafe_allow_html=True)
        
        # Botón TTS para mensajes del bot
        if msg["role"] == "bot":
            if st.button(f"🔊 Escuchar", key=f"tts_{msg['text'][:20]}"):
                tts = gTTS(text=msg["text"], lang='es')
                audio_bytes = BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                st.audio(audio_bytes, format='audio/mp3')
    
    # Input del usuario
    user_input = st.chat_input("Escribe tu mensaje...")
    
    if user_input:
        # Agregar mensaje del usuario
        st.session_state.chat_messages.append({"role": "user", "text": user_input})
        
        # Lógica del bot
        bot_response = ""
        if st.session_state.payment_step == 0:
            if "pagar" in user_input.lower() or "compra" in user_input.lower() or "carrito" in user_input.lower():
                bot_response = "¡Perfecto! Vamos a procesar tu pago. ¿Qué método de pago prefieres?\n1. Yape/Plin\n2. Tarjeta\n3. Contraentrega"
                st.session_state.payment_step = 1
            else:
                bot_response = "¡Claro! Estoy aquí para ayudarte. Si quieres probar el flujo de pago, escribe 'quiero pagar'."
        elif st.session_state.payment_step == 1:
            if "1" in user_input or "yape" in user_input.lower() or "plin" in user_input.lower():
                st.session_state.selected_payment = "Yape/Plin"
                bot_response = f"Has seleccionado {st.session_state.selected_payment}. Aquí tienes tu QR de pago simulado:"
                st.session_state.payment_step = 2
            elif "2" in user_input or "tarjeta" in user_input.lower():
                st.session_state.selected_payment = "Tarjeta"
                bot_response = f"Has seleccionado {st.session_state.selected_payment}. ¡Pago simulado confirmado! Tu pedido ha sido registrado con estado de pago: Pago confirmado."
                st.session_state.payment_step = 0
            elif "3" in user_input or "contraentrega" in user_input.lower():
                st.session_state.selected_payment = "Contraentrega"
                bot_response = f"Has seleccionado {st.session_state.selected_payment}. ¡Pedido registrado! Recuerda que pagas al recibir. Estado de pago: Pago pendiente."
                st.session_state.payment_step = 0
            else:
                bot_response = "Por favor selecciona una opción válida:\n1. Yape/Plin\n2. Tarjeta\n3. Contraentrega"
        elif st.session_state.payment_step == 2:
            bot_response = "¡Pago simulado confirmado! Tu pedido ha sido registrado. ¿Hay algo más en que pueda ayudarte?"
            st.session_state.payment_step = 0
        
        # Agregar respuesta del bot
        st.session_state.chat_messages.append({"role": "bot", "text": bot_response})
        st.rerun()
    
    # Mostrar QR si es Yape/Plin
    if st.session_state.payment_step == 2 and st.session_state.selected_payment == "Yape/Plin":
        # Generar QR simulado
        qr_data = f"payment_simulation_{datetime.now().strftime('%Y%m%d%H%M%S')}_100.00"
        qr_img = qrcode.make(qr_data)
    
        # SOLUCIÓN: Convertir PIL Image a bytes para Streamlit
        import io
        buffered = io.BytesIO()
        qr_img.save(buffered, format="PNG")
        qr_img_bytes = buffered.getvalue()
    
        # Mostrar la imagen usando los bytes
        st.image(
            qr_img_bytes,
            caption="QR de Pago Simulado (Yape/Plin)",
            use_container_width=False,
            width=200
        )
    
        if st.button("✅ Confirmar Pago Simulado"):
            st.session_state.chat_messages.append({"role": "bot", "text": "¡Pago simulado confirmado! Tu pedido ha sido registrado. ¿Hay algo más en que pueda ayudarte?"})
            st.session_state.payment_step = 0
            st.rerun()

    st.markdown("---")
    
    # Tabla de conversaciones
    st.markdown("### 📋 Lista de Conversaciones")
    
    # Preparar datos para mostrar
    display_conversations = filtered_conversations.copy()
    display_conversations['ID'] = display_conversations['id']
    display_conversations['Fecha'] = display_conversations['start_time'].dt.strftime('%d/%m/%Y %H:%M')
    display_conversations['Tipo'] = display_conversations['intent'].str.title()
    display_conversations['Mensajes'] = display_conversations['message_count'].astype(int)
    display_conversations['Satisfacción'] = display_conversations['satisfaction_score'].apply(lambda x: f"{x:.1f}/5")
    display_conversations['Tiempo Respuesta'] = display_conversations['avg_response_time'].apply(lambda x: f"{x:.0f}s")
    display_conversations['Estado'] = display_conversations['resolved'].apply(lambda x: "✅ Resuelto" if x else "❌ Pendiente")
    
    # Mostrar tabla
    st.dataframe(
        display_conversations[['ID', 'Fecha', 'Tipo', 'Mensajes', 'Satisfacción', 'Tiempo Respuesta', 'Estado']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Fecha": st.column_config.TextColumn("Fecha", width="medium"),
            "Tipo": st.column_config.TextColumn("Tipo de Consulta", width="medium"),
            "Mensajes": st.column_config.NumberColumn("Mensajes", width="small"),
            "Satisfacción": st.column_config.TextColumn("Satisfacción", width="small"),
            "Tiempo Respuesta": st.column_config.TextColumn("Tiempo Respuesta", width="small"),
            "Estado": st.column_config.TextColumn("Estado", width="medium")
        }
    )
    
    # Insights y recomendaciones
    st.markdown("### 💡 Insights y Recomendaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Análisis de intenciones más problemáticas
        intent_analysis = filtered_conversations.groupby('intent').agg({
            'resolved': 'mean',
            'satisfaction_score': 'mean',
            'id': 'count'
        }).round(2)
        
        intent_analysis.columns = ['resolution_rate', 'avg_satisfaction', 'count']
        problematic_intents = intent_analysis[
            (intent_analysis['resolution_rate'] < 0.7) | 
            (intent_analysis['avg_satisfaction'] < 3.5)
        ].sort_values('resolution_rate')
        
        if len(problematic_intents) > 0:
            st.warning(f"""
            **⚠️ Áreas de Mejora Identificadas:**
            
            **Intenciones con baja resolución:**
            {chr(10).join([f"• {intent}: {row['resolution_rate']:.1%} resolución" for intent, row in problematic_intents.head(3).iterrows()])}
            
            **Recomendación:** Revisar y mejorar las respuestas del chatbot para estas consultas.
            """)
        else:
            st.success("✅ **Excelente rendimiento:** Todas las intenciones tienen buenas tasas de resolución y satisfacción.")
    
    with col2:
        # Estadísticas generales
        peak_hour = filtered_conversations.groupby(
            filtered_conversations['start_time'].dt.hour
        ).size().idxmax()
        
        most_common_intent = filtered_conversations['intent'].value_counts().index[0]
        
        st.info(f"""
        **📊 Estadísticas Clave:**
        - Hora pico de conversaciones: {peak_hour}:00
        - Consulta más frecuente: {most_common_intent.title()}
        - Conversaciones filtradas: {len(filtered_conversations)}
        - Promedio mensajes por conversación: {filtered_conversations['message_count'].mean():.1f}
        """)

if __name__ == "__main__":
    main()
