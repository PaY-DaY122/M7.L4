import random
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from googletrans import Translator

duration = 5
sample_rate = 44100
errores_maximos = 3

palabras_por_niveles = {
    "facil": [
        "gato", "perro", "casa", "leche", "sol",
        "manzana", "agua", "libro", "mesa", "flor",
        "pan", "niño", "luna", "mar", "pie",
    ],
    "medio": [
        "escuela", "amigo", "ventana", "amarillo", "banano",
        "ciudad", "trabajo", "música", "tiempo", "puerta",
        "montaña", "familia", "coche", "jardín", "camino",
    ],
    "dificil": [
        "tecnologia", "universidad", "informacion", "pronunciacion", "imaginacion",
        "biblioteca", "computadora", "electricidad", "arquitectura", "comunicacion",
        "responsabilidad", "administracion", "conocimiento", "investigacion", "experiencia",
    ],
}

def elegir_nivel():
    while True:
        nivel = input("Elige un nivel (facil, medio, dificil): ").lower()
        if nivel in palabras_por_niveles:
            return nivel
        else:
            print("Nivel no válido. Escribe: facil, medio o dificil.")


def grabar_y_reconocer():
    print(f"\nGrabando {duration} segundos... ¡habla ahora!")
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )
    sd.wait()
    wav.write("output.wav", sample_rate, recording)
    print("Grabación completa, reconociendo...")

    recognizer = sr.Recognizer()
    with sr.AudioFile("output.wav") as source:
        audio = recognizer.record(source)

    try:
        recognized = recognizer.recognize_google(audio, language="en-US")
        return recognized.lower()
    except sr.UnknownValueError:
        print("No se pudo entender el audio.")
        return ""
    except sr.RequestError as e:
        print(f"Error del servicio: {e}")
        return ""

def calcular_puntos(nivel):
    puntos_base = {"facil": 10, "medio": 20, "dificil": 40}
    return puntos_base[nivel]

def obtener_multiplicador(racha):
    if racha >= 5:
        return 3
    elif racha >= 3:
        return 2
    else:
        return 1


def jugar():
    nivel = elegir_nivel()
    palabras = palabras_por_niveles[nivel]

    aciertos = 0
    errores = 0
    ronda = 0
    puntos = 0       
    racha = 0       

    while errores < errores_maximos and ronda < len(palabras):
        palabra = random.choice(palabras)
        ronda += 1

        traduccion = Translator().translate(palabra, src="es", dest="en").text.lower()

        print(f"\nRonda {ronda} | Aciertos: {aciertos} | Errores: {errores}/{errores_maximos}")
        print(f"Puntos: {puntos} | Racha: {racha}")  
        print(f"Palabra en español: {palabra.upper()}")
        print("Pronuncia su traducción en inglés.")
        input("Presiona ENTER para grabar...")

        dicho = grabar_y_reconocer()

        if dicho:
            if traduccion in dicho or dicho in traduccion:
                aciertos += 1
                racha += 1                                       

                multiplicador = obtener_multiplicador(racha)       
                ganados = calcular_puntos(nivel) * multiplicador   
                puntos += ganados                                  

                print(f"👍 ¡Correcto! Dijiste: '{dicho}'")
                print(f"+{ganados} puntos (x{multiplicador})", end="")  

                if racha == 3:
                    print(" | ¡Racha x2!")
                elif racha == 5:
                    print(" | ¡Racha x3!")
                else:
                    print()

            else:
                errores += 1
                racha = 0   
                print(f"👎 Incorrecto. Dijiste: '{dicho}' | Esperado: '{traduccion}'")
        else:
            errores += 1
            racha = 0      
            print("👎 Sin respuesta. Se cuenta como error.")

    print("\n--- RESULTADO FINAL ---")
    print(f"Aciertos: {aciertos} | Errores: {errores} | Puntos totales: {puntos}") 
    if errores >= errores_maximos:
        print("Llegaste a 3 errores. ¡Fin del juego!")
    else:
        print("¡Completaste todas las rondas!")

if __name__ == "__main__":
    jugar()
