"use client";

import { useState } from "react";

export default function ApplyPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    driveLink: "",
    github: "",
  });
  
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const availableRoles = [
    "AI Engineer",
    "Backend Systems Engineer",
    "Frontend Developer",
    "Full-Stack Developer",
    "Cloud Architect",
    "Quality Assurance",
    "Automation Engineer",
    "Data Analyst"
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const toggleRole = (role: string) => {
    if (selectedRoles.includes(role)) {
      setSelectedRoles(selectedRoles.filter((r) => r !== role));
    } else {
      setSelectedRoles([...selectedRoles, role]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || selectedRoles.length === 0) return;
    
    setIsSubmitting(true);
    
    // Simulate backend processing
    setTimeout(() => {
      setIsSubmitting(false);
      setIsSuccess(true);
    }, 2000);
  };

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#f8f9fa",
        fontFamily: "sans-serif",
        padding: "40px 20px",
      }}
    >
      <div
        style={{
          backgroundColor: "#ffffff",
          padding: "40px",
          borderRadius: "12px",
          boxShadow: "0 10px 25px rgba(0, 0, 0, 0.05)",
          width: "100%",
          maxWidth: "600px",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <h1 style={{ color: "#202124", margin: "0 0 8px 0", fontSize: "28px" }}>Join HireBand</h1>
          <p style={{ color: "#5f6368", margin: 0 }}>Apply for open roles.</p>
        </div>
        
        {isSuccess ? (
          <div style={{ textAlign: "center", padding: "40px 20px", backgroundColor: "#f0fdf4", borderRadius: "8px", border: "1px solid #bbf7d0" }}>
            <h2 style={{ color: "#166534", marginBottom: "16px", fontSize: "22px" }}>Application Submitted Successfully!</h2>
            <p style={{ color: "#15803d", fontSize: "15px", lineHeight: "1.5" }}>
              Our AI agents are currently extracting your Resume and GitHub data and storing your profile in our talent network database.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            {/* Personal Info */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label style={{ fontSize: "14px", fontWeight: "bold", color: "#3c4043" }}>Full Name *</label>
                <input
                  type="text"
                  name="name"
                  required
                  value={formData.name}
                  onChange={handleInputChange}
                  style={{ padding: "12px", borderRadius: "6px", border: "1px solid #dadce0", outline: "none", fontSize: "15px" }}
                />
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                <label style={{ fontSize: "14px", fontWeight: "bold", color: "#3c4043" }}>Email Address *</label>
                <input
                  type="email"
                  name="email"
                  required
                  value={formData.email}
                  onChange={handleInputChange}
                  style={{ padding: "12px", borderRadius: "6px", border: "1px solid #dadce0", outline: "none", fontSize: "15px" }}
                />
              </div>
            </div>

            {/* Links */}
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <label style={{ fontSize: "14px", fontWeight: "bold", color: "#3c4043" }}>Google Drive Resume Link *</label>
              <input
                type="url"
                name="driveLink"
                required
                placeholder="https://drive.google.com/file/d/..."
                value={formData.driveLink}
                onChange={handleInputChange}
                style={{ padding: "12px", borderRadius: "6px", border: "1px solid #dadce0", outline: "none", fontSize: "15px" }}
              />
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              <label style={{ fontSize: "14px", fontWeight: "bold", color: "#3c4043" }}>GitHub Username *</label>
              <input
                type="text"
                name="github"
                required
                placeholder="e.g. sawlanisagar"
                value={formData.github}
                onChange={handleInputChange}
                style={{ padding: "12px", borderRadius: "6px", border: "1px solid #dadce0", outline: "none", fontSize: "15px" }}
              />
            </div>

            {/* Role Multi-Select (Checkboxes) */}
            <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginTop: "8px" }}>
              <label style={{ fontSize: "14px", fontWeight: "bold", color: "#3c4043" }}>Roles Applying For (Select multiple) *</label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                {availableRoles.map((role) => (
                  <label key={role} style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer", color: "#3c4043", fontSize: "15px" }}>
                    <input
                      type="checkbox"
                      checked={selectedRoles.includes(role)}
                      onChange={() => toggleRole(role)}
                      style={{ width: "16px", height: "16px", cursor: "pointer" }}
                    />
                    {role}
                  </label>
                ))}
              </div>
              {selectedRoles.length === 0 && (
                <span style={{ fontSize: "13px", color: "#d93025" }}>Please select at least one role.</span>
              )}
            </div>

            <hr style={{ border: "none", borderTop: "1px solid #e8eaed", margin: "16px 0" }} />

            <button 
              type="submit"
              disabled={isSubmitting || !formData.name || selectedRoles.length === 0}
              style={{
                backgroundColor: isSubmitting || !formData.name || selectedRoles.length === 0 ? "#e8eaed" : "#1a73e8",
                color: isSubmitting || !formData.name || selectedRoles.length === 0 ? "#9aa0a6" : "#ffffff",
                padding: "16px",
                fontSize: "16px",
                fontWeight: "bold",
                border: "none",
                borderRadius: "6px",
                cursor: isSubmitting || !formData.name || selectedRoles.length === 0 ? "default" : "pointer",
                transition: "background-color 0.2s"
              }}
            >
              {isSubmitting ? "Processing Application..." : "Submit Application"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
