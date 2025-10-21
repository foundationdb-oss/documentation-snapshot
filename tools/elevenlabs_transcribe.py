#!/usr/bin/env python3
"""
Temporary helper to transcribe Summit 2018 audio assets with the ElevenLabs API.

Reads the API key from `.11labs.key`, submits each MP3 under
`sources/youtube/foundationdb-summit-2018/audio/`, and writes the raw JSON
response into `sources/youtube/foundationdb-summit-2018/transcripts/`.
"""

from __future__ import annotations

import json
import os
import pathlib
import time
from typing import Iterable

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
API_KEY_PATH = ROOT / ".11labs.key"
AUDIO_DIR = ROOT / "sources" / "youtube" / "foundationdb-summit-2018" / "audio"
TRANSCRIPTS_DIR = ROOT / "sources" / "youtube" / "foundationdb-summit-2018" / "transcripts"
API_URL = "https://api.elevenlabs.io/v1/speech-to-text"
MODEL_ID = "scribe_v1"
SLEEP_SECONDS = 1.0  # brief pause to be polite with the API


def load_api_key(path: pathlib.Path) -> str:
    key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError(f"API key file {path} is empty")
    return key


def iter_mp3_files(directory: pathlib.Path) -> Iterable[pathlib.Path]:
    return sorted(p for p in directory.glob("*.mp3") if p.is_file())


def transcribe_file(api_key: str, mp3_path: pathlib.Path, out_path: pathlib.Path) -> None:
    if out_path.exists():
        print(f"Skipping existing transcript: {out_path.name}")
        return

    print(f"Transcribing: {mp3_path.name}")
    headers = {"xi-api-key": api_key}
    data = {"model_id": MODEL_ID}
    with mp3_path.open("rb") as f:
        files = {"file": (mp3_path.name, f, "audio/mpeg")}
        response = requests.post(API_URL, headers=headers, data=data, files=files, timeout=600)
    response.raise_for_status()
    payload = response.json()

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved transcript: {out_path.name}")


def main() -> None:
    if not AUDIO_DIR.exists():
        raise RuntimeError(f"Audio directory not found: {AUDIO_DIR}")

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key(API_KEY_PATH)

    for mp3_path in iter_mp3_files(AUDIO_DIR):
        out_path = TRANSCRIPTS_DIR / (mp3_path.stem + ".json")
        try:
            transcribe_file(api_key, mp3_path, out_path)
        except requests.HTTPError as exc:
            print(f"HTTP error for {mp3_path.name}: {exc.response.status_code} {exc.response.text}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Failed to transcribe {mp3_path.name}: {exc}")
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
