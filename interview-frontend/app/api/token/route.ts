import { NextRequest, NextResponse } from "next/server";
import { AccessToken } from "livekit-server-sdk";

export async function GET(req: NextRequest) {
  const room = req.nextUrl.searchParams.get("room");
  const name = req.nextUrl.searchParams.get("name");

  if (!room || !name) {
    return NextResponse.json(
      { error: "Missing room or name" },
      { status: 400 }
    );
  }

  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;

  if (!apiKey || !apiSecret) {
    return NextResponse.json(
      { error: "LiveKit credentials not configured" },
      { status: 500 }
    );
  }

  const at = new AccessToken(apiKey, apiSecret, {
    identity: name,
    name: name,
  });

  at.addGrant({
    roomJoin: true,
    room: room,
  });

  const token = await at.toJwt();

  return NextResponse.json({ token });
}
