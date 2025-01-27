import asyncio
import json

# patchright here!
from patchright.async_api import async_playwright

class BestBuy:
    def __init__(self):
        self.browser = None
        self.page = None

    def read_json(self, file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

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
            config = self.read_json('data/user/config.json')
            if "BestBuy" not in config["logged_in"]:
                await self.login()
                #closing browser to force session save
                await self.browser.close()
                config["logged_in"] += "BestBuy"
                with open('data/user/config.json', 'w') as file:
                    json.dump(config, file)
                await self.initialize()
            else:
                await self.searchSite()

    async def login(self):
        userData = self.read_json('data/user/user_info.json')
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
            await self.page.goto('https://www.bestbuy.com/')
            #await self.page.goto('https://www.google.com/')
            await asyncio.sleep(30)
            await self.browser.close()