from loguru import logger
from lxml import html


class Request:

    def __init__(self, url: str, callback=None):
        self.url = url
        self.text = ""
        self.response = None  # TODO precise type
        self._tree = None
        self.callback = callback

    def __str__(self):
        return f"Request({self.url})"

    def xpath(self, xpath):  # TODO move to client Response
        if self.response is None:
            logger.error("xpath was called before GET")
            return []
        if self._tree is None:
            self._tree = html.fromstring(self.text.encode(self.response.charset, "ignore"))
        return self._tree.xpath(xpath)
