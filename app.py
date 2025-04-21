import streamlit as st
import time
import threading
from datetime import datetime, timedelta
import google.generativeai as genai

# Título de la aplicación
st.title("Calendario Inteligente con Gemini")

# Estructura de datos para almacenar las tareas y eventos
tareas = []

# Configura tu clave de API de Gemini
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# Para usar el modelo Gemini Pro
model = genai.GenerativeModel('gemini-2.0-flash')

# Función para agregar una tarea o evento
def agregar_tarea(descripcion, fecha, hora):
    tarea = {
        "descripcion": descripcion,
        "fecha": fecha,
        "hora": hora,
        "recordatorio": False  # Inicialmente, el recordatorio no está configurado
    }
    tareas.append(tarea)
    st.success(f"Tarea '{descripcion}' agregada para el {fecha} a las {hora}")
    
    # Obtener sugerencia de Gemini
    prompt = f"Dame una sugerencia para la tarea: {descripcion}"
    response = model.generate_content(prompt)
    st.info(f"Sugerencia de Gemini: {response.text}")

    programar_recordatorio(tarea)

# Función para programar un recordatorio
def programar_recordatorio(tarea):
    fecha_hora_str = f"{tarea['fecha']} {tarea['hora']}"
    fecha_hora_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
    
    # Calcular el tiempo restante hasta el recordatorio (30 minutos antes)
    tiempo_recordatorio = fecha_hora_obj - timedelta(minutes=30)
    tiempo_espera = (tiempo_recordatorio - datetime.now()).total_seconds()

    if tiempo_espera > 0:
        def mostrar_recordatorio():
            st.warning(f"Recordatorio: {tarea['descripcion']} el {tarea['fecha']} a las {tarea['hora']}")

        # Programar el recordatorio para que se ejecute en el futuro
        timer = threading.Timer(tiempo_espera, mostrar_recordatorio)
        timer.start()
        st.info(f"Recordatorio programado para {tiempo_recordatorio.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.warning("No se puede programar el recordatorio, la fecha y hora ya pasaron.")

# Función para mostrar la agenda diaria ordenada cronológicamente
def mostrar_agenda_diaria():
    st.header("Agenda Diaria")
    if not tareas:
        st.info("No hay tareas ni eventos programados para hoy.")
        return

    # Convertir la fecha y hora a objetos datetime para ordenar
    for tarea in tareas:
        tarea["datetime"] = datetime.strptime(f"{tarea['fecha']} {tarea['hora']}", "%Y-%m-%d %H:%M")

    # Ordenar las tareas por fecha y hora
    tareas_ordenadas = sorted(tareas, key=lambda x: x["datetime"])

    # Mostrar las tareas en una tabla
    st.table(tareas_ordenadas)

# Formulario para agregar tareas
with st.form("nueva_tarea"):
    st.subheader("Agregar Nueva Tarea/Evento")
    descripcion = st.text_input("Descripción de la tarea:")
    fecha = st.date_input("Fecha:")
    hora = st.time_input("Hora:")
    submitted = st.form_submit_button("Agregar Tarea")

    if submitted:
        agregar_tarea(descripcion, fecha.strftime("%Y-%m-%d"), hora.strftime("%H:%M"))

# Mostrar la agenda diaria
mostrar_agenda_diaria()

# Función para mostrar notificaciones en la consola
def mostrar_notificaciones_consola():
    for tarea in tareas:
        fecha_hora_str = f"{tarea['fecha']} {tarea['hora']}"
        fecha_hora_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
        tiempo_hasta_tarea = (fecha_hora_obj - datetime.now()).total_seconds()

        if 0 < tiempo_hasta_tarea <= 3600:  # Si la tarea es en la próxima hora
            print(f"¡Atención! La tarea '{tarea['descripcion']}' es en menos de una hora.")
        elif tiempo_hasta_tarea <= 0:
            print(f"La tarea '{tarea['descripcion']}' programada para el {tarea['fecha']} a las {tarea['hora']} ya ha pasado.")

# Llamar a la función de notificaciones en la consola (esto se ejecutará cada vez que se actualice la app)
mostrar_notificaciones_consola()

#TODO: Integrar con el modelo Gemini para sugerencias inteligentes
