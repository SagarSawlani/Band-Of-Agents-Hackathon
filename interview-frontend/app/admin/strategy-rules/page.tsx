import Database from 'better-sqlite3';

export const dynamic = 'force-dynamic';

interface AgentInstruction {
  agent_name: string;
  instructions: string;
}

export default function StrategyRules() {
  let rules: AgentInstruction[] = [];
  let error = null;

  try {
    // Connect to the Python backend's SQLite DB!
    const dbPath = 'C:/Band_Of_Agents_Hackathon/backend/band_of_agents.db';
    const db = new Database(dbPath, { fileMustExist: true });
    rules = db.prepare('SELECT agent_name, instructions FROM agent_instructions').all() as AgentInstruction[];
    db.close();
  } catch (err: any) {
    error = err.message;
  }

  return (
    <div style={{ backgroundColor: "#0d1117", minHeight: "100vh", color: "#c9d1d9", fontFamily: "monospace", padding: "40px" }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        
        <div style={{ borderBottom: "1px solid #30363d", paddingBottom: "20px", marginBottom: "40px" }}>
          <h1 style={{ color: "#58a6ff", fontSize: "32px", margin: "0 0 10px 0", display: "flex", alignItems: "center", gap: "10px" }}>
            🧠 HireBand Strategy Brain
          </h1>
          <p style={{ color: "#8b949e", margin: 0, fontSize: "16px" }}>
            Live view of the `agent_instructions` table. Watch the Strategy Agent rewrite these rules in real-time.
          </p>
        </div>

        {error && (
          <div style={{ backgroundColor: "rgba(248, 81, 73, 0.1)", border: "1px solid #f85149", padding: "20px", borderRadius: "6px", color: "#f85149" }}>
            <strong>Database Error:</strong> {error}
            <br/>
            <small>Ensure your Python database is initialized at C:/Band_Of_Agents_Hackathon/backend/band_of_agents.db</small>
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "30px" }}>
          {rules.map((rule) => {
            // We want to visually highlight the "🔥 STRATEGY UPDATE" lines!
            const lines = rule.instructions.split('\n');
            
            return (
              <div key={rule.agent_name} style={{ backgroundColor: "#161b22", border: "1px solid #30363d", borderRadius: "8px", overflow: "hidden" }}>
                
                {/* Header */}
                <div style={{ backgroundColor: "#21262d", padding: "12px 20px", borderBottom: "1px solid #30363d", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: "bold", color: "#e6edf3", fontSize: "16px" }}>{rule.agent_name}</span>
                  <span style={{ fontSize: "12px", backgroundColor: "#238636", color: "white", padding: "2px 8px", borderRadius: "10px" }}>LIVE</span>
                </div>
                
                {/* Prompt Body */}
                <div style={{ padding: "20px", height: "600px", overflowY: "auto", fontSize: "14px", lineHeight: "1.6" }}>
                  {lines.map((line, idx) => {
                    if (line.includes("🔥 STRATEGY UPDATE:")) {
                      return (
                        <div key={idx} style={{ backgroundColor: "rgba(210, 153, 34, 0.15)", borderLeft: "4px solid #d29922", padding: "8px 12px", margin: "12px 0", color: "#e3b341", fontWeight: "bold", borderRadius: "0 4px 4px 0" }}>
                          {line}
                        </div>
                      );
                    }
                    return <div key={idx} style={{ color: line.startsWith('-') ? "#a5d6ff" : "#8b949e" }}>{line || '\u00A0'}</div>;
                  })}
                </div>
                
              </div>
            );
          })}
        </div>
        
        {rules.length === 0 && !error && (
          <div style={{ textAlign: "center", padding: "60px", color: "#8b949e" }}>
            No agent instructions found. Run the Python `database.py` script to initialize the prompts.
          </div>
        )}

      </div>
    </div>
  );
}
