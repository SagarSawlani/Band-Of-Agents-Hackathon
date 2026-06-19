# 🎙️ HireBand: The Autonomous Hiring Ecosystem

[![Band.ai](https://img.shields.io/badge/Powered%20by-Band.ai-blue)](https://band.ai)
[![LangGraph](https://img.shields.io/badge/Framework-LangGraph-green)](https://python.langchain.com/docs/langgraph)
[![AIML](https://img.shields.io/badge/LLM-AIML%20API-orange)](https://aimlapi.com)
[![LiveKit](https://img.shields.io/badge/RealTime-LiveKit-red)](https://livekit.io/)

**Technical recruiting is broken.** Recruiters spend countless hours manually evaluating resumes and GitHub repositories. Worse, live technical interviews are increasingly compromised by candidates secretly reading ChatGPT outputs. 

**HireBand** solves this by replacing static hiring pipelines with a dynamic, self-improving ecosystem of 6 specialized AI agents.

---

## 🌟 The 6-Agent Ecosystem

Our agents communicate autonomously via the Band SDK to handle the entire recruiting pipeline from outbound sourcing to post-interview evaluation.

### Phase 1: Automated Sourcing & Screening
1. 📧 **Outreach Agent (The Sourcer):** Runs semantic vector searches across a database of verified candidates, calculates eligibility matches based on a Job Description, and autonomously fires off real interview invitations via Gmail.
2. 👑 **Candidate Overview Agent (Master Orchestrator):** The central hub. It receives the candidate's Google Drive resume, delegates deep analysis to specialized sub-agents, and performs a "Delta Analysis" to evaluate skill growth for returning candidates.
3. 📄 **Resume Agent (The Fact Checker):** Parses the raw resume PDF to extract hard facts, evaluates the candidate’s fit for the specific role, and generates initial screening questions.
4. 🐙 **GitHub Agent (The Code Reviewer):** Fetches the candidate's GitHub username, analyzes their top public repositories, and evaluates their actual code quality and production experience.

### Phase 2: Live Copiloting & System Auto-Correction
5. 🎧 **Interview Agent (The Copilot):** Uses LiveKit and OpenAI Whisper to transcribe the interview in real-time. It acts as a silent copilot, comparing the live audio to the candidate's resume to feed the human interviewer highly-specific follow-up questions in the chat.
6. 🚨 **Plagiarism Agent (The Anti-Cheat):** Continuously scans the live transcript using a HuggingFace Model. If it catches a robotic, ChatGPT-scripted answer, it instantly intercepts the interview and terminates it.
7. 🧠 **Strategy Agent (The Meta-Learner):** When the interview ends, this agent reads the entire transcript to figure out what technical skills the human interviewer prioritized. It autonomously updates the core database rubrics of the Resume and GitHub agents so they prioritize those exact skills for all future candidates. The system literally learns!

---

## 🛠️ Tech Stack

- **Agent Framework:** Band.ai (thenvoi) SDK & LangGraph
- **LLMs & Compute:** AIML API (GPT-4o, GPT-4o-mini)
- **Anti-Cheat ML:** Local HuggingFace DistilBERT
- **Real-Time Voice:** LiveKit & OpenAI Whisper
- **Database:** SQLite (Universal Talent Network & Dynamic Prompt Storage)
- **Integrations:** PyGithub API, Google Drive API
- **Frontend:** Next.js

---

## 🚀 Setup & Installation

To run HireBand locally, you will need to start both the Python backend (which houses the 6 agents) and the Next.js frontend.

### 1. Backend Setup (Agents)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend/` directory with your API keys:
```env
AIMLAPI_KEY=your_aiml_key
GROQ_API_KEY=your_groq_key
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
# Include your Band.ai Agent IDs and Keys here
```

**Run the Ecosystem:**
```bash
python start_agents.py
```
*This will spin up all 6 agents and connect them to the Band.ai platform.*

### 2. Frontend Setup (Live Interview UI)

```bash
cd interview-frontend
npm install
```

**Environment Variables:**
Create a `.env.local` file in the `interview-frontend/` directory:
```env
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
```

**Run the UI:**
```bash
npm run dev
```

Visit `http://localhost:3000` to access the live interview dashboard!

---

## 🤝 Built for the Band Of Agents Hackathon 2026
