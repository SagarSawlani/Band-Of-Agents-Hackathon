import asyncio
import httpx
import os

api_key = "band_a_1781391973_xQ4RrhB1Ut0boHpsPFsFcly9IBc2pU-m"
chat_id = "5f11b9da-853e-4e23-9676-c2d4185c7645"
url = f"https://app.thenvoi.com/api/v1/agent/chats/{chat_id}/messages"

headers_to_try = [
    {"X-API-Key": api_key}
]

payloads_to_try = [
    {"message": {"text": "test"}},
    {"message": {"content": "test"}},
    {"message": {"body": "test"}}
]

async def main():
    async with httpx.AsyncClient() as client:
        for payload in payloads_to_try:
            print(f"\n--- Trying payload {payload} ---")
            res = await client.post(url, headers=headers_to_try[0], json=payload)
            print(f"Status: {res.status_code}")
            if res.status_code == 422:
                print(f"422 DETAIL: {res.text}")

asyncio.run(main())
