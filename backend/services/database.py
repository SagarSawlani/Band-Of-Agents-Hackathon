import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "band_of_agents.db")

def get_db():
    """Returns a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates the necessary tables for our stateful agent ecosystem."""
    conn = get_db()
    cursor = conn.cursor()

    # 1. Candidates Table (Holds basic info and emails for Outreach)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT,
            location TEXT
        )
    ''')

    # 2. Candidate Snapshots (For Delta Analysis)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidate_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            resume_data TEXT,
            github_data TEXT,
            FOREIGN KEY(candidate_id) REFERENCES candidates(id)
        )
    ''')

    # 3. Agent Instructions (For Strategy Agent Feedback Loop)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_instructions (
            agent_name TEXT PRIMARY KEY,
            instructions TEXT
        )
    ''')
    
    # Insert default instructions if they don't exist
    default_resume_prompt = """
          You are ResumeAgent.

          PURPOSE:
          Analyze the given resume and generate interview questions 

          TOOLS:

          resume_facts_extraction(link)
          resume_evaluator(structured_resume_json, role)
          interview_questions(structured_resume_json, role)

          CRITICAL RULES:
          - When calling resume_facts_extraction, you MUST pass the EXACT Google Drive URL as the 'link' parameter.
          - Do NOT shorten, modify, paraphrase, or extract parts of the URL. Copy it character-for-character.
          - Example: if you receive "https://drive.google.com/file/d/1EmilKT9ZPhAcWecAcVWJEsAEUzdRFWw9/view?usp=drivesdk", pass that EXACT string.

          WORKFLOW:

          1. Call `resume_facts_extraction` and pass the EXACT google drive link.
          2. Wait for the tool result. Once received, pass that JSON output AND the user's job role into `resume_evaluator`.
          3. Wait for the tool result. Once received, pass that JSON output AND the user's job role into `interview_questions`.
          4. Wait for all three tools to finish. 
          
          5. ONCE ALL THREE TOOLS HAVE FINISHED, generate a SINGLE comprehensive reply containing:
             - @CandidateOverviewAgent (You MUST start your message with this tag)
             - A Resume Overview (convert the facts JSON into explainable words)
             - A Role Fit Analysis (convert the evaluator JSON into explainable words)
             - Interview Questions (formatted clearly with categories and answer points)
             - GitHub Links Found (explicitly list all GitHub profile and repository links found in the raw text or JSON)
             
          DO NOT send any messages until all three tools have finished executing.
"""
    
    default_github_prompt = """
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
"""
    
    cursor.execute("INSERT OR IGNORE INTO agent_instructions (agent_name, instructions) VALUES (?, ?)", ("ResumeAgent", default_resume_prompt))
    cursor.execute("INSERT OR IGNORE INTO agent_instructions (agent_name, instructions) VALUES (?, ?)", ("GitHubAgent", default_github_prompt))

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
