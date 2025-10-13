
# Importamos las librerías necesarias
import requests                     # Para realizar solicitudes HTTP a la API de TMDB
import pandas as pd                 # Para manejar los DataFrames (lectura de archivos .pkl)
from PIL import Image               # Para manejar imágenes (abrir, convertir, mostrar)
import streamlit as st              # Librería principal para la app web

# ------------------------------------------------------------
# --- Networking TMDB (The Movie Database) ---
# ------------------------------------------------------------

@st.cache_data(show_spinner=False)  # Cachea la función para no repetir solicitudes a la API
def fetch_poster(movie_id: int) -> Image.Image:
    """
    Devuelve el póster desde TMDB usando una API con key personal.
    Si falla, regresa un placeholder para no romper la app.
    """

    # Clave personal de la API. Permite autenticar las solicitudes a TMDB
    api_key = "0f3ddfe0d97c97f7b1ecd5a5ba358fda" 

    # URL base para acceder a los detalles de una película por ID
    base_url = f"https://api.themoviedb.org/3/movie/{movie_id}"

    # URL base para obtener imágenes en tamaño w500 (500px de ancho)
    img_base = "https://image.tmdb.org/t/p/w500"

    # URL de una imagen temporal (placeholder) en caso de que no exista póster
    placeholder_url = "https://via.placeholder.com/500x750?text=Sin+Poster"

    try:
        # Parámetros que se enviarán en la solicitud (API key + idioma)
        params = {"api_key": api_key, "language": "en-US"}

        # Realiza la solicitud HTTP GET a la API de TMDB
        response = requests.get(base_url, params=params, timeout=10)

        # Lanza un error si la respuesta no fue exitosa 
        response.raise_for_status()

        # Convierte la respuesta en formato JSON (diccionario de Python)
        data = response.json()

        # Extrae la ruta del póster desde el JSON
        poster_path = data.get("poster_path")

        # Si no hay póster, devuelve la imagen de placeholder
        if not poster_path:
            return Image.open(requests.get(placeholder_url, stream=True).raw).convert("RGB")

        # Si existe la ruta, se construye la URL completa del póster
        img_url = img_base + poster_path

        # Descarga la imagen y la convierte al formato RGB
        image = Image.open(requests.get(img_url, stream=True).raw).convert("RGB")

        # Devuelve la imagen del póster lista para mostrar en Streamlit
        return image

    # Si ocurre algún error en la solicitud o descarga
    except Exception as e:
        # Imprime el error en consola
        print(f"⚠️ Error al obtener el póster (ID {movie_id}): {e}")

        # Devuelve el placeholder para evitar que la app se rompa
        return Image.open(requests.get(placeholder_url, stream=True).raw).convert("RGB")


# ------------------------------------------------------------
# --- Carga de Modelos (archivos .pkl generados previamente) ---
# ------------------------------------------------------------

@st.cache_data(show_spinner=False)  # Cachea los datos para no recargar los .pkl en cada ejecución
def load_models():
    """Carga los pkl exactamente de las mismas rutas."""
    # Carga el archivo con la lista de películas procesadas (DataFrame)
    movies = pd.read_pickle('../DataCleaner/model/movie_list.pkl')

    # Carga el archivo con la matriz de similitud calculada con cosine similarity
    similarity = pd.read_pickle('../DataCleaner/model/similarity.pkl')

    # Devuelve ambos objetos (DataFrame de películas y matriz de similitud)
    return movies, similarity


# ------------------------------------------------------------
# --- Generación de recomendaciones ---
# ------------------------------------------------------------

def recommend(movie_title: str, movies: pd.DataFrame, similarity) -> tuple[list[str], list[Image.Image]]:
    """
    Misma lógica: top-5 más similares, excluyendo la propia.
    """
    
    # Busca el índice de la película seleccionada en el DataFrame 'movies'
    index = movies[movies['title'] == movie_title].index[0]

    # Calcula las distancias de similitud (ordenadas de mayor a menor)
    # enumerate() crea pares (índice, valor) para todas las películas
    # Se ordena por similitud descendente (key=lambda x: x[1])
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    # Listas vacías para almacenar los resultados
    recommended_movie_names: list[str] = []       # Nombres de las películas recomendadas
    recommended_movie_posters: list[Image.Image] = []  # Pósters correspondientes

    # Recorre las 5 películas más similares (omitiendo la primera, que es la misma)
    for i in distances[1:11]:
        # Obtiene el ID de la película similar
        movie_id = movies.iloc[i[0]].movie_id

        # Obtiene el póster de esa película usando la API TMDB
        recommended_movie_posters.append(fetch_poster(movie_id))

        # Agrega el nombre de la película a la lista
        recommended_movie_names.append(movies.iloc[i[0]].title)

    # Devuelve una tupla con las listas (nombres, imágenes)
    return recommended_movie_names, recommended_movie_posters
