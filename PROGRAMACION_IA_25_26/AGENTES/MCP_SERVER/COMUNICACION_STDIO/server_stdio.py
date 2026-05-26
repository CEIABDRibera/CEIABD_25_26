import json
import sys

sys.stdout.reconfigure(line_buffering=True) # Configura stdout para que no esté en buffer y que las respuestas se impriman inmediatamente

from utilities.messages import initializeResponse


initialized = False
    
while True:
    for line in sys.stdin:
        message = line.strip()
        if message == "hola":
            print(json.dumps({"respuesta": "¡Hola! ¿En qué puedo ayudarte?"}))
            sys.stdout.flush()
            
        elif message.startswith('{"jsonrpc":'):
            json_message = json.loads(message)
            method = json_message.get("method","")
            
            if not initialized:
                if method != "initialize" and method != "notifications/initialized":
                    print(json.dumps({"error": "Servidor no inicializado. Por favor, envía un mensaje de 'initialize' primero. Has enviado: " + method}))
                    sys.stdout.flush()
                    continue
                    
            match method:
                case "notifications/initialized":
                    # print("[SERVIDOR] Recibida notificación de inicialización del cliente.")
                    sys.stdout.flush()
                    initialized = True
                    break
                
                case "initialize":
                    print(json.dumps(initializeResponse))
                    sys.stdout.flush()
                    break
                
                case "tools/list":
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": json_message["id"],
                        "result": {
                            "tools": ["tool1", "tool2"]
                        }
                    }
                    
                    print(json.dumps(response))
                    sys.stdout.flush()
                    break
                
                case _:
                    print(f"Error: Método {method} no reconocido")
                    sys.stdout.flush()  
                    break
        elif message == "exit":
            print(json.dumps({"respuesta": "Servidor cerrando conexión. ¡Adiós!"}))
            sys.stdout.flush()
            sys.exit(0)
        else:
            print(f"Mensaje no reconocido: {message}")