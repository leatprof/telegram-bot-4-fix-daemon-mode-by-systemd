# -*- coding: utf-8 -*-
"""
Created on Mon Dec 24 17:18:51 2018

@author: Maksim Tverdikov
"""
import asyncio
import requests
import datetime
from configobj import ConfigObj
@asyncio.coroutine
def ping_and_compare(url,find_string):
    while True:
        try:
            r = requests.get(url,timeout=1)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            yield from queue.put(datetime.datetime.now().strftime('%H:%M:%S') + " Http Error: " + str(errh))
        except requests.exceptions.ConnectionError as errc:
            yield from queue.put(datetime.datetime.now().strftime('%H:%M:%S') + " Error Connecting: " + str(errc))
        except requests.exceptions.Timeout as errt:
            yield from queue.put(datetime.datetime.now().strftime('%H:%M:%S') + " Timeout Error: " + str(errt))
        except requests.exceptions.RequestException as err:
            yield from queue.put(datetime.datetime.now().strftime('%H:%M:%S') + " OOps: Something Else: " + str(err))
        else:
            if find_string not in r.text:
                yield from queue.put(datetime.datetime.now().strftime('%H:%M:%S') + ' "'+url+'" is broken. Server returned http status: ' + str(r.status_code) + '. String: "'+find_string+'" not found.\n')
        yield from asyncio.sleep(1)
 
@asyncio.coroutine
def send_result_to_telegram(telegram_url, chat_id):
    while True:
        value = ''
        if not queue.empty():
            while not queue.empty():
                value += yield from queue.get()
            params = {'chat_id': chat_id, 'text': value}
            r = requests.post(telegram_url + 'sendMessage', data=params)
            r.raise_for_status()
        yield from asyncio.sleep(30)

queue = asyncio.Queue()    

cfg = ConfigObj('config.ini')
url = cfg['Default']['url']
find_string = cfg['Default']['find_string']
telegram_bot_api_token = cfg['Default']['telegram_bot_api_token']
chat_id = cfg['Default']['chat_id']
telegram_url = 'https://api.telegram.org/bot'+telegram_bot_api_token+'/'

loop = asyncio.get_event_loop()
loop.create_task(ping_and_compare(url,find_string))
loop.create_task(send_result_to_telegram(telegram_url,chat_id))
loop.run_forever()
   


