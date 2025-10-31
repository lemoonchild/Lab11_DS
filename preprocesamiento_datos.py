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

def limpiar_cuadro18(df):
    """
    Limpia Cuadro 18: Vehículos por tipo de accidente y tipo de vehículo
    """
    # Eliminar la fila "Total"
    df = df[df['tipo_de_vehiculo'] != 'Total'].copy()
    
    # Eliminar columnas innecesarias
    columnas_eliminar = ['fuente_cuadro', 'col_12']
    for col in columnas_eliminar:
        if col in df.columns:
            df = df.drop(col, axis=1)
    
    # Convertir de wide a long format para tipos de accidente
    df_long = df.melt(
        id_vars=['tipo_de_vehiculo', 'total'],
        value_vars=['colision', 'atropello', 'derrape', 'choque', 'vuelco', 
                    'embarranco', 'encuneto', 'caida', 'ignorado'],
        var_name='tipo_accidente',
        value_name='cantidad'
    )
    
    # Eliminar columna total
    df_long = df_long.drop('total', axis=1)
    
    return df_long


def limpiar_cuadro38(df):
    """
    Limpia Cuadro 38: Lesionados por grupos de edad
    """
    # Eliminar la fila "Total"
    df = df[df['grupos_de_edad'] != 'Total'].copy()
    
    # Eliminar columna fuente_cuadro
    if 'fuente_cuadro' in df.columns:
        df = df.drop('fuente_cuadro', axis=1)
    
    return df


def limpiar_cuadro54(df):
    """
    Limpia Cuadro 54: Fallecidos por grupos de edad
    """
    # Eliminar la fila "Total"
    df = df[df['grupos_de_edad'] != 'Total'].copy()
    
    # Eliminar columna fuente_cuadro
    if 'fuente_cuadro' in df.columns:
        df = df.drop('fuente_cuadro', axis=1)
    
    return df


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
        df_cuadro18 = pd.read_csv('./data/cuadro18.csv', encoding='utf-8')
        df_cuadro31 = pd.read_csv('./data/cuadro31.csv', encoding='utf-8')
        df_cuadro38 = pd.read_csv('./data/cuadro38.csv', encoding='utf-8')
        df_cuadro47 = pd.read_csv('./data/cuadro47.csv', encoding='utf-8')
        df_cuadro54 = pd.read_csv('./data/cuadro54.csv', encoding='utf-8')
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
    
    df18_limpio = limpiar_cuadro18(df_cuadro18)
    print(f"Cuadro 18: {len(df18_limpio)} registros")
    
    df31_limpio = limpiar_cuadro31(df_cuadro31)
    print(f"Cuadro 31: {len(df31_limpio)} registros")
    
    df38_limpio = limpiar_cuadro38(df_cuadro38)
    print(f"Cuadro 38: {len(df38_limpio)} registros")
    
    df47_limpio = limpiar_cuadro47(df_cuadro47)
    print(f"Cuadro 47: {len(df47_limpio)} registros")
    
    df54_limpio = limpiar_cuadro54(df_cuadro54)
    print(f"Cuadro 54: {len(df54_limpio)} registros")
    
    print("\nGuardando datos procesados...")
    
    df1_limpio.to_csv('./data_clean/data_accidentes_anio_depto.csv', index=False)
    df3_limpio.to_csv('./data_clean/data_accidentes_dia_depto.csv', index=False)
    df7_limpio.to_csv('./data_clean/data_accidentes_dia_hora.csv', index=False)
    df9_limpio.to_csv('./data_clean/data_accidentes_tipo_mes.csv', index=False)
    df18_limpio.to_csv('./data_clean/data_vehiculos_tipo.csv', index=False)
    df31_limpio.to_csv('./data_clean/data_lesionados_anio_depto.csv', index=False)
    df38_limpio.to_csv('./data_clean/data_lesionados_edad.csv', index=False)
    df47_limpio.to_csv('./data_clean/data_fallecidos_anio_depto.csv', index=False)
    df54_limpio.to_csv('./data_clean/data_fallecidos_edad.csv', index=False)
    
    print("Todos los archivos guardados exitosamente")
    
    print("\n¡Preprocesamiento completado!")

if __name__ == "__main__":
    main()