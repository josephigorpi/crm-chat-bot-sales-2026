"""
Página del Dashboard (redireccionamiento)
Esta página redirige automáticamente a app.py (página principal)
"""

import streamlit as st
from sidebar import sidebar_navigation
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Dashboard", page_icon="🏠", layout="wide")

# Verificar autenticación
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    switch_page("app")

# Si está autenticado, mostrar sidebar y redirigir
sidebar_navigation()
sswitch_page("app")
