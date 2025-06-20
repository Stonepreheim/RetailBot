import asyncio
import os
import random
import time

import pygame
from patchright.async_api import async_playwright

from webstore_util import check_selector_exists, wait_for_selectors, wait_for_user_action, wait_then_click


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
                user_data_dir=os.path.join(os.getcwd(), "./data/browser/BestBuy"),
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
            if "BestBuy" not in self.config["logged_in"]:
                await self.login()
                await asyncio.sleep(3)
                await self.browser.close()
                self.config["logged_in"] += ["BestBuy"]
                await self.file_util.write_json('data/user/config.json', self.config)
                await self.initialize()
            else:
                await self.searchSite()

    async def login(self):
        await self.page.goto('https://www.bestbuy.com/')
        await self.page.wait_for_selector("span[class$='line-clamp']")
        await self.page.click("span[class$='line-clamp']")
        await self.page.wait_for_selector("a[data-testid='signInButton']")
        await self.page.click("a[data-testid='signInButton']")
        await self.page.wait_for_selector("input[aria-required='true']")
        await self.page.click("input[aria-required='true']")
        await self.page.type("input[aria-required='true']", self.userData["email"])
        await self.page.click("button[data-track$='Continue']")
        await self.page.wait_for_selector("#password-radio")
        await self.page.click("#password-radio")
        await self.page.wait_for_selector("#fld-p1")
        await self.page.click("#fld-p1")
        await self.page.type("#fld-p1", self.userData["BestBuy_pass"])
        await self.page.click("button[class*='cia-form']")

    async def searchSite(self):
        while True:
            await self.page.goto(self.target_url)
            # await self.page.goto('https://www.google.com/')
            # wait for page to load
            await self.page.wait_for_selector("body", timeout=3000)
            exists = await check_selector_exists(self.page, ".c-button.c-button-primary.c-button-sm.c-button-block.c-button-icon.c-button-icon-leading.add-to-cart-button")
            if exists:
                print(time.strftime("%H:%M:%S") + " FOUND ITEM!!! " + self.target_url)
                pygame.mixer.music.load("data/chimes/alert.mp3")
                pygame.mixer.music.play()
                await self.checkout()
            # else:
            #     print(time.strftime("%H:%M:%S") + " Item not found: " + self.target_url)
            # random wait time to appear human
            await asyncio.sleep(random.randint(1, 4))

    async def checkout(self):
        print("Best Buy is checking out...")
        await self.page.query_selector(".add-to-cart-button")
        await self.page.click(".add-to-cart-button")
        await self.page.wait_for_selector("a[class*='c-button-secondary']")
        await self.page.click("a[class*='c-button-secondary']")
        await self.page.wait_for_selector("button[data-track$='Top']")
        await self.page.click("button[data-track$='Top']")
        # There could be two different paths this goes from here
        selector = await wait_for_selectors(self.page, "#cvv", "button[data-track$='Continue']")
        if selector == "#cvv":
            await self.cvv_page()
        else:
            await self.page.click("button[data-track$='Continue']")
            await self.page.wait_for_selector("#password-radio")
            await self.page.click("#password-radio")
            await self.page.wait_for_selector("#fld-p1")
            await self.page.click("#fld-p1")
            await self.page.type("#fld-p1", self.userData["BestBuy_pass"])
            await self.page.wait_for_selector("button[class*='cia-form']")
            await self.page.click("button[class*='cia-form']")
            await self.cvv_page()

    async def cvv_page(self):
        await self.page.wait_for_selector("#cvv")
        await self.page.click("#cvv")
        await self.page.type("#cvv", self.userData["cvv"])
        # if not in debug mode press final checkout button
        if not self.config["debug_mode"]:
            await self.page.wait_for_selector(
                "div[class='flex-col gap-300 mt-100 d-none lg__flex '] button[data-track*='your']")
            await self.page.click("div[class='flex-col gap-300 mt-100 d-none lg__flex '] button[data-track*='your']")
        # Success! hopefully!
        pygame.mixer.music.load("data/chimes/order_placed.mp3")
        pygame.mixer.music.play()
        await wait_for_user_action()
        await self.browser.close()
