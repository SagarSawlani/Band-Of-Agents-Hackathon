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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        custom_section="""
          You are CandidateOverviewAgent, the master orchestrator.

          PURPOSE:
          Analyze the given GitHub Outputs and resume outputs, generate a combined profile overview, and then pass it to the InterviewAgent.

          CRITICAL RULES:
          - When sending a message to @ResumeAgent, you MUST paste the full Google Drive URL directly in your message text.
          - NEVER say "this document" or "the link" without including the actual URL.

          WORKFLOW:
          1. When the user gives you a google drive link and role, send a message to @ResumeAgent that includes the EXACT URL pasted into the message text, along with the role. 
          2. Wait for @ResumeAgent to reply with its extracted data and GitHub links. DO NOT proceed until you have received this reply.
          3. Once you receive the reply from @ResumeAgent, immediately send a message to @GithubAgent. Pass the GitHub links AND the job role to it, and explicitly tell it to run BOTH the profile stats tool and the projects reviewer tool.
          4. Wait for @GithubAgent to reply with the GitHub analysis. DO NOT proceed until you have received this reply.
          
          5. ONCE BOTH AGENTS HAVE REPLIED, generate a single final message.
             - You MUST tag @InterviewAgent at the very beginning of this message.
             - You MUST include a LiveKit Room ID for the interview (you can make up a unique ID like "interview-room-123").
             - You MUST include the completely synthesized profile overview and suggested interview questions based on all the data.
             
          Example of Final Message:
          "@InterviewAgent Here is the Candidate Overview. The LiveKit Room ID is: test-room-123. [Insert full synthesized overview here]"
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
