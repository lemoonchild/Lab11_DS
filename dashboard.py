import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

try:
    from modelos_tab import render_modelos_tab
except ImportError:
    st.error("No se pudo importar el módulo de modelos")
    render_modelos_tab = None

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

ESCALA_AZUL = ['#E3F2FD', '#90CAF9', '#42A5F5', '#1976D2', '#0D47A1']
ESCALA_CALOR = ['#FFFDE7', '#FFB300', '#F57C00', '#D32F2F']

# ESTADO DE LA APLICACIÓN (SESSION STATE)
if 'departamento_seleccionado' not in st.session_state:
    st.session_state.departamento_seleccionado = None

if 'tipo_accidente_seleccionado' not in st.session_state:
    st.session_state.tipo_accidente_seleccionado = None

if 'tipo_vehiculo_seleccionado' not in st.session_state:
    st.session_state.tipo_vehiculo_seleccionado = None

# FUNCIONES DE CARGA DE DATOS
@st.cache_data
def cargar_datos():
    """Carga todos los datos preprocesados"""
    try:
        df_accidentes = pd.read_csv('./data_clean/data_accidentes_anio_depto.csv')
        df_dia_hora = pd.read_csv('./data_clean/data_accidentes_dia_hora.csv')
        df_tipos = pd.read_csv('./data_clean/data_accidentes_tipo_mes.csv')
        df_vehiculos = pd.read_csv('./data_clean/data_vehiculos_tipo.csv')
        df_lesionados = pd.read_csv('./data_clean/data_lesionados_anio_depto.csv')
        df_lesionados_edad = pd.read_csv('./data_clean/data_lesionados_edad.csv')
        df_fallecidos = pd.read_csv('./data_clean/data_fallecidos_anio_depto.csv')
        df_fallecidos_edad = pd.read_csv('./data_clean/data_fallecidos_edad.csv')
        
        return (df_accidentes, df_dia_hora, df_tipos, df_vehiculos, 
                df_lesionados, df_lesionados_edad, df_fallecidos, df_fallecidos_edad)
    
    except FileNotFoundError as e:
        st.error(f"""
        **Error: No se encontraron los archivos de datos procesados**
        """)
        st.stop()

# VISUALIZACIÓN 1: DISTRIBUCIÓN POR DEPARTAMENTO CON CLICK FUNCIONAL
def crear_vis1_departamentos(df, anio_seleccionado):
    """Gráfico de barras por departamento con capacidad de click"""
    df_filtrado = df[df['año'] == anio_seleccionado].copy()
    df_filtrado = df_filtrado.sort_values('accidentes', ascending=True)
    
    max_val = df_filtrado['accidentes'].max()
    min_val = df_filtrado['accidentes'].min()
    
    def asignar_color(valor):
        norm = (valor - min_val) / (max_val - min_val) if max_val != min_val else 0.5
        if norm < 0.2: return ESCALA_AZUL[0]
        elif norm < 0.4: return ESCALA_AZUL[1]
        elif norm < 0.6: return ESCALA_AZUL[2]
        elif norm < 0.8: return ESCALA_AZUL[3]
        else: return ESCALA_AZUL[4]
    
    df_filtrado['color'] = df_filtrado['accidentes'].apply(asignar_color)
    
    # Resaltar departamento seleccionado
    if st.session_state.departamento_seleccionado:
        df_filtrado['color'] = df_filtrado.apply(
            lambda row: COLORES['rojo_critico'] if row['departamento'] == st.session_state.departamento_seleccionado else row['color'],
            axis=1
        )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_filtrado['departamento'],
        x=df_filtrado['accidentes'],
        orientation='h',
        marker=dict(color=df_filtrado['color'], line=dict(width=1, color='white')),
        text=df_filtrado['accidentes'],
        textposition='outside',
        texttemplate='%{text:,}',
        hovertemplate='<b>%{y}</b><br>Accidentes: %{x:,}<br><extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        title=f'📍 Distribución por Departamento - {anio_seleccionado}',
        xaxis_title='Cantidad de Accidentes',
        yaxis_title='',
        height=650,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=20,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        xaxis=dict(showgrid=True, gridcolor=COLORES['grid_oscuro'], color=COLORES['texto_claro']),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color=COLORES['texto_claro'])),
        margin=dict(l=120, r=50, t=80, b=50)
    )
    
    return fig, df_filtrado

