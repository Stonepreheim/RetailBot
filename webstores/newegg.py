import asyncio
import os
import random
import time

import pygame
from patchright.async_api import async_playwright

import webstore_util
from webstore_util import check_selector_exists, wait_for_selectors, wait_for_user_action, wait_then_click


class NewEgg:
    def __init__(self, file_util, target_url):
        self.file_util = file_util
        self.target_url = target_url
        self.browser = None
        self.page = None
        pygame.mixer.init()

    async def initialize(self):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch_persistent_context(
                user_data_dir=os.path.join(os.getcwd(), "./data/browser/newegg"),
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
            if "Newegg" not in self.config["logged_in"]:
                await self.login()
                await asyncio.sleep(3)
                await self.browser.close()
                self.config["logged_in"] += ["Newegg"]
                await self.file_util.write_json('data/user/config.json', self.config)
                await self.initialize()
            else:
                await self.searchSite()

    #going to try manual login come back and automate this later
    async def login(self):
        await self.page.goto('https://www.newegg.com/')
        print("Please login to your Newegg account")
        await wait_for_user_action()
        print("Logged in successfully")

    async def searchSite(self):
        while True:
            await self.page.goto(self.target_url)
            await self.page.wait_for_selector("#app > div.page-content > section > div > div > div.row-body > div:nth-child(1)", timeout=3000)
            exists = await check_selector_exists(self.page, 'button.btn.btn-primary.btn-mini[title^="Add "][title*=" to cart"]')
            if exists:
                print(time.strftime("%H:%M:%S") + " FOUND ITEM!!! " + self.target_url)
                pygame.mixer.music.load("data/chimes/alert.mp3")
                pygame.mixer.music.play()
                await self.checkout()
            await asyncio.sleep(random.randint(1, 4))

    async def checkout(self):
        await self.page.query_selector('button.btn.btn-primary.btn-mini[title^="Add "][title*=" to cart"]')
        await self.page.click('button.btn.btn-primary.btn-mini[title^="Add "][title*=" to cart"]')
        await wait_then_click(self.page, 'button.btn.btn-primary[title^="Proceed to checkout"]')
        selector = await wait_for_selectors(self.page, 'i.fas.fa-times', 'button.button.bg-orange.button-m.checkout-step-action-done[type="button"]')
        if selector == 'i.fas.fa-times':
            await wait_then_click(self.page, 'i.fas.fa-times')
            await wait_then_click(self.page, 'button.btn.btn-primary[title^="Proceed to checkout"]')
        await wait_then_click(self.page, 'button.button.bg-orange.button-m.checkout-step-action-done[type="button"]')
        await wait_then_click(self.page, 'input.form-text.mask-cvv-4[name="cvvNumber"][type="text"]')
        await self.page.type('input.form-text.mask-cvv-4[name="cvvNumber"][type="text"]', self.userData["cvv"])
        await wait_then_click(self.page, 'button.button.bg-orange.button-m.checkout-step-action-done[type="button"]')
        # input.form-text.is-wide.mask-cardnumber[name="cardnumber"][type="text"] locator for card number retype if it comes back
        await wait_for_user_action()