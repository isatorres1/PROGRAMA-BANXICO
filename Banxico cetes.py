#Codigo Banxico
"""""
Autor: Isabel Torres Hidalgo
Fecha: 07-10-26
Objetivo: Consultar una serie aleatoria de Banxico, posteriormente realizar una consulta con la serie de CETES y finalmente salir del programa
enviando por e-mail el reporte de resultados
Version extendida SMS o WhastApp solo si no se conecta el e-mail
"""""


import os
import requests
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
print("El programa está leyendo el archivo")

CORREO_REMITENTE = os.getenv("USERMAIL")
PASSWORD_APLICACION = os.getenv("PASSWORD")
TOKEN_BANXICO = os.getenv("TOKEN_BANXICO")

SERIE_X = "SF43718"


# FUNCION 1 CONSULTA UNA SERIE DE BANXICO
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

# 2 FUNCION CONSULTA DE ISC
def calcular_cetes(monto, tasa):
    """
    Calcula el rendimiento de ISC, utilizando CETES a 28 días.
    """
    rendimiento = monto * (tasa / 100) * (28 / 360)
    total = monto + rendimiento
    return rendimiento, total

# 3 FUNCION ENVIAR EL REPORTE 
    
def enviar_email(correo_destino, contenido_reporte):
    """Docstring: Envía el reporte por correo usando Gmail (puerto 587 con STARTTLS)."""
    try:
        mensaje = MIMEText(contenido_reporte, 'plain')
        mensaje['Subject'] = "Reporte ISC - Resultados de Cálculo"
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

#FUNCION 4 MENU DE OPCIONES
"""Docstring: Muestra el menu principal con las 3 opciones del flujo del programa y gestiona la opcion de salida"""
def menu():

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

                reporte = (
                    f"Reporte CETES\n"
                    f"Fecha: {fecha}\n"
                    f"Tasa anual: {tasa}%\n"
                    f"Monto invertido: ${monto:,.2f}\n"
                    f"Rendimiento estimado: ${rendimiento:,.2f}\n"
                    f"Monto total: ${total:,.2f}"
                )
                print("\n" + reporte)

                enviar = input("¿Deseas enviar el reporte por correo? (s/n): ")
                if enviar.lower() == 's':
                    destino = input("Escribe el correo destinatario: ")
                    enviar_email(destino, reporte)

        elif opcion == "3":
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

menu()