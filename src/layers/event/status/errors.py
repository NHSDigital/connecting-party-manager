class StatusNotOk(Exception):
    def __init__(self, exception: Exception):
        super().__init__(f"{exception}")