# VISUALIZACIÓN 2: SERIE TEMPORAL
def crear_vis2_serie_temporal(df, deptos_seleccionados, depto_desde_vis1=None):
    """Serie temporal con resaltado de departamento"""
    
    # Si hay un departamento seleccionado desde Vis1, agregarlo automáticamente
    deptos_a_mostrar = list(deptos_seleccionados)
    if depto_desde_vis1 and depto_desde_vis1 not in deptos_a_mostrar:
        deptos_a_mostrar.append(depto_desde_vis1)
    
    df_filtrado = df[df['departamento'].isin(deptos_a_mostrar)].copy()
    df_agrupado = df_filtrado.groupby(['año', 'departamento'])['accidentes'].sum().reset_index()
    
    fig = go.Figure()
    
    for depto in deptos_a_mostrar:
        df_depto = df_agrupado[df_agrupado['departamento'] == depto]
        
        # Resaltar el departamento seleccionado desde Vis1
        if depto == depto_desde_vis1:
            color = COLORES['rojo_critico']
            ancho = 4
            opacity = 1.0
            nombre_display = f"{depto}"  
        else:
            color = COLORES['azul_informativo']
            ancho = 2
            opacity = 0.7
            nombre_display = depto
        
        fig.add_trace(go.Scatter(
            x=df_depto['año'],
            y=df_depto['accidentes'],
            mode='lines+markers',
            name=nombre_display,
            line=dict(color=color, width=ancho),
            marker=dict(size=8, color=color),
            opacity=opacity,
            hovertemplate='<b>%{fullData.name}</b><br>Año: %{x}<br>Accidentes: %{y:,}<br><extra></extra>'
        ))
    
    fig.update_layout(
        title='📈 Evolución Temporal de Accidentes (2020-2024)',
        xaxis_title='Año',
        yaxis_title='Cantidad de Accidentes',
        height=400,
        hovermode='x unified',
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        xaxis=dict(showgrid=True, gridcolor=COLORES['grid_oscuro'], dtick=1, color=COLORES['texto_claro']),
        yaxis=dict(showgrid=True, gridcolor=COLORES['grid_oscuro'], color=COLORES['texto_claro']),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02, font=dict(color=COLORES['texto_claro']))
    )
    
    return fig

# VISUALIZACIÓN 3: TOP 10 TIPOS CON DRILL-DOWN
def crear_vis3_top_tipos(df, rango_temporal='Año completo'):
    """Top 10 tipos de accidentes con filtro temporal"""
    
    # Aplicar filtro de trimestre si se selecciona
    if rango_temporal == 'Q1':
        df = df[df['mes_num'].isin([1, 2, 3])]
    elif rango_temporal == 'Q2':
        df = df[df['mes_num'].isin([4, 5, 6])]
    elif rango_temporal == 'Q3':
        df = df[df['mes_num'].isin([7, 8, 9])]
    elif rango_temporal == 'Q4':
        df = df[df['mes_num'].isin([10, 11, 12])]
    
    df_agrupado = df.groupby('tipo_accidente')['cantidad'].sum().reset_index()
    df_agrupado = df_agrupado.sort_values('cantidad', ascending=True).tail(10)
    
    # Calcular porcentajes
    total = df_agrupado['cantidad'].sum()
    df_agrupado['porcentaje'] = (df_agrupado['cantidad'] / total * 100).round(1)
    
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
    
    # Resaltar si hay selección
    if st.session_state.tipo_accidente_seleccionado:
        df_agrupado['color'] = df_agrupado.apply(
            lambda row: COLORES['verde_positivo'] if row['tipo_accidente'] == st.session_state.tipo_accidente_seleccionado else row['color'],
            axis=1
        )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_agrupado['cantidad'],
        y=df_agrupado['tipo_accidente'],
        orientation='h',
        marker=dict(color=df_agrupado['color'], line=dict(width=0)),
        text=[f"{cant:,} ({pct}%)" for cant, pct in zip(df_agrupado['cantidad'], df_agrupado['porcentaje'])],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Cantidad: %{x:,}<br><extra></extra>'
    ))
    
    fig.update_layout(
        title=f'🏆 Top 10 Tipos de Accidentes - {rango_temporal}',
        xaxis_title='Cantidad de Accidentes',
        yaxis_title='',
        height=500,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        xaxis=dict(showgrid=True, gridcolor=COLORES['grid_oscuro'], color=COLORES['texto_claro']),
        yaxis=dict(showgrid=False, color=COLORES['texto_claro']),
        showlegend=False
    )
    
    return fig, df_agrupado

