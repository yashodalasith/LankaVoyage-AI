# 🌴 LankaVoyage AI

### Autonomous Multi-Agent Sri Lankan Tourism Itinerary Planner

LankaVoyage AI is an intelligent multi-agent system that generates personalized, optimized travel itineraries for Sri Lanka. It uses local data, AI reasoning, and structured tools to deliver accurate and user-friendly travel plans.

---

## 🚀 Features

- 🤖 Multi-agent architecture (Research, Optimizer, Personalizer)
- 🧠 Uses local LLM via Ollama (llama3 / phi3)
- 📊 SQLite-based tourism knowledge base (no external APIs)
- 🧭 Budget & time optimization
- 🎯 Personalized travel recommendations
- 📄 Generates clean itinerary reports (Markdown / PDF-ready)
- 📈 Observability with logs and state tracking

---

## 🧩 System Architecture

- **Orchestrator:** LangGraph (stateful multi-agent workflow)
- **Agents:**
  - Research Agent → fetches verified tourism data
  - Optimizer Agent → builds efficient itinerary
  - Personalizer Agent → enhances and formats output
- **Tools:**
  - tourism_db_query
  - itinerary_optimizer
  - report_generator

---

## 🔄 Workflow

User Input  
⬇  
Research Agent (data retrieval)  
⬇  
Optimizer Agent (planning & constraints)  
⬇  
Personalizer Agent (final output generation)  
⬇  
📄 Final Itinerary File

---

## 🛠️ Tech Stack

- Python
- LangGraph + LangChain
- Ollama (Local LLM)
- SQLite
- Pydantic
- Pytest

---

## ⚙️ Setup Instructions

```bash
# Clone repo
git clone https://github.com/<your-username>/lanka-voyage-ai-mas.git
cd lanka-voyage-ai-mas

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run Research Agent

```bash
# Pull local model once
ollama pull llama3.2

# Run research agent
python main.py "Plan a 4-day budget trip to Ella from Colombo under 80000 LKR"
```

If Ollama is not running, the research agent still returns verified DB-backed findings using a deterministic fallback summary.

## Run Tests

```bash
pytest -q
```
