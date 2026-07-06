# 🤖 AI Sales Chatbot Dashboard

Dashboard interactivo desarrollado en Streamlit para el análisis y gestión de un chatbot de ventas con IA. Proporciona análisis completo de conversaciones, productos, clientes, carritos abandonados, pedidos y reportes ejecutivos.

## 📋 Características Principales

### 🔐 Autenticación
- Sistema de login seguro
- Credenciales de prueba incluidas
- Gestión de sesiones

### 📊 Dashboard Principal
- Métricas clave de ventas y conversaciones
- Gráficos interactivos con Plotly
- Análisis temporal de mensajes
- Distribución de intenciones del chatbot

### 🛍️ Gestión de Productos
- Catálogo completo de productos
- Filtros avanzados (categoría, precio, estado)
- Análisis de inventario
- Alertas de stock bajo
- Distribución de precios por categoría

### 👥 Análisis de Clientes
- Segmentación de clientes
- Customer Lifetime Value (CLV)
- Análisis geográfico
- Embudo de conversión
- Heatmap de actividad

### 💬 Análisis de Conversaciones
- Métricas de efectividad del chatbot
- Análisis de satisfacción
- Tiempo de respuesta promedio
- Distribución de intenciones
- Heatmap de conversaciones por hora

### 🛒 Carritos Abandonados
- Análisis de abandono
- Estrategias de recuperación
- Valor potencial perdido
- Razones de abandono
- Timeline de recuperación

### 📦 Pedidos y Envíos
- Gestión completa de pedidos
- Seguimiento de envíos
- Análisis de rendimiento logístico
- Métricas de entrega
- Análisis geográfico

### 📈 Reportes Ejecutivos
- Generación de PDFs profesionales
- KPIs consolidados
- Análisis de tendencias
- Reportes personalizables
- Insights y recomendaciones

### ⚙️ Configuración
- Personalización del dashboard
- Configuración de notificaciones
- Gestión de usuarios
- Backup y restauración
- Logs del sistema

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd crm-chat-bot-sales
   ```

2. **Instalar dependencias**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python3 -m streamlit run app.py
   ```

4. **Acceder al dashboard**
   - Abrir navegador en: `http://localhost:8501`
   - Usar credenciales de prueba:
     - **Usuario**: `admin`
     - **Contraseña**: `admin123`

## 📁 Estructura del Proyecto

```
crm-chat-bot-sales/
├── app.py                          # Aplicación principal
├── requirements.txt                # Dependencias
├── README.md                      # Este archivo
├── pages/                         # Páginas del dashboard
│   ├── 01_Dashboard.py           # Dashboard principal
│   ├── 02_Productos.py           # Gestión de productos
│   ├── 03_Clientes.py            # Análisis de clientes
│   ├── 04_Conversaciones.py      # Análisis de conversaciones
│   ├── 05_Carritos_Abandonados.py # Carritos abandonados
│   ├── 06_Pedidos_y_Envios.py    # Pedidos y envíos
│   ├── 07_Reportes.py            # Reportes ejecutivos
│   └── 08_Configuracion.py       # Configuración
└── utils/                         # Utilidades
    ├── data_generator.py          # Generador de datos fake
    ├── chart_utils.py             # Funciones para gráficos
    └── pdf_generator.py           # Generador de PDFs
```

## 🔧 Dependencias

- **streamlit**: Framework web para aplicaciones de datos
- **plotly**: Gráficos interactivos
- **pandas**: Manipulación de datos
- **numpy**: Computación numérica
- **faker**: Generación de datos fake realistas
- **fpdf2**: Generación de PDFs
- **python-dateutil**: Manejo de fechas
- **pytz**: Zonas horarias
- **uuid**: Generación de identificadores únicos

## 🎯 Uso del Dashboard

### 1. Autenticación
- Ingresar credenciales en la página de login
- El sistema mantiene la sesión activa

### 2. Navegación
- Usar el menú lateral para navegar entre secciones
- Cada página tiene filtros específicos
- Los datos se actualizan automáticamente

### 3. Filtros y Búsquedas
- Cada sección incluye filtros relevantes
- Búsqueda por texto en tablas
- Filtros por fechas, categorías, estados, etc.

### 4. Exportación
- Generar reportes PDF desde la sección "Reportes"
- Descargar datos filtrados
- Exportar configuraciones

### 5. Configuración
- Personalizar notificaciones
- Ajustar parámetros del dashboard
- Gestionar usuarios y permisos

## 📊 Datos de Ejemplo

El sistema incluye un generador de datos fake que crea:
- **1000 clientes** con información realista
- **200 productos** en diferentes categorías
- **5000 conversaciones** con el chatbot
- **800 carritos** de compra (algunos abandonados)
- **600 pedidos** con diferentes estados
- **500 envíos** con tracking
- **3000 recomendaciones** de productos

## 🔒 Credenciales de Prueba

Para acceder al sistema, usar:
- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 🛠️ Personalización

### Modificar Datos
- Editar `utils/data_generator.py` para cambiar la estructura de datos
- Ajustar cantidades y tipos de datos generados

### Personalizar Gráficos
- Modificar `utils/chart_utils.py` para cambiar estilos
- Agregar nuevos tipos de visualizaciones

### Configurar Reportes
- Editar `utils/pdf_generator.py` para personalizar PDFs
- Agregar nuevos tipos de reportes

### Modificar Interfaz
- Editar archivos en `pages/` para cambiar la UI
- Personalizar CSS en cada página

## 🚨 Solución de Problemas

### Error: "streamlit command not found"
```bash
pip3 install streamlit
```

### Error: "Module not found"
```bash
pip3 install -r requirements.txt
```

### Puerto ocupado
```bash
python3 -m streamlit run app.py --server.port 8502
```

### Problemas de permisos
```bash
sudo pip3 install -r requirements.txt
```

## 📈 Métricas y KPIs

El dashboard incluye las siguientes métricas clave:

### Ventas
- Ingresos totales y por período
- Valor promedio de pedido
- Tasa de conversión
- Productos más vendidos

### Chatbot
- Tasa de resolución
- Satisfacción promedio
- Tiempo de respuesta
- Intenciones más comunes

### Clientes
- Customer Lifetime Value
- Segmentación por valor
- Retención y churn
- Análisis geográfico

### Operaciones
- Tasa de abandono de carritos
- Tiempo de entrega promedio
- Eficiencia logística
- Inventario y stock

## 🔄 Actualizaciones

Para mantener el sistema actualizado:

1. **Actualizar dependencias**
   ```bash
   pip3 install -r requirements.txt --upgrade
   ```

2. **Verificar compatibilidad**
   ```bash
   python3 -m streamlit --version
   ```

3. **Limpiar caché**
   - Usar la opción en Configuración
   - O reiniciar la aplicación

## 📞 Soporte

Para soporte técnico o consultas:
- Revisar la documentación en cada página
- Consultar logs en la sección Configuración
- Verificar la consola del navegador para errores

## 🎨 Características Técnicas

- **Responsive Design**: Adaptable a diferentes tamaños de pantalla
- **Caching**: Optimización de rendimiento con `@st.cache_data`
- **Interactividad**: Gráficos interactivos con Plotly
- **Exportación**: PDFs profesionales con FPDF2
- **Seguridad**: Sistema de autenticación básico
- **Escalabilidad**: Estructura modular y extensible

---

**Desarrollado con ❤️ usando Streamlit y Python**