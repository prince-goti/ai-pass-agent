from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
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
        

@app.get("/chat", response_class=HTMLResponse)
def chat_ui():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>AI-Pass Agent</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        .chat-box { background: white; border-radius: 10px; padding: 20px; min-height: 300px; margin-bottom: 20px; border: 1px solid #ddd; overflow-y: auto; max-height: 400px; }
        .message { margin: 10px 0; padding: 10px; border-radius: 8px; }
        .user { background: #007bff; color: white; text-align: right; }
        .agent { background: #e9ecef; color: #333; }
        .input-area { display: flex; gap: 10px; }
        input[type=text] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
        button:hover { background: #0056b3; }
        .status { color: #888; font-size: 12px; margin-top: 5px; }
        label { font-weight: bold; display: block; margin-top: 10px; margin-bottom: 5px; }
        textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; box-sizing: border-box; }
    </style>
</head>
<body>
    <h1>AI-Pass Agent 🤖</h1>
    <p>Upload a CSV and policy to analyze supplier offers.</p>

    <label>Policy Text:</label>
    <textarea id="policy" rows="2" placeholder="e.g. Always prefer lowest cost. Delivery must be under 10 days.">Always prefer lowest cost. Delivery must be under 10 days.</textarea>

    <label>Upload Supplier CSV:</label>
    <input type="file" id="csvFile" accept=".csv" />

    <div class="chat-box" id="chatBox">
        <div class="message agent">👋 Hi! I am the AI-Pass Agent. Type a task below and I will analyze your suppliers.</div>
    </div>

    <div class="input-area">
        <input type="text" id="taskInput" placeholder="e.g. Analyze these supplier offers and choose the best one" />
        <button onclick="sendTask()">Send</button>
    </div>
    <div class="status" id="status"></div>

    <script>
        async function sendTask() {
            const task = document.getElementById('taskInput').value;
            const policy = document.getElementById('policy').value;
            const csvFile = document.getElementById('csvFile').files[0];

            if (!task) return alert('Please enter a task');

            addMessage(task, 'user');
            document.getElementById('taskInput').value = '';
            document.getElementById('status').innerText = 'Agent is thinking...';

            const formData = new FormData();
            formData.append('task', task);
            formData.append('policy', policy);
            if (csvFile) formData.append('csv_file', csvFile);

            try {
                const response = await fetch('/task/run', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                const msg = `
                    <b>Decision: ${data.decision}</b><br>
                    <b>Confidence:</b> ${data.confidence}<br>
                    <b>Reasons:</b><br> ${data.reasons.join('<br>')}<br>
                    <b>Evidence:</b><br> ${data.evidence.join('<br>')}
                `;
                addMessage(msg, 'agent');
                document.getElementById('status').innerText = `Task ID: ${data.task_id} | Time: ${data.execution_time_seconds}s`;
            } catch (err) {
                addMessage('Error: Could not reach the agent. Please try again.', 'agent');
                document.getElementById('status').innerText = '';
            }
        }

        function addMessage(text, sender) {
            const box = document.getElementById('chatBox');
            const div = document.createElement('div');
            div.className = `message ${sender}`;
            div.innerHTML = text;
            box.appendChild(div);
            box.scrollTop = box.scrollHeight;
        }

        document.getElementById('taskInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendTask();
        });
    </script>
</body>
</html>
"""        


@app.get("/")
def root():
    return {"message": "AI-Pass Agent System is running", "endpoints": ["/task/run", "/task/{id}", "/logs"]}
