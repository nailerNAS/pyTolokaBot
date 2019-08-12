import asyncio
import re

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.webhook import get_new_configured_app
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton, InputFile
from aiogram.utils.executor import start_polling
from aiohttp.web import run_app

import config
from toloka import api

loop = asyncio.get_event_loop()

bot = Bot(config.TOKEN, loop)
dp = Dispatcher(bot, loop)

link_pattern = re.compile(r'\.torrent (?P<link>https:\/\/toloka\.to\/(?P<id>t\d+$))')


@dp.inline_handler(lambda q: q.query and not q.query.startswith('.torrent '))
async def inline_search(query: InlineQuery):
    inline_results = []

    toloka_results = await api.search_request(query.query)

    for n, toloka_result in enumerate(toloka_results):
        if n >= 50:
            break

        button = InlineKeyboardButton(text='Download',
                                      switch_inline_query=f'.torrent {toloka_result.link}')
        markup = InlineKeyboardMarkup()
        markup.insert(button)

        text = f'ID: {toloka_result.id}\n' \
               f'Link: {toloka_result.link}\n' \
               f'Title: {toloka_result.title}\n' \
               f'Forum name: {toloka_result.forum_name}\n' \
               f'Forum parent: {toloka_result.forum_parent}\n' \
               f'Comments: {toloka_result.comments}\n' \
               f'Size: {toloka_result.size}\n' \
               f'Seeders: {toloka_result.seeders}\n' \
               f'Leechers: {toloka_result.leechers}\n' \
               f'Complete: {toloka_result.complete}'

        description = f'S: {toloka_result.seeders} | L: {toloka_result.leechers} | C: {toloka_result.complete}'

        content = InputTextMessageContent(message_text=text,
                                          disable_web_page_preview=True)

        article = InlineQueryResultArticle(id=str(n),
                                           title=toloka_result.title,
                                           input_message_content=content,
                                           reply_markup=markup,
                                           description=description)

        inline_results.append(article)

    if not inline_results:
        text = f'Nothing found by {query.query}'
        content = InputTextMessageContent(message_text=text,
                                          disable_web_page_preview=True)
        article = InlineQueryResultArticle(id='1',
                                           title='Not found',
                                           input_message_content=content,
                                           description=text)
        inline_results.append(article)

    await query.answer(inline_results)


@dp.inline_handler(lambda q: q.query and q.query.startswith('.torrent '))
async def inline_torrent(query: InlineQuery):
    match = link_pattern.match(query.query)
    if not match:
        return

    link = match.group('link')
    id = match.group('id')
    filename = f'{id}.torrent'

    torrent_fs = await api.get_torrent_fs(link)
    torrent_fs.name = filename

    sent = await bot.send_document(config.CHANNEL, InputFile(torrent_fs))
    file_id = sent.document.file_id

    content = InputTextMessageContent(message_text=link,
                                      disable_web_page_preview=True)
    article = InlineQueryResultArticle(id='1',
                                       title=link,
                                       input_message_content=content,
                                       description=filename)

    await query.answer([article])


async def on_startup(*args, **kwargs):
    await bot.delete_webhook()
    await bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown(*args, **kwargs):
    await bot.delete_webhook()


def main():
    if config.USE_WEBHOOK:
        app = get_new_configured_app(dp, config.WEBHOOK_PATH)

        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        run_app(app, port=config.WEBHOOK_LOCAL_PORT)

    else:
        try:
            start_polling(dp, loop=loop, skip_updates=True)
        except KeyboardInterrupt:
            print('goodbye')
            dp.stop_polling()


if __name__ == '__main__':
    main()
