import asyncio
import httpx
import os

api_key = "band_a_1781391973_xQ4RrhB1Ut0boHpsPFsFcly9IBc2pU-m"
chat_id = "5f11b9da-853e-4e23-9676-c2d4185c7645"
base_url = f"https://app.thenvoi.com/api/v1/agent/chats/{chat_id}"

async def main():
    async with httpx.AsyncClient() as client:
        # Get participants
        res = await client.get(f"{base_url}/participants", headers={"X-API-Key": api_key})
        participants = res.json()
        
        # Grab first human participant
        participant_id = None
        for p in participants.get("data", []):
            if p.get("type") == "User":
                participant_id = p["id"]
                break
                
        if participant_id:
            payload = {"message": {"content": "Hello from Copilot!", "mentions": [{"id": participant_id}]}}
            
            res = await client.post(f"{base_url}/messages", headers={"X-API-Key": api_key}, json=payload)
            print(f"Status: {res.status_code}")
            if res.status_code == 422:
                print(f"422 DETAIL: {res.text}")
            elif res.status_code == 201:
                print("SUCCESS!")

asyncio.run(main())
