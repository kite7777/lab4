from fastapi import FastAPI, HTTPException, APIRouter, Depends, Request
from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Retrieve the API Key from environment
API_KEY = os.getenv("LAB_KEY")

# Task Model for Input Validation
class Task(BaseModel):
    task_title: str
    task_desc: Optional[str] = ""
    is_finished: bool = False

# Utility function to verify API key
def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-KEY") or request.query_params.get("api_key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key

# Generic task database (using dictionary for versioned data)
class TaskDatabase:
    def __init__(self):
        self.db = []

    def get_task_by_id(self, task_id: int):
        return next((task for task in self.db if task["task_id"] == task_id), None)

    def add_task(self, task: Task):
        task_id = len(self.db) + 1
        new_task = task.dict()
        new_task["task_id"] = task_id
        self.db.append(new_task)
        return new_task

    def update_task(self, task_id: int, task_data: Task):
        task_entry = self.get_task_by_id(task_id)
        if task_entry:
            task_entry.update(task_data.dict())
            return task_entry
        return None

    def delete_task(self, task_id: int):
        task = self.get_task_by_id(task_id)
        if task:
            self.db.remove(task)
            return True
        return False

# Initialize two separate task databases for v1 and v2
task_db_v1 = TaskDatabase()
task_db_v2 = TaskDatabase()

# APIV1 Router
apiv1 = APIRouter()

@apiv1.get("/task/{task_id}", tags=["v1"])
def get_task_v1(task_id: int, api_key: str = Depends(verify_api_key)):
    task = task_db_v1.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return task

@apiv1.post("/task", tags=["v1"])
def create_task_v1(task: Task, api_key: str = Depends(verify_api_key)):
    new_task = task_db_v1.add_task(task)
    return JSONResponse(status_code=201, content={"message": "Task successfully created.", "task": new_task})

@apiv1.patch("/task/{task_id}", tags=["v1"])
def update_task_v1(task_id: int, task: Task, api_key: str = Depends(verify_api_key)):
    updated_task = task_db_v1.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return JSONResponse(status_code=204, content={"message": "Task successfully updated."})

@apiv1.delete("/task/{task_id}", tags=["v1"])
def delete_task_v1(task_id: int, api_key: str = Depends(verify_api_key)):
    if not task_db_v1.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return JSONResponse(status_code=204, content={"message": "Task successfully deleted."})

# APIV2 Router
apiv2 = APIRouter()

@apiv2.get("/task/{task_id}", tags=["v2"])
def get_task_v2(task_id: int, api_key: str = Depends(verify_api_key)):
    task = task_db_v2.get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return task

@apiv2.post("/task", tags=["v2"])
def create_task_v2(task: Task, api_key: str = Depends(verify_api_key)):
    new_task = task_db_v2.add_task(task)
    return JSONResponse(status_code=201, content={"message": "Task successfully created.", "task": new_task})

@apiv2.patch("/task/{task_id}", tags=["v2"])
def update_task_v2(task_id: int, task: Task, api_key: str = Depends(verify_api_key)):
    updated_task = task_db_v2.update_task(task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return JSONResponse(status_code=204, content={"message": "Task successfully updated."})

@apiv2.delete("/task/{task_id}", tags=["v2"])
def delete_task_v2(task_id: int, api_key: str = Depends(verify_api_key)):
    if not task_db_v2.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task ID {task_id} not found.")
    return JSONResponse(status_code=204, content={"message": "Task successfully deleted."})

# Add routers to the main app
app.include_router(apiv1, prefix="/apiv1", tags=["v1"])
app.include_router(apiv2, prefix="/apiv2", tags=["v2"])

@app.get("/", tags=["root"])
def read_root():
    return {"message": "Welcome to the API. Access versioned endpoints with /apiv1/task/1 or /apiv2/task/1."}

@app.get("/health")
def health_check():
    return {"status": "API is GOOD"}
