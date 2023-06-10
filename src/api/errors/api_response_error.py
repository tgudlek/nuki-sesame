import requests


class APIResponseError(Exception):
    def __init__(self, message: str, response: requests.Response):
        super(APIResponseError, self).__init__(
            f"{message}: Code<{response.status_code}>, Body: {response.json()}"
        )
