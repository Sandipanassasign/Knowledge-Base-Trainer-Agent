# 🧠 DKI Assurance Platform — Agentic AI for Quality Engineering

An end-to-end **Agentic AI Defect Knowledge Intelligence (DKI) Assurance Platform** that transforms a static knowledge base into a dynamic, reasoning "brain" for Quality Engineering teams.

Built with **LangGraph** for orchestration, **Qdrant** for hybrid vector memory, **FastAPI** for the API layer, and a **React** dashboard for visualization.

---

## 🏗️ Architecture

```
React Dashboard (:5173) → FastAPI Backend (:8000) → LangGraph Agent
                                                      ├── Retriever Node → Qdrant (Hybrid Search)
                                                      ├── Pattern Recognition Node → LLM
                                                      ├── Predictive Node → LLM (BDD Scenarios)
                                                      └── Feedback Loop → Qdrant (Self-Learning)
```

## 🎯 Features

| Step | Feature | Description |
|------|---------|-------------|
| 1 | **Hybrid Memory** | Qdrant vector DB with semantic search + metadata filtering |
| 2 | **Agentic Workflow** | LangGraph with Retriever → Pattern Recognition → Predictive nodes |
| 3 | **Self-Learning** | Human-in-the-loop feedback saves corrections as High-Confidence References |
| 4 | **Predictive Guidance** | Predicts risky modules & generates BDD Gherkin test scenarios |
| 5 | **Dashboard** | Risk heatmap, severity charts, AI query panel, feedback UI |

---

## 🚀 Quick Start (Step-by-Step Setup)

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| **Python** | 3.10+ | [python.org](https://python.org) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org) |
| **Docker** | Latest | [docker.com](https://docker.com) |
| **Git** | Latest | [git-scm.com](https://git-scm.com) |

### Step 1: Clone the Repository

```bash
git clone https://github.com/Sandipanassasign/Knowledge-Base-Trainer-Agent.git
cd Knowledge-Base-Trainer-Agent
```

### Step 2: Start Qdrant (Vector Database)

Open a **new terminal** and run:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

> Keep this terminal running. Qdrant will be available at `http://localhost:6333`

### Step 3: Setup the Backend

Open a **new terminal**:

```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate it
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file from the example
cp .env.example .env
```

Now **edit the `.env` file** and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 4: Start the Backend Server

```bash
# Still in the backend/ directory with venv activated
python main.py
```

> Backend starts at `http://localhost:8000`  
> Swagger docs at `http://localhost:8000/docs`

### Step 5: Seed the Knowledge Base

Open a **new terminal**:

```bash
cd backend
source venv/bin/activate   # Activate venv again in this terminal
python seed_data.py
```

> This loads 15 sample defect records into Qdrant.

### Step 6: Setup & Start the Frontend

Open a **new terminal**:

```bash
cd frontend

# Install Node dependencies
npm install

# Start the dev server
npm run dev
```

> Frontend starts at `http://localhost:5173`

### Step 7: Open the Dashboard

Open your browser and go to: **http://localhost:5173**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/query` | Submit a testing problem to the AI agent |
| `POST` | `/api/feedback` | Rate a recommendation (correct/incorrect) |
| `GET`  | `/api/analytics` | Get risk analytics for the dashboard |
| `POST` | `/api/ingest` | Ingest a single defect record |
| `POST` | `/api/seed` | Seed database with sample data |
| `GET`  | `/docs` | Interactive Swagger API documentation |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangGraph (Python) |
| LLM | GPT-4o-mini (configurable) |
| Vector DB | Qdrant (Hybrid Search) |
| Embeddings | all-MiniLM-L6-v2 (384D) |
| API | FastAPI + Uvicorn |
| Frontend | React + Vite |
| Charts | Recharts |
| Icons | Lucide React |

---

## 📁 Project Structure

```
Knowledge-Base-Trainer-Agent/
├── backend/
│   ├── .env.example          # Environment variables template
│   ├── requirements.txt      # Python dependencies
│   ├── config.py             # Configuration loader
│   ├── main.py               # FastAPI application
│   ├── models.py             # Pydantic request/response models
│   ├── qdrant_store.py       # Qdrant client & hybrid search
│   ├── seed_data.py          # Sample defect data seeder
│   ├── agent/
│   │   ├── state.py          # AgentState TypedDict
│   │   ├── nodes.py          # Retriever, Pattern, Predictive nodes
│   │   ├── graph.py          # LangGraph workflow
│   │   └── prompts.py        # LLM prompt templates
│   └── routers/
│       ├── query.py          # /api/query endpoint
│       ├── feedback.py       # /api/feedback endpoint
│       └── analytics.py      # /api/analytics endpoint
├── frontend/
│   ├── index.html
│   ├── package.json
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css          # Design system
│       ├── api/client.js      # API client
│       └── components/
│           ├── Sidebar.jsx
│           ├── Header.jsx
│           ├── QueryPanel.jsx
│           ├── ResultsPanel.jsx
│           ├── FeedbackPanel.jsx
│           └── RiskHeatmap.jsx
└── prompt/
    └── Agent.md               # Original 5-step architecture guide
```

---

## 📝 License

MIT
