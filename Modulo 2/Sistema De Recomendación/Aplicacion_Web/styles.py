# ===========================================================
# Descripción general:
#   Este módulo define una función llamada inject_css() que
#   inyecta código CSS personalizado en una aplicación Streamlit.
#
# ¿Qué hace la función inject_css()?
#   - Aplica un fondo con gradiente de color a toda la app.
#   - Cambia la fuente global a "Montserrat" (desde Google Fonts).
#   - Pone el texto principal en color blanco para mejorar contraste.
#   - Personaliza los botones (color, borde, sombra y efecto hover).
#   - Ajusta el diseño de los selectbox (listas desplegables).
#   - Centra y estiliza los títulos con sombra y espaciado.
#
# ===========================================================
# Descripción breve de las clases CSS
# ===========================================================
# .stApp:
#   Aplica el fondo con gradiente de colores, fuente global “Montserrat”
#   y color de texto blanco en toda la aplicación.
#
# h1, h2, h3, h4, h5, h6, .stMarkdown, .stSelectbox label, .stButton button, .stText, .stSpinner div:
#   Fuerza que todos los textos, encabezados, etiquetas y botones usen color blanco
#   para mantener un contraste visual adecuado.
#
# h1:
#   Centra el título principal, agrega sombra para mejorar la legibilidad
#   y un margen inferior para separación estética.
#
# .stButton button:
#   Personaliza el botón principal (color verde-lima, bordes redondeados,
#   sombra suave y transición al pasar el cursor).
#
# .stButton button:hover:
#   Aplica un efecto de elevación y cambio de tono al pasar el cursor
#   para dar sensación de interactividad.
#
# .stSelectbox div[data-baseweb="select"] > div:
#   Da estilo al área visible del selectbox con fondo translúcido, bordes redondeados
#   y texto blanco.
#
# .stSelectbox div[data-baseweb="select"] > div > div > span:
#   Asegura que el texto del valor seleccionado en el selectbox sea blanco.
#
# div[data-baseweb="popover"] div[role="listbox"]:
#   Estiliza el menú desplegable del selectbox con fondo azul oscuro
#   y bordes redondeados.
#
# div[data-baseweb="popover"] div[role="option"] span:
#   Define el color blanco de las opciones dentro del menú desplegable.
#
# div[data-baseweb="popover"] div[role="option"]:hover:
#   Cambia el color de fondo de la opción al pasar el cursor (azul más claro).
#
# .rec-grid:
#   Crea una cuadrícula responsive para las tarjetas de películas recomendadas,
#   con espaciado uniforme, centrado y ajuste automático del número de columnas.
#
# .rec-card:
#   Define el estilo visual de las tarjetas de recomendación con efecto translúcido (“glass”),
#   bordes redondeados, sombra, padding interno y animación de elevación al pasar el cursor.
#
# .rec-title:
#   Centra el texto del título dentro de cada tarjeta tanto vertical como horizontalmente,
#   limita la altura a 2–3 líneas y evita el desbordamiento de texto.
#
# .rec-poster:
#   Ajusta la imagen del póster manteniendo la proporción 2:3,
#   recortando correctamente con object-fit: cover y bordes redondeados.
# ===========================================================
#
# Nota importante:
#   - Todos los estilos se inyectan en la interfaz mediante st.markdown().
#   - unsafe_allow_html=True permite incluir HTML y CSS.
#   - No se muestran comentarios ni texto visible en el codigo de la función debido
#     a que mediante el markdown se muestran en la app y no se deberia de mostrar.
# ===========================================================

import streamlit as st  # Librería principal de Streamlit


def inject_css() -> None:
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
<style>
.stApp {
  background-image: linear-gradient(to right top, #051937, #004d7a, #008793, #00bf72, #a8eb12);
  background-attachment: fixed;
  background-size: cover;
  color: white;
  font-family: 'Montserrat', sans-serif;
}
h1, h2, h3, h4, h5, h6, .stMarkdown, .stSelectbox label, .stButton button, .stText, .stSpinner div {
  color: white !important;
}
h1 {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  text-align: center;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
  margin-bottom: 20px;
}
.stButton button {
  background-color: #a8eb12;
  color: #051937 !important;
  border-radius: 8px;
  border: none;
  padding: 10px 20px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
  transition: all 0.2s ease-in-out;
}
.stButton button:hover {
  background-color: #c0ff3e;
  box-shadow: 3px 3px 8px rgba(0,0,0,0.4);
  transform: translateY(-2px);
}
.stSelectbox div[data-baseweb="select"] > div {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}
.stSelectbox div[data-baseweb="select"] > div > div > span { color: white !important; }
div[data-baseweb="popover"] div[role="listbox"] {
  background-color: #051937 !important;
  color: white !important;
  border-radius: 8px;
}
div[data-baseweb="popover"] div[role="option"] span { color: white !important; }
div[data-baseweb="popover"] div[role="option"]:hover { background-color: #004d7a !important; }
.rec-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 18px;
  align-items: stretch;
  justify-items: center;
  margin-top: 20px;
}
.rec-card {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  background: rgba(255,255,255,0.10);
  backdrop-filter: saturate(120%) blur(2px);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 16px;
  padding: 12px;
  height: 100%;
  width: 100%;
  max-width: 220px;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.25);
  transition: transform 0.2s ease-in-out, box-shadow 0.2s;
}
.rec-card:hover {
  transform: translateY(-3px);
  box-shadow: 3px 3px 8px rgba(0,0,0,0.35);
}
.rec-title {
  margin: 0 0 10px 0;
  font-weight: 700;
  line-height: 1.2;
  min-height: 3.6em;
  max-height: 3.6em;
  overflow: hidden;
  display: flex;                  
  align-items: center;            
  justify-content: center;        
  text-align: center;             
}
.rec-poster {
  width: 100%;
  aspect-ratio: 2 / 3;
  object-fit: cover;
  border-radius: 12px;
  flex: 1;
}
</style>
""", unsafe_allow_html=True)
