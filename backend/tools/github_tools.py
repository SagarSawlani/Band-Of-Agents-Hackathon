from github import Github
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

g = Github(os.getenv("GITHUB_TOKEN"))

def github_profile_stats(username):
  user = g.get_user(username)


  since = datetime.now(timezone.utc) - timedelta(days=180)
  total_commits = 0
  oss_prs = 0
  merged_oss_prs = 0
  oss_repositories = set()
  organizations = set()
  # Language Breakdown
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

  if total_bytes == 0:
      print("No code found.")
  else:
      print(f"Language breakdown for {username}:\n")

      for language, bytes_of_code in sorted(
          language_totals.items(),
          key=lambda x: x[1],
          reverse=True
      ):
          percentage = bytes_of_code / total_bytes * 100

          print(
              f"{language:<20}"
              f"{percentage:>6.2f}% "
          )
  print(f"Commits in the last 6 months: {total_commits}")
   

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

  print(f"OSS Repositories: {len(oss_repositories)}")
  print(f"OSS PRs Opened: {oss_prs}")
  print(f"OSS PRs Merged: {merged_oss_prs}")
  print(f"Acceptance Rate: {acceptance_rate:.2f}%")
  print("Organizations to which the candidate Contributed: ", sorted(organizations))
github_profile_stats("c0mpli")