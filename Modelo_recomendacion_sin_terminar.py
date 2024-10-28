import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import tkinter as tk
from tkinter import messagebox
import random

# MODELO DE RECOMENDACIÓN DE PELICULAS

def cargar_datos(archivo):
    try:
        datos = pd.read_csv(archivo)
        # Verificacion de columnas
        columnas = ['peli_id', 'nombre', 'genero', 'valoracion']
        if not set(columnas).issubset(set(datos.columns)):
            raise ValueError('Faltan columnas en el archivo CSV.')
        # Limpieza de datos
        datos.dropna(inplace = True)
        # Confirmación del formato correcto de cada columna
        datos['valoracion'] = pd.to_numeric(datos['valoracion'], errors='coerce').fillna(0)
        #datos['genero'] = datos['genero'].astype('category')
        print('Datos cargados y verificados correctamente.')
        return datos
    except Exception as e:
        print(f'Error al cargar datos: {e}')
        #return None
        return pd.DataFrame()

def content_based_recommendations(title, data, num_recommendations=5):
    # Vectorización de la columna de género
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['genero'])
    
    # Calcular la similitud del coseno
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    # Crear un índice inverso
    indices = pd.Series(data.index, index=data['nombre']).drop_duplicates()
    if title not in indices:
        print(f"El título '{title}' no fue encontrado en los datos.")
        return []
    # Buscar el índice de la película
    idx = indices[title]
    
    # Obtener las puntuaciones de similitud para todas las películas
    sim_scores = sorted(list(enumerate(cosine_sim[idx])), key=lambda x: x[1], reverse=True)
    #sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Ordenar y seleccionar las películas más similares
    #sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:num_recommendations+1]
    
    # Obtener los títulos de las películas recomendadas
    movie_indices = [i[0] for i in sim_scores]
    return data['nombre'].iloc[movie_indices].tolist()

def show_recommendations():
    title = entry.get()
    
    # Verificar si el título está en los datos
    if title not in datos_peliculas['nombre'].values:
        messagebox.showerror("Error", "Película no encontrada. Intente con otro título.")
        return
    
    # Obtener recomendaciones
    recommendations = content_based_recommendations(title, datos_peliculas)
    result_label.config(text="Recomendaciones: " + ", ".join(recommendations))

    
def remove_duplicates(data, subset_columns=None):
    """
    Elimina las entradas duplicadas de un DataFrame en función de columnas específicas o en todo el DataFrame.

    Parameters:
        data (pd.DataFrame): El DataFrame de pandas que contiene los datos.
        subset_columns (list, optional): Lista de nombres de columnas a considerar para detectar duplicados. 
                                         Si es None, se buscarán duplicados en todas las columnas.

    Returns:
        pd.DataFrame: Un nuevo DataFrame sin duplicados.
    """
    # Contar el número de duplicados antes de eliminarlos
    num_duplicates = data.duplicated(subset=subset_columns).sum()
    print(f"Entradas duplicadas encontradas: {num_duplicates}")

    # Eliminar duplicados
    clean_data = data.drop_duplicates(subset=subset_columns, keep='first').reset_index(drop=True)
    print("Duplicados eliminados correctamente.")

    return clean_data

    

# Listas de ejemplo para generar títulos y géneros aleatorios
titulos = [f"Peli {i}" for i in range(1, 101)] 
generos = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Documentary"]
valoraciones = [round(random.uniform(1, 5), 1) for _ in range(100)]

# Generar un DataFrame con datos de prueba
datos_peliculas = pd.DataFrame({
    "peli_id": range(1, 101),
    "nombre": titulos,      
    "genero": [random.choice(generos) for _ in range(100)],
    "valoracion": valoraciones})

# Guardar en un archivo CSV
archivoCSV = "peliculas.csv"
datos_peliculas.to_csv(archivoCSV, index=False)

print(f"Archivo '{archivoCSV}' creado con 100 películas de prueba.")


# Verificación de que el archivo se ha guardado correctamente y lectura de los datos
try:
    # Cargar el archivo CSV para asegurar que las columnas coincidan
    loaded_data = pd.read_csv(archivoCSV)
    
    # Verificar que las columnas necesarias existen en el archivo
    required_columns = {"peli_id", "nombre", "genero", "valoracion"}
    if not required_columns.issubset(loaded_data.columns):
        raise ValueError("Faltan columnas requeridas en el archivo CSV.")
    print("Archivo CSV cargado y verificado con éxito. Estructura correcta.")
    print(loaded_data.head(10))  # Muestra las primeras filas como confirmación

except Exception as e:
    print(f"Error al cargar o verificar el archivo CSV: {e}")

# Cargar datos de archivo CSV
datos_peliculas = cargar_datos("peliculas.csv")
# EL ARCHIVO SE EJECUTA EN LA CARPETA DEL PROYECTO PARA 
# PODER ABRIRLo Y VISUALIZAR EN TIEMPO REAL NUESTRA DATAFRAME 
# DE PRUEBA

# Ejemplo de uso
datos_peliculas = remove_duplicates(datos_peliculas, subset_columns=['nombre', 'genero'])


# Configuración de la ventana principal
root = tk.Tk()
root.title("Recomendador de Películas")
root.geometry("400x300")

# Entrada de texto para el título
label = tk.Label(root, text="Ingrese el título de una película:")
label.pack(pady=10)
entry = tk.Entry(root, width=30)
entry.pack(pady=10)

# Botón para obtener recomendaciones
button = tk.Button(root, text="Recomendar", command=show_recommendations)
button.pack(pady=10)

# Etiqueta para mostrar los resultados
result_label = tk.Label(root, text="Recomendaciones:")
result_label.pack(pady=20)

root.mainloop()


