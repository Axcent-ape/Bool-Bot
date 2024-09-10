import os
import random
from itertools import zip_longest
from utils.bool import Bool
from aiohttp.client_exceptions import ContentTypeError
from data import config
from utils.core import logger
import datetime
import pandas as pd
from utils.core.telegram import Accounts
import asyncio


async def start(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    bol = Bool(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await bol.login()
    logger.success(f"Thread {thread} | {account} | Login!")

    for task in await bol.get_tasks():
        if task['done']: continue
        if await bol.complete_task(task['assignmentId']):
            logger.success(f"Thread {thread} | {account} | Complete task «{task['title']}»! Reward: {task['reward']} tBOL")
        await asyncio.sleep(random.uniform(*config.DELAYS['TASK']))

    for task in await bol.get_daily_tasks():
        if task['done']: continue
        if await bol.complete_daily_task(task['assignmentId']):
            logger.success(f"Thread {thread} | {account} | Complete task «{task['title']}»! Reward: {task['reward']} tBOL")
        await asyncio.sleep(random.uniform(*config.DELAYS['TASK']))

    await bol.logout()


async def stats():
    accounts = await Accounts().get_accounts()

    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        tasks.append(asyncio.create_task(Bool(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy).stats()))

    data = await asyncio.gather(*tasks)

    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Balance', 'Rank', 'Referrals', 'Referral link', 'Proxy (login:password@ip:port)']

    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')

    logger.success(f"Saved statistics to {path}")
