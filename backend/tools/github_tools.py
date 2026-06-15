from github import Github
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import TypedDict
import os

load_dotenv()

llm = ChatGroq(
  model="meta-llama/llama-4-scout-17b-16e-instruct",
  temperature=0,
  max_tokens=None,
  timeout=None,
  max_retries=2,
)

def creation_date(user):
  created_at = user.created_at
  return f"Account Created: {created_at}"
     
def commits_data(user):
  since = datetime.now(timezone.utc) - timedelta(days=180)
  total_commits = 0

  language_totals = defaultdict(int)

  for repo in user.get_repos():
    if repo.fork:  
        continue

    languages = repo.get_languages()

    for language, bytes_of_code in languages.items():
        if not isinstance(bytes_of_code, int):
            continue
        language_totals[language] += bytes_of_code


    commits = repo.get_commits(author=user.login, since=since)
    total_commits += commits.totalCount

  total_bytes = sum(language_totals.values())

  result = ""
  if total_bytes == 0:
    result += "No code found.\n"
  else:
    result += "Language breakdown:\n"

    for language, bytes_of_code in sorted(
        language_totals.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        percentage = bytes_of_code / total_bytes * 100
        result += f"{language:<20}{percentage:>6.2f}%\n"

  result += f"Commits in the last 6 months: {total_commits}"
  return result

def open_source_data(username):
  oss_prs = 0
  merged_oss_prs = 0
  oss_repositories = set()
  organizations = set()

  # Search all PRs authored by the user
  for issue in g.search_issues(
      query=f"type:pr author:{username}"
  ):
      try:
          repo = issue.repository

          # Skip own repositories
          if repo.owner.login.lower() == username.lower():
              continue

          # Skip private repositories
          if repo.private:
              continue
          if repo.owner.type == "Organization":
            organizations.add(repo.owner.login)
          
          oss_prs += 1
          oss_repositories.add(repo.full_name)

          # Get actual PR object
          pr = repo.get_pull(issue.number)

          if pr.merged:
              merged_oss_prs += 1

      except Exception as e:
          print(f"Error processing PR #{issue.number}: {e}")

  acceptance_rate = (
      merged_oss_prs / oss_prs * 100
      if oss_prs
      else 0
  )

  issues_opened = g.search_issues(
    query=f"type:issue author:{username}"
  )

  open_source_info = (
    f"OSS Repositories: {len(oss_repositories)}\n"
    f"OSS PRs Opened: {oss_prs}\n"
    f"OSS PRs Merged: {merged_oss_prs}\n"
    f"Acceptance Rate: {acceptance_rate:.2f}%\n"
    f"Organizations Contributed To: {sorted(organizations)}\n"
    f"Issues opened: {issues_opened.totalCount}"
  )

  return open_source_info

def extract_code(repo_name, file_path):
  repo = g.get_repo(repo_name)
  file = repo.get_contents(file_path)
  if isinstance(file, list):
    return ""
  return file.decoded_content.decode(
        "utf-8",
        errors="ignore"
    )

def relevant_files_extract(role, repo_name):
  
  repo = g.get_repo(repo_name)

  tree = repo.get_git_tree(
    repo.default_branch,
    recursive=True
  )

  paths = [item.path for item in tree.tree]
  paths_str = "\n".join(paths)

  prompt = f"""You are a code reviewer. Given a repository file tree and a job role, select ONLY the files that contain source code directly relevant to evaluating a candidate for that role.

Job Role: {role}

Repository file tree:
{paths_str}

Rules:
- Only include source code files (.py, .js, .ts, .java, .cpp, .go, .rs, .jsx, .tsx, etc.)
- Exclude configs, lock files, READMEs, images, migration files, and boilerplate
- For the role "{role}", focus on files that demonstrate skills core to that role
- Return at most 10 most relevant file paths
- Output one file path per line, exactly as shown in the tree, nothing else"""

  response = llm.invoke(prompt)

  relevant_files = [
    line.strip() for line in response.content.strip().splitlines()
    if line.strip() and line.strip() in paths
  ]

  return relevant_files

def code_reviewer(role, repo):
  code = ""
  relevant_files = relevant_files_extract(role, repo)

  for file in relevant_files:
    code += file + ":\n" + extract_code(repo, file)

  prompt = f"""You are an experienced Staff Software Engineer and technical interviewer.

Your task is to evaluate a code sample against a target job role.

Role:
{role}

Code:
{code}

Evaluate the code across the following dimensions:

1. Role Relevance

* How relevant is this code to the target role?
* Does it demonstrate skills expected from someone in that role?
* Which role-specific competencies are present?
* Which expected competencies are missing?

2. Code Quality
   Rate from 0-100:

* Readability
* Maintainability
* Modularity
* Error Handling
* Testing Awareness
* Documentation Quality
* Security Awareness
* Performance Awareness

3. Engineering Maturity
   Assess:

* Evidence of planning and design
* Separation of concerns
* Appropriate abstractions
* Scalability considerations
* Production readiness

4. Authenticity Signals
   Look for evidence that the author understands the code they wrote.

Positive signals:

* Consistent architectural decisions
* Thoughtful naming
* Non-trivial business logic
* Appropriate tradeoffs
* Domain-specific reasoning
* Error handling decisions
* Testing considerations

Negative signals:

* Generated boilerplate with little customization
* Inconsistent patterns
* Dead code
* Unused abstractions
* Excessive complexity without purpose
* Generic comments
* Copy-paste structures
* Contradictory implementation decisions

5. AI-Assisted / "Vibe-Coded" Assessment

Estimate:

* Likelihood code was substantially AI-assisted (0-100)
* Likelihood author fully understands the implementation (0-100)

Important:
Do NOT assume AI assistance is bad.
Modern professional engineers frequently use AI tools.

Instead evaluate:

* Whether the implementation appears intentional.
* Whether design decisions appear understood.
* Whether the code looks reviewed and refined.

6. Seniority Signals

Estimate the demonstrated level:

* Beginner
* Junior
* Mid-Level
* Senior
* Staff+

Provide evidence.

7. Interview Questions for Conceptual Validation

Generate interview questions that verify conceptual understanding of the implementation.

IMPORTANT:
- Do NOT ask syntax questions.
- Do NOT ask language trivia.
- Do NOT ask questions that can be answered by reading the code aloud.

Instead focus on:
- Architectural decisions
- Library/framework choices
- Tradeoffs
- Scalability
- Reliability
- Security
- Performance
- Alternative approaches
- Design reasoning

Questions should help determine whether the candidate genuinely understands the implementation.

For each question provide a JSON object with: question, category, why_it_matters, strong_signal.

Generate 4-5 questions.

Output ONLY valid JSON:
""" + """
{
"role_relevance_score": 0,
"role_relevance_reasoning": "",
"quality_scores": {
  "readability": 0,
  "maintainability": 0,
  "modularity": 0,
  "error_handling": 0,
  "testing_awareness": 0,
  "documentation": 0,
  "security_awareness": 0,
  "performance_awareness": 0
},
"engineering_maturity_score": 0,
"vibe_coded_likelihood": 0,
"author_understanding_likelihood": 0,
"seniority_estimate": "",
"strengths": [],
"weaknesses": [],
"role_relevant_skills": [],
"missing_role_skills": [],
"interview_questions": [
  {
    "question": "",
    "category": "",
    "why_it_matters": "",
    "strong_signal": ""
  }
],
"summary": ""
}
"""

  response = llm.invoke(prompt)

  return response.content

g = Github(os.getenv("GITHUB_TOKEN"))

@tool
def github_profile_stats(username):
  """
    For the given Github Profile Username, this tool fetches the profile statistics
  """
  user = g.get_user(username)

  profile_stats = creation_date(user) + "\n" + commits_data(user) + "\n" + open_source_data(username)
  return profile_stats

@tool
def projects_reviewer(role, repos):
  """
    For the given role and github repositories, this tool reviews the code in each repository.
    repos must be a list of full repository paths in 'owner/repo' format, e.g. ['SagarSawlani/Band-Of-Agents-Hackathon']
  """
  projects_review = ""
  for repo in repos:
    projects_review += code_reviewer(role, repo)

  response = llm.invoke(
    f"""
      A review of all projects: {projects_review}. Make a combined Profile Review. follow the same format
  """) 

  return response.content