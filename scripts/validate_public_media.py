#!/usr/bin/env python3
"""Validate release-approved Aset YouTube packages in the public YT repository.

This is a technical integrity check only. It does not grant copyright permission,
approve editorial claims, or replace DOCS release gates.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVED = {"approved", "machine_approved"}
RAW_BASE = "https://raw.githubusercontent.com/artclass11/YT/main/"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def run_json(command: list[str]) -> dict:
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        fail(f"command failed: {' '.join(command)} ({exc})")


def direct_url_check(url: str) -> None:
    if not url.startswith(RAW_BASE):
        fail(f"public_video_url must use the exact raw GitHub base: {url}")
    request = urllib.request.Request(url, method="GET", headers={"Range": "bytes=0-0", "User-Agent": "Aset-Public-Media-Validator/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200 and response.status != 206:
                fail(f"raw URL returned HTTP {response.status}: {url}")
            if int(response.headers.get("Content-Length", "0") or "0") <= 0:
                fail(f"raw URL has no positive Content-Length: {url}")
            mime = (response.headers.get("Content-Type") or "").split(";")[0].lower()
            if mime != "video/mp4":
                fail(f"raw URL MIME is {mime!r}, expected video/mp4")
            response.read(1)
    except (urllib.error.URLError, TimeoutError) as exc:
        fail(f"raw URL is not anonymously downloadable: {exc}")


def validate_manifest(path: Path) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in {path}: {exc}")

    state = str(data.get("release_state", "")).lower()
    if state not in APPROVED:
        print(f"SKIP {path}: release_state={state or 'missing'} (not release-ready)")
        return

    for key in ("date", "stream", "format", "artifact", "public_video_url", "qa_report", "rights_manifest"):
        if key not in data:
            fail(f"{path}: missing required field {key}")

    artifact = data["artifact"]
    required = ("video", "thumbnail", "captions", "description", "sha256", "size_bytes",
                "duration_seconds", "width", "height", "fps", "audio_streams")
    for key in required:
        if key not in artifact:
            fail(f"{path}: artifact missing {key}")

    def local_file(value: str, label: str) -> Path:
        candidate = (path.parent / value).resolve()
        if ROOT.resolve() not in candidate.parents:
            fail(f"{path}: {label} must stay inside repository")
        if not candidate.is_file() or candidate.stat().st_size <= 0:
            fail(f"{path}: missing/empty {label}: {value}")
        return candidate

    video = local_file(artifact["video"], "video")
    local_file(artifact["thumbnail"], "thumbnail")
    local_file(artifact["captions"], "captions")
    local_file(artifact["description"], "description")
    local_file(data["qa_report"], "QA report")
    local_file(data["rights_manifest"], "rights manifest")

    size = video.stat().st_size
    if size != int(artifact["size_bytes"]):
        fail(f"{path}: size mismatch ({size} != {artifact['size_bytes']})")
    if size >= 100 * 1024 * 1024:
        fail(f"{path}: video must remain below GitHub's 100 MB file limit")

    digest = hashlib.sha256(video.read_bytes()).hexdigest()
    if digest.lower() != str(artifact["sha256"]).lower():
        fail(f"{path}: SHA-256 mismatch")

    probe = run_json(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)])
    streams = probe.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    if len(videos) != 1:
        fail(f"{path}: expected exactly one video stream")
    if len(audios) != int(artifact["audio_streams"]):
        fail(f"{path}: audio stream count mismatch")
    v = videos[0]
    if int(v.get("width", 0)) != int(artifact["width"]) or int(v.get("height", 0)) != int(artifact["height"]):
        fail(f"{path}: frame size mismatch")
    if float(probe.get("format", {}).get("duration", 0)) <= 0:
        fail(f"{path}: invalid duration")
    actual_duration = float(probe["format"]["duration"])
    if not math.isclose(actual_duration, float(artifact["duration_seconds"]), rel_tol=0.02, abs_tol=0.75):
        fail(f"{path}: duration mismatch ({actual_duration} vs {artifact['duration_seconds']})")
    fps_raw = v.get("avg_frame_rate", "0/1")
    num, den = fps_raw.split("/", 1)
    actual_fps = float(num) / max(float(den), 1.0)
    if not math.isclose(actual_fps, float(artifact["fps"]), rel_tol=0.02, abs_tol=0.5):
        fail(f"{path}: frame-rate mismatch ({actual_fps} vs {artifact['fps']})")

    subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"],
                   check=True, capture_output=True)
    expected_url = RAW_BASE + video.relative_to(ROOT).as_posix()
    if data["public_video_url"] != expected_url:
        fail(f"{path}: public_video_url does not match exact committed video path")
    direct_url_check(expected_url)
    print(f"PASS {path}: {artifact['sha256']} ({size} bytes), {actual_duration:.2f}s, {artifact['width']}x{artifact['height']} @ {actual_fps:.2f}fps")


def main() -> None:
    manifests = sorted(ROOT.glob("20??-??-??/**/manifest.json"))
    if not manifests:
        print("No release manifests found; no media is eligible for publication.")
        return
    for manifest in manifests:
        validate_manifest(manifest)


if __name__ == "__main__":
    main()
