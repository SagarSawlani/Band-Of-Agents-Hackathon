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

from tools.github_tools import github_profile_stats, projects_reviewer

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


async def main():
    load_dotenv()

    agent_id = os.getenv("GITHUB_AGENT_ID")
    api_key = os.getenv("GITHUB_AGENT_KEY")

    llm = ChatOpenAI(
        api_key=os.getenv("AIMLAPI_KEY"),
        base_url="https://api.aimlapi.com/v1",
        model="gpt-4o-mini",
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

          You MUST ALWAYS run BOTH the github_profile_stats tool AND the projects_reviewer tool.
          
          If the user provides a GitHub profile link or username (but no specific repositories):
            1. Run github_profile_stats(username)
            2. Run projects_reviewer(role, username=username) 
          
          If the user explicitly provides specific repository links with or without stating they are hyperlinks:
            1. Run github_profile_stats(username)
            2. Run projects_reviewer(role, repos=[repo1, repo2])
            
          Always use both tools before generating your final output.
          
          CRITICAL RULE: You MUST start your final response message by tagging @CandidateOverviewAgent so it knows you have finished. (e.g. "@CandidateOverviewAgent Here is the github analysis...")
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