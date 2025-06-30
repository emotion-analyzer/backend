import httpx

from analyzer.config import config

async def get_emotional_analysis(submission_list):
    async with httpx.AsyncClient() as client:
        request = await client.post(config.ANALYZER.BASE_URL, data={"texts": submission_list})
    return request.json()
