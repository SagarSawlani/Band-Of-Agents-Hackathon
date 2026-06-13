"use client";

import {
  useParticipants,
} from "@livekit/components-react";

export default function ParticipantsPanel() {
  const participants = useParticipants();

  return (
    <div>
      <h2>Participants</h2>

      {participants.map((participant) => (
        <div
          key={participant.identity}
          style={{
            padding: "8px",
            marginTop: "8px",
            border: "1px solid #ddd",
            borderRadius: "6px",
          }}
        >
          🟢 {participant.identity}
        </div>
      ))}
    </div>
  );
}