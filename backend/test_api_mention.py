import asyncio
import httpx

api_key = "band_a_1781391973_xQ4RrhB1Ut0boHpsPFsFcly9IBc2pU-m"
chat_id = "5f11b9da-853e-4e23-9676-c2d4185c7645"
url = f"https://app.thenvoi.com/api/v1/agent/chats/{chat_id}/messages"

payload = {"message": {"content": "test", "mentions": [{"id": "all"}]}}

async def main():
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers={"X-API-Key": api_key}, json=payload)
        print(f"Status: {res.status_code}")
        if res.status_code == 422:
            print(f"422 DETAIL: {res.text}")

asyncio.run(main())
