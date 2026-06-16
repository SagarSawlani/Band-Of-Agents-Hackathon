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

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

async def main():
    load_dotenv()

    agent_id = os.getenv("CANDIDATE_OVERVEIW_AGENT_ID")
    api_key = os.getenv("CANDIDATE_OVERVEIW_AGENT_KEY")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        custom_section="""
          You are CandidateOverviewAgent.

          PURPOSE:
          Analyze the given GitHub Outputs and resume outputs and generate a combined profile overview and suggest interview questions 

          AGENTS:

          @GithubAgent
          @ResumeAgent

          WORKFLOW:
          1. When the user gives you the google drive link, tag the ResumeAAgent (using @ResumeAgent) and tell it to use the google drive link and perform its actions and extract all the GitHub links mentioned in the resume.
          2. The ResumeAgent will produce 4 outputs, wait for it till it doesn't extract the Github Links
          3. After it extracts the Github Links, take those links and tag the GithubAgent (using @GithubAgent) and tell it to perform its action
          4. Wait till it doesnt give 2 outputs (Profile Stats and Projects Overview)
          5. After you get the 2, take the output of ResumeAgent & GithubAgent and make a combined overview for the Interviewer
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