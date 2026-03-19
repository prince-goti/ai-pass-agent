from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uuid, json, os
from datetime import datetime
from agent.orchestrator import run_agent

app = FastAPI(title="AI-Pass Agent System")
task_store = {}
log_file = "logs/agent_logs.json"
os.makedirs("logs", exist_ok=True)

def write_log(entry: dict):
    logs = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)

@app.post("/task/run")
async def run_task(
    task: str = Form(...),
    policy: str = Form(""),
    csv_file: UploadFile = File(None)
):
    task_id = str(uuid.uuid4())[:8]
    csv_bytes = await csv_file.read() if csv_file else None

    result = run_agent(task, csv_bytes, policy)
    result["task_id"] = task_id
    result["timestamp"] = datetime.utcnow().isoformat()

    task_store[task_id] = result
    write_log({"task_id": task_id, "task": task, "result": result})

    return JSONResponse(content=result)

@app.get("/task/{task_id}")
def get_task(task_id: str):
    if task_id not in task_store:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return task_store[task_id]

@app.get("/logs")
def get_logs():
    if not os.path.exists(log_file):
        return []
    with open(log_file) as f:
        try:
            return json.load(f)
        except:
            return []
        
        


@app.get("/")
def root():
    return {"message": "AI-Pass Agent System is running", "endpoints": ["/task/run", "/task/{id}", "/logs"]}
