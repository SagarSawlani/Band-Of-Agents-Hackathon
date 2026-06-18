import subprocess
import sys
import time
import os

# Ensure database is initialized before agents start
print("Initializing database...")
subprocess.run([sys.executable, "services/database.py"], check=True)

agents = [
    "agents/candidate_overview_agent.py",
    "agents/github_agent.py",
    "agents/interview_agent.py",
    "agents/outreach_agent.py",
    "agents/plagarism_agent.py",
    "agents/resume_agent.py",
    "agents/strategy_agent.py"
]

processes = []

print("Starting all Band.ai Agents...")

# Launch all agents in parallel
for agent in agents:
    if os.path.exists(agent):
        print(f"Starting {agent}...")
        p = subprocess.Popen([sys.executable, agent])
        processes.append((agent, p))
    else:
        print(f"Warning: Could not find {agent}")

try:
    # Keep the main script running
    while True:
        time.sleep(1)
        # Check if any agent crashed
        for agent, p in list(processes):
            if p.poll() is not None:
                print(f"CRITICAL: {agent} crashed with exit code {p.returncode}. Restarting...")
                new_p = subprocess.Popen([sys.executable, agent])
                processes.remove((agent, p))
                processes.append((agent, new_p))
except KeyboardInterrupt:
    print("Shutting down all agents...")
    for agent, p in processes:
        p.terminate()
    sys.exit(0)
