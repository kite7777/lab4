from fastapi import FastAPI, APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from a .env file
load_dotenv()
API_KEY = os.getenv("API_PASS_KEY")

# Check if the API_KEY is set
if not API_KEY:
    raise RuntimeError("API_PASS_KEY is not set in the .env file. Please add it before running.")

# Simulated databases
apiv1_tasks = [
    {"task_id": 1, "task_title": "Lab Activity", "task_desc": "Create Lab Act 2", "is_finished": False}
]
apiv2_tasks = [
    {"task_id": 1, "task_title": "Lab Activity", "task_desc": "Create Lab Act 2", "is_finished": False}
]

# Function to find a task by its ID
def find_task(task_list, task_id):
    for task in task_list:
        if task["task_id"] == task_id:
            return task
    return None

# API key validation function
def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid.")
    return True

# Model to describe a task
class Task(BaseModel):
    task_title: str
    task_desc: Optional[str] = ""
    is_finished: bool = False

# Create API routers for different versions
apiv1_router = APIRouter()
apiv2_router = APIRouter()

# Routes for version 1
@apiv1_router.get("/taks/{task_id}")
def get_task_v1(task_id: int, x_api_key: str = Depends(check_api_key)):
    task = find_task(apiv1_tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="not found.")
    return {"task": task}

@apiv1_router.post("/taks")
def create_task_v1(task: Task, x_api_key: str = Depends(check_api_key)):
    new_task = task.dict()
    new_task["task_id"] = len(apiv1_tasks) + 1
    apiv1_tasks.append(new_task)
    return {"message": "Task created!", "task": new_task}

@apiv1_router.patch("/taks/{task_id}")
def update_task_v1(task_id: int, task: Task, x_api_key: str = Depends(check_api_key)):
    existing_task = find_task(apiv1_tasks, task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="not found.")
    
    existing_task.update(task.dict())
    return {"message": "Task updated!", "task": existing_task}

@apiv1_router.delete("/taks/{task_id}")
def delete_task_v1(task_id: int, x_api_key: str = Depends(check_api_key)):
    task = find_task(apiv1_tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    apiv1_tasks.remove(task)
    return {"message": "Task deleted!"}

# Routes for version 2
@apiv2_router.get("/taks/{task_id}")
def get_task_v2(task_id: int, x_api_key: str = Depends(check_api_key)):
    task = find_task(apiv2_tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="not found.")
    return {"task": task}

@apiv2_router.post("/taks")
def create_task_v2(task: Task, x_api_key: str = Depends(check_api_key)):
    new_task = task.dict()
    new_task["task_id"] = len(apiv2_tasks) + 1
    apiv2_tasks.append(new_task)
    return {"message": "Task created!", "task": new_task}

@apiv2_router.patch("/taks/{task_id}")
def update_task_v2(task_id: int, task: Task, x_api_key: str = Depends(check_api_key)):
    existing_task = find_task(apiv2_tasks, task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="not found.")
    
    # Update only the fields provided
    for key, value in task.dict(exclude_unset=True).items():
        existing_task[key] = value
    return {"message": "Task updated!"}

@apiv2_router.delete("/taks/{task_id}")
def delete_task_v2(task_id: int, x_api_key: str = Depends(check_api_key)):
    task = find_task(apiv2_tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="not found.")
    apiv2_tasks.remove(task)
    return {"message": "Task deleted!"}

# Create the main FastAPI app
app = FastAPI()

# Add routers for the two API versions
app.include_router(apiv1_router, prefix="/apiv1", tags=["V1.1"])
app.include_router(apiv2_router, prefix="/apiv2", tags=["V2.1"])
