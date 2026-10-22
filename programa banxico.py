# Codigo Banxico
"""
Autor: Isabel Torres Hidalgo
Fecha: 07-10-26
Objetivo: Consultar una serie aleatoria de Banxico, posteriormente realizar una
consulta con la serie de CETES y finalmente salir del programa enviando por
e-mail el reporte de resultados.
Version extendida SMS o WhatsApp solo si no se conecta el e-mail.
"""

import os
import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

CORREO_REMITENTE = os.getenv("USERMAIL")
PASSWORD_APLICACION = os.getenv("PASSWORD")
TOKEN_BANXICO = os.getenv("TOKEN_BANXICO")
SERIE_X = "SF43718"

# FUNCION 1: CONSULTA UNA SERIE DE BANXICO
def consultar_banxico(serie):
    """
    Consulta una serie de Banxico en tiempo real.
    Comprueba la conectividad, el estatus de la respuesta HTTP y extrae el valor.
    """
    url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie}/datos/oportuno"
    headers = {"Bmx-Token": TOKEN_BANXICO}

    try:
        print(f"\nConectando con Banxico para la serie {serie}...")
        respuesta = requests.get(url, headers=headers, timeout=5)

        if respuesta.status_code == 200:
            datos = respuesta.json()
            info_serie = datos['bmx']['series'][0]['datos'][0]
            valor = float(info_serie['dato'])
            fecha = info_serie['fecha']

            print("Conexión exitosa!")
            print(f"Serie: {serie} | Fecha: {fecha} | Valor: {valor}")
            return valor, fecha
        else:
            print(f"Error: El servidor respondió con el código de estatus {respuesta.status_code}")
            return None, None

    except requests.exceptions.RequestException as error:
        print(f"Error de red o conectividad: {error}")
        return None, None
    except (KeyError, IndexError, ValueError) as error:
        print(f"Error al procesar los datos de la respuesta: {error}")
        return None, None

# FUNCION 2: CALCULO DE INTERES SIMPLE CON CETES
def calcular_cetes(monto, tasa):
    """
    Calcula el interés simple usando la tasa de CETES a 28 días.
    Fórmula: I = C * i * t
    """
    rendimiento = monto * (tasa / 100) * (28 / 360)
    total = monto + rendimiento
    return rendimiento, total

# FUNCION 3: ENVIAR EL REPORTE POR CORREO
def enviar_email(correo_destino, contenido_reporte, asunto="Reporte ISC - Resultados de Cálculo"):
    """Envía el reporte por correo usando Gmail (puerto 587 con STARTTLS)."""
    try:
        mensaje = MIMEText(contenido_reporte, 'plain')
        mensaje['Subject'] = asunto
        mensaje['From'] = CORREO_REMITENTE
        mensaje['To'] = correo_destino

        print("1. Conectando con Gmail...")
        servidor = smtplib.SMTP('smtp.gmail.com', 587, timeout=15)
        servidor.ehlo()
        servidor.starttls()
        servidor.ehlo()

        print("2. Iniciando sesión...")
        servidor.login(CORREO_REMITENTE, PASSWORD_APLICACION)

        print("3. Enviando correo...")
        servidor.send_message(mensaje)
        servidor.quit()
        print("¡Correo enviado con éxito!")

    except smtplib.SMTPAuthenticationError:
        print("Error de autenticación: revisa el correo o la contraseña de aplicación.")
    except Exception as error:
        print(f"Error al enviar el correo: {error}")

# FUNCION 4: MENU
def menu():
    """Muestra el menú principal con las 3 opciones y gestiona la salida."""
    while True:
        print("\n--- MENÚ DE OPCIONES ---")
        print("1. Consultar serie Banxico (SF43718)")
        print("2. Consultar ISC (SF43783) y calcular")
        print("3. Salir")

        opcion = input("Selecciona una opción (1-3): ")

        if opcion == "1":
            valor, fecha = consultar_banxico(SERIE_X)
            if valor is not None:
                reporte = f"Reporte Banxico\nSerie: {SERIE_X}\nFecha: {fecha}\nValor: {valor}"
                print("\n" + reporte)
                enviar = input("¿Deseas enviar el reporte por correo? (s/n): ")
                if enviar.lower() == 's':
                    destino = input("Escribe el correo destinatario: ")
                    enviar_email(destino, reporte)

        elif opcion == "2":
            serie_cetes = "SF43783"
            tasa, fecha = consultar_banxico(serie_cetes)
            if tasa is not None:
                try:
                    monto = float(input("Ingrese el monto a invertir: $"))
                except ValueError:
                    print("Error: Ingresa un valor numérico válido.")
                    continue

                rendimiento, total = calcular_cetes(monto, tasa)

                destino = ""
                enviar = input("¿Deseas enviar el reporte por correo? (s/n): ")
                if enviar.lower() == 's':
                    destino = input("Escribe el correo destinatario: ")

                ahora = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
                reporte = (
                    f"REPORTE DE CÁLCULO: INTERÉS SOBRE CAPITAL (ISC)\n\n"
                    f"REMITENTE: {CORREO_REMITENTE}\n"
                    f"DESTINATARIO: {destino}\n\n"
                    f"Objetivo Inicial: Calcular el Interés sobre Capital "
                    f"utilizando la tasa vigente de Banxico.\n\n"
                    f"Datos del Mercado Financiero:\n"
                    f"- Identificador de Serie Banxico: {serie_cetes}\n"
                    f"- Concepto: Cetes a 28 días - Tasa de rendimiento\n"
                    f"- Tasa de Interés Actual: {tasa}% (Fecha: {fecha})\n\n"
                    f"Resultado de la Evaluación Financiera:\n"
                    f"- Capital Inicial Evaluado: ${monto:,.2f} MXN\n"
                    f"- Rendimiento / Interés generado (28 días): ${rendimiento:,.2f} MXN\n"
                    f"- Monto total: ${total:,.2f} MXN\n\n"
                    f"Atentamente,\n"
                    f"Sistema de Reportes Python\n"
                    f"Fecha de ejecución: {ahora}"
                )
                print("\n" + reporte)

                if destino:
                    enviar_email(destino, reporte, f"Reporte ISC Automatizado - Tasa {tasa}%")

        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    menu()