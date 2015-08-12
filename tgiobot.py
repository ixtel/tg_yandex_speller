import os
import asyncio
import aiohttp
from aiotg import TgBot

api = ''
bot = TgBot(api)


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
    yield from queue.put(message)
    


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
def handler_message():
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
                        q+='/'
                    q+= '{}'.format(_)
                s+= "Ви помилились, не '{}', а '{}'\n".format(f['word'],q)
        return s

    while 1:
        item = yield from queue.get()
        speller = yield from get_speller(item.text)
        s = rewriter(speller)
        yield from item.reply(s)




if __name__ == '__main__':     
    loop = asyncio.get_event_loop()
    queue =  asyncio.Queue(loop=loop)
    tasks = [
        asyncio.async(bot.loop()),
        ]
    for _ in range(5):
        tasks.append(asyncio.async(handler_message()))

    try:
        loop.run_until_complete(asyncio.wait(tasks))
    except KeyboardInterrupt:
        pass    
    finally:
        loop.close()
