import io
from typing import List

from aiohttp import ClientSession, FormData
from bs4 import BeautifulSoup, Tag

import config
from .toloka_result import TolokaResult

API_BASE = 'https://toloka.to/api.php'

cs = ClientSession()


async def login():
    form = FormData()
    form.add_field('username', config.TOLOKA_USERNAME)
    form.add_field('password', config.TOLOKA_PASSWORD)
    form.add_field('autologin', 'on')
    form.add_field('ssl', 'on')
    form.add_field('redirect', 'index.php?')
    form.add_field('login', 'Вхід')

    await cs.post('https://toloka.to/login.php', data=form)


async def search_request(search: str) -> List[TolokaResult]:
    if not search:
        raise ValueError('Search query is empty')

    params = {'search': search}
    async with cs.get(API_BASE, params=params) as r:
        results_dict = await r.json()

        return [TolokaResult.from_dict(result_dict) for result_dict in results_dict]


async def get_torrent_fs(link: str) -> io.BytesIO:
    async with cs.get(link) as r:
        html = await r.text()

    bs = BeautifulSoup(html, 'html.parser')
    tag: Tag = bs.find('a', text='Завантажити')

    if not tag:
        await login()

        return await get_torrent_fs(link)

    href = tag.attrs['href']

    download_link = f'https://toloka.to/{href}'

    async with cs.get(download_link) as r:
        toloka_torrent = io.BytesIO()
        toloka_torrent.name = 'toloka.torrent'
        toloka_torrent.write(await r.read())
        toloka_torrent.seek(0)

        return toloka_torrent
