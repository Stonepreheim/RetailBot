import asyncio
import os
import stat
import webstores.BestBuy as bestBuy

async def main():
    # Define the directory path
    user_data_dir = "data/browser/"

    # Create the directory if it doesn't exist
    os.makedirs(user_data_dir, exist_ok=True)

    # Change the permissions of the directory
    os.chmod(user_data_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

    bb = bestBuy.BestBuy()

    tasks = [
        #run for each site here
        bb.initialize()
    ]

    # Run tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())