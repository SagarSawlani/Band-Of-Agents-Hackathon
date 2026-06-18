import asyncio
import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter

from langchain_core.tools import tool
from services.database import get_db
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def save_and_fetch_candidate_snapshot(candidate_name: str, candidate_email: str, current_resume_data: str, current_github_data: str) -> str:
    """
    Saves the current candidate's data as a snapshot in the Universal Talent Network database.
    If the candidate has applied before, it returns their PREVIOUS snapshot so you can analyze their growth!
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Ensure candidate exists
    cursor.execute("SELECT id FROM candidates WHERE email = ?", (candidate_email,))
    row = cursor.fetchone()
    
    if row:
        candidate_id = row["id"]
        # 2. Fetch the MOST RECENT snapshot (before we insert the new one)
        cursor.execute("SELECT timestamp, resume_data, github_data FROM candidate_snapshots WHERE candidate_id = ? ORDER BY timestamp DESC LIMIT 1", (candidate_id,))
        last_snapshot = cursor.fetchone()
        
        previous_data_str = "No previous snapshot found."
        if last_snapshot:
            previous_data_str = f"🔥 RETURNING CANDIDATE! PREVIOUS SNAPSHOT ({last_snapshot['timestamp']}):\nResume: {last_snapshot['resume_data']}\nGitHub: {last_snapshot['github_data']}"
    else:
        candidate_id = "cand_" + str(uuid.uuid4())[:8]
        cursor.execute("INSERT INTO candidates (id, name, email) VALUES (?, ?, ?)", (candidate_id, candidate_name, candidate_email))
        previous_data_str = "This is a first-time applicant. No previous historical data."
        
    # 3. Insert the new snapshot
    cursor.execute("INSERT INTO candidate_snapshots (candidate_id, resume_data, github_data) VALUES (?, ?, ?)", 
                   (candidate_id, current_resume_data, current_github_data))
    
    conn.commit()
    conn.close()
    
    return previous_data_str

async def main():
    load_dotenv()

    agent_id = os.getenv("CANDIDATE_OVERVEIW_AGENT_ID")
    api_key = os.getenv("CANDIDATE_OVERVEIW_AGENT_KEY")

    llm = ChatOpenAI(
        api_key=os.getenv("AIMLAPI_KEY"),
        base_url="https://api.aimlapi.com/v1",
        model="gpt-4o",
        temperature=0.2,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        additional_tools=[save_and_fetch_candidate_snapshot],
        custom_section="""
          You are CandidateOverviewAgent, the master orchestrator.

          PURPOSE:
          Analyze the given GitHub Outputs and resume outputs, check if the candidate has applied in the past (Delta Analysis), generate a combined profile overview, and then pass it to the InterviewAgent.

          CRITICAL RULES:
          - When sending a message to @ResumeAgent, you MUST paste the full Google Drive URL directly in your message text.
          - NEVER say "this document" or "the link" without including the actual URL.

          WORKFLOW:
          1. When the user gives you a google drive link and role, send a message to @ResumeAgent that includes the EXACT URL pasted into the message text, along with the role. 
          2. Wait for @ResumeAgent to reply with its extracted data and GitHub links. DO NOT proceed until you have received this reply.
          3. Once you receive the reply from @ResumeAgent, immediately send a message to @GithubAgent. Pass the GitHub links AND the job role to it, and explicitly tell it to run BOTH the profile stats tool and the projects reviewer tool.
          4. Wait for @GithubAgent to reply with the GitHub analysis. DO NOT proceed until you have received this reply.
          5. ONCE BOTH AGENTS HAVE REPLIED, you MUST extract the candidate's full Name and Email Address directly from the ResumeAgent's summary. Then, you MUST call the `save_and_fetch_candidate_snapshot` tool. Pass the extracted name, extracted email, and the raw text outputs from the Resume and GitHub agents. 
          6. Wait for the tool result. If it returns a PREVIOUS SNAPSHOT, you MUST perform a "Delta Analysis" (analyze how much the candidate's skills have grown since their last application!).
          
          7. FINALLY, you MUST use the `thenvoi_send_message` tool to output your final message using EXACTLY this markdown template. Do NOT deviate:
          
          @InterviewAgent
          # 📋 Candidate Overview
          [Synthesize the resume and github data into a summary]
          
          # 📈 Growth Delta Report
          [ONLY IF THEY ARE A RETURNING CANDIDATE: Compare their old snapshot to their new snapshot and explicitly detail what new skills or projects they have gained since last time. If they are a new candidate, write "First-time applicant."]
          
          # ❓ Suggested Interview Questions
          [Insert suggested questions]
          
          **LiveKit Room ID:** interview-room-123
        """
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
    )

    logger.info("CandidateOverviewAgent running...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
