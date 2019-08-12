import io
from typing import List

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

import config
from .toloka_result import TolokaResult

API_BASE = 'https://toloka.to/api.php'


async def search_request(search: str) -> List[TolokaResult]:
    if not search:
        raise ValueError('Search query is empty')

    async with ClientSession() as cs:
        params = {'search': search}
        async with cs.get(API_BASE, params=params) as r:
            results_dict = await r.json()

            return [TolokaResult.from_dict(result_dict) for result_dict in results_dict]


async def get_torrent_fs(link: str) -> io.BytesIO:
    async with ClientSession(cookies=config.COOKIES) as cs:
        async with cs.get(link) as r:
            html = await r.text()

        bs = BeautifulSoup(html, 'html.parser')
        tag: Tag = bs.find('a', text='Завантажити')
        href = tag.attrs['href']

        download_link = f'https://toloka.to/{href}'

        async with cs.get(download_link) as r:
            toloka_torrent = io.BytesIO()
            toloka_torrent.name = 'toloka.torrent'
            toloka_torrent.write(await r.read())
            toloka_torrent.seek(0)

            return toloka_torrent
