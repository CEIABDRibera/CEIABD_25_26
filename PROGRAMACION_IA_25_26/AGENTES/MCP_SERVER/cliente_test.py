import asyncio
from fastmcp import Client

async def main():
    # Conecta al servidor MCP
    client = Client("/home/jordi/Documentos/Ribera/Curso_25_26/CEIABD/CEIABD_25_26/PROGRAMACION_IA_25_26/AGENTES/MCP_SERVER/mcp_server.py")

    
    async with client:
        #Lista las herramientas disponibles en el servidor
        herramientas = await client.list_tools()
        print("Herramientas disponibles en el servidor MCP:", herramientas)
        for herramienta in herramientas:
            print(f"- {herramienta.name}: {herramienta.description}")
        
        print("\n" + "-"*50 + "\n")
    
        # Llama a la herramienta 'obtener_tiempo' con un argumento
        resultado = await client.call_tool("obtener_tiempo", 
                                        {"ciudad": "Blanes"})
        # Llama a la herramienta 'calcular' con una expresión matemática
        operacion = "2 + 3"
        calculo = await client.call_tool("calcular", 
                                         {"expresion": operacion})
        
        
        #print("Resultado del servidor MCP:", resultado)
        datos = resultado.data
        print(f"""
        🌤️  Tiempo en {datos['ciudad']} ({datos['pais']})
        {'─'*40}
        🌡️  Temperatura : {datos['temperatura']}
        💧 Humedad     : {datos['humedad']}
        💨 Viento      : {datos['viento']}
        ☁️  Condición   : {datos['condicion'].capitalize()}
        """)
        
        print("\n" + "-"*50 + "\n")
        respuesta = calculo.data
        print(f"Resultado del cálculo en el servidor MCP: {operacion} = {respuesta['resultado']}")

if __name__ == "__main__":
    asyncio.run(main())