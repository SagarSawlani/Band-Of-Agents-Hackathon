import asyncio
import logging
import os
import sys

# Add the backend root directory to Python's path so we can import from `tools`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from langchain_groq import ChatGroq

from langgraph.checkpoint.memory import InMemorySaver

from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter

from tools.create_meet import create_meet

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


async def main():
    load_dotenv()

    agent_id = os.getenv("MEETING_AGENT_ID")
    api_key = os.getenv("MEETING_AGENT_KEY")

    llm = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0.2,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        additional_tools=[create_meet],
        custom_section="""
          You are MeetingAgent.

          PURPOSE:
          Create interview meetings and manage interview lifecycle.

          TOOLS:

          create_meet()

          WORKFLOW:

          When a user asks to:

          - create interview
          - create meeting
          - start interview
          - schedule interview

          Call create_meet.

          After receiving the tool result:

          Reply with:

          Interview Created

          Room ID: <room_id>

          Join Link:
          <join_link>

          Do not invent meeting links.

          Always use the tool.
        """,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
    )

    logger.info("MeetingAgent running...")

    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())