# Cliente de LM Studio para llamar a un servidor MCP
# Este cliente se conecta a un servidor MCP (definido en mcp_server.py)
# y le hace preguntas usando un modelo local en LM Studio.

#!pip install fastmcp openai
import asyncio
import json
from openai import OpenAI
from fastmcp import Client

# ── Configuración ──────────────────────────────────────────
LM_STUDIO_URL = "http://localhost:1234/v1"
SERVIDOR_MCP  = "/home/jordi/Documentos/Ribera/Curso_25_26/CEIABD/CEIABD_25_26/PROGRAMACION_IA_25_26/AGENTES/MCP_SERVER/mcp_server.py"

# Cliente de LM Studio (API compatible con OpenAI)
llm = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")


# ── Paso 1: Obtener las herramientas del servidor MCP ──────
async def obtener_herramientas_openai():
    """Convierte las herramientas MCP al formato que entiende OpenAI/LM Studio."""
    async with Client(SERVIDOR_MCP) as client:
        herramientas = await client.list_tools()
    
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.inputSchema
            }
        }
        for t in herramientas
    ]


# ── Paso 2: Llamar a una herramienta MCP ──────────────────
async def llamar_herramienta(nombre: str, argumentos: dict):
    async with Client(SERVIDOR_MCP) as client:
        resultado = await client.call_tool(nombre, argumentos)
    return resultado.data


# ── Paso 3: El agente completo ────────────────────────────
async def agente(pregunta: str):
    herramientas = await obtener_herramientas_openai()
    mensajes = [{"role": "user", "content": pregunta}]

    print(f"\n👤 Usuario: {pregunta}")

    # Primera llamada al LLM
    respuesta = llm.chat.completions.create(
        model="local-model",  # el nombre da igual en LM Studio
        messages=mensajes,
        tools=herramientas,
        tool_choice="auto"
    )

    mensaje = respuesta.choices[0].message

    # ¿El LLM quiere usar una herramienta?
    if mensaje.tool_calls:
        for tool_call in mensaje.tool_calls:
            nombre     = tool_call.function.name
            argumentos = json.loads(tool_call.function.arguments)

            print(f"\n🔧 LLM llama a la herramienta: {nombre}({argumentos})")

            # Llamamos al servidor MCP
            resultado = await llamar_herramienta(nombre, argumentos)
            print(f"📦 Resultado MCP: {resultado}")

            # Añadimos el resultado a la conversación
            mensajes.append(mensaje)
            mensajes.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(resultado, ensure_ascii=False)
            })

        # Segunda llamada: el LLM formula la respuesta final con los datos
        respuesta_final = llm.chat.completions.create(
            model="local-model",
            messages=mensajes
        )
        print(f"\n🤖 Respuesta: {respuesta_final.choices[0].message.content}")

    else:
        # El LLM respondió directamente sin herramientas
        print(f"\n🤖 Respuesta: {mensaje.content}")


# ── Ejecución ─────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(agente("¿Qué tiempo hace ahora mismo en Valladolid?"))
    asyncio.run(agente("¿Cuánto es 1234 * 5678?"))
    asyncio.run(agente("¿Quién es Hedi Lamarr?"))