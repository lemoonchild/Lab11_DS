import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pickle
import json

# PALETA DE COLORES (debe coincidir con dashboard.py)
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

@st.cache_data
def cargar_metricas_modelos():
    """Carga las métricas de los modelos desde el archivo JSON"""
    try:
        with open('./models/resumen_modelos.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("No se encontró el archivo de métricas de modelos")
        return None

def crear_matriz_confusion(matriz, titulo, modelo_nombre):
    """
    Crea una visualización de matriz de confusión
    
    Args:
        matriz: Lista de listas con la matriz de confusión
        titulo: Título del gráfico
        modelo_nombre: Nombre del modelo para personalizar etiquetas
    """
    # Determinar etiquetas según el modelo
    if "gravedad" in titulo.lower() or "Modelo 1" in titulo:
        labels = ['Baja Gravedad', 'Alta Gravedad']
    elif "tipo" in titulo.lower() or "Modelo 3" in titulo:
        labels = ['Riesgo Bajo', 'Riesgo Medio', 'Riesgo Alto']
    else:
        # Por defecto para clasificación binaria
        labels = ['Clase 0', 'Clase 1']
    
    # Convertir matriz a numpy array si no lo es
    matriz_np = np.array(matriz)
    
    # Crear texto para cada celda con valores y porcentajes
    total = matriz_np.sum()
    text = []
    for i in range(len(matriz_np)):
        row_text = []
        for j in range(len(matriz_np[i])):
            valor = matriz_np[i][j]
            porcentaje = (valor / total * 100) if total > 0 else 0
            row_text.append(f"{valor}<br>({porcentaje:.1f}%)")
        text.append(row_text)
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matriz_np,
        x=[f'Predicho: {l}' for l in labels],
        y=[f'Real: {l}' for l in labels],
        text=text,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
        colorscale=[
            [0, COLORES['verde_positivo']], 
            [0.5, COLORES['amarillo_preventivo']], 
            [1, COLORES['rojo_critico']]
        ],
        showscale=True,
        colorbar=dict(title="Frecuencia", thickness=15)
    ))
    
    fig.update_layout(
        title=titulo,
        xaxis_title="Predicción",
        yaxis_title="Valor Real",
        height=500,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        xaxis=dict(color=COLORES['texto_claro']),
        yaxis=dict(color=COLORES['texto_claro'])
    )
    
    return fig

def crear_grafico_metricas_clasificacion(metricas_dict, nombre_modelo):
    """
    Crea un gráfico de barras comparando métricas de clasificación
    
    Args:
        metricas_dict: Diccionario con las métricas (accuracy, precision, recall, f1_score)
        nombre_modelo: Nombre del modelo
    """
    metricas_nombres = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    metricas_keys = ['accuracy', 'precision', 'recall', 'f1_score']
    
    valores = [metricas_dict.get(key, 0) for key in metricas_keys]
    
    # Asignar colores según el valor
    colores_barras = []
    for val in valores:
        if val >= 0.8:
            colores_barras.append(COLORES['verde_positivo'])
        elif val >= 0.6:
            colores_barras.append(COLORES['amarillo_preventivo'])
        else:
            colores_barras.append(COLORES['naranja_alerta'])
    
    fig = go.Figure(data=[
        go.Bar(
            x=metricas_nombres,
            y=valores,
            marker=dict(color=colores_barras, line=dict(width=1, color='white')),
            text=[f"{v:.4f}" for v in valores],
            textposition='outside',
            textfont=dict(size=14, color=COLORES['texto_claro'])
        )
    ])
    
    fig.update_layout(
        title=f'Métricas de Clasificación - {nombre_modelo}',
        xaxis_title='Métrica',
        yaxis_title='Valor',
        yaxis=dict(range=[0, 1.1], showgrid=True, gridcolor=COLORES['grid_oscuro'], color=COLORES['texto_claro']),
        height=450,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        xaxis=dict(showgrid=False, color=COLORES['texto_claro']),
        showlegend=False
    )
    
    return fig

