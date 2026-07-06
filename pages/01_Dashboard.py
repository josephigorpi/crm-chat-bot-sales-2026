"""
Página principal del Dashboard
Redirige al dashboard principal en app.py
"""

import streamlit as st

st.markdown("# 🏠 Dashboard Principal")
st.markdown("Esta página redirige automáticamente al dashboard principal.")
st.markdown("Por favor, usa la navegación en la barra lateral para acceder a las diferentes secciones.")

# Información sobre la navegación
st.info("""
💡 **Tip:** Usa el menú de la barra lateral para navegar entre las diferentes secciones:
- 🏠 Dashboard: Vista general con métricas principales
- 📦 Productos: Análisis y gestión de productos  
- 👥 Clientes: Gestión y análisis de clientes
- 💬 Conversaciones: Análisis del chatbot
- 🛒 Carritos Abandonados: Recuperación de ventas
- 📦 Pedidos y Envíos: Gestión de órdenes
- 📊 Reportes: Generación de informes
- ⚙️ Configuración: Ajustes del sistema
""")