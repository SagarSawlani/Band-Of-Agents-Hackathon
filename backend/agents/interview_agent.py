import sys
import os
import logging
import asyncio
import httpx
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from livekit import api, rtc
from stt import transcribe_audio_chunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- GLOBAL STATE FOR THE BACKGROUND AUDIO LOOP ---
transcript_buffer = []
is_listening = False
# --------------------------------------------------

async def handle_audio_stream(track: rtc.RemoteAudioTrack, speaker_name: str, agent_id: str, api_key: str, thenvoi_chat_id: str):
    global transcript_buffer
    audio_stream = rtc.AudioStream(track)
    
    buffer = bytearray()
    frame_count = 0
    
    logger.info(f"Started listening to {speaker_name}...")
    
    async for event in audio_stream:
        frame = event.frame
        buffer.extend(frame.data)
        frame_count += 1
        
        # Process every ~10 seconds of audio
        if frame_count >= 1000:
            pcm_data = bytes(buffer)
            buffer.clear()
            frame_count = 0
            
            text = await transcribe_audio_chunk(pcm_data, frame.sample_rate, frame.num_channels)
            
            if text and len(text) > 5: 
                chunk_str = f"[{speaker_name}]: {text}"
                transcript_buffer.append(chunk_str)
                logger.info(f"Transcribed: {chunk_str}")
                
                # If we hit 3 chunks, trigger the LLM!
                if len(transcript_buffer) >= 3:
                    combined_transcript = "\n".join(transcript_buffer)
                    transcript_buffer.clear()
                    
                    if thenvoi_chat_id:
                        logger.info("Generating Copilot question...")
                        
                        # 1. Generate the question using the LLM directly
                        llm = ChatOpenAI(
                            api_key=os.getenv("AIMLAPI_KEY"),
                            base_url="https://api.aimlapi.com/v1",
                            model="gpt-4o-mini",
                            temperature=0.2,
                        )
                        
                        resp = await llm.ainvoke([
                            SystemMessage(content="You are an Interview Copilot. Read the recent transcript and generate exactly ONE short, highly specific follow-up question to ask the candidate. Do not include any other text."),
                            HumanMessage(content=f"Transcript:\n{combined_transcript}")
                        ])
                        
                        copilot_question = f"💡 **Copilot Suggestion:**\n{resp.content}"
                        logger.info(f"Generated Question: {copilot_question}")
                        
                        # 2. Fetch the human user ID from the room
                        async with httpx.AsyncClient() as client:
                            base_url = f"https://app.thenvoi.com/api/v1/agent/chats/{thenvoi_chat_id}"
                            
                            res = await client.get(f"{base_url}/participants", headers={"X-API-Key": api_key})
                            participants = res.json().get("data", [])
                            
                            user_id = None
                            for p in participants:
                                if p.get("type") == "User":
                                    user_id = p["id"]
                                    break
                            
                            # 3. Post the message tagging the user!
                            if user_id:
                                payload = {
                                    "message": {
                                        "content": copilot_question,
                                        "mentions": [{"id": user_id}]
                                    }
                                }
                                
                                final_res = await client.post(
                                    f"{base_url}/messages",
                                    headers={"X-API-Key": api_key},
                                    json=payload
                                )
                                
                                if final_res.status_code in [200, 201]:
                                    logger.info("🎉 Successfully pushed Copilot question to Band.ai UI!")
                                else:
                                    logger.error(f"Failed. API returned: {final_res.text}")


async def connect_to_livekit_bg(room_name: str, agent_id: str, api_key: str, thenvoi_chat_id: str):
    """Background task that connects to LiveKit and attaches audio listeners."""
    url = os.getenv("NEXT_PUBLIC_LIVEKIT_URL")
    lk_api_key = os.getenv("LIVEKIT_API_KEY")
    lk_api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    token = api.AccessToken(lk_api_key, lk_api_secret).with_identity("Agent_Copilot").with_name("AI Copilot").with_grants(api.VideoGrants(room_join=True, room=room_name)).to_jwt()
    
    room = rtc.Room()
    
    @room.on("track_subscribed")
    def on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            asyncio.create_task(handle_audio_stream(track, participant.identity, agent_id, api_key, thenvoi_chat_id))

    await room.connect(url, token)
    logger.info(f"Successfully connected to LiveKit room: {room_name}")


@tool
async def connect_to_interview(livekit_room_id: str, config: RunnableConfig):
    """
    Call this tool immediately when you receive the LiveKit Room ID to join the interview.
    """
    global is_listening
    
    # Extract the actual Band.ai chat room ID directly from LangGraph's internal state!
    thenvoi_chat_id = config.get("configurable", {}).get("thread_id")
    
    if not is_listening and thenvoi_chat_id:
        agent_id = os.getenv("MEETING_AGENT_ID")
        api_key = os.getenv("MEETING_AGENT_KEY")
        # Start the livekit connection in the background
        asyncio.create_task(connect_to_livekit_bg(livekit_room_id, agent_id, api_key, thenvoi_chat_id))
        is_listening = True
        return "Successfully joined the LiveKit room. I am now listening to the audio."
    return "Already listening or missing Chat ID."


async def main():
    load_dotenv()

    agent_id = os.getenv("MEETING_AGENT_ID")
    api_key = os.getenv("MEETING_AGENT_KEY")

    llm = ChatOpenAI(
        api_key=os.getenv("AIMLAPI_KEY"),
        base_url="https://api.aimlapi.com/v1",
        model="gpt-4o-mini",
        temperature=0.2,
    )

    adapter = LangGraphAdapter(
        llm=llm,
        checkpointer=InMemorySaver(),
        additional_tools=[connect_to_interview],
        custom_section="""
          You are InterviewAgent, an AI copilot assisting a human interviewer.
          
          PURPOSE:
          You listen to transcripts of an ongoing interview and suggest intelligent, probing follow-up questions.
          
          WORKFLOW:
          1. The CandidateOverviewAgent will initially send you a Candidate Overview and a LiveKit Room ID.
          2. You MUST immediately call the `connect_to_interview` tool using that Room ID.
          3. Reply acknowledging that you are connected, and output a brief 2-sentence summary of the candidate's profile to prepare the interviewer.
          4. Every few minutes, you will receive batches of live transcript chunks automatically.
          5. When you receive transcript chunks, compare them to the candidate's overview, and generate 1 highly specific follow-up question for the human interviewer to ask.
        """
    )

    agent = Agent.create(
        adapter=adapter,
        agent_id=agent_id,
        api_key=api_key,
    )

    logger.info("InterviewAgent running...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
