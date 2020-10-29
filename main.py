from fakapy import Fakapy, Request, Item
from fakapy import logger

app = Fakapy()


@app.parse
def parse(request: Request):
    logger.info("Parsing func {}", request)
    logger.info("TEXT len: {}", len(request.text))

    for i in request.xpath('//div[@class="card border-0"]/a/@href'):
        logger.info("URL https://realpython.com{}", i)
        yield Request(f"https://realpython.com{i}")
    yield Item("TEST11")

@app.parse_item
def parse_item(itm: Item):
    logger.info("GOOD ITEM {}", itm)


# @app.parse
# def parse(request: Request):
#     yield Item("TEST11")


if __name__ == '__main__':
    app.run("https://realpython.com")
