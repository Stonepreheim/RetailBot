import asyncio
import os
import stat

import webstores.BestBuy as bestBuy
from FileUtil import FileUtil


async def main():
    # Define the directory path
    user_data_dir = "data/browser/"

    # Create the directory if it doesn't exist
    os.makedirs(user_data_dir, exist_ok=True)

    # Change the permissions of the directory
    os.chmod(user_data_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    file_util = FileUtil()
    tasks = []
    config = await file_util.read_json('data/user/config.json')
    if config["debug_mode"]:
        # Warn user in red color that debug is enabled
        print("\033[91m" + "Debug mode is enabled. Purchases WILL NOT be placed!!" + "\033[0m")
    for item in config["items"]:
        if item["store"] == "BestBuy":
            tasks.append(bestBuy.BestBuy(file_util, item["target_url"]).initialize())
        # add future stores here

    # Run tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())