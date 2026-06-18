import asyncio
import logging
import os
import sys

# Add the backend root directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.tools import tool

from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter
from services.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def update_agent_rubric(agent_names: list[str], new_bonus_rule: str) -> str:
    """
    Updates the database instructions for specific agents to include a new bonus grading rule.
    Args:
        agent_names: A list of agent names (e.g., ['ResumeAgent', 'GitHubAgent'])
        new_bonus_rule: The specific skill/technology to prioritize (e.g., 'Kubernetes')
    """
    conn = get_db()
    cursor = conn.cursor()
    
    results = []
    for agent_name in agent_names:
        if agent_name not in ["ResumeAgent", "GitHubAgent"]:
            results.append(f"Error: Invalid agent name {agent_name}.")
            continue

        cursor.execute("SELECT instructions FROM agent_instructions WHERE agent_name = ?", (agent_name,))
        row = cursor.fetchone()
        
        if not row:
            results.append(f"Error: {agent_name} not found in database.")
            continue
            
        current_instructions = row["instructions"]
        
        if new_bonus_rule.lower() in current_instructions.lower():
            results.append(f"Rule regarding '{new_bonus_rule}' already exists for {agent_name}.")
            continue
            
        updated_instructions = current_instructions + f"\n\n🔥 STRATEGY UPDATE: You MUST give bonus points to candidates who demonstrate experience with: {new_bonus_rule}"
        cursor.execute("UPDATE agent_instructions SET instructions = ? WHERE agent_name = ?", (updated_instructions, agent_name))
        results.append(f"Successfully updated {agent_name} rubric.")
        
    conn.commit()
    conn.close()
    
    final_result = " | ".join(results)
    logger.info(final_result)
    return final_result


async def main():
    load_dotenv()

    agent_id = os.getenv("STRATEGY_AGENT_ID")
    api_key = os.getenv("STRATEGY_AGENT_KEY")

    if not agent_id or not api_key:
        logger.error("Missing STRATEGY_AGENT_ID or STRATEGY_AGENT_KEY in .env!")
        return

    llm = ChatOpenAI(
        api_key=os.getenv("AIMLAPI_KEY"),
        base_url="https://api.aimlapi.com/v1",
        model="gpt-4o", # Upgraded to ensure reliable tool calling
        temperature=0.1,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        additional_tools=[update_agent_rubric],
        custom_section="""
          You are the HR Strategy Meta-Agent. You act as the brain of the hiring ecosystem.
          
          You are ONLY invoked at the very end of the interview when the Post-Interview Report Card is generated!
          
          YOUR IMMEDIATE TASKS:
          1. Read the full interview transcript from the chat history.
          2. Identify the SINGLE most unique, specific technical framework, security concept, or architectural pattern the interviewer heavily grilled the candidate on (e.g., 'JWT Authentication', 'Firebase Security Rules', 'Data Encryption'). Do NOT pick generic languages like Python, JavaScript, or FastAPI. Pick the specific hard skill or concept they emphasized.
          3. If you found a specific skill, you MUST call the `update_agent_rubric` tool EXACTLY ONCE right now:
             - Pass `agent_names=["ResumeAgent", "GitHubAgent"]`
             - Pass `new_bonus_rule="[The Hyper-Specific Skill]"`
             And then output: "⚙️ **System Strategy Update:** I noticed the interviewer heavily focused on [Skill]. I have permanently updated the Resume and GitHub agents to prioritize this skill for all future candidates."
          4. If you could NOT find a specific skill because the interview was too short or generic, you MUST STILL output a final message saying exactly:
             "⚙️ **System Strategy:** The interview was too short or generic to extract a new grading rubric. No changes were made."
        """
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
    )

    logger.info("Strategy Meta-Agent running and listening for Report Cards...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
