from aiohttp import ClientResponse
from bs4 import BeautifulSoup
from loguru import logger
from lxml import html


class Response:
    def __init__(self, r: ClientResponse, text: str):
        self.r = r
        self.text = text
        self.response = r  # TODO precise type
        self._tree = None

    def xpath(self, xpath: str):
        if self.response is None:
            logger.error("xpath was called before GET")
            return []
        if self._tree is None:
            self._tree = html.fromstring(self.text.encode(self.response.charset, "ignore"))
        return self._tree.xpath(xpath)

    def __call__(self, *args, **kwargs):
        pass

    def soup(self):
        if self.response is None:
            logger.error("soup was called before GET")
            return BeautifulSoup("", 'html.parser')
        return BeautifulSoup(self.response.content, 'html.parser')
