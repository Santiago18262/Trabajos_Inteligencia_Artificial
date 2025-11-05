
# -------------------------------------------------------------
# Importaciones principales
# -------------------------------------------------------------
import streamlit as st                                     # Librería principal para crear la interfaz web interactiva
from styles import inject_css                              # Importa la función que aplica el estilo visual (CSS)
from services import load_models, recommend, fetch_poster  # Importa las funciones de lógica: cargar modelos, recomendar y obtener pósters

# -------------------------------------------------------------
# Aplicación de estilos personalizados
# -------------------------------------------------------------
inject_css()  # Llama a la función definida en styles.py para aplicar el diseño visual (colores, fondo, botones, etc.)
    
# -------------------------------------------------------------
# Carga de modelos (archivos .pkl con los datos y similitudes)
# -------------------------------------------------------------
# Muestra un spinner (animación de carga) mientras se leen los archivos pickle
with st.spinner('Cargando la magia del cine... ⏳'):
    movies, similarity = load_models()  # Carga el DataFrame de películas y la matriz de similitud

# Obtiene la lista de títulos de películas para el menú desplegable
movie_list = movies['title'].values

# -------------------------------------------------------------
# Interfaz principal de la aplicación
# -------------------------------------------------------------
# Título principal de la app
st.title('Tu Asistente de Películas 🍿')

# Línea divisora (separador visual)
st.markdown("---")

# Texto introductorio con formato Markdown y emojis
st.markdown("✨ **Encuentra tu próxima joya cinematográfica con un solo clic.**")

# Otra línea divisora
st.markdown("---")

# Crea un selectbox (lista desplegable) con las películas disponibles
selected_movie = st.selectbox("🔎 **Selecciona una película que te guste:**", movie_list)

# -------------------------------------------------------------
# Sección de Recomendaciones
# -------------------------------------------------------------
# Cuando el usuario presiona el botón “Obtener Recomendaciones”
if st.button('🚀 Obtener Recomendaciones'):
    # Muestra un spinner mientras se calculan las recomendaciones
    with st.spinner('Buscando en la galaxia del cine... 🌌'):
        # Llama a la función recommend() pasando la película elegida, el DataFrame y la matriz de similitud
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)

    # Separador visual
    st.markdown("---")

    # ---------------------------------------------------------
    # Mostrar la película seleccionada por el usuario
    # ---------------------------------------------------------
    st.subheader(f'Has Seleccionado: {selected_movie} 🌟')  # Muestra el título de la película elegida

    # Obtiene el ID de la película seleccionada desde el DataFrame
    selected_movie_id = movies[movies['title'] == selected_movie].iloc[0].movie_id

    # Descarga el póster de la película usando la función fetch_poster()
    selected_poster = fetch_poster(selected_movie_id)

    # Divide el espacio en dos columnas (1 para la imagen, 2 para texto)
    col_img_sel, col_info_sel = st.columns([1, 2])

    # Muestra la imagen del póster en la primera columna
    with col_img_sel:
        st.image(selected_poster, use_container_width=True)

    # Muestra el texto informativo en la segunda columna
    with col_info_sel:
        st.write("¡Una excelente elección para inspirar tus próximas aventuras fílmicas!")
        # Ejemplos de datos adicionales que podrían mostrarse si se agregan más columnas al DataFrame:
        # st.write(f"**Géneros:** {movies[movies['title'] == selected_movie]['genres'].iloc[0]}")
        # st.write(f"**Año:** {movies[movies['title'] == selected_movie]['release_date'].iloc[0][:4]}")

    # Separador visual
    st.markdown("---")

    # ---------------------------------------------------------
    # Mostrar las recomendaciones basadas en la selección
    # ---------------------------------------------------------
    st.subheader('✨ Películas que te Podrían Gustar ✨')  # Subtítulo
    st.write("Aquí tienes 5 sugerencias basadas en tu selección:")  # Descripción corta

    # Crea una fila con 5 columnas (una por película recomendada)
    cols = st.columns(5)

    # Itera sobre las películas recomendadas y las muestra en las columnas
    for i in range(len(recommended_movie_names)):
        col = cols[i % 5]  # Usa el operador módulo para recorrer las columnas
        with col:
            st.markdown(f'<div class="rec-title">{recommended_movie_names[i]}</div>', unsafe_allow_html=True)
            st.image(recommended_movie_posters[i], use_container_width=True)  # Muestra el póster

    # Separador final
    st.markdown("---")

    # Mensaje de éxito final (tipo alerta verde)
    st.success("¡Esperamos que encuentres tu próxima película favorita!")

# Línea final para cerrar la estructura visual
st.markdown("---")
