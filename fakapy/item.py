class Item:

    def __init__(self, url):
        self.url = url

    def __str__(self):
        return f"Item({self.url})"


