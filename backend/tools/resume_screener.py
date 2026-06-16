import os
import sys

# Add the backend root directory to Python's path so we can import from `services`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.resume_content_extract import drive_file_content
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from  dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
  api_key=os.getenv("AIMLAPI_KEY"),
  base_url="https://api.aimlapi.com/v1",
  model="deepseek/deepseek-chat",
  temperature=0,
  streaming=False,
)

@tool
def resume_facts_extraction(link):
  """
    Extracts meaningful facts from a resume hosted on Google Drive.
    The 'link' parameter MUST be the exact, full Google Drive URL (e.g. https://drive.google.com/file/d/XXXXX/view?usp=drivesdk).
    Do NOT shorten, paraphrase, or modify the URL in any way. Pass it exactly as received.
  """
  resume_content = drive_file_content(link)

  response = llm.invoke(
    f"""
      You are an expert resume parser.

      Your task is to extract factual information from the resume.

      Rules:
      - Extract only information explicitly stated.
      - Do not infer skills, experience, or seniority.
      - Do not evaluate the candidate.
      - If information is missing, use null.
      - Output valid JSON only.

      Resume:
      {resume_content}

      Output Schema:

      {{
        "candidate_name": "",
        "location": "",
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "portfolio": "",

        "education": [
          {{
            "institution": "",
            "degree": "",
            "field": "",
            "start_date": "",
            "end_date": ""
          }}
        ],

        "experience": [
          {{
            "company": "",
            "title": "",
            "start_date": "",
            "end_date": "",
            "duration_months": 0,
            "responsibilities": [],
            "achievements": []
          }}
        ],

        "projects": [
          {{
            "name": "",
            "description": "",
            "technologies": [],
            "achievements": []
          }}
        ],

        "skills": [],

        "certifications": [],

        "awards": [],

        "publications": [],

        "Github_project_links": []
      }}
    """
  )

  return response.content

@tool
def resume_evaluator(structured_resume_json, role):
  """
    the sructured_resume_json content and the job role is served as an input and it is used to evaluate the qualities of the candidate 
  """
  response = llm.invoke(f"""
    You are a Staff Software Engineer and Hiring Manager.

Your task is to evaluate a candidate against a target role.

Role:
{role}

Candidate Profile:
{structured_resume_json}

Evaluation Criteria:

1. Skill Match
- Which required skills are supported by evidence?
- Which are partially supported?
- Which are missing?

2. Experience Match
- How relevant is the candidate's experience?
- Which prior roles are most relevant?

3. Project Relevance
- Which projects align with the target role?
- Which projects demonstrate required competencies?

4. Seniority Assessment
Evaluate:
- Junior
- Mid-Level
- Senior
- Staff+

Provide evidence.

5. Strength Signals
Look for:
- Ownership
- Leadership
- Promotions
- Technical complexity
- Impact metrics
- Cross-functional work

6. Weak Signals
Look for:
- Buzzword stuffing
- Skill lists without evidence
- Frequent job hopping
- Lack of impact metrics
- Generic project descriptions

7. Evidence Confidence

For every important conclusion:
- High Confidence
- Medium Confidence
- Low Confidence

Output ONLY JSON:

{{
  "overall_match_score": 0,
  "seniority_estimate": "",
  "matched_skills": [],
  "partial_matches": [],
  "missing_skills": [],
  "strengths": [],
  "weaknesses": [],
  "evidence_confidence": "",
  "summary": ""
}}
  """
  )
  return response.content
@tool
def interview_questions(structured_resume_json, role):
  """
    the sructured_resume_json content and the job role is served as an input and it outputs the relevant interview questions 
  """

  response = llm.invoke(f"""
    You are an experienced technical interviewer.

Your goal is to verify whether the candidate genuinely possesses the skills and experience claimed in the resume.

Role:
{role}

Candidate Profile:
{structured_resume_json}

Generate interview questions that validate:

- Architectural understanding
- Design decisions
- Technology choices
- Scalability knowledge
- Failure handling
- Tradeoff reasoning
- Project ownership

DO NOT ask:
- Syntax questions
- Language trivia
- Definitions
- Questions answerable by memorization

Generate questions that force the candidate to explain reasoning.

For every question include:

{{
  "question": "",
  "category": "",
  "target_skill": "",
  "why_it_matters": "",
  "strong_answer_signals": []
}}

Categories:
- Architecture
- Scalability
- Tradeoffs
- Failure Modes
- Project Ownership
- Technology Choice
- Security
- Performance

Output ONLY JSON:

{{
  "questions": []
}}
  """
  )
  return response.content
