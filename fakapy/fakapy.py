from loguru import logger

from .item import Item
from .request import Request
from .scheduler import Scheduler


class Fakapy:
    def __init__(self):
        self._func = {"parse": self._parse, "item": self._item}
        self._scheduler = Scheduler()

    def run(self, url: str):
        logger.info("running...")
        logger.info("arg: {}", url)
        # Making first callback with callback being default parse
        func = self._func["parse"]
        self._scheduler.add_request(Request(url), func)
        self._scheduler.wait()

    # Default function to parse url
    def _parse(self, url: str):
        logger.info("Not implemented yet, did you use @app.parse decorator?")
        logger.info("Input was {}", url)

    # Default function to parse items
    def _item(self, itm):
        logger.info("Not implemented yet, did you use @app.parseItem decorator?")
        logger.info("Input was {}", itm)

    # Decorator to get the PARSE function
    def parse(self, func):

        def _get_parse(url):
            self._scheduler.used()
            logger.debug("Scheduling {}", url)
            ret = func(url)
            # If ret is not None it will be a yield
            if ret:
                for elem in ret:
                    if isinstance(elem, Item):
                        _item_func = self._func["item"]
                        self._scheduler.add_item(elem, _item_func)
                    elif isinstance(elem, Request):
                        _req_func = self._func["parse"]
                        self._scheduler.add_request(elem, _req_func)
                    else:
                        logger.error("Unknown element {}", elem)
            logger.debug("Scheduling done", url)
            self._scheduler.freed()

        self._func["parse"] = _get_parse

        def wrapper():
            pass

        return wrapper

    def parseItem(self, func):
        self._func["item"] = func

        def wrapper():
            pass

        return wrapper


