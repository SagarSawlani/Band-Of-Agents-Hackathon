import sqlite3

conn = sqlite3.connect('C:/Band_Of_Agents_Hackathon/backend/band_of_agents.db')
c = conn.cursor()

c.execute("SELECT instructions FROM agent_instructions WHERE agent_name = 'GitHubAgent'")
row = c.fetchone()
if row:
    prompt = row[0]
    # Check if we need to add the tool
    if "thenvoi_send_message" not in prompt:
        prompt = prompt.replace(
            "projects_reviewer(role, repos)\n", 
            "projects_reviewer(role, repos)\n          thenvoi_send_message(content)\n"
        )
        prompt = prompt.replace(
            "Always use both tools before generating your final output.",
            "Always use both tools before generating your final output.\n\n          ONCE BOTH TOOLS HAVE FINISHED, you MUST call the `thenvoi_send_message` tool to output your final reply to the chat."
        )
        c.execute("UPDATE agent_instructions SET instructions = ? WHERE agent_name = 'GitHubAgent'", (prompt,))
        conn.commit()
        print("Fixed GitHubAgent!")

conn.close()