# Visualización 3.1: Evolución mensual del tipo seleccionado 

def crear_vis3_1_evolucion_tipo(df, tipo_seleccionado=None):
    """Gráfico de línea mostrando evolución mensual del tipo de accidente seleccionado"""
    
    if tipo_seleccionado:
        df_filtrado = df[df['tipo_accidente'] == tipo_seleccionado].copy()
        
        df_mensual = df_filtrado.groupby('mes_num')['cantidad'].sum().reset_index()
        
        meses_nombres = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        
        df_mensual['mes_nombre'] = df_mensual['mes_num'].map(meses_nombres)
        df_mensual = df_mensual.sort_values('mes_num')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_mensual['mes_nombre'],
            y=df_mensual['cantidad'],
            mode='lines+markers',
            name=tipo_seleccionado.title(),
            line=dict(color=COLORES['rojo_critico'], width=3),
            marker=dict(size=10, color=COLORES['rojo_critico']),
            fill='tozeroy',
            fillcolor='rgba(211, 47, 47, 0.2)',
            hovertemplate='<b>%{x}</b><br>Accidentes: %{y:,}<br><extra></extra>'
        ))
        
        fig.update_layout(
            title=f'📊 Evolución Mensual: {tipo_seleccionado.title()}',
            xaxis_title='Mes',
            yaxis_title='Cantidad de Accidentes',
            height=400,
            font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
            title_font_size=18,
            paper_bgcolor=COLORES['fondo_oscuro'],
            plot_bgcolor=COLORES['fondo_oscuro'],
            xaxis=dict(showgrid=False, color=COLORES['texto_claro'], tickangle=-45),
            yaxis=dict(showgrid=True, gridcolor=COLORES['grid_oscuro'], color=COLORES['texto_claro']),
            showlegend=False
        )
        
    else:
        # Si no hay tipo seleccionado, mostrar mensaje
        fig = go.Figure()
        
        fig.add_annotation(
            text="Selecciona un tipo de accidente arriba<br>para ver su evolución mensual",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color=COLORES['gris_neutro']),
            align="center"
        )
        
        fig.update_layout(
            title='📊 Evolución Mensual por Tipo de Accidente',
            height=400,
            font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
            title_font_size=18,
            paper_bgcolor=COLORES['fondo_oscuro'],
            plot_bgcolor=COLORES['fondo_oscuro'],
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False)
        )
    
    return fig

