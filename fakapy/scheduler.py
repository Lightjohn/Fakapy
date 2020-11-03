import asyncio

import aiohttp
import async_timeout
import loguru

from fakapy.item import Item
from fakapy.request import Request
from fakapy.response import Response


class Scheduler:

    def __init__(self):
        self.queue_requests = asyncio.Queue()
        self.queue_items = asyncio.Queue()
        self.session = aiohttp.ClientSession()
        self.log = loguru.logger
        self.can_continue = True
        self.event = asyncio.Event()
        self._count = 0

        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        self._req_task = self.loop.create_task(self.loop_requests(), name="loop_requests")
        self._item_task = self.loop.create_task(self.loop_items(), name="loop_items")
        self.loop.create_task(self.cleanup())
        self.loop.create_task(self.watcher())

    async def loop_requests(self):
        while self.can_continue:
            req, callback = await self.queue_requests.get()
            self.log.trace("Processing {}", req)
            # Special request when we close everything
            if req.url == "":
                self.queue_requests.task_done()
                continue
            try:
                async with async_timeout.timeout(10):
                    async with self.session.get(req.url) as response:
                        text = await response.text()
                        res = Response(response, text)
                        callback(res)
            except Exception as e:
                self.log.warning("Exception {}", e)
            self.queue_requests.task_done()
        self.log.debug("Request loop finished")

    async def loop_items(self):
        while self.can_continue:
            itm, callback = await self.queue_items.get()
            self.log.trace("Processing {}", itm)
            # Special request when we close everything
            if itm.url == "":
                self.queue_items.task_done()
                continue
            try:
                callback(itm)
            except Exception as e:
                self.log.warning("Exception {}", e)
            self.queue_items.task_done()
        self.log.debug("Item loop finished")

    def add_request(self, req: Request, callback):
        if self.can_continue:
            self.log.trace("Adding {}", req)
            self.queue_requests.put_nowait((req, callback))
        else:
            self.log.trace("Dropping Request: {}", req)

    def add_item(self, item: Item, callback):
        if self.can_continue:
            self.log.trace("Adding {}", item)
            self.queue_items.put_nowait((item, callback))
        else:
            self.log.trace("Dropping Item: {}", item)

    async def cleanup(self):
        await self.event.wait()
        self.log.trace("Start cleaning")
        await self.session.close()
        # Create empty request & item to wake queue
        self.queue_requests.put_nowait((Request(""), None))
        self.queue_items.put_nowait((Item(""), None))

        self.log.trace("Waiting queues")

        await self.queue_items.join()
        await self.queue_requests.join()

        self.log.trace("Cancelling tasks")
        self._req_task.cancel()
        self._item_task.cancel()

        await self._req_task
        await self._item_task

        self.log.trace("Closing loop")
        self.loop.stop()

    async def watcher(self):
        while True:
            await asyncio.sleep(1)
            s1 = self.queue_requests.qsize()
            s2 = self.queue_items.qsize()
            if s1 == 0 and s2 == 0 and self._count == 0:
                self.log.debug("All queues are empty: stopping")
                self.loop.create_task(self._stop())
                break

    async def _stop(self):
        await asyncio.sleep(3)
        self.log.trace("Stop was called")
        self.can_continue = False
        self.event.set()

    def stop(self):
        self.loop.create_task(self._stop())

    def wait(self):
        self.log.trace("Waiting")
        self.loop.run_forever()
        self.log.trace("Wait done")

    def used(self):
        self._count += 1

    def freed(self):
        self._count -= 1
