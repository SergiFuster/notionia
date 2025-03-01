from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.notion_agent import NotionAgent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class TaskRequest(BaseModel):
    task: str

notion_agent = NotionAgent()

@app.post("/execute-task")
async def execute_notion_task(request: TaskRequest):
    try:
        result = notion_agent.run(request.task)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
