from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from src.api.client import NukiClient
from src.api.errors.api_response_error import APIResponseError
from src.models.smartlock_model import SmartlockModel


class SmartlockAuthorizationModel:
    def __init__(
        self, auth_id: int, name: str, auth_type: str, code: Optional[int] = None
    ):
        self.id = auth_id
        self.name = name
        self.type = auth_type
        self.code = code

    def __str__(self):
        return f"SmartlockAuthorizationModel(id={self.id}, name={self.name}, type={self.type}, code={self.code})"

    @classmethod
    def parse_from_json(cls, json: dict) -> SmartlockAuthorizationModel:
        return cls(json["id"], json["name"], json["type"], json.get("code"))

    @classmethod
    def get_all(
        cls, nuki_client: NukiClient, smartlock: SmartlockModel
    ) -> List[SmartlockAuthorizationModel]:
        response = nuki_client.get(
            f"/smartlock/{smartlock.id}/auth", query={"types": "13"}
        )
        if response.status_code != 200:
            raise APIResponseError("Authorizations could not be fetched", response)

        return [cls.parse_from_json(json) for json in response.json()]

    @classmethod
    def get_by_id(
        cls, nuki_client: NukiClient, auth_id: int
    ) -> SmartlockAuthorizationModel:
        response = nuki_client.get(f"/auth/{auth_id}")
        if response.status_code != 200:
            raise APIResponseError("Authorization could not be fetched", response)

        return cls.parse_from_json(response.json())

    @classmethod
    def get_by_code(
        cls, nuki_client: NukiClient, smartlock: SmartlockModel, code: int
    ) -> SmartlockAuthorizationModel:
        all_authorizations = cls.get_all(nuki_client=nuki_client, smartlock=smartlock)
        target_authorization = next(
            (auth for auth in all_authorizations if auth.code == code), None
        )
        if not target_authorization:
            raise LookupError(
                f"Target code {code} could not be found among authorizations of {smartlock}: "
                f"{[str(auth) for auth in all_authorizations]}"
            )
        return target_authorization

    @staticmethod
    def _add_time_unit(start_time: datetime, duration: str) -> datetime:
        if duration.endswith("d"):
            return start_time + timedelta(days=int(duration[:-1]))
        elif duration.endswith("h"):
            return start_time + timedelta(hours=int(duration[:-1]))
        elif duration.endswith("m"):
            return start_time + timedelta(minutes=int(duration[:-1]))
        else:
            raise ValueError(f"Unknown duration format: {duration}")

    @classmethod
    def create_code(
        cls,
        nuki_client: NukiClient,
        smartlock: SmartlockModel,
        code: int,
        duration: str,
    ) -> None:
        start_time = datetime.now()
        end_time = cls._add_time_unit(start_time, duration)

        payload = {
            "name": f"NukiCLI -- {code}",
            "allowedFromDate": start_time.astimezone(timezone.utc).isoformat(),
            "allowedUntilDate": end_time.astimezone(timezone.utc).isoformat(),
            "allowedWeekDays": 127,
            "remoteAllowed": True,
            "smartActionsEnabled": False,
            "type": 13,
            "code": code,
            "smartlockIds": [smartlock.id],
        }

        response = nuki_client.put(f"/smartlock/{smartlock.id}/auth", body=payload)
        if response.status_code != 204:
            raise APIResponseError(
                "Authorization could not be created", response.json()
            )

    @staticmethod
    def delete(nuki_client: NukiClient, smartlock: SmartlockModel, code: int) -> None:
        auth = SmartlockAuthorizationModel.get_by_code(nuki_client, smartlock, code)
        if not auth:
            raise Exception(f"Authorization with code {code} not found.")

        response = nuki_client.delete(f"/smartlock/{smartlock.id}/auth/{auth.id}")
        if response.status_code != 204:
            raise APIResponseError(
                f"Authorization could not be deleted", response.json()
            )
