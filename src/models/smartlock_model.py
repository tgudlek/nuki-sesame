from __future__ import annotations
from dataclasses import dataclass
from typing import List
from src.api.client import NukiClient
from src.api.errors.api_response_error import APIResponseError


@dataclass
class SmartlockModel:
    id: int
    name: str

    def __str__(self):
        return f"Smartlock(id={self.id}, name='{self.name}')"

    @classmethod
    def parse_from_json(cls, json: dict) -> SmartlockModel:
        return cls(json["smartlockId"], json["name"])

    @classmethod
    def get_all(cls, nuki_client: NukiClient) -> List[SmartlockModel]:
        response = nuki_client.get("/smartlock")
        if response.status_code != 200:
            raise APIResponseError("Smartlocks could not be fetched", response)

        return [cls.parse_from_json(json) for json in response.json()]

    @classmethod
    def get_by_id(cls, nuki_client: NukiClient, smartlock_id: int) -> SmartlockModel:
        response = nuki_client.get(f"/smartlock/{smartlock_id}")
        if response.status_code != 200:
            raise APIResponseError("Smartlock could not be fetched", response.json())

        return cls.parse_from_json(response.json())

    def trigger_lock(self, nuki_client: NukiClient) -> None:
        response = nuki_client.post(f"/smartlock/{self.id}/action/lock")
        if response.status_code != 204:
            raise APIResponseError(f"Smartlock could not be locked", response)

    def trigger_unlock(self, nuki_client: NukiClient) -> None:
        response = nuki_client.post(f"/smartlock/{self.id}/action/unlock")
        if response.status_code != 204:
            raise APIResponseError(f"Smartlock could not be unlocked", response)
