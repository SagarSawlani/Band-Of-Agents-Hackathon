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
from services.database import get_db

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

async def main():
    load_dotenv()

    agent_id = os.getenv("RESUME_AGENT_ID")
    api_key = os.getenv("RESUME_AGENT_KEY")

    llm = ChatOpenAI(
        api_key=os.getenv("AIMLAPI_KEY"),
        base_url="https://api.aimlapi.com/v1",
        model="gpt-4o",
        temperature=0.2,
    )

    # Fetch the dynamic prompt from the database!
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT instructions FROM agent_instructions WHERE agent_name = ?", ("ResumeAgent",))
    row = cursor.fetchone()
    dynamic_prompt = row["instructions"] if row else "You are ResumeAgent."
    conn.close()

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        additional_tools=[resume_facts_extraction, resume_evaluator, interview_questions],
        custom_section=dynamic_prompt # <-- Uses the database instead of hardcoded text
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