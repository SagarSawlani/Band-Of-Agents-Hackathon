import asyncio
import logging
import os
import sys
import smtplib
from email.message import EmailMessage

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

def send_real_email(to_email: str, subject: str, body: str):
    """Helper function to send a real email using Gmail SMTP"""
    sender_email = os.getenv("GMAIL_ADDRESS")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not sender_email or not sender_password:
        logger.error("Missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in .env")
        return False

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

@tool
def find_and_email_eligible_candidates(company_name: str, job_role: str, required_skills: str) -> str:
    """
    Searches the database for candidates matching the required skills, calculates eligibility, 
    and sends them real outreach emails via Gmail.
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch all candidates and their latest snapshot
    cursor.execute('''
        SELECT c.name, c.email, s.resume_data, s.github_data 
        FROM candidates c
        JOIN candidate_snapshots s ON c.id = s.candidate_id
        GROUP BY c.id
        ORDER BY s.timestamp DESC
    ''')
    candidates = cursor.fetchall()
    conn.close()

    emails_sent_log = []
    
    # Keyword-based scoring simulation
    required_keywords = [skill.strip().lower() for skill in required_skills.split(",")]
    
    for row in candidates:
        resume_text = row["resume_data"] or ""
        github_text = row["github_data"] or ""
        candidate_data = (resume_text + " " + github_text).lower()
        
        # Calculate percentage match based on keywords
        matches = sum(1 for keyword in required_keywords if keyword in candidate_data)
        eligibility_pct = int((matches / len(required_keywords)) * 100) if required_keywords else 0
        
        if eligibility_pct >= 50:  # Only email if they are at least 50% eligible
            subject = f"Interview Invitation: {job_role} at {company_name}"
            body = f"""Hi {row['name']},

Based on your verified AI assessments and GitHub trajectory on our platform, you are a {eligibility_pct}% Match for an open position!

🏢 Company: {company_name}
💼 Role: {job_role}
🔑 Required Skills: {required_skills}

We think your background is a fantastic fit. Click below to fast-track your application:
https://app.thenvoi.com/apply

Best regards,
Band.ai Automated Outreach"""

            # SEND THE REAL EMAIL
            success = send_real_email(row['email'], subject, body)
            
            if success:
                emails_sent_log.append(f"✅ Sent real email to {row['name']} at {row['email']} ({eligibility_pct}% Match)")
            else:
                emails_sent_log.append(f"❌ Failed to send email to {row['email']}")

    if not emails_sent_log:
        return "No candidates met the minimum eligibility threshold (50%) for this role."

    return "\n".join(emails_sent_log)


async def main():
    load_dotenv()

    agent_id = os.getenv("OUTREACH_AGENT_ID")
    api_key = os.getenv("OUTREACH_AGENT_KEY")

    if not agent_id or not api_key:
        logger.error("Missing OUTREACH_AGENT_ID or OUTREACH_AGENT_KEY in .env!")
        return

    llm = ChatOpenAI(
        api_key=os.getenv("AIMLAPI_KEY"),
        base_url="https://api.aimlapi.com/v1",
        model="gpt-4o",
        temperature=0.2,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        additional_tools=[find_and_email_eligible_candidates],
        custom_section="""
          You are the Outreach Agent.
          
          PURPOSE:
          When a recruiter provides a Job Description, you search the talent pool database to find top candidates and automatically send them real outreach emails.
          
          WORKFLOW:
          1. The user will provide a Job Description (JD) containing the Company Name, Role, and Required Skills.
          2. Extract the company name, role, and a comma-separated list of required skills.
          3. Call the `find_and_email_eligible_candidates` tool with those extracted parameters.
          4. Output the exact log returned by the tool to prove the outreach was successful.
        """
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
    )

    logger.info("Outreach Agent running...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
