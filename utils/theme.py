"""
Módulo de temas (theme.py)
Maneja la lógica de tema oscuro/claro con inyección de CSS dinámico
"""

import streamlit as st
from typing import Dict, Tuple

# Paletas de colores para cada tema
THEMES = {
    "light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f8fafc",
        "bg_tertiary": "#f3f4f6",
        "text_primary": "#1f2937",
        "text_secondary": "#6b7280",
        "border": "#e5e7eb",
        "border_light": "#e2e8f0",
        "gradient_primary": "#667eea",
        "gradient_secondary": "#764ba2",
        "gradient_success": "#10b981",
        "gradient_success_dark": "#059669",
        "card_shadow": "0 2px 10px rgba(0,0,0,0.1)",
        "card_shadow_hover": "0 5px 15px rgba(0,0,0,0.2)",
        "button_bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    },
    "dark": {
        "bg_primary": "#1a1a2e",
        "bg_secondary": "#16213e",
        "bg_tertiary": "#0f3460",
        "text_primary": "#e0e0e0",
        "text_secondary": "#a0a0a0",
        "border": "#404040",
        "border_light": "#505050",
        "gradient_primary": "#667eea",
        "gradient_secondary": "#764ba2",
        "gradient_success": "#10b981",
        "gradient_success_dark": "#059669",
        "card_shadow": "0 2px 10px rgba(0,0,0,0.3)",
        "card_shadow_hover": "0 5px 15px rgba(0,0,0,0.5)",
        "button_bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    }
}

def init_theme_state():
    """
    Inicializa el estado del tema en session_state si no existe.
    Por defecto: light mode
    """
    if 'theme' not in st.session_state:
        st.session_state.theme = 'light'
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def toggle_theme():
    """
    Alterna entre tema claro y oscuro.
    Actualiza tanto 'theme' como 'dark_mode' para compatibilidad.
    """
    if st.session_state.theme == 'light':
        st.session_state.theme = 'dark'
        st.session_state.dark_mode = True
    else:
        st.session_state.theme = 'light'
        st.session_state.dark_mode = False

def get_theme() -> str:
    """Retorna el tema actual ('light' o 'dark')"""
    init_theme_state()
    return st.session_state.theme

def get_colors() -> Dict[str, str]:
    """
    Retorna el diccionario de colores para el tema actual.
    
    Returns:
        Dict con colores: bg_primary, bg_secondary, text_primary, etc.
    """
    init_theme_state()
    return THEMES[st.session_state.theme]

def inject_theme_css():
    """
    Inyecta CSS dinámico según el tema activo.
    Se debe llamar en app.py después de st.set_page_config()
    """
    init_theme_state()
    colors = get_colors()
    theme = st.session_state.theme
    
    # Ajustar fondo de Streamlit según tema
    if theme == "dark":
        st.markdown("""
        <style>
            [data-testid="stAppViewContainer"] {
                background-color: #1a1a2e;
                color: #e0e0e0;
            }
            [data-testid="stSidebar"] {
                background-color: #16213e;
                color: #e0e0e0;
            }
            [data-testid="stHeader"] {
                background-color: #1a1a2e;
            }
            input, textarea, select {
                background-color: #16213e !important;
                color: #e0e0e0 !important;
                border-color: #404040 !important;
            }
            .stTextInput > div > div > input {
                background-color: #16213e !important;
                color: #e0e0e0 !important;
            }
            .stNumberInput > div > div > input {
                background-color: #16213e !important;
                color: #e0e0e0 !important;
            }
            .stTextArea > div > div > textarea {
                background-color: #16213e !important;
                color: #e0e0e0 !important;
            }
            .stSelectbox > div > div > select {
                background-color: #16213e !important;
                color: #e0e0e0 !important;
            }
            .stSlider > div > div > div {
                color: #e0e0e0 !important;
            }
            .stCheckbox > label {
                color: #e0e0e0 !important;
            }
            .stRadio > label {
                color: #e0e0e0 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    
    # CSS dinámico genérico para ambos temas
    css_template = f"""
    <style>
        :root {{
            --bg-primary: {colors['bg_primary']};
            --bg-secondary: {colors['bg_secondary']};
            --bg-tertiary: {colors['bg_tertiary']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --border: {colors['border']};
            --border-light: {colors['border_light']};
            --card-shadow: {colors['card_shadow']};
            --card-shadow-hover: {colors['card_shadow_hover']};
        }}
        
        /* Main Header */
        .main-header {{
            font-size: 2.5rem;
            font-weight: bold;
            color: {colors['text_primary']};
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: {colors['button_bg']};
            padding: 1rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin: 0.5rem 0;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        /* Sidebar */
        .sidebar-logo {{
            text-align: center;
            padding: 1rem 0;
            border-bottom: 1px solid {colors['border']};
            margin-bottom: 1rem;
            color: {colors['text_primary']};
        }}
        
        .user-info {{
            background: {colors['bg_tertiary']};
            padding: 0.8rem;
            border-radius: 8px;
            margin: 1rem 0;
            text-align: center;
            color: {colors['text_primary']};
        }}
        
        /* Login */
        .login-container {{
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: {colors['bg_primary']};
            border-radius: 15px;
            box-shadow: {colors['card_shadow']};
            color: {colors['text_primary']};
        }}
        
        .login-header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .login-title {{
            font-size: 2rem;
            font-weight: bold;
            color: {colors['text_primary']};
            margin-bottom: 0.5rem;
        }}
        
        .login-subtitle {{
            color: {colors['text_secondary']};
            font-size: 1rem;
        }}
        
        .stButton > button {{
            width: 100%;
            background: {colors['button_bg']};
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: {colors['card_shadow_hover']};
        }}
        
        /* Welcome Message */
        .welcome-message {{
            background: linear-gradient(135deg, {colors['gradient_success']} 0%, {colors['gradient_success_dark']} 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
        }}
        
        /* Tables & Data */
        .table-container {{
            background: {colors['bg_primary']};
            padding: 1rem;
            border-radius: 10px;
            box-shadow: {colors['card_shadow']};
            margin: 1rem 0;
            color: {colors['text_primary']};
        }}
        
        /* Products Page */
        .product-header {{
            background: {colors['button_bg']};
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .filter-container {{
            background: {colors['bg_tertiary']};
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid {colors['border_light']};
            margin-bottom: 2rem;
            color: {colors['text_primary']};
        }}
        
        .metric-box {{
            background: {colors['bg_primary']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: {colors['card_shadow']};
            text-align: center;
            border-left: 4px solid #3b82f6;
            color: {colors['text_primary']};
        }}
        
        .alert-box {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            color: {colors['text_primary']};
        }}
        
        .success-box {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            color: {colors['text_primary']};
        }}
        
        .add-product-form {{
            background: {colors['bg_tertiary']};
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid {colors['border_light']};
            margin: 2rem 0;
            color: {colors['text_primary']};
        }}
        
        .form-header {{
            background: linear-gradient(135deg, {colors['gradient_success']} 0%, {colors['gradient_success_dark']} 100%);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        
        /* General Text */
        h1, h2, h3, h4, h5, h6 {{
            color: {colors['text_primary']};
        }}
        
        p, span, div {{
            color: {colors['text_primary']};
        }}
        
        /* Info/Alert boxes */
        .stInfo {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border-color: {colors['border']};
        }}
        
        .stSuccess {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border-color: {colors['border']};
        }}
        
        .stWarning {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border-color: {colors['border']};
        }}
        
        .stError {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border-color: {colors['border']};
        }}
    </style>
    """
    
    st.markdown(css_template, unsafe_allow_html=True)

def get_plotly_template() -> str:
    """
    Retorna el template de Plotly según el tema activo.
    
    Returns:
        String del template: 'plotly_white' (light) o 'plotly_dark' (dark)
    """
    theme = get_theme()
    return 'plotly_dark' if theme == 'dark' else 'plotly_white'

def get_chart_template_colors() -> Tuple[str, str]:
    """
    Retorna tuple (template, colors_list) para gráficos según el tema.
    
    Returns:
        (template: str, colors: list) - Template de Plotly y lista de colores
    """
    colors = get_colors()
    theme = get_theme()
    
    # Colores para gráficos
    chart_colors = [
        '#3B82F6',  # Azul
        '#10B981',  # Verde
        '#F59E0B',  # Amarillo
        '#EF4444',  # Rojo
        '#F97316',  # Naranja
        '#06B6D4',  # Cian
        '#22C55E',  # Verde claro
        '#8B5CF6',  # Púrpura
        '#EC4899',  # Rosa
        '#6B7280',  # Gris
    ]
    
    template = 'plotly_dark' if theme == 'dark' else 'plotly_white'
    
    return template, chart_colors
