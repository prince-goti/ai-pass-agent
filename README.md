# AI-Pass Agent System

## Live URL
https://ai-pass-agent-v6oc.onrender.com/docs

## Architecture
User → POST /task/run → Agent Orchestrator → [Data Tool + RAG Tool + Decision Tool] → Structured JSON Output

## Agent Pipeline
1. Intake - receives task, CSV, and policy text
2. Plan - LLM generates execution plan (Groq llama3 with mock fallback)
3. Execute - runs 3 tools in sequence
4. Evaluate - scores confidence
5. Deliver - returns structured JSON result

## Tools
- **Data Tool** - parses CSV using Pandas, returns structured metrics
- **RAG Tool** - chunks policy text, stores in ChromaDB, retrieves relevant context
- **Decision Tool** - rule-based PASS/FAIL/NEEDS_INFO with reasons and evidence

## Model Integration
- Primary: Groq API (llama3-8b-8192)
- Fallback: mock plan if API fails or key not set

## API Endpoints
- POST /task/run - run the agent
- GET /task/{id} - retrieve result by task ID
- GET /logs - view all execution logs

## Real vs Mocked
- Real: CSV parsing, RAG retrieval, decision logic, API layer, JSON logging
- Simplified: ChromaDB default embeddings (not fine-tuned)

## What I Would Improve
- Add retry logic on LLM calls
- Add proper vector embeddings
- Add Docker setup
- Add n8n integration for workflow orchestration
