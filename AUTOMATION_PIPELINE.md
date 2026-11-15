# Aset YouTube public media and publishing pipeline

Repository: `artclass11/YT` (public), branch `main`.
Channel: [Aset](https://www.youtube.com/channel/UCyQvyoHocWUexgxuyzRYGXg).

This repository is the canonical public delivery store and publication archive for the Aset YouTube publisher. The private `artclass11/YOUTUBE` and `artclass11/DOCS` repositories remain the place for production code, private operational records, credentials, and internal QA evidence.

## Daily package layout

Only release-approved, public-safe deliverables may be committed:

```text
YYYY-MM-DD/
  publishing-status.json
  <stream>/
    <format>/
      video.mp4
      thumbnail.jpg
      captions.srt
      description.md
      manifest.json
      qa-report.json
      rights-manifest.json
```

Allowed stream slugs: `au-invest`, `brandstudio`, `arcstudio91`, `aset-original`. Any create-only brand lane must remain out of the publishing queue unless the saved authorization explicitly changes.

The package is immutable after upload approval: if any media bytes change, recompute SHA-256, rerun all applicable release gates, and create a new manifest/commit before publishing.

## Required manifest

Each format directory must include `manifest.json` with:
- `schema_version`, `date`, `stream`, `format`, and `release_state`
- `artifact.video`, `artifact.thumbnail`, `artifact.captions`, `artifact.description`
- `artifact.sha256` and `artifact.size_bytes` for the exact MP4
- `artifact.duration_seconds`, `artifact.width`, `artifact.height`, `artifact.fps`, and `artifact.audio_streams`
- `public_video_url`, `qa_report`, and `rights_manifest`
- `machine_approval` with `decision: "PASS"`, timestamp, score and evidence reference whenever the relevant saved release policy permits machine approval.

`release_state` must be `machine_approved` or `approved` before media can be scheduled. A human-review-required lane must include its required human approval in the private DOCS evidence; machine approval alone does not override it. A held/failed item must not contain a public release-ready MP4.

## Direct media URL

Use only the stable raw URL, derived from the exact committed path:

`https://raw.githubusercontent.com/artclass11/YT/main/YYYY-MM-DD/<stream>/<format>/video.mp4`

The automation must verify this URL anonymously after the commit: HTTP 200, non-zero content length, `video/mp4`, and matching SHA-256/size. A GitHub blob/tree page, archive ZIP, local path, signed temporary URL, or unverified CDN URL is not a publishing asset URL.

## Required publication sequence

1. Research, script, render and complete the brand-specific DOCS release process in the authorized production worker.
2. Run the DOCS policy/release validators against the exact final MP4. Record the final SHA-256, file size, duration, streams, dimensions, frame rate, rights evidence and approval record. Do not invent successful checks.
3. Copy the approved public-safe package into the dated layout above in this repository. Use an authenticated Git client or a configured GitHub Actions/self-hosted worker with write access. Keep credentials in the runner's secret store or credential helper; never place tokens in files, URLs, command output or commits.
4. Commit and push the package to `main`. Binary MP4 files must be committed as actual binary bytes, not as base64 text in a `.txt`/JSON file. Keep individual files below GitHub's 100 MB hard limit; prefer substantially smaller MP4s. Do not use Git LFS unless its raw-download behaviour has been separately verified for Buffer.
5. Update `publishing-status.json` and root `content-index.json` in the same or a subsequent verified commit. Preserve older entries and never overwrite a different date or prior post record.
6. Pass the exact raw MP4 URL to Buffer only after an anonymous direct-download check and duplicate-history check. Re-read the live Buffer account/channel; use only the connected, unlocked Aset YouTube channel. Use brand-specific title, description, category and disclosures.
7. Verify the exact Buffer post by ID. `scheduled` means scheduled, not published. Report published only when Buffer returns `sent` and `sentAt`, with a verified YouTube permalink.
8. Record Buffer post ID, provider status, due/sent time, permalink and raw media URL in the dated publication status. Update the daily index without erasing prior dates.

## Public/private boundary

Never commit credentials, OAuth tokens, API keys, private customer data, unpublished third-party footage, private reviewer data, or internal account identifiers. Public manifests may contain public source URLs, factual QA summaries, public release scores, file hashes and platform post IDs only when safe. Keep full internal evidence in the authorized private DOCS/YOUTUBE repository.

Do not place a draft, music-only asset where narration is required, incomplete render, unlicensed asset, failed decode, or unapproved video in this public repository. If the production runner cannot transfer actual binary bytes to GitHub, mark the item `BLOCKED: public GitHub binary upload unavailable`; do not invent a raw URL and do not silently fall back to a different host.

## Validation

The GitHub Actions workflow `.github/workflows/validate-public-media.yml` runs `scripts/validate_public_media.py` after changes. It checks approved package manifests, file presence, SHA-256, dimensions/streams/duration, full FFmpeg decode and the permanent raw URL. This technical workflow supplements—not replaces—the DOCS factual, licensing, editorial, privacy, language, platform and creative release gates.
