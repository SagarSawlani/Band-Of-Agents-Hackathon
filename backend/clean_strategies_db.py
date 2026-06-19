import sqlite3
import re

conn = sqlite3.connect('C:/Band_Of_Agents_Hackathon/backend/band_of_agents.db')
c = conn.cursor()

def clean_prompt(prompt):
    # Remove all lines containing "🔥 STRATEGY UPDATE:"
    lines = prompt.split('\n')
    cleaned_lines = [line for line in lines if "STRATEGY UPDATE:" not in line]
    cleaned_prompt = '\n'.join(cleaned_lines).strip()
    
    # Append the requested strategy
    strategy = "\n\n🔥 STRATEGY UPDATE: You MUST give bonus points to candidates who demonstrate experience with: large-scale datasets and real-time systems"
    return cleaned_prompt + strategy

for agent in ['GitHubAgent', 'ResumeAgent']:
    c.execute("SELECT instructions FROM agent_instructions WHERE agent_name = ?", (agent,))
    row = c.fetchone()
    if row:
        new_prompt = clean_prompt(row[0])
        c.execute("UPDATE agent_instructions SET instructions = ? WHERE agent_name = ?", (new_prompt, agent))

conn.commit()
conn.close()
print("Cleaned up strategies in DB!")
