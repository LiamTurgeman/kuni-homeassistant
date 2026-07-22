"""Constants for the KUNI integration."""

from datetime import timedelta

DOMAIN = "kuni"

CONF_CLIENT_ID = "client_id"
CONF_REFRESH_TOKEN = "refresh_token"
CONF_ORGANIZATION_ID = "organization_id"
CONF_DEVICE_ID = "device_id"

TOKEN_URL = (
    "https://aroma-prod-end-users.auth.us-east-1."
    "amazoncognito.com/oauth2/token"
)

API_BASE_URL = (
    "https://api.aroma-republic.co.il/"
    "mobile-app/api/v1"
)

DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

DEFAULT_RUN_DURATION_MINUTES = 120
MIN_RUN_DURATION_MINUTES = 1
MAX_RUN_DURATION_MINUTES = 1440

PLATFORMS = [
    "switch",
    "number",
    "select",
    "sensor",
    "button",
]