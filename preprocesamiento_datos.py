import pandas as pd
import numpy as np

def limpiar_cuadro1(df):
    """
    Limpia Cuadro 1: Accidentes por año y departamento
    Transforma de formato wide a long para facilitar visualizaciones
    """
    # Eliminar la fila "Total" 
    df = df[df['departamento'] != 'Total'].copy()
    
    # Eliminar columna fuente_cuadro 
    if 'fuente_cuadro' in df.columns:
        df = df.drop('fuente_cuadro', axis=1)
    
    # Convertir de wide a long format
    df_long = df.melt(
        id_vars=['departamento'],
        value_vars=['2020', '2021', '2022', '2023', '2024'],
        var_name='año',
        value_name='accidentes'
    )
    
    # Convertir año a entero
    df_long['año'] = df_long['año'].astype(int)
    
    # Eliminar valores nulos
    df_long = df_long.dropna(subset=['accidentes'])
    
    # Convertir accidentes a entero
    df_long['accidentes'] = df_long['accidentes'].astype(int)
    
    return df_long


def limpiar_cuadro3(df):
    """
    Limpia Cuadro 3: Accidentes por día de la semana y departamento
    """
    # Eliminar la fila "Total"
    df = df[df['departamento'] != 'Total'].copy()
    
    # Eliminar columna fuente_cuadro
    if 'fuente_cuadro' in df.columns:
        df = df.drop('fuente_cuadro', axis=1)
    
    # Convertir de wide a long format para días
    df_long = df.melt(
        id_vars=['departamento', 'total'],
        value_vars=['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'],
        var_name='dia_semana',
        value_name='accidentes'
    )
    
    # Eliminar columna total 
    df_long = df_long.drop('total', axis=1)
    
    return df_long


def limpiar_cuadro7(df):
    """
    Limpia Cuadro 7: Accidentes por día de la semana y hora
    """
    # Eliminar la fila "Total"
    df = df[df['hora_de_ocurrencia'] != 'Total'].copy()
    
    # Eliminar la fila "Ignorada" si existe
    df = df[df['hora_de_ocurrencia'] != 'Ignorada'].copy()
    
    # Eliminar columna fuente_cuadro
    if 'fuente_cuadro' in df.columns:
        df = df.drop('fuente_cuadro', axis=1)
    
    # Convertir de wide a long format
    df_long = df.melt(
        id_vars=['hora_de_ocurrencia', 'total'],
        value_vars=['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'],
        var_name='dia_semana',
        value_name='accidentes'
    )
    
    # Eliminar columna total
    df_long = df_long.drop('total', axis=1)
    
    # Extraer solo la hora de inicio 
    # "00:00 a 00:59" -> 0
    df_long['hora_num'] = df_long['hora_de_ocurrencia'].str.extract('(\d+):').astype(int)
    
    return df_long


def limpiar_cuadro9(df):
    """
    Limpia Cuadro 9: Accidentes por tipo y mes
    """
    # Eliminar la fila "Total"
    df = df[df['mes_de_ocurrencia'] != 'Total'].copy()
    
    # Eliminar columna fuente_cuadro
    if 'fuente_cuadro' in df.columns:
        df = df.drop('fuente_cuadro', axis=1)
    
    # Convertir de wide a long format para tipos de accidente
    df_long = df.melt(
        id_vars=['mes_de_ocurrencia', 'total'],
        value_vars=['colision', 'atropello', 'derrape', 'choque', 'vuelco', 
                    'embarranco', 'encuneto', 'caida', 'ignorado'],
        var_name='tipo_accidente',
        value_name='cantidad'
    )
    
    # Eliminar columna total
    df_long = df_long.drop('total', axis=1)
    
    # Mapear nombres de meses a números para facilitar ordenamiento
    meses_dict = {
        'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
        'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
        'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
    }
    df_long['mes_num'] = df_long['mes_de_ocurrencia'].map(meses_dict)
    
    return df_long


def limpiar_cuadro31(df):
    """
    Limpia Cuadro 31: Lesionados por año y departamento
    Similar a Cuadro 1
    """
    df = df[df['departamento'] != 'Total'].copy()
    
    if 'fuente_cuadro' in df.columns:
        df = df.drop('fuente_cuadro', axis=1)
    
    df_long = df.melt(
        id_vars=['departamento'],
        value_vars=['2020', '2021', '2022', '2023', '2024'],
        var_name='año',
        value_name='lesionados'
    )
    
    df_long['año'] = df_long['año'].astype(int)
    df_long = df_long.dropna(subset=['lesionados'])
    df_long['lesionados'] = df_long['lesionados'].astype(int)
    
    return df_long


