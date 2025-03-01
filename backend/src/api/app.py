from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sys
import os
import traceback
from pathlib import Path
from ..agent.notion_agent import NotionAgent
from pydantic import BaseModel

app = FastAPI(title="Notionia API", description="API para interactuar con el agente de Notion")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar el agente de Notion
try:
    agent = NotionAgent()
    print("Agente de Notion inicializado correctamente")
except Exception as e:
    print(f"Error al inicializar el agente de Notion: {str(e)}")
    traceback.print_exc()
    raise

# Modelo de datos para la solicitud
class PromptRequest(BaseModel):
    prompt: str

# Modelo de datos para la respuesta
class AgentResponse(BaseModel):
    response: str

@app.post("/api/agent/invoke", response_model=AgentResponse)
async def invoke_agent(request: PromptRequest):
    """
    Invoca al agente de Notion con un prompt y devuelve su respuesta.
    """
    print(f"Recibido prompt: {request.prompt}")
    
    if not request.prompt:
        print("Error: No se proporcionó un prompt")
        raise HTTPException(status_code=400, detail="No se proporcionó un prompt")
    
    try:
        print("Invocando al agente...")
        response = agent.invoke(request.prompt)
        print(f"Respuesta del agente: {response[:100]}...")  # Mostrar solo los primeros 100 caracteres
        return AgentResponse(response=response)
    except Exception as e:
        error_msg = f"Error al invocar al agente: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

# Endpoint adicional para compatibilidad con versiones anteriores
@app.post("/default/execute_notion_task_execute_task_post")
async def execute_notion_task_execute_task_post(request: PromptRequest):
    """
    Endpoint alternativo para compatibilidad con versiones anteriores.
    Redirige al endpoint principal.
    """
    print(f"Recibido prompt en endpoint de compatibilidad: {request.prompt}")
    return await invoke_agent(request)

# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = f"Error no manejado: {str(exc)}"
    print(error_msg)
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": error_msg},
    )
