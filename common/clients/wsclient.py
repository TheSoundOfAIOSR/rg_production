from rgws.interface import WebsocketClient
import asyncio

class STTClient(WebsocketClient):
    def __init__(self, **kwargs):
        super(STTClient, self).__init__(**kwargs)

    async def _producer(self, websocket):

        while True:
            await asyncio.sleep(100)

class TTSClient(WebsocketClient):
    def __init__(self, **kwargs):
        super(TTSClient, self).__init__(**kwargs)

    async def _producer(self, websocket):
        while True:
            await asyncio.sleep(100)

        # logging.debug(await self.example_func("blo"))
        # if you want to pass function with arguments, you can use functools.partial(func, args)
        # logging.debug(await self.read_data_stream(websocket, self.stream_func))

class SGClient(WebsocketClient):
    def __init__(self, **kwargs):
        super(SGClient, self).__init__(**kwargs)

    async def _producer(self, websocket):
        while True:
            await asyncio.sleep(100)
