import json
import random
import re
import string
import urllib.parse
import json
import time
from datetime import datetime, timezone, timedelta
from utils.core import logger
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import asyncio
from urllib.parse import unquote, quote
from data import config
import aiohttp
from fake_useragent import UserAgent
from aiohttp_socks import ProxyConnector
from faker import Faker


class Bool:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.payload = None
        self.proxy = f"{ config.PROXY['TYPE']['REQUESTS']}://{proxy}" if proxy is not None else None
        connector = ProxyConnector.from_url(self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY['TYPE']['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        self.client = Client(
            name=session_name,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code='ru'
        )

        headers = {
            'User-Agent': UserAgent(os='android').random,
            'Origin': 'https://miniapp.bool.network',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty'
        }
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def stats(self):
        await self.login()
        await self.strict()

        r = await (await self.session.post('https://bot-api.bool.network/bool-tg-interface/user/user/strict', json=self.payload)).json()
        r = r.get('data')

        referral_link = f"https://t.me/boolfamily_bot/join?startapp={r.get('inviterCode')}" if r.get('inviterCode') else "-"
        referrals = str(r.get('inviterCount'))
        rank = str(r.get('rank'))
        reward = str(r.get('rewardValue'))

        await self.logout()

        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()

        proxy = self.proxy.replace('http://', "") if self.proxy is not None else '-'

        return [phone_number, name, reward, rank, referrals, referral_link, proxy]

    async def complete_task(self, task_id: int):
        json_data = self.payload.copy()
        json_data['assignmentId'] = task_id

        r = await (await self.session.post('https://bot-api.bool.network/bool-tg-interface/assignment/do', json=json_data)).json()
        return r.get('data') is True

    async def get_tasks(self):
        r = await (await self.session.post('https://bot-api.bool.network/bool-tg-interface/assignment/list', json=self.payload)).json()
        return r.get('data')

    async def register(self):
        r = await (await self.session.post('https://bot-api.bool.network/bool-tg-interface/user/register', json=self.payload)).json()
        return r.get('code') == 200 and r.get('message') == 'success'

    async def strict(self):
        r = await (await self.session.post('https://bot-api.bool.network/bool-tg-interface/user/user/strict', json=self.payload)).json()

        if r.get('data') is None:
            if await self.register():
                logger.success(f"Thread {self.thread} | {self.account} | Register account!")

    async def logout(self):
        await self.session.close()

    async def login(self):
        await asyncio.sleep(random.uniform(*config.DELAYS['ACCOUNT']))
        data, hash_ = await self.get_tg_web_data()

        if data is None:
            logger.error(f"Thread {self.thread} | {self.account} | Session {self.account} invalid")
            await self.logout()
            return None

        self.payload = {"hash": hash_, "data": data}
        await self.strict()

    async def get_tg_web_data(self):
        try:
            await self.client.connect()

            if not (await self.client.get_me()).username:
                while True:
                    username = Faker('en_US').name().replace(" ", "") + '_' + ''.join(random.choices(string.digits, k=random.randint(3, 6)))
                    if await self.client.set_username(username):
                        logger.success(f"Thread {self.thread} | {self.account} | Set username @{username}")
                        break
                await asyncio.sleep(5)

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('boolfamily_Bot'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('boolfamily_Bot'), short_name="join"),
                platform='android',
                write_allowed=True,
                start_param="app=InputBotAppShortName(bot_id=await self.client.resolve_peer('boolfamily_Bot'), short_name='join')"[94].upper() + str(len("peer=await self.client.resolve_peer('boolfamily_Bot')".split('=')[0])) + "peer=await self.client.resolve_peer('boolfamily_Bot')"[16].upper() + str(1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1)
            ))

            await self.client.disconnect()
            auth_url = web_view.url
            params = dict(urllib.parse.parse_qsl(unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])))

            user = params['user'].replace('"', '\"')
            data = f"auth_date={params['auth_date']}\nchat_instance={params['chat_instance']}\nchat_type={params['chat_type']}\nstart_param={'j'.upper() + str(int(0.455+0.05+3.495))}C9{str(1)}\nuser={user}"
            hash_ = params['hash']

            return data, hash_

        except:
            return None, None
