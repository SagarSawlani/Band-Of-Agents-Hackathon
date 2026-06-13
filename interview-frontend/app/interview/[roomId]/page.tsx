"use client";

import { useParams } from "next/navigation";
import { useState } from "react";

import {
  LiveKitRoom,
  VideoConference,
} from "@livekit/components-react";

import "@livekit/components-styles";

import ParticipantsPanel from "../../components/ParticipantsPanel";

export default function InterviewRoom() {
  const params = useParams();
  const roomId = params.roomId as string;

  const [token, setToken] = useState("");
  const [connected, setConnected] = useState(false);

  async function joinRoom() {
    const username = prompt("Enter your name") || "Guest";

    const roomName = roomId;

    const res = await fetch(
      `http://localhost:8000/token?room=${roomName}&name=${username}`
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
        }}
      >
        <button onClick={joinRoom}>
          Join Interview
        </button>
      </div>
    );
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={process.env.NEXT_PUBLIC_LIVEKIT_URL}
      connect={true}
      video={true}
      audio={true}
      style={{ height: "100vh" }}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "250px 1fr 350px",
          height: "100%",
        }}
      >
        {/* LEFT PANEL */}
        <div
          style={{
            borderRight: "1px solid #ddd",
            padding: "16px",
            overflowY: "auto",
          }}
        >
          <ParticipantsPanel />
        </div>

        {/* CENTER PANEL */}
        <div style={{ height: "100%" }}>
          <VideoConference />
        </div>

        {/* RIGHT PANEL */}
        <div
          style={{
            borderLeft: "1px solid #ddd",
            padding: "16px",
            overflowY: "auto",
          }}
        >
          <h2>Live Transcript</h2>

          <div
            style={{
              minHeight: "200px",
              border: "1px solid #ddd",
              padding: "12px",
              marginBottom: "20px",
            }}
          >
            Waiting for transcription...
          </div>

          <h2>AI Suggestions</h2>

          <div
            style={{
              border: "1px solid #ddd",
              padding: "12px",
            }}
          >
            Waiting for candidate response...
          </div>
        </div>
      </div>
    </LiveKitRoom>
  );
}