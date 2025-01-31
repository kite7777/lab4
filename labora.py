from fastapi import FastAPI, HTTPException, APIRouter, Depends, Request
from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
api_app = FastAPI()

# Retrieve the API Key from environment
SECRET_API_KEY = os.getenv("LAB_KEY")

# Task Model for Input Validation
class TaskDetails(BaseModel):
    title: str
    description: Optional[str] = ""
    completed: bool = False

# Utility function to verify API key
def validate_api_key(req: Request):
    api_key = req.headers.get("X-API-KEY") or req.query_params.get("api_key")
    if api_key != SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Access Denied: Incorrect API Key")
    return api_key

# Task Data Storage Class
class TaskStorage:
    def __init__(self):
        self.data = []

    def find_task_by_id(self, task_id: int):
        return next((task for task in self.data if task["id"] == task_id), None)

    def add_new_task(self, task: TaskDetails):
        task_id = len(self.data) + 1
        new_task = task.dict()
        new_task["id"] = task_id
        self.data.append(new_task)
        return new_task

    def modify_task(self, task_id: int, task_data: TaskDetails):
        task_entry = self.find_task_by_id(task_id)
        if task_entry:
            task_entry.update(task_data.dict())
            return task_entry
        return None

    def remove_task(self, task_id: int):
        task = self.find_task_by_id(task_id)
        if task:
            self.data.remove(task)
            return True
        return False

# Initialize different task storage for versions
v1_task_storage = TaskStorage()
v2_task_storage = TaskStorage()

# API Router for Version 1
v1_router = APIRouter()

@v1_router.get("/taks/{task_id}", tags=["v1"])
def retrieve_task_v1(task_id: int, api_key: str = Depends(validate_api_key)):
    task = v1_task_storage.find_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found in Version 1.")
    return task

@v1_router.post("/taks", tags=["v1"])
def add_task_v1(task: TaskDetails, api_key: str = Depends(validate_api_key)):
    new_task = v1_task_storage.add_new_task(task)
    return JSONResponse(status_code=201, content={"message": "Task added successfully to Version 1.", "task": new_task})

@v1_router.patch("/taks/{task_id}", tags=["v1"])
def edit_task_v1(task_id: int, task: TaskDetails, api_key: str = Depends(validate_api_key)):
    updated_task = v1_task_storage.modify_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found in Version 1.")
    return JSONResponse(status_code=204, content={"message": "Task updated in Version 1."})

@v1_router.delete("/taks/{task_id}", tags=["v1"])
def delete_task_v1(task_id: int, api_key: str = Depends(validate_api_key)):
    if not v1_task_storage.remove_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} does not exist in Version 1.")
    return JSONResponse(status_code=204, content={"message": "Task removed from Version 1."})

# API Router for Version 2
v2_router = APIRouter()

@v2_router.get("/taks/{task_id}", tags=["v2"])
def retrieve_task_v2(task_id: int, api_key: str = Depends(validate_api_key)):
    task = v2_task_storage.find_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found in Version 2.")
    return task

@v2_router.post("/taks", tags=["v2"])
def add_task_v2(task: TaskDetails, api_key: str = Depends(validate_api_key)):
    new_task = v2_task_storage.add_new_task(task)
    return JSONResponse(status_code=201, content={"message": "Task successfully created in Version 2.", "task": new_task})

@v2_router.patch("/taks/{task_id}", tags=["v2"])
def edit_task_v2(task_id: int, task: TaskDetails, api_key: str = Depends(validate_api_key)):
    updated_task = v2_task_storage.modify_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found in Version 2.")
    return JSONResponse(status_code=204, content={"message": "Task updated in Version 2."})

@v2_router.delete("/taks/{task_id}", tags=["v2"])
def delete_task_v2(task_id: int, api_key: str = Depends(validate_api_key)):
    if not v2_task_storage.remove_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found in Version 2.")
    return JSONResponse(status_code=204, content={"message": "Task successfully deleted from Version 2."})

# Register routers with the main app
api_app.include_router(v1_router, prefix="/v1api", tags=["v1"])
api_app.include_router(v2_router, prefix="/v2api", tags=["v2"])

@api_app.get("/", tags=["root"])
def root_message():
    return {"message": "Greetings! Access versioned API endpoints with /v1api/taks/{id} or /v2api/taks/{id}."}

@api_app.get("/health")
def api_health_check():
    return {"status": "Everything is up and running."}
