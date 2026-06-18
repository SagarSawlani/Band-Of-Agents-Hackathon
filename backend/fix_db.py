import sqlite3

conn = sqlite3.connect('C:/Band_Of_Agents_Hackathon/backend/band_of_agents.db')
c = conn.cursor()

c.execute("UPDATE agent_instructions SET instructions = REPLACE(instructions, '- @CandidateOverviewAgent (You MUST start your message with this tag)', 'Include the tag @CandidateOverviewAgent exactly ONCE at the very beginning of your message.') WHERE agent_name = 'ResumeAgent'")

c.execute("UPDATE agent_instructions SET instructions = REPLACE(instructions, 'CRITICAL RULE: You MUST start your final response message by tagging @CandidateOverviewAgent', 'CRITICAL RULE: Include the tag @CandidateOverviewAgent exactly ONCE at the very beginning of your final response message') WHERE agent_name = 'GitHubAgent'")

conn.commit()
conn.close()
print('Database tags fixed!')
