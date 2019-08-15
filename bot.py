import asyncio
import re
import ssl

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.webhook import get_new_configured_app
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton, InputFile, InlineQueryResultCachedDocument, ParseMode
from aiogram.utils.executor import start_polling
from aiohttp.web import run_app

import config
from toloka import api, TolokaResult

loop = asyncio.get_event_loop()

bot = Bot(config.TOKEN, loop)
dp = Dispatcher(bot, loop)

link_pattern = re.compile(r'\.torrent (?P<link>https:\/\/toloka\.to\/(?P<id>t\d+$))')


def prepare_result(result: TolokaResult) -> str:
    return f'*Назва:* {result.title}\n' \
           f'*Посилання:* {result.link}\n' \
           f'*Форум:* {result.forum_name}. {result.forum_parent}\n' \
           f'*Розмір:* {result.size}\n' \
           f'*Роздають:* {result.seeders}\n' \
           f'*Завантажують:* {result.leechers}\n' \
           f'*Завантажили:* {result.complete}'


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

        text = prepare_result(toloka_result)

        description = f'{toloka_result.size}|{toloka_result.seeders}/{toloka_result.leechers}'

        content = InputTextMessageContent(message_text=text,
                                          disable_web_page_preview=True,
                                          parse_mode=ParseMode.MARKDOWN)

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

    document = InlineQueryResultCachedDocument(id='1',
                                               title=link,
                                               document_file_id=file_id,
                                               description=filename,
                                               caption=link)

    await query.answer([document])
    torrent_fs.close()


async def on_startup(*args, **kwargs):
    await api.login()

    await bot.delete_webhook()
    if config.CUSTOM_SSL_CERT:
        with open(config.SSL_CERT, 'rb') as file:
            cert = InputFile(file)
            await bot.set_webhook(config.WEBHOOK_URL, cert)
    else:
        await bot.set_webhook(config.WEBHOOK_URL)


async def on_shutdown(*args, **kwargs):
    await bot.delete_webhook()


def main():
    if config.USE_WEBHOOK:
        app = get_new_configured_app(dp, config.WEBHOOK_PATH)

        app.on_startup.append(on_startup)
        if not config.HEROKU:
            app.on_shutdown.append(on_shutdown)

        context = None
        if config.CUSTOM_SSL_CERT:
            context = ssl.SSLContext()
            context.load_cert_chain(config.SSL_CERT, config.SSL_PRIV)

        run_app(app, port=config.WEBHOOK_LOCAL_PORT, ssl_context=context)

    else:
        async def proxy_login(*args, **kwargs):
            await api.login()

        try:
            start_polling(dp, loop=loop, skip_updates=True, on_startup=proxy_login)
        except KeyboardInterrupt:
            print('goodbye')
            dp.stop_polling()


if __name__ == '__main__':
    main()
