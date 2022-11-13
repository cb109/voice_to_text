import os
import json

import pytest


@pytest.fixture
def audio_file():
    here = os.path.dirname(__file__)
    return os.path.join(here, "tests_data", "taunt.wav")


@pytest.fixture
def mocked_replicate_service(monkeypatch):
    def mocked_transcribe(*args, **kwargs):
        return {"text": "Now go away or I shall taunt you a second time!", "time": 3.05}

    monkeypatch.setattr(
        "shared_whispers.core.views._transcribe_audio_file_with_replicate",
        mocked_transcribe,
    )


def test_api_transcribe_audio_file(client, audio_file, mocked_replicate_service):
    url = "/api/transcribe/"

    with open(audio_file, "rb") as audio_content:
        payload = {
            "token": "ABCDE",
            "model": "tiny",
            "audio": audio_content,
        }
        response = client.post(url, payload)

    assert json.loads(response.content) == {
        "text": "Now go away or I shall taunt you a second time!",
        "time": 3.05,
    }
