"""
Página del Dashboard (redireccionamiento)
Esta página redirige automáticamente a app.py (página principal)
"""

import streamlit as st
from sidebar import sidebar_navigation

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.switch_page("app.py")

# Si está autenticado, mostrar sidebar y redirigir
sidebar_navigation()
st.switch_page("app.py")