# VISUALIZACIÓN 4: HEATMAP
def crear_vis4_heatmap(df):
    """Heatmap día/hora de accidentes"""
    
    df_filtrado = df.copy()
    
    df_pivot = df_filtrado.pivot_table(
        values='accidentes',
        index='hora_de_ocurrencia',
        columns='dia_semana',
        aggfunc='sum'
    )
    
    dias_ordenados = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    df_pivot = df_pivot[dias_ordenados]
    
    if 'hora_num' in df_filtrado.columns:
        orden_horas = df_filtrado[['hora_de_ocurrencia', 'hora_num']].drop_duplicates()
        orden_horas = orden_horas.sort_values('hora_num')
        df_pivot = df_pivot.reindex(orden_horas['hora_de_ocurrencia'].values)
    
    fig = go.Figure(data=go.Heatmap(
        z=df_pivot.values,
        x=[d.capitalize() for d in df_pivot.columns],
        y=df_pivot.index,
        colorscale=ESCALA_CALOR,
        hovertemplate='<b>%{y}</b><br>%{x}<br>Accidentes: %{z:,}<br><extra></extra>',
        colorbar=dict(title="Accidentes", thicknessmode="pixels", thickness=15, lenmode="pixels", len=300)
    ))
    
    fig.update_layout(
        title='🔥 Patrones Temporales: Accidentes por Día y Hora',
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

# VISUALIZACIÓN 5: DISTRIBUCIÓN DE VEHÍCULOS
def crear_vis5_vehiculos(df):
    """Donut chart de vehículos con interacción"""
    
    df_agrupado = df.groupby('tipo_de_vehiculo')['cantidad'].sum().reset_index()
    df_agrupado = df_agrupado.sort_values('cantidad', ascending=False)
    
    total = df_agrupado['cantidad'].sum()
    df_agrupado['porcentaje'] = (df_agrupado['cantidad'] / total * 100).round(1)
    
    colores = px.colors.qualitative.Set3[:len(df_agrupado)]
    
    if st.session_state.tipo_vehiculo_seleccionado:
        colores = [COLORES['verde_positivo'] if v == st.session_state.tipo_vehiculo_seleccionado else '#CCCCCC' 
                   for v in df_agrupado['tipo_de_vehiculo']]
    
    fig = go.Figure(data=[go.Pie(
        labels=df_agrupado['tipo_de_vehiculo'],
        values=df_agrupado['cantidad'],
        hole=0.4,
        marker=dict(colors=colores, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>Cantidad: %{value:,}<br>Porcentaje: %{percent}<br><extra></extra>'
    )])
    
    fig.update_layout(
        title='🚙 Distribución de Vehículos Involucrados',
        height=500,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        showlegend=True,
        legend=dict(font=dict(color=COLORES['texto_claro']))
    )
    
    return fig, df_agrupado

# VISUALIZACIÓN 6: FALLECIDOS VS LESIONADOS
def crear_vis6_fallecidos_lesionados(df_fallecidos, df_lesionados, departamento=None):
    """Comparación fallecidos vs lesionados"""
    
    if departamento:
        df_fall = df_fallecidos[df_fallecidos['departamento'] == departamento].copy()
        df_les = df_lesionados[df_lesionados['departamento'] == departamento].copy()
    else:
        df_fall = df_fallecidos.groupby('año')['fallecidos'].sum().reset_index()
        df_les = df_lesionados.groupby('año')['lesionados'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_fall['año'],
        y=df_fall['fallecidos'],
        mode='lines+markers',
        name='Fallecidos',
        line=dict(color=COLORES['rojo_critico'], width=3),
        marker=dict(size=10, color=COLORES['rojo_critico']),
        hovertemplate='<b>Fallecidos</b><br>Año: %{x}<br>Cantidad: %{y:,}<br><extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_les['año'],
        y=df_les['lesionados'],
        mode='lines+markers',
        name='Lesionados',
        line=dict(color=COLORES['naranja_alerta'], width=3),
        marker=dict(size=10, color=COLORES['naranja_alerta']),
        hovertemplate='<b>Lesionados</b><br>Año: %{x}<br>Cantidad: %{y:,}<br><extra></extra>'
    ))
    
    titulo = '💔 Comparación: Fallecidos vs Lesionados (2020-2024)'
    if departamento:
        titulo += f' - {departamento}'
    
    fig.update_layout(
        title=titulo,
        xaxis_title='Año',
        yaxis_title='Cantidad de Personas',
        height=400,
        hovermode='x unified',
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        xaxis=dict(showgrid=True, gridcolor=COLORES['grid_oscuro'], dtick=1, color=COLORES['texto_claro']),
        yaxis=dict(showgrid=True, gridcolor=COLORES['grid_oscuro'], color=COLORES['texto_claro']),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=COLORES['texto_claro']))
    )
    
    return fig

