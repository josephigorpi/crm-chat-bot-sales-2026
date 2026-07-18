"""
Módulo de temas (theme.py)
Maneja la lógica de tema oscuro/claro con inyección de CSS dinámico
"""

import streamlit as st
from typing import Dict, Tuple, List

# Paletas de colores para cada tema
THEMES = {
    "light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f8fafc",
        "bg_tertiary": "#f1f5f9",
        "bg_card": "#ffffff",
        "bg_hover": "#f3f4f6",
        "text_primary": "#1f2937",
        "text_secondary": "#6b7280",
        "text_light": "#9ca3af",
        "border": "#e5e7eb",
        "border_light": "#e2e8f0",
        "border_dark": "#d1d5db",
        "gradient_primary": "#667eea",
        "gradient_secondary": "#764ba2",
        "gradient_success": "#10b981",
        "gradient_success_dark": "#059669",
        "gradient_danger": "#ef4444",
        "gradient_warning": "#f59e0b",
        "card_shadow": "0 2px 10px rgba(0,0,0,0.1)",
        "card_shadow_hover": "0 5px 15px rgba(0,0,0,0.2)",
        "button_bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "input_bg": "#ffffff",
        "input_text": "#1f2937",
        "input_border": "#d1d5db",
        "sidebar_bg": "#ffffff",
        "sidebar_text": "#1f2937",
        "sidebar_hover": "#f3f4f6",
        "header_bg": "#ffffff",
    },
    "dark": {
        "bg_primary": "#0f0f1a",
        "bg_secondary": "#1a1a2e",
        "bg_tertiary": "#16213e",
        "bg_card": "#1a1a2e",
        "bg_hover": "#2d2d44",
        "text_primary": "#e8e8e8",
        "text_secondary": "#a0aec0",
        "text_light": "#718096",
        "border": "#2d3748",
        "border_light": "#404060",
        "border_dark": "#1a202c",
        "gradient_primary": "#667eea",
        "gradient_secondary": "#764ba2",
        "gradient_success": "#10b981",
        "gradient_success_dark": "#059669",
        "gradient_danger": "#ef4444",
        "gradient_warning": "#f59e0b",
        "card_shadow": "0 2px 10px rgba(0,0,0,0.4)",
        "card_shadow_hover": "0 5px 15px rgba(0,0,0,0.6)",
        "button_bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "input_bg": "#1a1a2e",
        "input_text": "#e8e8e8",
        "input_border": "#404060",
        "sidebar_bg": "#0f0f1a",
        "sidebar_text": "#e8e8e8",
        "sidebar_hover": "#2d2d44",
        "header_bg": "#0f0f1a",
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


def is_dark_mode() -> bool:
    """Retorna True si el tema actual es oscuro."""
    init_theme_state()
    return st.session_state.dark_mode


def get_colors() -> Dict[str, str]:
    """
    Retorna el diccionario de colores para el tema actual.
    
    Returns:
        Dict con colores: bg_primary, bg_secondary, text_primary, etc.
    """
    init_theme_state()
    return THEMES[st.session_state.theme]


def get_plotly_template() -> str:
    """
    Retorna el template de Plotly según el tema activo.
    
    Returns:
        String del template: 'plotly_white' (light) o 'plotly_dark' (dark)
    """
    theme = get_theme()
    return 'plotly_dark' if theme == 'dark' else 'plotly_white'


def get_chart_colors() -> List[str]:
    """
    Retorna lista de colores para gráficos según el tema.
    
    Returns:
        Lista de colores hex
    """
    # Colores consistentes para ambos temas
    return [
        '#3B82F6',  # Azul
        '#10B981',  # Verde
        '#F59E0B',  # Amarillo
        '#EF4444',  # Rojo
        '#8B5CF6',  # Púrpura
        '#EC4899',  # Rosa
        '#06B6D4',  # Cian
        '#F97316',  # Naranja
        '#22C55E',  # Verde claro
        '#6B7280',  # Gris
    ]


def get_chart_template_colors() -> Tuple[str, List[str]]:
    """
    Retorna tuple (template, colors_list) para gráficos según el tema.
    
    Returns:
        (template: str, colors: list) - Template de Plotly y lista de colores
    """
    return get_plotly_template(), get_chart_colors()


def inject_theme_css():
    """
    Inyecta CSS dinámico según el tema activo.
    Se debe llamar en cada página después de st.set_page_config()
    """
    init_theme_state()
    colors = get_colors()
    theme = st.session_state.theme
    
    # CSS para el sidebar de Streamlit
    sidebar_css = f"""
    <style>
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {colors['sidebar_bg']};
            color: {colors['sidebar_text']};
            border-right: 1px solid {colors['border']};
        }}
        [data-testid="stSidebar"] * {{
            color: {colors['sidebar_text']};
        }}
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stCheckbox label {{
            color: {colors['sidebar_text']} !important;
        }}
        [data-testid="stSidebar"] .stSelectbox select,
        [data-testid="stSidebar"] .stTextInput input,
        [data-testid="stSidebar"] .stNumberInput input {{
            background-color: {colors['bg_tertiary']};
            color: {colors['sidebar_text']};
            border-color: {colors['border']};
        }}
        [data-testid="stSidebar"] .stButton > button {{
            background-color: {colors['bg_tertiary']};
            color: {colors['sidebar_text']};
            border-color: {colors['border']};
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background-color: {colors['sidebar_hover']};
        }}
    """
    
    # CSS adicional para modo oscuro
    if theme == "dark":
        sidebar_css += """
            [data-testid="stSidebar"] .stSelectbox select option {
                background-color: #1a1a2e;
                color: #e8e8e8;
            }
        """
    
    sidebar_css += "</style>"
    st.markdown(sidebar_css, unsafe_allow_html=True)
    
    # CSS para el contenido principal
    main_css = f"""
    <style>
        /* Variables CSS para usar en todas las páginas */
        :root {{
            --bg-primary: {colors['bg_primary']};
            --bg-secondary: {colors['bg_secondary']};
            --bg-tertiary: {colors['bg_tertiary']};
            --bg-card: {colors['bg_card']};
            --bg-hover: {colors['bg_hover']};
            --text-primary: {colors['text_primary']};
            --text-secondary: {colors['text_secondary']};
            --text-light: {colors['text_light']};
            --border: {colors['border']};
            --border-light: {colors['border_light']};
            --border-dark: {colors['border_dark']};
            --card-shadow: {colors['card_shadow']};
            --card-shadow-hover: {colors['card_shadow_hover']};
            --button-bg: {colors['button_bg']};
            --gradient-primary: {colors['gradient_primary']};
            --gradient-secondary: {colors['gradient_secondary']};
            --gradient-success: {colors['gradient_success']};
            --gradient-success-dark: {colors['gradient_success_dark']};
        }}
        
        /* Fondo principal */
        [data-testid="stAppViewContainer"] {{
            background-color: {colors['bg_primary']};
        }}
        
        [data-testid="stHeader"] {{
            background-color: {colors['header_bg']};
        }}
        
        /* Textos */
        .stMarkdown, .stText, .stCaption, .stCode, .stLatex {{
            color: {colors['text_primary']};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {colors['text_primary']};
        }}
        
        p, span, div, label {{
            color: {colors['text_primary']};
        }}
        
        /* Inputs */
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea,
        .stSelectbox select {{
            background-color: {colors['input_bg']};
            color: {colors['input_text']};
            border-color: {colors['input_border']};
        }}
        
        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus {{
            border-color: {colors['gradient_primary']};
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }}
        
        /* Checkboxes y Radios */
        .stCheckbox label,
        .stRadio label {{
            color: {colors['text_primary']};
        }}
        
        /* Sliders */
        .stSlider .stSlider > div {{
            color: {colors['text_primary']};
        }}
        
        /* Selectbox */
        .stSelectbox > div > div {{
            background-color: {colors['input_bg']};
            color: {colors['input_text']};
        }}
        
        /* Dataframes */
        .stDataFrame {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
        }}
        .stDataFrame table {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
        }}
        .stDataFrame th {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
        }}
        .stDataFrame td {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
        }}
        .stDataFrame tr:hover td {{
            background-color: {colors['bg_hover']};
        }}
        
        /* Métricas de Streamlit */
        [data-testid="stMetricValue"] {{
            color: {colors['text_primary']};
        }}
        [data-testid="stMetricDelta"] {{
            color: {colors['text_secondary']};
        }}
        [data-testid="stMetricLabel"] {{
            color: {colors['text_secondary']};
        }}
        
        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border-color: {colors['border']};
        }}
        .streamlit-expanderContent {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
            background-color: {colors['bg_secondary']};
            border-radius: 8px;
            padding: 4px;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {colors['text_secondary']};
            border-radius: 6px;
            padding: 8px 16px;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {colors['bg_card']};
            color: {colors['text_primary']};
            box-shadow: {colors['card_shadow']};
        }}
        
        /* Botones */
        .stButton > button {{
            background: {colors['button_bg']};
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: {colors['card_shadow_hover']};
        }}
        .stButton > button:active {{
            transform: translateY(0px);
        }}
        .stButton > button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}
        
        /* Info/Warning/Success/Error boxes */
        .stAlert {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
            border-color: {colors['border']};
        }}
        
        /* Code blocks */
        .stCodeBlock {{
            background-color: {colors['bg_secondary']};
            color: {colors['text_primary']};
        }}
        
        /* Plotly charts - ajuste de fondo */
        .js-plotly-plot .plotly .main-svg {{
            background-color: transparent !important;
        }}
        .js-plotly-plot .plotly .cartesianlayer {{
            background-color: transparent !important;
        }}
        
        /* Scrollbar personalizada */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: {colors['bg_secondary']};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb {{
            background: {colors['border']};
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {colors['text_light']};
        }}
        
        /* Estilos para elementos de las vistas */
        .welcome-message {{
            background: linear-gradient(135deg, {colors['gradient_success']} 0%, {colors['gradient_success_dark']} 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 1rem 0;
        }}
        .welcome-message * {{
            color: white;
        }}
        
        .table-container {{
            background: {colors['bg_card']};
            padding: 1rem;
            border-radius: 10px;
            box-shadow: {colors['card_shadow']};
            margin: 1rem 0;
        }}
        
        .metric-box {{
            background: {colors['bg_card']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: {colors['card_shadow']};
            text-align: center;
            border-left: 4px solid {colors['gradient_primary']};
        }}
        .metric-box h3 {{
            color: {colors['gradient_primary']};
            font-size: 1.8rem;
            margin-bottom: 0.25rem;
        }}
        .metric-box p {{
            color: {colors['text_secondary']};
            margin: 0;
        }}
        
        .filter-container {{
            background: {colors['bg_tertiary']};
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid {colors['border_light']};
            margin-bottom: 2rem;
        }}
        
        .add-product-form,
        .add-customer-form,
        .add-order-form {{
            background: {colors['bg_tertiary']};
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid {colors['border_light']};
            margin: 2rem 0;
        }}
        
        .form-header {{
            background: {colors['button_bg']};
            color: white;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 1.5rem;
        }}
        .form-header * {{
            color: white;
        }}
        
        .alert-box {{
            background: #fef2f2;
            border: 1px solid #fecaca;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }}
        .alert-box h4 {{
            color: #dc2626;
            margin-bottom: 0.5rem;
        }}
        
        .success-box {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }}
        .success-box h4 {{
            color: #16a34a;
            margin-bottom: 0.5rem;
        }}
        
        /* Segment cards */
        .segment-card {{
            background: {colors['bg_card']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: {colors['card_shadow']};
            margin-bottom: 1rem;
            border-left: 4px solid {colors['gradient_primary']};
        }}
        .segment-card h4 {{
            color: {colors['text_primary']};
            margin-bottom: 0.5rem;
        }}
        .segment-card p {{
            color: {colors['text_secondary']};
            margin: 0;
        }}
        
        /* Conversación bubbles */
        .chat-bubble {{
            background: {colors['bg_secondary']};
            padding: 1rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            border-left: 4px solid {colors['gradient_primary']};
        }}
        .bot-bubble {{
            background: {colors['bg_tertiary']};
            border-left: 4px solid {colors['gradient_secondary']};
        }}
        .user-bubble {{
            background: {colors['bg_hover']};
            border-left: 4px solid {colors['gradient_success']};
        }}
        
        /* Metric card para conversaciones */
        .metric-card {{
            background: {colors['bg_card']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: {colors['card_shadow']};
            text-align: center;
            border-top: 4px solid {colors['gradient_primary']};
        }}
        .metric-card h3 {{
            color: {colors['gradient_primary']};
            font-size: 1.8rem;
            margin-bottom: 0.25rem;
        }}
        .metric-card p {{
            color: {colors['text_secondary']};
            margin: 0;
        }}
        
        /* High contrast metric cards */
        .metric-highlight {{
            background: {colors['button_bg']};
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
        }}
        .metric-highlight h3 {{
            color: white;
            font-size: 1.8rem;
            margin-bottom: 0.25rem;
        }}
        .metric-highlight p {{
            color: rgba(255,255,255,0.9);
            margin: 0;
        }}
        
        .kpi-card {{
            background: {colors['button_bg']};
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
        }}
        .kpi-card .kpi-value {{
            color: white;
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        .kpi-card .kpi-label {{
            color: rgba(255,255,255,0.9);
            font-size: 0.9rem;
        }}
        
        /* Abandoned carts */
        .abandoned-cart-card {{
            background: {colors['bg_card']};
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: {colors['card_shadow']};
            margin-bottom: 1rem;
            border-left: 4px solid {colors['gradient_warning']};
        }}
        .high-value-cart {{
            border-left: 4px solid #dc2626;
            background: #fef2f2;
        }}
        .medium-value-cart {{
            border-left: 4px solid #f59e0b;
            background: #fffbeb;
        }}
        .low-value-cart {{
            border-left: 4px solid #65a30d;
            background: #f7fee7;
        }}
        
        .recovery-action {{
            background: #fef3c7;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #f59e0b;
            margin: 0.5rem 0;
        }}
        
        .product-item {{
            background: {colors['bg_secondary']};
            padding: 0.5rem;
            border-radius: 5px;
            margin: 0.2rem 0;
            font-size: 0.9rem;
        }}
        
        .shipment-info {{
            background: {colors['bg_tertiary']};
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid {colors['border_light']};
            margin: 1rem 0;
        }}
        
        .tracking-timeline {{
            background: {colors['bg_secondary']};
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }}
        
        .timeline-step.completed {{
            color: {colors['gradient_success']};
        }}
        .timeline-step.current {{
            color: {colors['gradient_primary']};
            font-weight: bold;
        }}
        .timeline-step.pending {{
            color: {colors['text_light']};
        }}
        
        .intent-tag {{
            background: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            padding: 0.25rem 0.5rem;
            border-radius: 15px;
            font-size: 0.8rem;
            margin: 0.2rem;
            display: inline-block;
            border: 1px solid {colors['border_light']};
        }}
        
        /* Cards de reportes */
        .report-card {{
            background: {colors['bg_card']};
            padding: 2rem;
            border-radius: 15px;
            box-shadow: {colors['card_shadow']};
            margin-bottom: 2rem;
            border-top: 4px solid {colors['gradient_primary']};
            transition: transform 0.3s ease;
        }}
        .report-card:hover {{
            transform: translateY(-5px);
            box-shadow: {colors['card_shadow_hover']};
        }}
        .report-type h3 {{
            color: {colors['text_primary']};
            margin: 0;
        }}
        .report-description {{
            color: {colors['text_secondary']};
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }}
        
        /* Configuración */
        .config-section {{
            background: {colors['bg_card']};
            padding: 2rem;
            border-radius: 15px;
            box-shadow: {colors['card_shadow']};
            margin-bottom: 2rem;
            border-left: 4px solid {colors['gradient_primary']};
        }}
        .setting-title {{
            font-size: 1.2rem;
            font-weight: bold;
            color: {colors['text_primary']};
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
        }}
        .setting-description {{
            color: {colors['text_secondary']};
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}
        .config-item {{
            background: {colors['bg_secondary']};
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1rem 0;
            border: 1px solid {colors['border_light']};
        }}
        .user-profile {{
            display: flex;
            align-items: center;
            padding: 1rem;
            background: {colors['bg_tertiary']};
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        .user-avatar {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: {colors['button_bg']};
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            margin-right: 1rem;
        }}
        .backup-info {{
            background: #f0fdf4;
            border: 1px solid #10b981;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }}
        
        /* Status indicators */
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        .status-active {{
            background-color: {colors['gradient_success']};
        }}
        .status-inactive {{
            background-color: {colors['gradient_danger']};
        }}
        .status-warning {{
            background-color: {colors['gradient_warning']};
        }}
    </style>
    """
    
    st.markdown(main_css, unsafe_allow_html=True)
