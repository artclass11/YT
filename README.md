# Aset YouTube — Public Publication Archive

This repository is the public-safe index of Aset YouTube publishing activity.

- Channel: [Aset](https://www.youtube.com/channel/UCyQvyoHocWUexgxuyzRYGXg)
- Central production code and private operational ledger: [artclass11/YOUTUBE](https://github.com/artclass11/YOUTUBE)
- Daily index: [content-index.json](content-index.json)
- Dated publication reports: `YYYY-MM-DD/publishing-status.json`

Only public-safe metadata and final assets that have passed the DOCS release process may be placed here. This repository must never contain credentials, OAuth tokens, private customer data, unpublished third-party content, or unapproved media.

A status of `no_publication` or `blocked` means no video was approved or uploaded. Planned slot times are not Buffer bookings.

## Automated delivery

The complete public media and Buffer publishing contract is in [AUTOMATION_PIPELINE.md](AUTOMATION_PIPELINE.md). Release-ready packages live under dated folders; each format contains its MP4, thumbnail, captions, description, manifest, technical QA report and public rights manifest.

- Direct video URLs use `raw.githubusercontent.com`, never GitHub preview pages.
- [Validation workflow](.github/workflows/validate-public-media.yml) checks approved packages after commits.
- [Validator](scripts/validate_public_media.py) checks exact hashes, file integrity, MP4 streams, full decode and anonymous direct-download access.
- Only the authorized Aset publishing automation may submit approved assets to Buffer. The public repo is not permission to publish create-only brand lanes.
- Unapproved drafts, secrets, credentials and private reviewer evidence do not belong in this public repository.
