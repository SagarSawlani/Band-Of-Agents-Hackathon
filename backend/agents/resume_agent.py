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

from tools.resume_screener import resume_facts_extraction, resume_evaluator, interview_questions

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

async def main():
    load_dotenv()

    agent_id = os.getenv("RESUME_AGENT_ID")
    api_key = os.getenv("RESUME_AGENT_KEY")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
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

          resume_facts_extraction()
          resume_evaluator()
          interview_questions()

          WORKFLOW:

          When resume google drive link:

          Call resume_facts_extraction and pass the link as a parameter.

          After receiving the tool result:

          reply with a resume overview (convert JSON to explainable words), if you find something which is non-useful, discard it

          Now take the JSON Output recieved from resume_facts_extraction tool and pass it into resume_evaluator along with the job role given by the user.

          After receiving the tool result:
          reply with a Role Fit Analysis (convert JSON to explainable words), if you find something which is non-useful, discard it

          Now take the JSON Output recieved from resume_facts_extraction tool and pass it into interview_questions tool along with the job role given by the user.
          After receiving the tool result:
          reply with the interview questions which came into the output, the category on the next line and the answer points on the next, between each set of questions keep a one line gap to ensure readability
          Always use the tool.
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