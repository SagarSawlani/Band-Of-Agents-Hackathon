"use client";

import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  function createRoom() {
    const roomId =
      crypto.randomUUID();

    router.push(
      `/interview/${roomId}`
    );
  }

  return (
    <div
      style={{
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <button onClick={createRoom}>
        Create Interview
      </button>
    </div>
  );
}