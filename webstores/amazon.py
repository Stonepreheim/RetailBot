import asyncio
import os
import random
import time

import pygame
from patchright.async_api import async_playwright

from webstore_util import check_selector_exists, wait_for_selectors, wait_for_user_action, wait_then_click


class Amazon:
    def __init__(self, file_util, target_url):
        self.file_util = file_util
        self.target_url = target_url
        self.browser = None
        self.page = None
        pygame.mixer.init()

    async def initialize(self):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch_persistent_context(
                user_data_dir=os.path.join(os.getcwd(), "./data/browser/Amazon"),
                channel="chrome",
                headless=False,
                no_viewport=True
            )
            self.page = await self.browser.new_page()
            self.page.set_default_timeout(0)
            self.userData = await self.file_util.read_json('data/user/user_data.json')
            self.config = await self.file_util.read_json('data/user/config.json')
            # get login status from data/user/config.json
            # if missing login, login
            # else, start searchSite
            if "Amazon" not in self.config["logged_in"]:
                await self.login()
                await asyncio.sleep(3)
                await self.browser.close()
                self.config["logged_in"] += ["Amazon"]
                await self.file_util.write_json('data/user/config.json', self.config)
                await self.initialize()
            else:
                await self.searchSite()

    async def login(self):
        await self.page.goto('https://www.amazon.com/')
        print("Please login to your Amazon account")
        await wait_for_user_action()
        print("Logged in successfully")

    async def searchSite(self):
        while True:
            await self.page.goto(self.target_url)
            await self.page.wait_for_selector("body", timeout=3000)
            exists = await check_selector_exists(self.page, '[id^="a-autoid-"][id$="-announce"]')
            if exists:
                print(time.strftime("%H:%M:%S") + " FOUND ITEM!!! " + self.target_url)
                pygame.mixer.music.load("data/chimes/alert.mp3")
                pygame.mixer.music.play()
                await self.checkout()
            await asyncio.sleep(random.randint(1, 4))

    async def checkout(self):
        await wait_then_click(self.page, '[id^="a-autoid-"][id$="-announce"]')
        await wait_for_user_action()