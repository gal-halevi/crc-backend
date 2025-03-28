import os
from dataclasses import dataclass
import pytest
import requests
from lambda_visitor_counter import lambda_handler


REQUIRED_ENV_VARS = ["API_URL", "TABLE_NAME", "PRIMARY_KEY"]

@dataclass
class APIDetails:
    url: str
    headers: dict
    payload: dict


@pytest.fixture(scope="module")
def api_details():
    provided_env_vars = [var for var in REQUIRED_ENV_VARS if os.environ.get(var)]
    if len(provided_env_vars) != len(REQUIRED_ENV_VARS):
        pytest.fail(f"Missing required env vars! Required = {REQUIRED_ENV_VARS}. Received = {provided_env_vars}")
    return APIDetails(
        url=os.environ.get("API_URL"),
        headers={"Content-Type": "application/json"},
        payload={"tableName": os.environ.get("TABLE_NAME"),
                 "primaryKey": os.environ.get("PRIMARY_KEY")}
    )


def test_api_sanity(api_details):
    _send_valid_request(api_details)

def test_api_health(api_details):
    current_counter = _send_valid_request(api_details)["visitorCount"]
    assert current_counter < _send_valid_request(api_details)["visitorCount"]

def _send_valid_request(api_details):
    response = requests.post(url=api_details.url, headers=api_details.headers, json=api_details.payload)
    assert response.status_code == 200
    return response.json()

