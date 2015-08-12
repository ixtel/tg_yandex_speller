import os
import asyncio
import aiohttp
from aiotg import TgBot

#Debug mode
# PYTHONASYNCIODEBUG = 1

API = ''
NUM_HANDLERS = 5

bot = TgBot(API)
sem = asyncio.Semaphore(NUM_HANDLERS)


@bot.command(r"/(start|help)")
def help(message, match):
    return message.reply(
        'Бот автоматично виправляє повідомлення на синтаксично правильні,\
        щоб корисуватись ботом, просто пишіть в чат\n\
        /help -- це повідомлення\
        в своїй роботі використовує https://tech.yandex.ru/speller/'
        )

@bot.default
def message_def(message):
    asyncio.Task(handler_message(message),loop=loop)
    


@asyncio.coroutine
def get_speller(s):
    data = { 'text': s,
        'lang':'ru,en,uk'
        }
    url = 'http://speller.yandex.net/services/spellservice.json/checkTexts'

    r = yield from aiohttp.request('GET', url,params = data)
    raw = yield from r.json()
    return raw[0]

@asyncio.coroutine
def handler_message(item):
    def rewriter(response):
        s = ''
        w = set()
        for f in response:
            if str(f['word']) in w:
                continue
            else:
                w.add( str(f['word']) )

            if f['s']:
                q = ''
                for _ in f['s']:
                    if q:
                        q+="' або '"
                    q+= '{}'.format(_)
                s+= "Ви помилились, не '{}', а '{}'\n".format(f['word'],q)
        return s


    with (yield from sem):
        speller = yield from get_speller(item.text)
        s = rewriter(speller)
        if s:
            yield from item.reply(s)




if __name__ == '__main__':     
    loop = asyncio.get_event_loop()
    queue =  asyncio.Queue(loop=loop)

    try:
        loop.run_until_complete(asyncio.async(bot.loop()))
    except KeyboardInterrupt:
        pass    
    finally:
        loop.close()