def limpiar_cuadro47(df):
    """
    Limpia Cuadro 47: Fallecidos por año y departamento
    Similar a Cuadro 1
    """
    df = df[df['departamento'] != 'Total'].copy()
    
    # Eliminar columnas innecesarias
    columnas_eliminar = ['fuente_cuadro', 'Unnamed: 6', 'col_10']
    for col in columnas_eliminar:
        if col in df.columns:
            df = df.drop(col, axis=1)
    
    df_long = df.melt(
        id_vars=['departamento'],
        value_vars=['2020', '2021', '2022', '2023', '2024'],
        var_name='año',
        value_name='fallecidos'
    )
    
    df_long['año'] = df_long['año'].astype(int)
    df_long = df_long.dropna(subset=['fallecidos'])
    df_long['fallecidos'] = df_long['fallecidos'].astype(int)
    
    return df_long


def main():
    """
    Función principal que carga, limpia y guarda todos los datos
    """
    print("Iniciando preprocesamiento de datos...")
    
    # Cargar datos
    print("\nCargando archivos CSV...")
    try:
        df_cuadro1 = pd.read_csv('./data/cuadro1.csv', encoding='utf-8')
        df_cuadro3 = pd.read_csv('./data/cuadro3.csv', encoding='utf-8')
        df_cuadro7 = pd.read_csv('./data/cuadro7.csv', encoding='utf-8')
        df_cuadro9 = pd.read_csv('./data/cuadro9.csv', encoding='utf-8')
        df_cuadro31 = pd.read_csv('./data/cuadro31.csv', encoding='utf-8')
        df_cuadro47 = pd.read_csv('./data/cuadro47.csv', encoding='utf-8')
        print("Archivos cargados exitosamente")
    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        return
    
    # Limpiar datos
    print("\nLimpiando y transformando datos...")
    
    df1_limpio = limpiar_cuadro1(df_cuadro1)
    print(f"Cuadro 1: {len(df1_limpio)} registros")
    
    df3_limpio = limpiar_cuadro3(df_cuadro3)
    print(f"Cuadro 3: {len(df3_limpio)} registros")
    
    df7_limpio = limpiar_cuadro7(df_cuadro7)
    print(f"Cuadro 7: {len(df7_limpio)} registros")
    
    df9_limpio = limpiar_cuadro9(df_cuadro9)
    print(f"Cuadro 9: {len(df9_limpio)} registros")
    
    df31_limpio = limpiar_cuadro31(df_cuadro31)
    print(f"Cuadro 31: {len(df31_limpio)} registros")
    
    df47_limpio = limpiar_cuadro47(df_cuadro47)
    print(f"Cuadro 47: {len(df47_limpio)} registros")
    
    # Guardar datos limpios
    print("\nGuardando datos procesados...")
    
    df1_limpio.to_csv('./data_clean/data_accidentes_anio_depto.csv', index=False)
    df3_limpio.to_csv('./data_clean/data_accidentes_dia_depto.csv', index=False)
    df7_limpio.to_csv('./data_clean/data_accidentes_dia_hora.csv', index=False)
    df9_limpio.to_csv('./data_clean/data_accidentes_tipo_mes.csv', index=False)
    df31_limpio.to_csv('./data_clean/data_lesionados_anio_depto.csv', index=False)
    df47_limpio.to_csv('./data_clean/data_fallecidos_anio_depto.csv', index=False)
    
    print("Todos los archivos guardados exitosamente")
    
    # Mostrar vista previa
    print("\n Vista previa de datos procesados:")
    print("\n--- Cuadro 1 (Accidentes por año) ---")
    print(df1_limpio.head())
    
    print("\n--- Cuadro 7 (Accidentes por día/hora) ---")
    print(df7_limpio.head())
    
    print("\n--- Cuadro 9 (Tipos de accidente) ---")
    print(df9_limpio.head())
    
    print("\n¡Preprocesamiento completado!")

if __name__ == "__main__":
    main()