from fakapy import Fakapy, Request, Response, Item, logger

app = Fakapy()


@app.parse
def parse(response: Response):
    logger.info("Parsing func {}", response)
    logger.info("TEXT len: {}", len(response.text))

    for i in response.xpath('//div[@class="card border-0"]/a/@href'):
        logger.info("URL https://realpython.com{}", i)
        yield Request(f"https://realpython.com{i}")
    yield Item("TEST11")


@app.parse_item
def parse_item(item: Item):
    logger.info("GOOD ITEM {}", item)


# @app.parse
# def parse(request: Request):
#     yield Item("TEST11")


if __name__ == '__main__':
    app.run("https://realpython.com")
