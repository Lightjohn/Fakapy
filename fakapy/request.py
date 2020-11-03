class Request:

    def __init__(self, url: str, callback=None):
        self.url = url
        self.text = ""
        self.callback = callback

    def __str__(self):
        return f"Request({self.url})"