# VISUALIZACIÓN 7: TABLA RESUMEN
def crear_vis7_tabla_resumen(df_accidentes, df_fallecidos, df_lesionados, anio):
    """Tabla resumen por departamento"""
    
    df_acc = df_accidentes[df_accidentes['año'] == anio].copy()
    df_fall = df_fallecidos[df_fallecidos['año'] == anio].copy()
    df_les = df_lesionados[df_lesionados['año'] == anio].copy()
    
    df_resumen = df_acc.merge(df_fall, on='departamento', how='left')
    df_resumen = df_resumen.merge(df_les, on='departamento', how='left')
    
    df_resumen['tasa_fatalidad'] = (df_resumen['fallecidos'] / df_resumen['accidentes'] * 100).round(2)
    
    df_resumen = df_resumen.sort_values('accidentes', ascending=False)
    
    df_resumen = df_resumen[['departamento', 'accidentes', 'fallecidos', 'lesionados', 'tasa_fatalidad']]
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Departamento</b>', '<b>Accidentes</b>', '<b>Fallecidos</b>', '<b>Lesionados</b>', '<b>Tasa Fatalidad (%)</b>'],
            fill_color=COLORES['azul_informativo'],
            align='left',
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[df_resumen['departamento'], 
                    df_resumen['accidentes'].apply(lambda x: f"{x:,}"),
                    df_resumen['fallecidos'].apply(lambda x: f"{x:,}"),
                    df_resumen['lesionados'].apply(lambda x: f"{x:,}"),
                    df_resumen['tasa_fatalidad']],
            fill_color=[['#2C2C2C', '#1E1E1E'] * (len(df_resumen) // 2 + 1)],
            align='left',
            font=dict(color=COLORES['texto_claro'], size=11),
            height=30
        )
    )])
    
    fig.update_layout(
        title=f'📊 Tabla Resumen Estadístico - {anio}',
        height=600,
        font=dict(family="Segoe UI, sans-serif"),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# VISUALIZACIÓN 8: DISTRIBUCIÓN POR EDAD
def crear_vis8_distribucion_edad(df_lesionados, df_fallecidos, modo='comparativo'):
    """Distribución por grupos de edad"""
    
    fig = go.Figure()
    
    if modo == 'comparativo':
        fig.add_trace(go.Bar(
            x=df_fallecidos['grupos_de_edad'],
            y=df_fallecidos['total'],
            name='Fallecidos',
            marker=dict(color=COLORES['rojo_critico'], opacity=0.7),
            hovertemplate='<b>Fallecidos</b><br>Edad: %{x}<br>Cantidad: %{y:,}<br><extra></extra>'
        ))
        
        fig.add_trace(go.Bar(
            x=df_lesionados['grupos_de_edad'],
            y=df_lesionados['total'],
            name='Lesionados',
            marker=dict(color=COLORES['naranja_alerta'], opacity=0.7),
            hovertemplate='<b>Lesionados</b><br>Edad: %{x}<br>Cantidad: %{y:,}<br><extra></extra>'
        ))
        
        barmode = 'group'
    else:
        fig.add_trace(go.Bar(
            x=df_fallecidos['grupos_de_edad'],
            y=df_fallecidos['total'],
            name='Fallecidos',
            marker=dict(color=COLORES['rojo_critico']),
            hovertemplate='<b>Fallecidos</b><br>Edad: %{x}<br>Cantidad: %{y:,}<br><extra></extra>'
        ))
        barmode = 'relative'
    
    fig.update_layout(
        title='👥 Distribución por Grupos de Edad',
        xaxis_title='Grupos de Edad',
        yaxis_title='Cantidad de Personas',
        height=400,
        barmode=barmode,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        xaxis=dict(showgrid=False, color=COLORES['texto_claro']),
        yaxis=dict(showgrid=True, gridcolor=COLORES['grid_oscuro'], color=COLORES['texto_claro']),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=COLORES['texto_claro']))
    )
    
    return fig

