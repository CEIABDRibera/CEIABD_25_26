# CLIENTE STDIO PARA COMUNICARSE CON EL SERVIDOR STDIO
# Este cliente se comunica con el servidor a través de stdin/stdout, enviando mensajes y leyendo respuestas.
# El cliente envía un mensaje de saludo, luego una solicitud JSON-RPC para listar herramientas, y finalmente 
# un comando para cerrar el servidor. Las respuestas del servidor se imprimen en la consola del cliente.

import subprocess
import json
import os
import sys

sys.stdout.reconfigure(line_buffering=True) # Configura stdout para que no esté en buffer y que las respuestas se impriman inmediatamente

from utilities.messages import initialize_message, initialized_message, list_tools_message


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_PATH = os.path.join(BASE_DIR, "server_stdio.py")

# Proceso del servidor se inicia como un subproceso, con stdin y stdout configurados para la comunicación
proc = subprocess.Popen(
    ["python", SERVER_PATH], # Ejecuta el servidor como un proceso hijo usando el intérprete de Python y la ruta al archivo del servidor.
    stdin=subprocess.PIPE, # Configura stdin para enviar mensajes al servidor. PIPE permite escribir en el stdin del proceso hijo (servidor).
    stdout=subprocess.PIPE, # Configura stdout para leer respuestas del servidor
    text=True # Configura la comunicación en modo texto, lo que permite enviar y recibir cadenas de texto en lugar de bytes.
)


message = 'Hola\n' # Mensaje de saludo para el servidor.

def send_message(message: str):
    """Envia un mensaje al servidor a través de stdin."""
    print_response(message, prefix='[CLIENTE]: ')
    proc.stdin.write(message)
    proc.stdin.flush()
    
def serialize_message(message: dict) -> str:
    """Serializa un mensaje JSON para enviarlo al servidor."""
    return json.dumps(message) + "\n"


def print_response(response, prefix= ''):
    """Imprime la respuesta del servidor con un prefijo para identificar el contexto."""
    try:
        parsed = json.loads(response)
        print(prefix,json.dumps(parsed, indent=2))
    except json.JSONDecodeError:
        print(prefix, response.strip())

def connect():
    """Función para establecer conexión con el servidor y manejar la comunicación."""
    print("[CLIENTE] Conectando al servidor...")
    #1.- Preguntar por capacidades del servidor
    send_message(serialize_message(initialize_message))
    #2.- Leer respuesta del servidor
    response = proc.stdout.readline()
    print_response(response, prefix='[SERVIDOR]: \n')
    #3.- Enviar mensaje de saludo
    send_message(serialize_message(initialized_message))
    
    
def send_simple_message(message):
    # Envia un mensaje simple al servidor y espera una respuesta.
    send_message(message)

    response = proc.stdout.readline()
    print_response(response, prefix='[SERVIDOR]: \n')  
    
    
def list_tools():
    """Función para solicitar la lista de herramientas al servidor."""
    print("[CLIENTE] Solicitando lista de herramientas al servidor...")
    send_message(serialize_message(list_tools_message))
    response = proc.stdout.readline()
    print_response(response, prefix='[SERVIDOR]: \n')
    

def close_server():
    """Función para cerrar el servidor de forma ordenada."""
    print("[CLIENTE] Enviando comando para cerrar el servidor...")
    send_message("exit\n")
    
    exit_code = proc.wait() # Esperar a que el proceso del servidor termine y obtener su código de salida
    print(f"[SERVIDOR] Servidor cerrado con código de salida: {exit_code}") # Imprime el código de salida del servidor para confirmar que se cerró correctamente
    



def main():
    connect() # Establece conexión con el servidor y maneja la comunicación inicial
    list_tools() # Solicita la lista de herramientas al servidor
    close_server() # Cierra el servidor de forma ordenada
    

main()



### NOTA JSON-RPC (Protocolo de llamadas a procedimientos remotos en formato JSON)
# El mensaje JSON-RPC enviado al servidor tiene la siguiente estructura:
# {
#     "jsonrpc": "2.0",  # Versión del protocolo JSON-RPC
#     "id": 1,           # Identificador único para correlacionar solicitudes y respuestas
#     "method": "tools/list",  # Método que se desea invocar
#     "params": {}       # Parámetros para el método (vacío en este caso)
# }     
# El servidor responde con una estructura similar:
# { 
#     "jsonrpc": "2.0",  # Versión del protocolo JSON-RPC
#     "id": 1,           # Mismo identificador para correlacionar con la solicitud
#     "result": ["tool1", "tool2"]  # Resultado de la invocación del método, en este caso una lista de herramientas
# }
#
# En caso de error, el servidor podría responder con una estructura de error JSON-RPC:
# {
#     "jsonrpc": "2.0",
#     "id": 1,
#     "error": {
#         "code": -32601,  # Código de error (por ejemplo, método no encontrado)
#         "message": "Method not found"  # Mensaje de error descriptivo
#     }
# }
# Para gestion de notificaciones, el servidor podría enviar mensajes sin el campo "id", 
# indicando que no se espera una respuesta correlacionada:
# {
#     "jsonrpc": "2.0",
#     "method": "notification/event",
#     "params": {"event": "something_happened"}  # Parámetros de la notificación
# } 
# MCP usa JSON-RPC para la comunicación entre agentes y herramientas, por lo que es importante 
# seguir esta estructura para asegurar una comunicación efectiva.