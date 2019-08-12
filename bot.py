import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton

import config
from toloka import api

loop = asyncio.get_event_loop()

bot = Bot(config.TOKEN, loop)
dp = Dispatcher(bot, loop)


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
