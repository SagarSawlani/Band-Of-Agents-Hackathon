import asyncio
import logging
import os
import sys

# Add the backend root directory to Python's path so we can import from `tools`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

from langgraph.checkpoint.memory import InMemorySaver

from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter

from tools.resume_screener import resume_facts_extraction, resume_evaluator, interview_questions

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

async def main():
    load_dotenv()

    agent_id = os.getenv("RESUME_AGENT_ID")
    api_key = os.getenv("RESUME_AGENT_KEY")

    llm = ChatOpenAI(
        api_key=os.getenv("AIMLAPI_KEY"),
        base_url="https://api.aimlapi.com/v1",
        model="gpt-4o-mini",
        temperature=0.2,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        additional_tools=[resume_facts_extraction, resume_evaluator, interview_questions],
        custom_section="""
          You are ResumeAgent.

          PURPOSE:
          Analyze the given resume and generate interview questions 

          TOOLS:

          resume_facts_extraction(link)
          resume_evaluator(structured_resume_json, role)
          interview_questions(structured_resume_json, role)

          CRITICAL RULES:
          - When calling resume_facts_extraction, you MUST pass the EXACT Google Drive URL as the 'link' parameter.
          - Do NOT shorten, modify, paraphrase, or extract parts of the URL. Copy it character-for-character.
          - Example: if you receive "https://drive.google.com/file/d/1EmilKT9ZPhAcWecAcVWJEsAEUzdRFWw9/view?usp=drivesdk", pass that EXACT string.

          WORKFLOW:

          1. Call `resume_facts_extraction` and pass the EXACT google drive link.
          2. Wait for the tool result. Once received, pass that JSON output AND the user's job role into `resume_evaluator`.
          3. Wait for the tool result. Once received, pass that JSON output AND the user's job role into `interview_questions`.
          4. Wait for all three tools to finish. 
          
          5. ONCE ALL THREE TOOLS HAVE FINISHED, generate a SINGLE comprehensive reply containing:
             - @CandidateOverviewAgent (You MUST start your message with this tag)
             - A Resume Overview (convert the facts JSON into explainable words)
             - A Role Fit Analysis (convert the evaluator JSON into explainable words)
             - Interview Questions (formatted clearly with categories and answer points)
             - GitHub Links Found (explicitly list all GitHub profile and repository links found in the raw text or JSON)
             
          DO NOT send any messages until all three tools have finished executing.
        """
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
    )

    logger.info("ResumeAgent running...")

    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())