from fastapi import FastAPI, HTTPException, APIRouter, Depends, Request
from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Initialize environment variables from the .env file
load_dotenv()

# Create FastAPI application instance
app = FastAPI()

# Retrieve the API Key from environment variables
API_KEY = os.getenv("API_PASS_KEY")

def authenticate_api_key(request: Request):
    # Retrieve API key from headers or query parameters
    api_key = request.headers.get("X-API-KEY") or request.query_params.get("API_KEY")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
    return api_key

# Example task database for storing task information
tasks_list_v1 = [
    {"task_id": 1, "task_title": "Laboratory Activity", "task_description": "Forge Lab Act the Second", "is_fulfilled": False}
]

# Another task database for a different version of the API
tasks_list_v2 = [
    {"task_id": 1, "task_title": "Laboratory Activity", "task_description": "Forge Lab Act the Second", "is_fulfilled": False}
]

# Task model to validate incoming task data
class Task(BaseModel):
    task_title: str
    task_desc: Optional[str] = ""
    is_finished: bool = False

# Router for API version 1
api_v1_router = APIRouter()

@api_v1_router.get("assign/{task_id}", tags=["v1"])
def get_task_v1(task_id: int, api_key: str = Depends(authenticate_api_key)):
    task = next((task for task in tasks_list_v1 if task["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return task

@api_v1_router.post("assign", tags=["v1"])
def create_task_v1(task: Task, api_key: str = Depends(authenticate_api_key)):
    task_id = len(tasks_list_v1) + 1
    new_task = task.dict()
    new_task["task_id"] = task_id
    tasks_list_v1.append(new_task)
    return JSONResponse(status_code=201, content={"message": "Thy new task hath been created with great success", "task": new_task})

@api_v1_router.patch("assign/{task_id}", tags=["v1"])
def update_task_v1(task_id: int, task: Task, api_key: str = Depends(authenticate_api_key)):
    task_entry = next((task for task in tasks_list_v1 if task["task_id"] == task_id), None)
    if not task_entry:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    task_entry.update(task.dict())
    return JSONResponse(status_code=204, content={"message": "Thy task hath been updated with triumph."})

@api_v1_router.delete("assign/{task_id}", tags=["v1"])
def delete_task_v1(task_id: int, api_key: str = Depends(authenticate_api_key)):
    task = next((task for task in tasks_list_v1 if task["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    tasks_list_v1.remove(task)
    return JSONResponse(status_code=204, content={"message": "Thy task hath been deleted with triumph."})

# Router for API version 2
api_v2_router = APIRouter()

@api_v2_router.get("assign/{task_id}", tags=["v2"])
def get_task_v2(task_id: int, api_key: str = Depends(authenticate_api_key)):
    task = next((task for task in tasks_list_v2 if task["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return task

@api_v2_router.post("assign", tags=["v2"])
def create_task_v2(task: Task, api_key: str = Depends(authenticate_api_key)):
    task_id = len(tasks_list_v2) + 1
    new_task = task.dict()
    new_task["task_id"] = task_id
    tasks_list_v2.append(new_task)
    return JSONResponse(status_code=201, content={"message": "Thy new task hath been created with great successy.", "task": new_task})

@api_v2_router.patch("assign/{task_id}", tags=["v2"])
def update_task_v2(task_id: int, task: Task, api_key: str = Depends(authenticate_api_key)):
    task_entry = next((task for task in tasks_list_v2 if task["task_id"] == task_id), None)
    if not task_entry:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    task_entry.update(task.dict())
    return JSONResponse(status_code=204, content={"message": "Thy task hath been updated with triumph."})

@api_v2_router.delete("assign/{task_id}", tags=["v2"])
def delete_task_v2(task_id: int, api_key: str = Depends(authenticate_api_key)):
    task = next((task for task in tasks_list_v2 if task["task_id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    tasks_list_v2.remove(task)
    return JSONResponse(status_code=204, content={"message": "Thy task hath been deleted with triumph."})

# Include routers for version 1 and version 2
app.include_router(api_v1_router, prefix="/version1", tags=["v1"])
app.include_router(api_v2_router, prefix="/version2", tags=["v2"])

@app.get("/", tags=["root"])
def home():
    return {"message": "Greetings, noble traveler, to this humble API. Seek ye the versioned endpoints through /apiv1assign/1 or /apiv2assign/1."}

@app.get("/health")
def health_status():
    return {"status": "The API doth remain in full operation"}
