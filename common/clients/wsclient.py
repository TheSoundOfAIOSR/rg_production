from rgws.interface import WebsocketClient
import asyncio

class STTClient(WebsocketClient):
    def __init__(self, module, **kwargs):
        super(STTClient, self).__init__(**kwargs)
        self.module = module
        self.setup = False

    async def startup(self):
        print(f"Setting up {self.module}...")
        asyncio.create_task(self.run())

        await asyncio.sleep(5)

        i = 1

        while True:
            await asyncio.sleep(1)
            try:
                await self.status()
                break
            except:
                pass

        if self.module == "stt" or self.module == "sg":
            await self.setup_model()

    async def _producer(self, websocket):
        while True:
            await asyncio.sleep(100)
