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

from tools.github_tools import github_profile_stats, projects_reviewer

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


async def main():
    load_dotenv()

    agent_id = os.getenv("GITHUB_AGENT_ID")
    api_key = os.getenv("GITHUB_AGENT_KEY")

    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        temperature=0.2,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        additional_tools=[github_profile_stats, projects_reviewer],
        custom_section="""
          You are GithubAgent.

          PURPOSE:
          To fetch github profile statistics and profile fit of the candidate for the job role according to the code written by the user

          TOOLS:

          github_profile_stats(username)
          projects_reviewer(role, repos)

          WORKFLOW:

          When a user:
            - Gives the GitHub username / GitHib profile link use the github_profile_stats tool
            - Gives the GitHub repository Link / repository path use the projects_reviewer tool
            - Gives both, use both the tools

          Always use the tool/tools.
        """,
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
    )

    logger.info("GithubAgent running...")

    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())