"""
Dashboard de Accidentes de Tránsito en Guatemala 2020-2024
Aplicación Streamlit con visualizaciones interactivas

Autor: [Tu nombre]
Fecha: Octubre 2024
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Accidentes Guatemala",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PALETA DE COLORES 
COLORES = {
    'rojo_critico': '#D32F2F',
    'naranja_alerta': '#F57C00',
    'amarillo_preventivo': '#FBC02D',
    'azul_informativo': '#1976D2',
    'verde_positivo': '#388E3C',
    'gris_neutro': '#455A64',
    'fondo_claro': '#F5F5F5',
    'fondo_oscuro': '#1E1E1E',      
    'texto_claro': '#FFFFFF',        
    'grid_oscuro': '#3A3A3A'         
}

# Escala secuencial azul para mapas
ESCALA_AZUL = ['#E3F2FD', '#90CAF9', '#42A5F5', '#1976D2', '#0D47A1']

# Escala de calor para heatmap (amarillo-naranja-rojo)
ESCALA_CALOR = ['#FFFDE7', '#FFB300', '#F57C00', '#D32F2F']

# FUNCIONES DE CARGA DE DATOS

@st.cache_data
def cargar_datos():
    """
    Carga todos los datos preprocesados
    Usa caché de Streamlit para optimizar rendimiento
    """
    try:
        df_accidentes = pd.read_csv('./data_clean/data_accidentes_anio_depto.csv')
        df_dia_hora = pd.read_csv('./data_clean/data_accidentes_dia_hora.csv')
        df_tipos = pd.read_csv('./data_clean/data_accidentes_tipo_mes.csv')
        df_lesionados = pd.read_csv('./data_clean/data_lesionados_anio_depto.csv')
        df_fallecidos = pd.read_csv('./data_clean/data_fallecidos_anio_depto.csv')
        
        return df_accidentes, df_dia_hora, df_tipos, df_lesionados, df_fallecidos
    
    except FileNotFoundError:
        st.error(
            """
            **Error: No se encontraron los archivos de datos procesados**
            """
        )
        st.stop()

# VISUALIZACIÓN 1: MAPA GEOGRÁFICO DE GUATEMALA

def crear_mapa_guatemala(df, anio_seleccionado):
    """
    Crea un gráfico de barras representando los departamentos de Guatemala
    (Alternativa visual al mapa real)
    """
    # Filtrar por año
    df_filtrado = df[df['año'] == anio_seleccionado].copy()
    
    # Ordenar por cantidad de accidentes
    df_filtrado = df_filtrado.sort_values('accidentes', ascending=True)
    
    # Normalizar valores para color
    max_val = df_filtrado['accidentes'].max()
    min_val = df_filtrado['accidentes'].min()
    
    # Asignar colores basados en escala azul
    def asignar_color(valor):
        # Normalizar entre 0 y 1
        norm = (valor - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        
        if norm < 0.2:
            return ESCALA_AZUL[0]
        elif norm < 0.4:
            return ESCALA_AZUL[1]
        elif norm < 0.6:
            return ESCALA_AZUL[2]
        elif norm < 0.8:
            return ESCALA_AZUL[3]
        else:
            return ESCALA_AZUL[4]
    
    df_filtrado['color'] = df_filtrado['accidentes'].apply(asignar_color)
    
    # Crear gráfico de barras horizontales
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_filtrado['departamento'],
        x=df_filtrado['accidentes'],
        orientation='h',
        marker=dict(
            color=df_filtrado['color'],
            line=dict(width=1, color='white')
        ),
        text=df_filtrado['accidentes'],
        textposition='outside',
        texttemplate='%{text:,}',
        hovertemplate='<b>%{y}</b><br>' +
                      'Accidentes: %{x:,}<br>' +
                      '<extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        title=f'Distribución por Departamento - {anio_seleccionado}',
        xaxis_title='Cantidad de Accidentes',
        yaxis_title='',
        height=650,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['gris_neutro']),
        title_font_size=20,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORES['grid_oscuro'],    
            color=COLORES['texto_claro'] 
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=11, color=COLORES['texto_claro'])
        ),
        margin=dict(l=120, r=50, t=80, b=50)
    )
    
    return fig


# VISUALIZACIÓN 2: SERIE TEMPORAL

def crear_serie_temporal(df, deptos_seleccionados, depto_destacado=None):
    """
    Crea gráfico de líneas con evolución temporal
    """
    # Filtrar departamentos seleccionados
    df_filtrado = df[df['departamento'].isin(deptos_seleccionados)].copy()
    
    # Agrupar por año y departamento
    df_agrupado = df_filtrado.groupby(['año', 'departamento'])['accidentes'].sum().reset_index()
    
    fig = go.Figure()
    
    for depto in deptos_seleccionados:
        df_depto = df_agrupado[df_agrupado['departamento'] == depto]
        
        # Determinar color y grosor
        if depto == depto_destacado:
            color = COLORES['rojo_critico']
            ancho = 3
            opacity = 1.0
        else:
            color = COLORES['azul_informativo']
            ancho = 2
            opacity = 0.6
        
        fig.add_trace(go.Scatter(
            x=df_depto['año'],
            y=df_depto['accidentes'],
            mode='lines+markers',
            name=depto,
            line=dict(color=color, width=ancho),
            marker=dict(size=8, color=color),
            opacity=opacity,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                          'Año: %{x}<br>' +
                          'Accidentes: %{y:,}<br>' +
                          '<extra></extra>'
        ))
    
    fig.update_layout(
        title='Evolución Temporal de Accidentes (2020-2024)',
        xaxis_title='Año',
        yaxis_title='Cantidad de Accidentes',
        height=400,
        hovermode='x unified',
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),  
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],  
        plot_bgcolor=COLORES['fondo_oscuro'],   
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORES['grid_oscuro'],   
            dtick=1,
            color=COLORES['texto_claro']        
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORES['grid_oscuro'],   
            color=COLORES['texto_claro']        
        ),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(color=COLORES['texto_claro'])  
        )
    )
    
    return fig


# VISUALIZACIÓN 3: TOP 10 TIPOS DE ACCIDENTES

def crear_top_tipos(df):
    """
    Crea gráfico de barras horizontales con top 10 tipos de accidentes
    """
    # Calcular totales por tipo
    df_agrupado = df.groupby('tipo_accidente')['cantidad'].sum().reset_index()
    df_agrupado = df_agrupado.sort_values('cantidad', ascending=True).tail(10)
    
    # Asignar colores según gravedad (puedes ajustar esto)
    colores_tipos = {
        'atropello': COLORES['rojo_critico'],
        'colision': COLORES['naranja_alerta'],
        'choque': COLORES['naranja_alerta'],
        'vuelco': COLORES['amarillo_preventivo'],
        'derrape': COLORES['amarillo_preventivo'],
        'embarranco': COLORES['rojo_critico'],
        'encuneto': COLORES['amarillo_preventivo'],
        'caida': COLORES['naranja_alerta'],
        'ignorado': COLORES['gris_neutro']
    }
    
    df_agrupado['color'] = df_agrupado['tipo_accidente'].map(
        lambda x: colores_tipos.get(x, COLORES['azul_informativo'])
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_agrupado['cantidad'],
        y=df_agrupado['tipo_accidente'],
        orientation='h',
        marker=dict(
            color=df_agrupado['color'],
            line=dict(width=0)
        ),
        text=df_agrupado['cantidad'],
        textposition='outside',
        texttemplate='%{text:,}',
        hovertemplate='<b>%{y}</b><br>' +
                      'Cantidad: %{x:,}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title='Top 10 Tipos de Accidentes Más Frecuentes',
        xaxis_title='Cantidad de Accidentes',
        yaxis_title='',
        height=500,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']), 
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],  
        plot_bgcolor=COLORES['fondo_oscuro'],   
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORES['grid_oscuro'],   
            color=COLORES['texto_claro']        
        ),
        yaxis=dict(
            showgrid=False,
            color=COLORES['texto_claro']        
        ),
        showlegend=False
    )
    
    return fig


# VISUALIZACIÓN 4: HEATMAP DÍA/HORA

def crear_heatmap_dia_hora(df):
    """
    Crea heatmap matricial de día de la semana vs hora del día
    """
    # Crear pivot table
    df_pivot = df.pivot_table(
        values='accidentes',
        index='hora_de_ocurrencia',
        columns='dia_semana',
        aggfunc='sum'
    )
    
    # Ordenar días de la semana correctamente
    dias_ordenados = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    df_pivot = df_pivot[dias_ordenados]
    
    # Ordenar por hora (usar hora_num si está disponible, sino por hora_de_ocurrencia)
    if 'hora_num' in df.columns:
        # Crear diccionario de ordenamiento
        orden_horas = df[['hora_de_ocurrencia', 'hora_num']].drop_duplicates()
        orden_horas = orden_horas.sort_values('hora_num')
        df_pivot = df_pivot.reindex(orden_horas['hora_de_ocurrencia'].values)
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=[d.capitalize() for d in df_pivot.columns],
        y=df_pivot.index,
        colorscale=ESCALA_CALOR,
        hovertemplate='<b>%{y}</b><br>' +
                      '%{x}<br>' +
                      'Accidentes: %{z:,}<br>' +
                      '<extra></extra>',
        colorbar=dict(
            title="Accidentes",
            thicknessmode="pixels",
            thickness=15,
            lenmode="pixels",
            len=300
        )
    ))
    
    fig.update_layout(
        title='Patrones Temporales: Accidentes por Día y Hora',
        xaxis_title='Día de la Semana',
        yaxis_title='Hora del Día',
        height=600,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),  
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],  
        plot_bgcolor=COLORES['fondo_oscuro'],   
        xaxis=dict(color=COLORES['texto_claro']),  
        yaxis=dict(color=COLORES['texto_claro'])   
    )
    
    return fig


# INTERFAZ PRINCIPAL

def main():
    """
    Función principal de la aplicación
    """
    
    # Título principal
    st.markdown(
        f"""
        <h1 style='text-align: center; color: {COLORES['fondo_claro']};'>
        🚗 Dashboard de Accidentes de Tránsito
        </h1>
        <h3 style='text-align: center; color: {COLORES['gris_neutro']};'>
        Guatemala 2020-2024
        </h3>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Cargar datos
    with st.spinner('Cargando datos...'):
        df_accidentes, df_dia_hora, df_tipos, df_lesionados, df_fallecidos = cargar_datos()
    
    # ========================================================================
    # SIDEBAR - FILTROS
    # ========================================================================
    
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Flag_of_Guatemala.svg/320px-Flag_of_Guatemala.svg.png", width=100)
        st.title("⚙️ Filtros y Configuración")
        st.markdown("---")
        
        # Selector de año
        st.subheader("📅 Período Temporal")
        anio_seleccionado = st.select_slider(
            "Seleccionar Año:",
            options=[2020, 2021, 2022, 2023, 2024],
            value=2024
        )
        
        st.markdown("---")
        
        # Selector de departamentos para serie temporal
        st.subheader("📍 Departamentos")
        todos_deptos = sorted(df_accidentes['departamento'].unique())
        
        deptos_defecto = ['Guatemala', 'Escuintla', 'Quetzaltenango']
        deptos_disponibles = [d for d in deptos_defecto if d in todos_deptos]
        
        deptos_seleccionados = st.multiselect(
            "Departamentos a comparar:",
            options=todos_deptos,
            default=deptos_disponibles
        )
        
        st.markdown("---")
        
        # Estadísticas rápidas
        st.subheader("📊 Estadísticas Rápidas")
        total_accidentes_anio = df_accidentes[df_accidentes['año'] == anio_seleccionado]['accidentes'].sum()
        total_fallecidos_anio = df_fallecidos[df_fallecidos['año'] == anio_seleccionado]['fallecidos'].sum()
        total_lesionados_anio = df_lesionados[df_lesionados['año'] == anio_seleccionado]['lesionados'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚗 Accidentes", f"{total_accidentes_anio:,}")
        with col2:
            st.metric("💀 Fallecidos", f"{total_fallecidos_anio:,}")
        
        st.metric("🏥 Lesionados", f"{total_lesionados_anio:,}")
    
    # LAYOUT PRINCIPAL
    
    # Fila 1: Mapa y Serie Temporal
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("📍 Distribución Geográfica de Accidentes")
        st.plotly_chart(
            crear_mapa_guatemala(df_accidentes, anio_seleccionado),
            use_container_width=True,
            config={'displayModeBar': False}
        )
        st.caption("💡 **Insight**: Gráfico de barras mostrando la distribución de accidentes por departamento. Barras más oscuras = mayor cantidad de accidentes")
    
    with col2:
        st.subheader("📈 Evolución Temporal")
        
        if not deptos_seleccionados:
            st.warning("⚠️ Selecciona al menos un departamento en el panel lateral")
        else:
            # Permitir destacar un departamento
            depto_destacar = st.selectbox(
                "Resaltar departamento:",
                options=['Ninguno'] + deptos_seleccionados,
                index=0
            )
            
            depto_destacado = None if depto_destacar == 'Ninguno' else depto_destacar
            
            st.plotly_chart(
                crear_serie_temporal(df_accidentes, deptos_seleccionados, depto_destacado),
                use_container_width=True,
                config={'displayModeBar': False}
            )
            st.caption("💡 **Insight**: Tendencia de accidentes a lo largo de los años por departamento")
    
    st.markdown("---")
    
    # Fila 2: Top 10 Tipos y Heatmap
    col3, col4 = st.columns([1, 1.2])
    
    with col3:
        st.subheader("🏆 Top 10 Tipos de Accidentes")
        st.plotly_chart(
            crear_top_tipos(df_tipos),
            use_container_width=True,
            config={'displayModeBar': False}
        )
        st.caption("💡 **Insight**: Los tipos de accidentes más frecuentes. Colores indican gravedad (rojo=crítico, naranja=grave, amarillo=moderado)")
    
    with col4:
        st.subheader("🔥 Patrones de Accidentalidad por Día y Hora")
        st.plotly_chart(
            crear_heatmap_dia_hora(df_dia_hora),
            use_container_width=True,
            config={'displayModeBar': False}
        )
        st.caption("💡 **Insight**: Identifica las horas y días con mayor accidentalidad. Colores más oscuros = mayor frecuencia")
    
    st.markdown("---")
    
    # Footer
    st.markdown(
        f"""
        <div style='text-align: center; color: {COLORES['gris_neutro']}; padding: 20px;'>
        <p><b>Dashboard de Accidentes de Tránsito - Guatemala 2020-2024</b></p>
        <p>Datos: Instituto Nacional de Estadística (INE)</p>
        <p>Desarrollado con Streamlit + Plotly | Octubre 2024</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# EJECUTAR APLICACIÓN

if __name__ == "__main__":
    main()