# INTERFAZ PRINCIPAL
def main():
    """Función principal de la aplicación"""
    
    st.markdown("""
        <style>
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #2C2C2C;
            border-radius: 4px 4px 0px 0px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1976D2;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(
        f"""
        <h1 style='text-align: center; color: {COLORES['fondo_claro']};'>
        Dashboard de Accidentes de Tránsito
        </h1>
        <h3 style='text-align: center; color: {COLORES['azul_informativo']};'>
        Guatemala 2020-2024
        </h3>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    with st.spinner('Cargando datos...'):
        (df_accidentes, df_dia_hora, df_tipos, df_vehiculos, 
         df_lesionados, df_lesionados_edad, df_fallecidos, df_fallecidos_edad) = cargar_datos()
    
    # SIDEBAR
    with st.sidebar:
        st.title("Panel de Control")
        st.markdown("---")
        
        st.subheader("📅 Período Temporal")
        anio_seleccionado = st.select_slider(
            "Año (distribución por departamento):",
            options=[2020, 2021, 2022, 2023, 2024],
            value=2024
        )
        
        st.markdown("---")
        
        st.subheader("📍 Departamentos")
        todos_deptos = sorted(df_accidentes['departamento'].unique())
        
        deptos_defecto = ['Guatemala', 'Escuintla', 'Quetzaltenango']
        deptos_disponibles = [d for d in deptos_defecto if d in todos_deptos]
        
        deptos_seleccionados = st.multiselect(
            "Seleccionar departamentos (evolución temporal):",
            options=todos_deptos,
            default=deptos_disponibles
        )
        
        st.markdown("---")
        
        st.subheader("👁️ Visualizaciones")
        mostrar_vis = st.multiselect(
            "Mostrar gráficas:",
            options=['Todas', 'Distribución Departamental', 'Serie Temporal', 'Top Tipos', 
                     'Heatmap', 'Vehículos', 'Fallecidos vs Lesionados', 'Tabla Resumen', 'Edad'],
            default=['Todas']
        )
        
        mostrar_todas = 'Todas' in mostrar_vis
        
        st.markdown("---")
        
        st.subheader("📊 Métricas del Año")
        total_acc = df_accidentes[df_accidentes['año'] == anio_seleccionado]['accidentes'].sum()
        total_fall = df_fallecidos[df_fallecidos['año'] == anio_seleccionado]['fallecidos'].sum()
        total_les = df_lesionados[df_lesionados['año'] == anio_seleccionado]['lesionados'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🚗 Accidentes", f"{total_acc:,}")
        with col2:
            st.metric("💀 Fallecidos", f"{total_fall:,}")
        
        st.metric("🏥 Lesionados", f"{total_les:,}")
        
        st.markdown("---")
        
        # Botón de reset
        if st.button("🔄 Resetear Filtros"):
            st.session_state.departamento_seleccionado = None
            st.session_state.tipo_accidente_seleccionado = None
            st.session_state.tipo_vehiculo_seleccionado = None
            st.rerun()
        
        # Mostrar selecciones activas
        if st.session_state.departamento_seleccionado:
            st.info(f"Depto: **{st.session_state.departamento_seleccionado}**")
        if st.session_state.tipo_accidente_seleccionado:
            st.info(f"Tipo de accidente: **{st.session_state.tipo_accidente_seleccionado}**")
        if st.session_state.tipo_vehiculo_seleccionado:
            st.info(f"Vehículo: **{st.session_state.tipo_vehiculo_seleccionado}**")
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["Vista General", "Análisis Detallado", "Comparativas", "Modelos"])
    
    # TAB 1: VISTA GENERAL
    with tab1:
        if mostrar_todas or 'Distribución Departamental' in mostrar_vis or 'Serie Temporal' in mostrar_vis:
            col1, col2 = st.columns([1.2, 1])
            
            with col1:
                if mostrar_todas or 'Distribución Departamental' in mostrar_vis:
                    st.subheader("Distribución por Departamento")
                    fig1, df_dept = crear_vis1_departamentos(df_accidentes, anio_seleccionado)
                    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
                    
                    depto_click = st.selectbox(
                        "Selecciona un departamento para comparar:",
                        options=['Ninguno'] + list(df_dept['departamento']),
                        key='selector_depto'
                    )
                    
                    if depto_click != 'Ninguno':
                        st.session_state.departamento_seleccionado = depto_click
                    else:
                        st.session_state.departamento_seleccionado = None
                    
                    st.caption("**Tip:** Selecciona un departamento para agregarlo automáticamente a la comparación temporal")
            
            with col2:
                if mostrar_todas or 'Serie Temporal' in mostrar_vis:
                    st.subheader("Evolución Temporal")
                    
                    if not deptos_seleccionados:
                        st.warning("Selecciona departamentos en el panel lateral")
                    else:
                        fig2 = crear_vis2_serie_temporal(
                            df_accidentes, 
                            deptos_seleccionados,
                            depto_desde_vis1=st.session_state.departamento_seleccionado
                        )
                        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
                        
                        if st.session_state.departamento_seleccionado:
                            st.success(f"Comparando **{st.session_state.departamento_seleccionado}** con departamentos base")
                        else:
                            st.caption("Selecciona un departamento arriba para agregarlo a la comparación")
        
        st.markdown("---")
        
        # NUEVO LAYOUT: Top Tipos con su evolución mensual (CORREGIDO)
        if mostrar_todas or 'Top Tipos' in mostrar_vis:
            col3, col4 = st.columns([1, 1.2])
            
            with col3:
                st.subheader("Top 10 Tipos de Accidentes")
                
                # FILTRO DRILL-DOWN
                rango = st.selectbox(
                    "Rango temporal:", 
                    ['Año completo', 'Q1', 'Q2', 'Q3', 'Q4'], 
                    key='rango_tipos'
                )
                
                fig3_temp, df_tipos_top = crear_vis3_top_tipos(df_tipos, rango)
                
                tipos_disponibles = df_tipos_top['tipo_accidente'].tolist()
                
                tipo_click = st.selectbox(
                    "Selecciona un tipo para ver su evolución mensual:",
                    options=['Ninguno'] + tipos_disponibles,
                    key='selector_tipo'
                )
                
                if tipo_click != 'Ninguno':
                    st.session_state.tipo_accidente_seleccionado = tipo_click
                else:
                    st.session_state.tipo_accidente_seleccionado = None
                
                fig3, _ = crear_vis3_top_tipos(df_tipos, rango)
                st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
                            
            with col4:
                st.subheader("Evolución Mensual del Tipo Seleccionado")
                
                fig_evol = crear_vis3_1_evolucion_tipo(
                    df_tipos, 
                    tipo_seleccionado=st.session_state.tipo_accidente_seleccionado
                )
                st.plotly_chart(fig_evol, use_container_width=True, config={'displayModeBar': False})
                
                if st.session_state.tipo_accidente_seleccionado:
                    st.info(f"Mostrando evolución mensual de **{st.session_state.tipo_accidente_seleccionado}**")
                else:
                    st.caption("Selecciona un tipo de accidente para ver su patrón mensual")
        
        st.markdown("---")
        
        # HEATMAP 
        if mostrar_todas or 'Heatmap' in mostrar_vis:
            st.subheader("Patrones Temporales Generales: Día y Hora")
            fig4 = crear_vis4_heatmap(df_dia_hora)
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
            st.caption("Visualización general de todos los accidentes por día y hora (sin filtros)")

    # TAB 2: ANÁLISIS DETALLADO
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            if mostrar_todas or 'Vehículos' in mostrar_vis:
                st.subheader("Distribución de Vehículos")
                
                fig5_temp, df_veh = crear_vis5_vehiculos(df_vehiculos)
                
                veh_click = st.selectbox(
                    "Selecciona un tipo de vehículo:",
                    options=['Ninguno'] + list(df_veh['tipo_de_vehiculo']),
                    key='selector_veh'
                )
                
                if veh_click != 'Ninguno':
                    st.session_state.tipo_vehiculo_seleccionado = veh_click
                else:
                    st.session_state.tipo_vehiculo_seleccionado = None
                
                fig5, _ = crear_vis5_vehiculos(df_vehiculos)
                st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
                
                if st.session_state.tipo_vehiculo_seleccionado:
                    st.success(f"Resaltando: **{st.session_state.tipo_vehiculo_seleccionado}**")
                else:
                    st.caption("Selecciona un tipo de vehículo para resaltarlo")
        
        with col2:
            if mostrar_todas or 'Edad' in mostrar_vis:
                st.subheader("Distribución por Edad")
                
                modo = st.radio("Modo de vista:", ['comparativo', 'individual'], horizontal=True, key='modo_edad')
                
                fig8 = crear_vis8_distribucion_edad(df_lesionados_edad, df_fallecidos_edad, modo)
                st.plotly_chart(fig8, use_container_width=True, config={'displayModeBar': False})
                st.caption("Análisis demográfico de víctimas")
        
        st.markdown("---")
        
        if mostrar_todas or 'Tabla Resumen' in mostrar_vis:
            st.subheader("Tabla Resumen Estadístico")
            fig7 = crear_vis7_tabla_resumen(df_accidentes, df_fallecidos, df_lesionados, anio_seleccionado)
            st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar': False})
            st.caption("Resumen completo con tasa de fatalidad por departamento")
    
    # TAB 3: COMPARATIVAS
    with tab3:
        if mostrar_todas or 'Fallecidos vs Lesionados' in mostrar_vis:
            st.subheader("Comparación: Fallecidos vs Lesionados")
            
            depto_comparar = st.selectbox(
                "Filtrar por departamento (opcional):",
                ['Todos'] + sorted(df_accidentes['departamento'].unique()),
                key='depto_comparar'
            )
            
            depto_filtro = None if depto_comparar == 'Todos' else depto_comparar
            
            fig6 = crear_vis6_fallecidos_lesionados(df_fallecidos, df_lesionados, depto_filtro)
            st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
            st.caption("Evolución temporal comparativa de fallecidos y lesionados")

    with tab4:
        if render_modelos_tab is not None:
            render_modelos_tab()
        else:
            st.error('''
            ⚠️ La pestaña de modelos no está disponible.
            
            Asegúrate de que:
            1. El archivo modelos_tab.py esté en el mismo directorio que dashboard.py
            2. La carpeta models/ contenga resumen_modelos.json
            3. No haya errores de sintaxis en el import
            ''')

if __name__ == "__main__":
    main()