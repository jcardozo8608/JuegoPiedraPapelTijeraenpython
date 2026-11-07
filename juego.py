
import random
import tkinter as tk
import pygame
import pyttsx3
import numpy as np
import threading
import queue


# ==========================================
# 1. CONFIGURACION DE SONIDO
# ==========================================

FRECUENCIA = 44100
DURACION = 60 / 110 * 16

canal_musica = None
sonido_musica = None


try:

    pygame.mixer.pre_init(FRECUENCIA, -16, 2, 512)
    pygame.init()

    pygame.mixer.init(
        frequency=FRECUENCIA,
        size=-16,
        channels=2,
        buffer=512
    )

    # GENERAR MUSICA ELECTRONICA CYBERPUNK

    def generar_musica():

        total = int(FRECUENCIA * DURACION)

        audio = np.zeros(
            total,
            dtype=np.float32
        )

        bpm = 110
        beat = 60 / bpm

        def agregar_nota(
            inicio,
            duracion,
            frecuencia,
            volumen
        ):

            posicion = int(inicio * FRECUENCIA)

            cantidad = min(
                int(duracion * FRECUENCIA),
                total - posicion
            )

            if cantidad <= 0:
                return

            t = np.arange(cantidad) / FRECUENCIA

            envolvente = np.minimum(
                1,
                t / 0.015
            )

            envolvente *= np.maximum(
                0,
                np.minimum(1, (duracion - t) / 0.04)
            )

            onda = (
                np.sin(2 * np.pi * frecuencia * t)
                + 0.35 * np.sin(4 * np.pi * frecuencia * t)
            )

            audio[posicion:posicion + cantidad] += (
                onda * envolvente * volumen
            )

        # BAJO ELECTRONICO

        notas_bajo = [55, 55, 65.41, 73.42]

        for i in range(16):

            inicio = i * beat

            frecuencia = notas_bajo[(i // 4) % 4]

            agregar_nota(
                inicio,
                beat * 0.75,
                frecuencia,
                0.25
            )

        # MELODIA FUTURISTA

        melodia = [
            440, 523.25, 659.25, 587.33,
            523.25, 659.25, 783.99, 659.25,
            440, 523.25, 659.25, 880,
            783.99, 659.25, 523.25, 440
        ]

        for i, nota in enumerate(melodia):

            agregar_nota(
                i * beat / 2,
                beat * 0.40,
                nota,
                0.10
            )

        # BATERIA ELECTRONICA

        for i in range(16):

            inicio = i * beat

            # BOMBO

            if i % 4 == 0 or i % 4 == 2:

                duracion_bombo = 0.20

                cantidad = int(
                    duracion_bombo * FRECUENCIA
                )

                t = np.arange(cantidad) / FRECUENCIA

                golpe = np.sin(
                    2 * np.pi * (
                        100 - 65 * t / duracion_bombo
                    ) * t
                )

                golpe *= np.exp(-18 * t)

                posicion = int(inicio * FRECUENCIA)

                audio[posicion:posicion + cantidad] += (
                    golpe * 0.45
                )

            # CAJA ELECTRONICA

            if i % 4 == 1 or i % 4 == 3:

                duracion_caja = 0.12

                cantidad = int(
                    duracion_caja * FRECUENCIA
                )

                ruido = np.random.uniform(
                    -1,
                    1,
                    cantidad
                )

                t = np.arange(cantidad) / FRECUENCIA

                ruido *= np.exp(-25 * t)

                posicion = int(inicio * FRECUENCIA)

                audio[posicion:posicion + cantidad] += (
                    ruido * 0.12
                )

            # PLATILLOS

            for subdivision in [0, 1]:

                inicio_platillo = (
                    inicio + subdivision * beat / 2
                )

                cantidad = int(0.035 * FRECUENCIA)

                ruido = np.random.uniform(
                    -1,
                    1,
                    cantidad
                )

                t = np.arange(cantidad) / FRECUENCIA

                ruido *= np.exp(-100 * t)

                posicion = int(
                    inicio_platillo * FRECUENCIA
                )

                if posicion + cantidad <= total:

                    audio[posicion:posicion + cantidad] += (
                        ruido * 0.035
                    )

        # CONTROL DE VOLUMEN

        audio = np.tanh(audio * 1.5) * 0.55

        # CONVERTIR A SONIDO ESTEREO

        stereo = np.column_stack((audio, audio))

        sonido = pygame.mixer.Sound(
            buffer=(
                (stereo * 32767)
                .astype(np.int16)
                .tobytes()
            )
        )

        return sonido

    sonido_musica = generar_musica()

    sonido_musica.set_volume(0.30)

    canal_musica = sonido_musica.play(loops=-1)

    print("Musica CYBERPUNK activada")

except Exception as error:

    print("Error de sonido:", error)


# ==========================================
# 2. SISTEMA DE VOZ CORREGIDO
# ==========================================

cola_voz = queue.Queue()


def trabajador_voz():

    try:

        motor = pyttsx3.init()

        motor.setProperty("rate", 155)
        motor.setProperty("volume", 1.0)

        # BUSCAR VOZ EN ESPAÑOL

        voces = motor.getProperty("voices")

        for v in voces:

            datos = (
                str(v.id).lower()
                + str(v.name).lower()
            )

            if (
                "spanish" in datos
                or "español" in datos
                or "es_" in datos
                or "helena" in datos
            ):

                motor.setProperty("voice", v.id)
                break

        # REPRODUCIR LOS MENSAJES EN ORDEN

        while True:

            mensaje = cola_voz.get()

            if mensaje is None:

                cola_voz.task_done()
                break

            motor.say(mensaje)
            motor.runAndWait()

            cola_voz.task_done()

        motor.stop()

    except Exception as error:

        print("Error en el sistema de voz:", error)


hilo_voz = threading.Thread(
    target=trabajador_voz,
    daemon=True
)

cola_voz = queue.Queue()

def hablar(mensaje):
    cola_voz.put(mensaje)

def trabajador_voz():

    try:

        motor = pyttsx3.init()

        motor.setProperty("rate", 155)
        motor.setProperty("volume", 1.0)

        voces = motor.getProperty("voices")

        for v in voces:

            datos = (
                str(v.id).lower()
                + str(v.name).lower()
            )

            if (
                "spanish" in datos
                or "español" in datos
                or "es_" in datos
                or "helena" in datos
            ):
                motor.setProperty("voice", v.id)
                break

        while True:

            mensaje = cola_voz.get()

            if mensaje is None:
                cola_voz.task_done()
                break

            motor.say(mensaje)
            motor.runAndWait()

            cola_voz.task_done()

        motor.stop()

    except Exception as error:
        print("Error en el sistema de voz:", error)

hilo_voz = threading.Thread(
    target=trabajador_voz,
    daemon=True
)

hilo_voz.start()

hablar(
    "Bienvenido a Piedra Papel o Tijera. El sistema está listo."
)


# ==========================================
# 3. VARIABLES PRINCIPALES
# ==========================================

modalidad = 0

puntosJugador = 0
puntosPC = 0
empates = 0

turno = 1
jugadorAleatorio = 1

eleccionJugador1 = ""

emojis = {
    "piedra": "✊",
    "papel": "✋",
    "tijera": "✌️"
}


# ==========================================
# 4. INICIAR JUEGO
# ==========================================

def iniciar_juego(opcion):

    global modalidad
    global puntosJugador, puntosPC, empates
    global turno, jugadorAleatorio
    global eleccionJugador1

    modalidad = opcion

    puntosJugador = 0
    puntosPC = 0
    empates = 0

    turno = 1
    eleccionJugador1 = ""

    frame_menu.pack_forget()

    frame_juego.pack(
        fill="both",
        expand=True
    )

    if modalidad == 1:

        lbl_titulo_juego.config(
            text="MODALIDAD: PC VS USUARIO"
        )

        lbl_nombre_jugador.config(
            text="Usuario 1"
        )

        lbl_nombre_pc.config(
            text="Computadora"
        )

        lbl_instruccion.config(
            text="Selecciona tu jugada"
        )

        hablar(
            "Comienza la partida. Usuario uno contra computadora."
        )

    elif modalidad == 2:

        jugadorAleatorio = random.choice([1, 2])

        lbl_titulo_juego.config(
            text="MODALIDAD: PC VS ALEATORIO"
        )

        lbl_nombre_jugador.config(
            text=f"Usuario {jugadorAleatorio}"
        )

        lbl_nombre_pc.config(
            text="Computadora"
        )

        lbl_instruccion.config(
            text=(
                f"El destino eligió al Usuario "
                f"{jugadorAleatorio}. ¡Haz tu jugada!"
            )
        )

        hablar(
            f"Comienza la partida. "
            f"El jugador elegido es el usuario {jugadorAleatorio}."
        )

    elif modalidad == 3:

        lbl_titulo_juego.config(
            text="MODALIDAD: USUARIO 1 VS USUARIO 2"
        )

        lbl_nombre_jugador.config(
            text="Usuario 1"
        )

        lbl_nombre_pc.config(
            text="Usuario 2"
        )

        lbl_instruccion.config(
            text="Turno de Usuario 1 (Jugada Oculta)"
        )

        hablar(
            "Comienza la partida. Usuario uno contra usuario dos."
        )

    actualizar_marcador()

    lbl_simbolo_jugador.config(text="❔")
    lbl_simbolo_pc.config(text="❔")

    lbl_resultado.config(
        text="¡Que comience el juego!",
        fg="#ff9d00"
    )


# ==========================================
# 5. REALIZAR JUGADA
# ==========================================

def jugar(eleccion):

    global turno, eleccionJugador1

    lbl_simbolo_jugador.config(text="❔")
    lbl_simbolo_pc.config(text="❔")

    if modalidad == 1 or modalidad == 2:

        opciones = [
            "piedra",
            "papel",
            "tijera"
        ]

        eleccionPC = random.choice(opciones)

        lbl_simbolo_jugador.config(
            text=emojis[eleccion]
        )

        lbl_simbolo_pc.config(
            text=emojis[eleccionPC]
        )

        if modalidad == 1:

            victoria = "¡Ganaste tú!"
            derrota = "¡Ganó la computadora!"

        else:

            victoria = (
                f"¡Ganó el Usuario {jugadorAleatorio}!"
            )

            derrota = "¡Ganó la computadora!"

        procesar_ganador(
            eleccion,
            eleccionPC,
            victoria,
            derrota
        )

    elif modalidad == 3:

        if turno == 1:

            eleccionJugador1 = eleccion

            turno = 2

            lbl_instruccion.config(
                text="Turno de Usuario 2 (Jugada Oculta)"
            )

            lbl_resultado.config(
                text="Jugada guardada. ¡Usuario 2, juega!",
                fg="#ff9d00"
            )

        else:

            lbl_simbolo_jugador.config(
                text=emojis[eleccionJugador1]
            )

            lbl_simbolo_pc.config(
                text=emojis[eleccion]
            )

            procesar_ganador(
                eleccionJugador1,
                eleccion,
                "¡Ganó el Usuario 1!",
                "¡Ganó el Usuario 2!"
            )

            turno = 1

            eleccionJugador1 = ""

            lbl_instruccion.config(
                text="Turno de Usuario 1 (Jugada Oculta)"
            )


# ==========================================
# 6. DETERMINAR GANADOR Y ANUNCIAR POR VOZ
# ==========================================

def procesar_ganador(
    jugada1,
    jugada2,
    msgVictoria,
    msgDerrota
):

    global puntosJugador, puntosPC, empates

    

    # EMPATE

    if jugada1 == jugada2:

        lbl_resultado.config(
            text="¡Es un Empate! 🤝",
            fg="#ff9d00"
        )

        empates += 1

        hablar("¡Empate!")

    # GANA JUGADOR 1

    elif (
        (jugada1 == "piedra" and jugada2 == "tijera")
        or
        (jugada1 == "papel" and jugada2 == "piedra")
        or
        (jugada1 == "tijera" and jugada2 == "papel")
    ):

        lbl_resultado.config(
            text=msgVictoria + " 🎉",
            fg="#00f3ff"
        )

        puntosJugador += 1

        if modalidad == 1:

            hablar("¡Ganó el usuario 1!")

        elif modalidad == 2:

            hablar(
                f"¡Ganó el usuario {jugadorAleatorio}!"
            )

        elif modalidad == 3:

            hablar("¡Ganó el usuario 1!")

    # GANA JUGADOR 2 O COMPUTADORA

    else:

        lbl_resultado.config(
            text=msgDerrota + " ❌",
            fg="#ff0055"
        )

        puntosPC += 1

        if modalidad == 1 or modalidad == 2:

            hablar("¡Ganó la PC!")

        elif modalidad == 3:

            hablar("¡Ganó el usuario 2!")

    actualizar_marcador()


# ==========================================
# 7. ACTUALIZAR MARCADOR
# ==========================================

def actualizar_marcador():

    if modalidad == 3:

        txt = (
            f"Usuario 1: {puntosJugador} | "
            f"Usuario 2: {puntosPC} | "
            f"Empates: {empates}"
        )

    elif modalidad == 2:

        txt = (
            f"Usuario {jugadorAleatorio}: {puntosJugador} | "
            f"Computadora: {puntosPC} | "
            f"Empates: {empates}"
        )

    else:

        txt = (
            f"Usuario 1: {puntosJugador} | "
            f"Computadora: {puntosPC} | "
            f"Empates: {empates}"
        )

    lbl_marcador_valores.config(
        text=txt
    )


# ==========================================
# 8. REINICIAR PARTIDA
# ==========================================

def reiniciar_marcador():

    global puntosJugador, puntosPC
    global empates, turno, eleccionJugador1

    puntosJugador = 0
    puntosPC = 0
    empates = 0

    turno = 1
    eleccionJugador1 = ""

    lbl_simbolo_jugador.config(
        text="❔"
    )

    lbl_simbolo_pc.config(
        text="❔"
    )

    lbl_resultado.config(
        text="¡Que comience el juego!",
        fg="#ff9d00"
    )

    if modalidad == 3:

        lbl_instruccion.config(
            text="Turno de Usuario 1 (Jugada Oculta)"
        )

    elif modalidad == 2:

        lbl_instruccion.config(
            text=(
                f"El destino eligió al Usuario "
                f"{jugadorAleatorio}. ¡Haz tu jugada!"
            )
        )

    else:

        lbl_instruccion.config(
            text="Selecciona tu jugada"
        )

    actualizar_marcador()

    hablar(
        "Partida reiniciada. ¡Comencemos de nuevo!"
    )


# ==========================================
# 9. VOLVER AL MENU
# ==========================================

def volver_menu():

    global modalidad
    global turno, eleccionJugador1

    modalidad = 0
    turno = 1
    eleccionJugador1 = ""

    frame_juego.pack_forget()

    frame_menu.pack(
        fill="both",
        expand=True
    )

    hablar(
        "Has regresado al menú principal."
    )


# ==========================================
# 10. CERRAR JUEGO
# ==========================================

def cerrar_juego():

    try:

        # DETENER MUSICA

        if canal_musica:
            canal_musica.stop()

        pygame.mixer.quit()
        pygame.quit()

    except Exception as error:

        print("Error al cerrar sonido:", error)

    # DETENER EL SISTEMA DE VOZ

    try:

        cola_voz.put(None)

    except Exception as error:

        print("Error al cerrar voz:", error)

    ventana.destroy()


# ==========================================
# 11. INTERFAZ GRAFICA NEON HUD
# ==========================================

ventana = tk.Tk()

ventana.title(
    "PIEDRA, PAPEL O TIJERA - NEON HUD"
)

ventana.geometry("700x650")

ventana.configure(
    bg="#08091a"
)

ventana.resizable(
    False,
    False
)

ventana.protocol(
    "WM_DELETE_WINDOW",
    cerrar_juego
)


# ==========================================
# 12. MENU PRINCIPAL
# ==========================================

frame_menu = tk.Frame(
    ventana,
    bg="#08091a"
)

frame_menu.pack(
    fill="both",
    expand=True
)


lbl_header_title = tk.Label(
    frame_menu,
    text="✊ PIEDRA, PAPEL O TIJERA ✂",
    font=("Arial", 24, "bold"),
    bg="#08091a",
    fg="#00f3ff"
)

lbl_header_title.pack(
    pady=(40, 10)
)


lbl_header_subtitle = tk.Label(
    frame_menu,
    text="¡DEMUESTRA QUIÉN ES EL MEJOR!",
    font=("Arial", 12, "bold"),
    bg="#08091a",
    fg="#5f7597"
)

lbl_header_subtitle.pack(
    pady=(0, 30)
)


# OPCION 1

btn_modo1 = tk.Button(
    frame_menu,
    text="OPCIÓN 1 - PC VS USUARIO",
    font=("Arial", 11, "bold"),
    bg="#101432",
    fg="#00f3ff",
    bd=2,
    relief="flat",
    activebackground="#00f3ff",
    activeforeground="#050714",
    height=2,
    command=lambda: iniciar_juego(1)
)

btn_modo1.pack(
    fill="x",
    padx=100,
    pady=10
)


# OPCION 2

btn_modo2 = tk.Button(
    frame_menu,
    text="OPCIÓN 2 - PC VS USUARIO ALEATORIO",
    font=("Arial", 11, "bold"),
    bg="#101432",
    fg="#00f3ff",
    bd=2,
    relief="flat",
    activebackground="#00f3ff",
    activeforeground="#050714",
    height=2,
    command=lambda: iniciar_juego(2)
)

btn_modo2.pack(
    fill="x",
    padx=100,
    pady=10
)


# OPCION 3

btn_modo3 = tk.Button(
    frame_menu,
    text="OPCIÓN 3 - USUARIO 1 VS USUARIO 2",
    font=("Arial", 11, "bold"),
    bg="#101432",
    fg="#00f3ff",
    bd=2,
    relief="flat",
    activebackground="#00f3ff",
    activeforeground="#050714",
    height=2,
    command=lambda: iniciar_juego(3)
)

btn_modo3.pack(
    fill="x",
    padx=100,
    pady=10
)


# ==========================================
# 13. PANTALLA DE JUEGO
# ==========================================

frame_juego = tk.Frame(
    ventana,
    bg="#0a0e26"
)


lbl_titulo_juego = tk.Label(
    frame_juego,
    text="MODALIDAD",
    font=("Arial", 14, "bold"),
    bg="#0a0e26",
    fg="#00f3ff"
)

lbl_titulo_juego.pack(
    pady=(20, 5)
)


lbl_instruccion = tk.Label(
    frame_juego,
    text="Instrucción",
    font=("Arial", 12),
    bg="#0a0e26",
    fg="#8fa0be"
)

lbl_instruccion.pack(
    pady=(0, 20)
)


# ==========================================
# 14. JUGADORES
# ==========================================

frame_combate = tk.Frame(
    frame_juego,
    bg="#0a0e26"
)

frame_combate.pack(
    pady=10
)


frame_p1 = tk.Frame(
    frame_combate,
    bg="#16163a",
    bd=1,
    relief="solid"
)

frame_p1.grid(
    row=0,
    column=0,
    padx=20,
    pady=15
)


lbl_nombre_jugador = tk.Label(
    frame_p1,
    text="Usuario",
    font=("Arial", 12, "bold"),
    bg="#16163a",
    fg="#a0aec0"
)

lbl_nombre_jugador.pack(
    padx=15,
    pady=5
)


lbl_simbolo_jugador = tk.Label(
    frame_p1,
    text="❔",
    font=("Arial", 48),
    bg="#16163a",
    fg="#ffffff"
)

lbl_simbolo_jugador.pack(
    pady=10
)


lbl_versus = tk.Label(
    frame_combate,
    text="VS",
    font=("Arial", 22, "bold"),
    bg="#0a0e26",
    fg="#ff0055"
)

lbl_versus.grid(
    row=0,
    column=1,
    padx=10
)


frame_p2 = tk.Frame(
    frame_combate,
    bg="#16163a",
    bd=1,
    relief="solid"
)

frame_p2.grid(
    row=0,
    column=2,
    padx=20,
    pady=15
)


lbl_nombre_pc = tk.Label(
    frame_p2,
    text="Computadora",
    font=("Arial", 12, "bold"),
    bg="#16163a",
    fg="#a0aec0"
)

lbl_nombre_pc.pack(
    padx=15,
    pady=5
)


lbl_simbolo_pc = tk.Label(
    frame_p2,
    text="❔",
    font=("Arial", 48),
    bg="#16163a",
    fg="#ffffff"
)

lbl_simbolo_pc.pack(
    pady=10
)


# ==========================================
# 15. RESULTADO
# ==========================================

lbl_resultado = tk.Label(
    frame_juego,
    text="¡Que comience el juego!",
    font=("Arial", 16, "bold"),
    bg="#0a0e26",
    fg="#ff9d00"
)

lbl_resultado.pack(
    pady=20
)


# ==========================================
# 16. BOTONES DE JUGADA
# ==========================================

frame_botones_accion = tk.Frame(
    frame_juego,
    bg="#0a0e26"
)

frame_botones_accion.pack(
    pady=10
)


btn_piedra = tk.Button(
    frame_botones_accion,
    text="✊ PIEDRA",
    font=("Arial", 10, "bold"),
    bg="#101432",
    fg="#00f3ff",
    width=12,
    height=2,
    command=lambda: jugar("piedra")
)

btn_piedra.grid(
    row=0,
    column=0,
    padx=5
)


btn_papel = tk.Button(
    frame_botones_accion,
    text="✋ PAPEL",
    font=("Arial", 10, "bold"),
    bg="#101432",
    fg="#00f3ff",
    width=12,
    height=2,
    command=lambda: jugar("papel")
)

btn_papel.grid(
    row=0,
    column=1,
    padx=5
)


btn_tijera = tk.Button(
    frame_botones_accion,
    text="✌️ TIJERA",
    font=("Arial", 10, "bold"),
    bg="#101432",
    fg="#00f3ff",
    width=12,
    height=2,
    command=lambda: jugar("tijera")
)

btn_tijera.grid(
    row=0,
    column=2,
    padx=5
)


# ==========================================
# 17. MARCADOR
# ==========================================

frame_score = tk.Frame(
    frame_juego,
    bg="#060818",
    bd=1,
    relief="solid"
)

frame_score.pack(
    fill="x",
    padx=80,
    pady=20
)


lbl_marcador_titulo = tk.Label(
    frame_score,
    text="MARCADOR DE CONTROL",
    font=("Arial", 9, "bold"),
    bg="#060818",
    fg="#5f7597"
)

lbl_marcador_titulo.pack(
    pady=(5, 0)
)


lbl_marcador_valores = tk.Label(
    frame_score,
    text="Cargando...",
    font=("Arial", 11, "bold"),
    bg="#060818",
    fg="#00f3ff"
)

lbl_marcador_valores.pack(
    pady=5
)


# ==========================================
# 18. CONTROLES
# ==========================================

frame_controles = tk.Frame(
    frame_juego,
    bg="#0a0e26"
)

frame_controles.pack(
    pady=10
)


btn_reiniciar = tk.Button(
    frame_controles,
    text="REINICIAR PARTIDA",
    font=("Arial", 9, "bold"),
    bg="#0a0e26",
    fg="#ff9d00",
    bd=1,
    relief="solid",
    command=reiniciar_marcador
)

btn_reiniciar.grid(
    row=0,
    column=0,
    padx=10,
    pady=5
)


btn_volver = tk.Button(
    frame_controles,
    text="VOLVER AL MENÚ",
    font=("Arial", 9, "bold"),
    bg="#0a0e26",
    fg="#ff0055",
    bd=1,
    relief="solid",
    command=volver_menu
)

btn_volver.grid(
    row=0,
    column=1,
    padx=10,
    pady=5
)


# ==========================================
# 19. INICIAR APLICACION
# ==========================================

ventana.mainloop()
