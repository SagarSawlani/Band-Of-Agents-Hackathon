import os, sys, asyncio
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from dotenv import load_dotenv
load_dotenv('backend/.env')

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from thenvoi.adapters import LangGraphAdapter

from tools.resume_screener import resume_facts_extraction, resume_evaluator, interview_questions

async def main():
    llm = ChatOpenAI(
        api_key=os.getenv('AIMLAPI_KEY'),
        base_url='https://api.aimlapi.com/v1',
        model='gpt-4o',
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

          WORKFLOW:

          1. Call `resume_facts_extraction` and pass the EXACT google drive link.
          2. Wait for the tool result. Once received, pass that JSON output AND the user's job role into `resume_evaluator`.
          3. Wait for the tool result. Once received, pass that JSON output AND the user's job role into `interview_questions`.
          4. Wait for all three tools to finish. 
          
          5. ONCE ALL THREE TOOLS HAVE FINISHED, generate a SINGLE comprehensive reply containing:
             - A Resume Overview
             - A Role Fit Analysis
             - Interview Questions
             - GitHub Username
             
          Include the tag @CandidateOverviewAgent exactly ONCE at the very beginning of your message.
        """
    )
    
    config = {"configurable": {"thread_id": "test_thread_1"}}
    
    # We will simulate the LangGraph run directly using the adapter's runnable
    runnable = adapter.runnable
    
    async for event in runnable.astream_events(
        {"messages": [("user", "https://drive.google.com/file/d/1YikrzRB5tqzzgiwJ04Y9HFDFbXsbPs10/view?usp=drive_link \n Role: Backend Streaming Engineer")]},
        config=config,
        version="v1"
    ):
        kind = event["event"]
        if kind == "on_chat_model_stream":
            print(event["data"]["chunk"].content, end="", flush=True)
        elif kind == "on_tool_start":
            print(f"\n[TOOL START] {event['name']} with args: {event['data'].get('input')}\n")
        elif kind == "on_tool_end":
            print(f"\n[TOOL END] {event['name']}\n")

if __name__ == "__main__":
    asyncio.run(main())
