import sqlite3

conn = sqlite3.connect('C:/Band_Of_Agents_Hackathon/backend/band_of_agents.db')
c = conn.cursor()

# 1. Update GitHubAgent
c.execute("SELECT instructions FROM agent_instructions WHERE agent_name = 'GitHubAgent'")
row = c.fetchone()
if row:
    prompt = row[0]
    prompt = prompt.replace("ONCE BOTH TOOLS HAVE FINISHED, generate a SINGLE comprehensive reply containing:", "ONCE BOTH TOOLS HAVE FINISHED, you MUST use the `thenvoi_send_message` tool to output your final reply to the chat containing:")
    # Ensure tool is explicitly mentioned
    if "thenvoi_send_message(content)" not in prompt:
        prompt = prompt.replace("TOOLS:\n          github_profile_stats(username)\n          projects_reviewer(role, repos, username)", "TOOLS:\n          github_profile_stats(username)\n          projects_reviewer(role, repos, username)\n          thenvoi_send_message(content)")
    c.execute("UPDATE agent_instructions SET instructions = ? WHERE agent_name = 'GitHubAgent'", (prompt,))

# 2. Update StrategyAgent
c.execute("SELECT instructions FROM agent_instructions WHERE agent_name = 'StrategyAgent'")
row = c.fetchone()
if row:
    prompt = row[0]
    prompt = prompt.replace("ONCE ALL TOOLS HAVE FINISHED, reply to the chat with", "ONCE ALL TOOLS HAVE FINISHED, you MUST use the `thenvoi_send_message` tool to reply to the chat with")
    if "thenvoi_send_message(content)" not in prompt:
        prompt = prompt.replace("TOOLS:\n          decision_maker(report_card, candidate_overview)", "TOOLS:\n          decision_maker(report_card, candidate_overview)\n          thenvoi_send_message(content)")
    c.execute("UPDATE agent_instructions SET instructions = ? WHERE agent_name = 'StrategyAgent'", (prompt,))

conn.commit()
conn.close()
print("Updated GitHubAgent and StrategyAgent prompts in DB.")
