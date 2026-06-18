"use client";

import { useParams } from "next/navigation";
import { useState } from "react";

import {
  LiveKitRoom,
  VideoConference,
} from "@livekit/components-react";

import "@livekit/components-styles";

export default function InterviewRoom() {
  const params = useParams();
  const roomId = params.roomId as string;

  const [token, setToken] = useState("");
  const [connected, setConnected] = useState(false);
  const [username, setUsername] = useState("");

  async function joinRoom(e: React.FormEvent) {
    e.preventDefault();
    if (!username.trim()) return;

    const roomName = roomId;

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    const res = await fetch(
      `${backendUrl}/token?room=${roomName}&name=${username}`
    );

    const data = await res.json();

    setToken(data.token);
    setConnected(true);
  }

  if (!connected) {
    return (
      <div
        style={{
          display: "flex",
          height: "100vh",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#202124",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            backgroundColor: "#ffffff",
            padding: "40px",
            borderRadius: "8px",
            boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
            textAlign: "center",
            width: "100%",
            maxWidth: "400px",
          }}
        >
          <h1 style={{ color: "#202124", marginBottom: "8px", fontSize: "24px" }}>Ready to join?</h1>
          <p style={{ color: "#5f6368", marginBottom: "24px" }}>Please enter your name to enter the interview.</p>
          
          <form onSubmit={joinRoom} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <input
              type="text"
              placeholder="Your Name"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                padding: "12px",
                fontSize: "16px",
                borderRadius: "4px",
                border: "1px solid #dadce0",
                outline: "none",
                color: "#202124",
              }}
              autoFocus
            />
            <button 
              type="submit"
              disabled={!username.trim()}
              style={{
                backgroundColor: username.trim() ? "#1a73e8" : "#e8eaed",
                color: username.trim() ? "#ffffff" : "#9aa0a6",
                padding: "12px",
                fontSize: "16px",
                fontWeight: "bold",
                border: "none",
                borderRadius: "4px",
                cursor: username.trim() ? "pointer" : "default",
                transition: "background-color 0.2s"
              }}
            >
              Join Interview
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div style={{ height: "100vh", backgroundColor: "#202124" }}>
      <LiveKitRoom
        token={token}
        serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL}
        connect={true}
        video={true}
        audio={true}
        data-lk-theme="default"
        style={{ height: "100%" }}
      >
        <VideoConference />
      </LiveKitRoom>
    </div>
  );
}