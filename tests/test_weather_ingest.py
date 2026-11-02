import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from ingestion import weather_ingest

FAKE_RESPONSE = {"current": {"temperature_2m": 21.5, "wind_speed_10m": 4.2}}


def _mock_ok_response():
    mock = MagicMock()
    mock.json.return_value = FAKE_RESPONSE
    mock.raise_for_status.return_value = None
    return mock


def test_fetch_weather_returns_json():
    with patch("ingestion.weather_ingest.requests.get", return_value=_mock_ok_response()):
        result = weather_ingest.fetch_weather(33.749, -84.388)
    assert result == FAKE_RESPONSE


def test_fetch_weather_retries_then_succeeds():
    side_effects = [requests.ConnectionError("boom"), _mock_ok_response()]
    with patch("ingestion.weather_ingest.requests.get", side_effect=side_effects), \
         patch("ingestion.weather_ingest.time.sleep"):  # skip real waiting
        result = weather_ingest.fetch_weather(33.749, -84.388)
    assert result == FAKE_RESPONSE


def test_fetch_weather_raises_after_max_retries():
    with patch("ingestion.weather_ingest.requests.get",
               side_effect=requests.ConnectionError("down")), \
         patch("ingestion.weather_ingest.time.sleep"):
        with pytest.raises(requests.RequestException):
            weather_ingest.fetch_weather(33.749, -84.388)


def test_save_raw_writes_valid_json(tmp_path):
    path = weather_ingest.save_raw(FAKE_RESPONSE, "atlanta", raw_dir=tmp_path)
    assert path.exists()
    assert path.name.startswith("atlanta_")
    assert json.loads(path.read_text()) == FAKE_RESPONSE

def test_correct_coordinates_are_used():
    with patch("ingestion.weather_ingest.requests.get", return_value=_mock_ok_response()) as mock_get:
        weather_ingest.fetch_weather(33.749, -84.388)
    mock_get.assert_called_once()
    call_args = mock_get.call_args[1]
    assert call_args["params"]["latitude"] == 33.749
