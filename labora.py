from fastapi import FastAPI, HTTPException, APIRouter, Depends, Request
from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Get the API Key from environment variables
API_KEY = os.getenv("API_PASS_KEY")

def verify_api_key(request: Request):
    # Check API key from both headers and query parameters
    api_key = request.headers.get("X-API-KEY") or request.query_params.get("api_key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# Define task database
task_db = [
    {"task_id": 1, "task_title": "Lab Activity", "task_description": "Create Lab Act 2", "is_finished": False}
]

# Define second task database (task_db2)
task_db2 = [
    {"task_id": 1, "task_title": "Lab Activity", "task_description": "Create Lab Act 2", "is_finished": False}
]

# Task model for input validation
class Task(BaseModel):
    task_title: str
    task_desc: Optional[str] = ""
    is_finished: bool = False

# APIV1 Router (Version 1)
apiv1 = APIRouter()

@apiv1.get("/task/{task_id}", tags=["v1"])
def get_task_v1(task_id: int, api_key: str = Depends(verify_api_key)):
    task = next((task for task in task_db if task["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return task

@apiv1.post("/task", tags=["v1"])
def create_task_v1(task: Task, api_key: str = Depends(verify_api_key)):
    task_id = len(task_db) + 1
    new_task = task.dict()
    new_task["task_id"] = task_id
    task_db.append(new_task)
    return JSONResponse(status_code=201, content={"message": "Thy new task hath been created with great successy.", "task": new_task})

@apiv1.patch("/task/{task_id}", tags=["v1"])
def update_task_v1(task_id: int, task: Task, api_key: str = Depends(verify_api_key)):
    task_db_entry = next((task for task in task_db if task["task_id"] == task_id), None)
    if not task_db_entry:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    task_db_entry.update(task.dict())
    return JSONResponse(status_code=204, content={"message": "Thy task hath been updated with triumph."})

@apiv1.delete("/task/{task_id}", tags=["v1"])
def delete_task_v1(task_id: int, api_key: str = Depends(verify_api_key)):
    task = next((task for task in task_db if task["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    task_db.remove(task)
    return JSONResponse(status_code=204, content={"message": "Thy task hath been deleted with triumph."})

# APIV2 Router (Version 2) - Now using task_db2
apiv2 = APIRouter()

@apiv2.get("/task/{task_id}", tags=["v2"])
def get_task_v2(task_id: int, api_key: str = Depends(verify_api_key)):
    task = next((task for task in task_db2 if task["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return task

@apiv2.post("/task", tags=["v2"])
def create_task_v2(task: Task, api_key: str = Depends(verify_api_key)):
    task_id = len(task_db2) + 1
    new_task = task.dict()
    new_task["task_id"] = task_id
    task_db2.append(new_task)
    return JSONResponse(status_code=201, content={"message": "Thy new task hath been created with great successy.", "task": new_task})

@apiv2.patch("/task/{task_id}", tags=["v2"])
def update_task_v2(task_id: int, task: Task, api_key: str = Depends(verify_api_key)):
    task_db_entry = next((task for task in task_db2 if task["task_id"] == task_id), None)
    if not task_db_entry:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    task_db_entry.update(task.dict())
    return JSONResponse(status_code=204, content={"message": "Thy task hath been updated with triumph."})

@apiv2.delete("/task/{task_id}", tags=["v2"])
def delete_task_v2(task_id: int, api_key: str = Depends(verify_api_key)):
    task = next((task for task in task_db2 if task["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    task_db2.remove(task)
    return JSONResponse(status_code=204, content={"message": "Thy task hath been deleted with triumph"})

# Include the routers in the main app
app.include_router(apiv1, prefix="/apiv1", tags=["v1"])
app.include_router(apiv2, prefix="/apiv2", tags=["v2"])

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Greetings, noble traveler, to this humble API. Seek ye the versioned endpoints through /apiv1/task/1 or /apiv2/task/1"}

@app.get("/health")
def health_check():
    return {"status": "The API doth remain in full operation"}
