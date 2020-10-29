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

    def _schedule(self, func, input_value):
        self._scheduler.used()
        logger.debug("Scheduling {}", input_value)
        ret = func(input_value)
        self._parse_return(ret)
        logger.debug("Scheduling done", input_value)
        self._scheduler.freed()

    def _parse_return(self, return_value):
        # If ret is not None it will be a yield
        if return_value:
            for elem in return_value:
                if isinstance(elem, Item):
                    _item_func = self._func["item"]
                    self._scheduler.add_item(elem, _item_func)
                elif isinstance(elem, Request):
                    _req_func = self._func["parse"]
                    self._scheduler.add_request(elem, _req_func)
                else:
                    logger.error("Unknown element {}", elem)

    # Decorator to get the PARSE function
    def parse(self, func):

        def _get_parse(url):
            self._schedule(func, url)

        self._func["parse"] = _get_parse

        def wrapper():
            pass

        return wrapper

    # Decorator to get the PARSE items
    def parse_item(self, func):

        def _item_parse(item):
            self._schedule(func, item)

        self._func["item"] = _item_parse

        def wrapper():
            pass

        return wrapper
