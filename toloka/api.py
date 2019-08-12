from typing import List

from aiohttp import ClientSession

from .toloka_result import TolokaResult

API_BASE = 'https://toloka.to/api.php'


async def search_request(search: str) -> List[TolokaResult]:
    if not search:
        raise ValueError('Search query is empty')

    async with ClientSession() as cs:
        params = {'search', search}
        async with cs.get(API_BASE, params=params) as r:
            results_dict = await r.json()

            return [TolokaResult.from_dict(result_dict) for result_dict in results_dict]
