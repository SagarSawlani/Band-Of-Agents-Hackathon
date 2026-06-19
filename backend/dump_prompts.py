import sqlite3
import io

with io.open('prompts_dump.txt', 'w', encoding='utf-8') as f:
    conn = sqlite3.connect('C:/Band_Of_Agents_Hackathon/backend/band_of_agents.db')
    c = conn.cursor()
    c.execute("SELECT agent_name, instructions FROM agent_instructions WHERE agent_name IN ('GitHubAgent', 'ResumeAgent')")
    rows = c.fetchall()
    f.write('\n' + '='*50 + '\n')
    for row in rows:
        f.write(f'[{row[0]} PROMPT]:\n{row[1]}\n' + '='*50 + '\n')
    conn.close()
