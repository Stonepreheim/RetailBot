import asyncio
import json

import aiofiles


# This class will handle all file read and write operations to ensure that only one operation is happening at a time
class FileUtil:
    def __init__(self):
        self.lock = asyncio.Lock()

    async def read_json(self, file_path):
        async with self.lock:
            async with aiofiles.open(file_path, 'r') as file:
                content = await file.read()
                return json.loads(content)

    async def write_json(self, file_path, data):
        async with self.lock:
            async with aiofiles.open(file_path, 'w') as file:
                await file.write(json.dumps(data))

    async def read_file(self, file_path):
        async with self.lock:
            async with aiofiles.open(file_path, 'r') as file:
                return await file.read()

    async def write_file(self, file_path, data):
        async with self.lock:
            async with aiofiles.open(file_path, 'w') as file:
                await file.write(data)
