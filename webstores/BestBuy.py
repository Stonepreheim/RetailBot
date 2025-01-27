import asyncio
import random
import time

import pygame
from patchright.async_api import async_playwright


class BestBuy:
    def __init__(self, file_util, target_url):
        self.file_util = file_util
        self.target_url = target_url
        self.browser = None
        self.page = None
        pygame.mixer.init()

    async def initialize(self):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch_persistent_context(
                user_data_dir="./data/browser/BestBuy",
                channel="chrome",
                headless=False,
                no_viewport=True
            )
            self.page = await self.browser.new_page()
            self.page.set_default_timeout(0)
            # get login status from data/user/config.json
            # if missing login, login
            # else, start searchSite
            config = await self.file_util.read_json('data/user/config.json')
            if "BestBuy" not in config["logged_in"]:
                await self.login()
                await self.browser.close()
                config["logged_in"] += "BestBuy"
                await self.file_util.write_json('data/user/config.json', config)
                await self.initialize()
            else:
                await self.searchSite()

    async def login(self):
        userData = await self.file_util.read_json('data/user/user_data.json')
        await self.page.goto('https://www.bestbuy.com/')
        await self.page.wait_for_selector("span[class$='line-clamp']")
        await self.page.click("span[class$='line-clamp']")
        await self.page.wait_for_selector("a[data-testid='signInButton']")
        await self.page.click("a[data-testid='signInButton']")
        await self.page.wait_for_selector("input[aria-required='true']")
        await self.page.click("input[aria-required='true']")
        await self.page.type("input[aria-required='true']", userData["email"])
        await self.page.click("button[data-track$='Continue']")
        await self.page.wait_for_selector("#password-radio")
        await self.page.click("#password-radio")
        await self.page.wait_for_selector("#fld-p1")
        await self.page.click("#fld-p1")
        await self.page.type("#fld-p1", userData["BestBuy_pass"])
        await self.page.click("button[class*='cia-form']")

    async def searchSite(self):
        while True:
            await self.page.goto(self.target_url)
            # await self.page.goto('https://www.google.com/')
            # wait for page to load
            await self.page.wait_for_selector("body", timeout=3000)
            exists = await self.check_selector_exists(self.page, ".add-to-cart-button")
            if exists:
                print(time.strftime("%H:%M:%S") + " FOUND ITEM!!!" + self.target_url)
                pygame.mixer.music.load("data/chimes/alert.mp3")
                pygame.mixer.music.play()
                await self.checkout()
            else:
                print(time.strftime("%H:%M:%S") + " Item not found: " + self.target_url)
            await asyncio.sleep(random.randint(1, 3))
        await self.browser.close()

    async def checkout(self):
        print("Checking out...")

    @staticmethod
    async def check_selector_exists(page, selector):
        elements = await page.query_selector_all(selector)
        return len(elements) > 0
