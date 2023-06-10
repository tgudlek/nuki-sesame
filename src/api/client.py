import os
from pathlib import Path
from typing import Optional

import requests

from src.api.errors.api_response_error import APIResponseError


class NukiClient:
    NUKI_API_BASE_URL = "https://api.nuki.io"
    DEFAULT_TOKEN_PATH = "~/.nuki/bearer_token"

    def __init__(self, token: str):
        self.token = token
        self.check_auth()

    def check_auth(self) -> None:
        response = self.get("/smartlock")
        if response.status_code != 200:
            raise APIResponseError("The token is invalid", response)

    @classmethod
    def load(cls, token_path: str = DEFAULT_TOKEN_PATH) -> "NukiClient":
        full_token_path = Path(token_path).expanduser()
        with open(full_token_path, "r") as token_file:
            token = token_file.read().strip()
        return cls(token)

    def store_locally(self, token_path: str = DEFAULT_TOKEN_PATH) -> None:
        full_token_path = Path(token_path).expanduser()

        os.makedirs(os.path.dirname(full_token_path), exist_ok=True)
        with open(full_token_path, "w") as token_file:
            token_file.write(self.token)
        os.chmod(
            full_token_path, 0o600
        )  # Permissions set to -rw------- (only owner can read and write)

    def _create_headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def get(self, path: str, query: Optional[dict] = None) -> requests.Response:
        url = f"{self.NUKI_API_BASE_URL}{path}"
        response = requests.get(url, headers=self._create_headers(), params=query)
        return response

    def post(
        self, path: str, body: Optional[dict] = None, query: Optional[dict] = None
    ) -> requests.Response:
        url = f"{self.NUKI_API_BASE_URL}{path}"
        response = requests.post(
            url, headers=self._create_headers(), params=query, json=body
        )
        return response

    def put(
        self, path: str, body: Optional[dict] = None, query: Optional[dict] = None
    ) -> requests.Response:
        url = f"{self.NUKI_API_BASE_URL}{path}"
        response = requests.put(
            url, headers=self._create_headers(), params=query, json=body
        )
        return response

    def delete(self, path: str, query: Optional[dict] = None) -> requests.Response:
        url = f"{self.NUKI_API_BASE_URL}{path}"
        response = requests.delete(url, headers=self._create_headers(), params=query)
        return response