def crear_grafico_metricas_regresion(metricas_dict, nombre_modelo):
    """
    Crea visualización de métricas de regresión
    
    Args:
        metricas_dict: Diccionario con métricas (mse, rmse, mae, r2)
        nombre_modelo: Nombre del modelo
    """
    # Crear dos subgráficos: uno para R² y otro para errores
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Coeficiente de Determinación (R²)', 'Métricas de Error'),
        specs=[[{"type": "indicator"}, {"type": "bar"}]]
    )
    
    # Gráfico de indicador para R²
    r2_val = metricas_dict.get('r2', 0)
    color_r2 = COLORES['verde_positivo'] if r2_val >= 0.9 else COLORES['amarillo_preventivo'] if r2_val >= 0.7 else COLORES['naranja_alerta']
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=r2_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "R²", 'font': {'color': COLORES['texto_claro']}},
            delta={'reference': 0.8},
            gauge={
                'axis': {'range': [None, 1], 'tickcolor': COLORES['texto_claro']},
                'bar': {'color': color_r2},
                'bgcolor': COLORES['gris_neutro'],
                'borderwidth': 2,
                'bordercolor': COLORES['texto_claro'],
                'steps': [
                    {'range': [0, 0.7], 'color': COLORES['naranja_alerta']},
                    {'range': [0.7, 0.9], 'color': COLORES['amarillo_preventivo']},
                    {'range': [0.9, 1], 'color': COLORES['verde_positivo']}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': 0.95
                }
            }
        ),
        row=1, col=1
    )
    
    # Gráfico de barras para errores
    error_nombres = ['RMSE', 'MAE']
    error_valores = [
        metricas_dict.get('rmse', 0),
        metricas_dict.get('mae', 0)
    ]
    
    fig.add_trace(
        go.Bar(
            x=error_nombres,
            y=error_valores,
            marker=dict(color=COLORES['azul_informativo'], line=dict(width=1, color='white')),
            text=[f"{v:.2f}" for v in error_valores],
            textposition='outside',
            textfont=dict(size=14, color=COLORES['texto_claro'])
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title=f'Métricas de Regresión - {nombre_modelo}',
        height=450,
        font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
        title_font_size=18,
        paper_bgcolor=COLORES['fondo_oscuro'],
        plot_bgcolor=COLORES['fondo_oscuro'],
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=False, color=COLORES['texto_claro'], row=1, col=2)
    fig.update_yaxes(showgrid=True, gridcolor=COLORES['grid_oscuro'], color=COLORES['texto_claro'], row=1, col=2)
    
    return fig

def crear_tabla_comparativa(modelos_data, modelos_seleccionados):
    """
    Crea una tabla comparativa de los modelos seleccionados
    
    Args:
        modelos_data: Datos completos de todos los modelos
        modelos_seleccionados: Lista de modelos a comparar
    """
    data_tabla = []
    
    for modelo_key in modelos_seleccionados:
        if modelo_key == 'modelo1_gravedad':
            nombre_base = 'Modelo 1: Gravedad'
            modelo_info = modelos_data['modelo1_gravedad']
            
            # Obtener el mejor algoritmo
            mejor_algo = max(
                modelo_info['metricas'].items(),
                key=lambda x: x[1].get('f1_score', 0)
            )
            
            data_tabla.append({
                'Modelo': nombre_base,
                'Tipo': 'Clasificación',
                'Algoritmo': mejor_algo[0],
                'Métrica Principal': f"F1: {mejor_algo[1]['f1_score']:.4f}",
                'Accuracy': f"{mejor_algo[1]['accuracy']:.4f}",
                'Descripción': modelo_info['descripcion']
            })
            
        elif modelo_key == 'modelo2_cantidad':
            nombre_base = 'Modelo 2: Cantidad'
            modelo_info = modelos_data['modelo2_cantidad']
            
            # Obtener el mejor algoritmo
            mejor_algo = min(
                modelo_info['metricas'].items(),
                key=lambda x: x[1].get('rmse', float('inf'))
            )
            
            data_tabla.append({
                'Modelo': nombre_base,
                'Tipo': 'Regresión',
                'Algoritmo': mejor_algo[0],
                'Métrica Principal': f"RMSE: {mejor_algo[1]['rmse']:.2f}",
                'Accuracy': f"R²: {mejor_algo[1]['r2']:.4f}",
                'Descripción': modelo_info['descripcion']
            })
            
        elif modelo_key == 'modelo3_tipo':
            nombre_base = 'Modelo 3: Nivel de Riesgo'
            modelo_info = modelos_data['modelo3_tipo']
            
            # Obtener el mejor algoritmo
            mejor_algo = max(
                modelo_info['metricas'].items(),
                key=lambda x: x[1].get('f1_score', 0)
            )
            
            data_tabla.append({
                'Modelo': nombre_base,
                'Tipo': 'Clasificación',
                'Algoritmo': mejor_algo[0],
                'Métrica Principal': f"F1: {mejor_algo[1]['f1_score']:.4f}",
                'Accuracy': f"{mejor_algo[1]['accuracy']:.4f}",
                'Descripción': modelo_info['descripcion']
            })
    
    df_comparacion = pd.DataFrame(data_tabla)
    return df_comparacion

def mostrar_desempeno_modelo(modelo_key, modelo_info, algoritmo_seleccionado):
    """
    Muestra el desempeño detallado de un modelo específico
    
    Args:
        modelo_key: Clave del modelo (modelo1_gravedad, modelo2_cantidad, modelo3_tipo)
        modelo_info: Información del modelo
        algoritmo_seleccionado: Algoritmo seleccionado para mostrar
    """
    metricas = modelo_info['metricas'][algoritmo_seleccionado]
    
    # Título según el modelo
    if modelo_key == 'modelo1_gravedad':
        titulo = "Modelo 1: Clasificación de Gravedad de Accidente"
    elif modelo_key == 'modelo2_cantidad':
        titulo = "Modelo 2: Predicción de Cantidad de Accidentes"
    else:
        titulo = "Modelo 3: Clasificación de Nivel de Riesgo"
    
    st.subheader(f"{titulo} - {algoritmo_seleccionado}")
    
    # Mostrar descripción
    with st.expander("Descripción del Modelo", expanded=False):
        st.write(modelo_info['descripcion'])
        st.write(f"**Características utilizadas:** {', '.join(modelo_info['features'])}")
        st.write(f"**Tamaño del dataset:** {modelo_info['n_samples']} muestras")
    
    # Mostrar métricas según el tipo de modelo
    if modelo_key == 'modelo2_cantidad':
        # Modelo de regresión
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.metric("RMSE", f"{metricas['rmse']:.2f}")
            st.metric("MAE", f"{metricas['mae']:.2f}")
        
        with col2:
            st.metric("R²", f"{metricas['r2']:.4f}")
            st.metric("MSE", f"{metricas['mse']:.2f}")
        
        # Gráfico de métricas
        fig = crear_grafico_metricas_regresion(metricas, algoritmo_seleccionado)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    else:
        # Modelo de clasificación
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Accuracy", f"{metricas['accuracy']:.4f}")
        with col2:
            st.metric("Precision", f"{metricas['precision']:.4f}")
        with col3:
            st.metric("Recall", f"{metricas['recall']:.4f}")
        with col4:
            st.metric("F1-Score", f"{metricas['f1_score']:.4f}")
        
        # Gráfico de métricas
        col_a, col_b = st.columns([1, 1])
        
        with col_a:
            fig_metricas = crear_grafico_metricas_clasificacion(metricas, algoritmo_seleccionado)
            st.plotly_chart(fig_metricas, use_container_width=True, config={'displayModeBar': False})
        
        with col_b:
            # Matriz de confusión
            if 'confusion_matrix' in metricas:
                fig_matriz = crear_matriz_confusion(
                    metricas['confusion_matrix'],
                    f'Matriz de Confusión - {algoritmo_seleccionado}',
                    modelo_key
                )
                st.plotly_chart(fig_matriz, use_container_width=True, config={'displayModeBar': False})

def render_modelos_tab():
    """
    Función principal que renderiza la pestaña de Modelos
    """
    st.markdown(
        f"""
        <h2 style='text-align: center; color: {COLORES['azul_informativo']};'>
        Exploración de Modelos Predictivos
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Cargar métricas
    modelos_data = cargar_metricas_modelos()
    
    if modelos_data is None:
        st.error("No se pudieron cargar los datos de los modelos")
        return
    
    # Información general
    st.info(f"""
    **Información General:**
    - **Fecha de entrenamiento:** {modelos_data['fecha_entrenamiento']}
    - **Modelos disponibles:** 3 (Gravedad, Cantidad, Nivel de Riesgo)
    """)
    
    st.markdown("---")
    
    # Sección 1: Exploración individual de modelos
    st.markdown("## Exploración Individual de Modelos")
    
    # Selector de modelo
    modelos_disponibles = {
        'Modelo 1: Clasificación de Gravedad': 'modelo1_gravedad',
        'Modelo 2: Predicción de Cantidad': 'modelo2_cantidad',
        'Modelo 3: Clasificación de Nivel de Riesgo': 'modelo3_tipo'
    }
    
    modelo_seleccionado_nombre = st.selectbox(
        "Selecciona un modelo para explorar:",
        list(modelos_disponibles.keys())
    )
    
    modelo_key = modelos_disponibles[modelo_seleccionado_nombre]
    modelo_info = modelos_data[modelo_key]
    
    # Selector de algoritmo
    algoritmos = list(modelo_info['metricas'].keys())
    algoritmo_seleccionado = st.selectbox(
        "Selecciona el algoritmo:",
        algoritmos
    )
    
    # Mostrar desempeño
    mostrar_desempeno_modelo(modelo_key, modelo_info, algoritmo_seleccionado)
    
    st.markdown("---")
    
    # Sección 2: Tabla comparativa
    st.markdown("## Comparación de Modelos")
    
    st.write("Selecciona los modelos que deseas comparar:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        check_modelo1 = st.checkbox("Modelo 1: Gravedad", value=True)
    with col2:
        check_modelo2 = st.checkbox("Modelo 2: Cantidad", value=True)
    with col3:
        check_modelo3 = st.checkbox("Modelo 3: Nivel de Riesgo", value=True)
    
    # Construir lista de modelos seleccionados
    modelos_a_comparar = []
    if check_modelo1:
        modelos_a_comparar.append('modelo1_gravedad')
    if check_modelo2:
        modelos_a_comparar.append('modelo2_cantidad')
    if check_modelo3:
        modelos_a_comparar.append('modelo3_tipo')
    
    if len(modelos_a_comparar) < 2:
        st.warning("Por favor selecciona al menos 2 modelos para comparar")
    else:
        df_comparacion = crear_tabla_comparativa(modelos_data, modelos_a_comparar)
        
        st.markdown("### Tabla Comparativa de Mejores Algoritmos")
        
        # Estilizar la tabla
        st.dataframe(
            df_comparacion,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Modelo": st.column_config.TextColumn("Modelo", width="medium"),
                "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                "Algoritmo": st.column_config.TextColumn("Mejor Algoritmo", width="medium"),
                "Métrica Principal": st.column_config.TextColumn("Métrica Principal", width="small"),
                "Accuracy": st.column_config.TextColumn("Accuracy/R²", width="small"),
                "Descripción": st.column_config.TextColumn("Descripción", width="large")
            }
        )
        
        # Gráfico comparativo
        st.markdown("### Comparación Visual de Desempeño")
        
        # Crear gráfico de radar/barras comparativo
        fig_comparativo = go.Figure()
        
        for modelo_key in modelos_a_comparar:
            if modelo_key == 'modelo1_gravedad':
                nombre = 'Gravedad'
                mejor = max(modelos_data[modelo_key]['metricas'].items(), key=lambda x: x[1].get('f1_score', 0))
                valor = mejor[1]['f1_score']
                metrica = 'F1-Score'
            elif modelo_key == 'modelo2_cantidad':
                nombre = 'Cantidad'
                mejor = min(modelos_data[modelo_key]['metricas'].items(), key=lambda x: x[1].get('rmse', float('inf')))
                # Normalizar RMSE a escala 0-1 (invertido porque menor es mejor)
                valor = mejor[1]['r2']  # Usar R² que ya está en escala 0-1
                metrica = 'R²'
            else:
                nombre = 'Nivel Riesgo'
                mejor = max(modelos_data[modelo_key]['metricas'].items(), key=lambda x: x[1].get('f1_score', 0))
                valor = mejor[1]['f1_score']
                metrica = 'F1-Score'
            
            fig_comparativo.add_trace(go.Bar(
                name=nombre,
                x=[nombre],
                y=[valor],
                text=f"{valor:.4f}",
                textposition='outside'
            ))
        
        fig_comparativo.update_layout(
            title='Comparación de Mejor Desempeño por Modelo',
            yaxis_title='Valor de Métrica (0-1)',
            yaxis=dict(
                range=[0, 1.1],
                showgrid=True,
                gridcolor=COLORES['grid_oscuro'],
                color=COLORES['texto_claro']
            ),
            height=400,
            font=dict(family="Segoe UI, sans-serif", color=COLORES['texto_claro']),
            title_font_size=18,
            paper_bgcolor=COLORES['fondo_oscuro'],
            plot_bgcolor=COLORES['fondo_oscuro'],
            xaxis=dict(showgrid=False, color=COLORES['texto_claro']),
            showlegend=False
        )
        
        st.plotly_chart(fig_comparativo, use_container_width=True, config={'displayModeBar': False})