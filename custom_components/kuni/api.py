"""API client for the KUNI integration."""

from __future__ import annotations

import json
from typing import Any
import urllib.error
import urllib.parse
import urllib.request

from .const import API_BASE_URL, TOKEN_URL


class KuniApiError(RuntimeError):
    """Raised when communication with KUNI fails."""


class KuniAuthError(KuniApiError):
    """Raised when KUNI authentication fails."""


class KuniApiClient:
    """Client for Amazon Cognito and the KUNI cloud API."""

    def __init__(
        self,
        client_id: str,
        refresh_token: str,
        organization_id: str,
        device_id: str,
        timeout: int = 20,
    ) -> None:
        self._client_id = client_id
        self._refresh_token = refresh_token
        self._organization_id = organization_id
        self._device_id = device_id
        self._timeout = timeout

    def _refresh_tokens(self) -> tuple[str, str]:
        """Exchange the refresh token for fresh ID and access tokens."""
        body = urllib.parse.urlencode(
            {
                "grant_type": "refresh_token",
                "client_id": self._client_id,
                "refresh_token": self._refresh_token,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            TOKEN_URL,
            data=body,
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self._timeout,
            ) as response:
                payload = json.load(response)

        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )
            raise KuniAuthError(
                f"Cognito returned HTTP {exc.code}: {error_body}"
            ) from exc

        except urllib.error.URLError as exc:
            raise KuniApiError(
                f"Could not reach Cognito: {exc.reason}"
            ) from exc

        try:
            return payload["id_token"], payload["access_token"]
        except KeyError as exc:
            raise KuniAuthError(
                "Cognito response did not contain the expected tokens."
            ) from exc

    def _headers(self) -> dict[str, str]:
        """Return authenticated headers for the KUNI API."""
        id_token, access_token = self._refresh_tokens()

        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "idtoken": id_token,
            "organizationid": self._organization_id,
        }

    def _request(
        self,
        url: str,
        method: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        """Perform an authenticated KUNI API request."""
        body = None

        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers=self._headers(),
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self._timeout,
            ) as response:
                response_text = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode(
                "utf-8",
                errors="replace",
            )

            if exc.code in (401, 403):
                raise KuniAuthError(
                    f"KUNI rejected authentication: {error_body}"
                ) from exc

            raise KuniApiError(
                f"KUNI returned HTTP {exc.code}: {error_body}"
            ) from exc

        except urllib.error.URLError as exc:
            raise KuniApiError(
                f"Could not reach KUNI: {exc.reason}"
            ) from exc

        if not response_text:
            return None

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return response_text

    def get_status(self) -> dict[str, dict[str, Any]]:
        """Return the current KUNI device state."""
        url = (
            f"{API_BASE_URL}/devices/{self._device_id}/shadow/"
            f"?id={self._device_id}"
        )

        payload = self._request(
            url=url,
            method="GET",
        )

        return {
            item["name"]: {
                "desired": item.get("desired"),
                "reported": item.get("reported"),
            }
            for item in payload
        }

    def set_value(self, name: str, value: Any) -> Any:
        """Update a KUNI shadow property."""
        url = (
            f"{API_BASE_URL}/devices/"
            f"{self._device_id}/shadow/update/"
        )

        return self._request(
            url=url,
            method="PUT",
            payload={
                "name": name,
                "value": value,
            },
        )

    def turn_on(self) -> Any:
        """Turn the diffuser on."""
        return self.set_value("power", 1)

    def turn_off(self) -> Any:
        """Turn the diffuser off."""
        return self.set_value("power", 0)

    def turn_on_for(self, seconds: int) -> Any:
        """Turn the diffuser on for a number of seconds."""
        if seconds <= 1:
            raise ValueError("Timer must be longer than one second.")

        return self.set_value("power", seconds)

    def set_intensity(self, intensity: int) -> Any:
        """Set intensity from 0 to 6."""
        if not 0 <= intensity <= 6:
            raise ValueError("Intensity must be between 0 and 6.")

        return self.set_value("intensity", intensity)

    def set_position(self, position: int) -> Any:
        """Select capsule position 0, 1, or 2."""
        if position not in (0, 1, 2):
            raise ValueError("Position must be 0, 1, or 2.")

        return self.set_value("position", position)