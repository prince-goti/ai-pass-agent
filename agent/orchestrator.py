import time
import json
import os
from groq import Groq
from agent.tools.data_tool import run_data_tool
from agent.tools.rag_tool import load_policy, retrieve_context
from agent.tools.decision_tool import run_decision_tool

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def run_agent(task_input: str, csv_bytes: bytes = None, policy_text: str = "") -> dict:
    steps = []
    start = time.time()

   
    steps.append({"step": "intake", "input": task_input})


    try:
        plan_response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are an AI agent planner. Given a task, return a short bullet-point plan (max 4 steps)."},
                {"role": "user", "content": task_input}
            ]
        )
        plan = plan_response.choices[0].message.content
        model_used = "llama3-8b-8192 (Groq)"
    except Exception as e:
        plan = "Fallback: analyze data → retrieve policy → make decision → return result"
        model_used = "mock_fallback"

    steps.append({"step": "plan", "plan": plan, "model": model_used})


    tool_outputs = {}

  
    if csv_bytes:
        data_result = run_data_tool(csv_bytes)
        tool_outputs["data_tool"] = data_result
        steps.append({"step": "execute", "tool": "data_tool", "status": data_result["status"]})
    else:
        tool_outputs["data_tool"] = {"status": "skipped", "metrics": {}}
        steps.append({"step": "execute", "tool": "data_tool", "status": "skipped"})

    if policy_text:
        load_policy(policy_text)
        context = retrieve_context(task_input)
        tool_outputs["rag_tool"] = {"context": context}
        steps.append({"step": "execute", "tool": "rag_tool", "chunks_retrieved": len(context)})
    else:
        context = "No policy provided."
        steps.append({"step": "execute", "tool": "rag_tool", "status": "skipped"})

    decision_result = run_decision_tool(tool_outputs["data_tool"], context)
    tool_outputs["decision_tool"] = decision_result
    steps.append({"step": "execute", "tool": "decision_tool", "decision": decision_result["decision"]})

    steps.append({"step": "evaluate", "confidence": decision_result["confidence"]})


    execution_time = round(time.time() - start, 2)
    output = {
        "decision": decision_result["decision"],
        "reasons": decision_result["reasons"],
        "evidence": decision_result["evidence"],
        "confidence": decision_result["confidence"],
        "steps": steps,
        "model_used": model_used,
        "execution_time_seconds": execution_time
    }

    steps.append({"step": "deliver", "execution_time": execution_time})
    return output