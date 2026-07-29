# Revised-Paper Baseline Before Thesis Development

This milestone identifies the repository state that corresponds to the MOS2
round-one revised manuscript and reviewer-response package, before any
thesis-specific algorithm or experiment development.

## Canonical Snapshot

- Commit: `9721bec21bfb9bf5f2cb619849d163f4b451309b`
- Original revision tag: `revision-round1-2026-07-22`
- Pre-thesis tag: `revised-paper-pre-thesis-2026-07-29`
- Archive branch: `archive/revised-paper-pre-thesis-2026-07-29`
- Frozen research package: `research_archive/2026-07-22_round1/`

The pre-thesis tag points directly to the canonical snapshot commit. The
archive branch preserves the same code, experiment data, figures, and
manuscript artifacts together with the milestone and verified integrity
metadata added during archival. Both references exclude later local-only Mac
compatibility changes.

## Branch Roles After This Milestone

- `main` contains reviewed, reproducible milestones.
- `dev` is the integration branch for thesis development.
- New thesis work starts on focused branches created from the current remote
  `dev`, and returns to `dev` only after verification.
- A verified thesis milestone is merged from `dev` into `main`.
- The pre-thesis tag and archive branch remain unchanged.

## Recovery and Comparison

Inspect the exact source snapshot without changing a branch:

```bash
git switch --detach revised-paper-pre-thesis-2026-07-29
```

Create a recovery branch from the verification-ready archive:

```bash
git switch -c recovery/revised-paper archive/revised-paper-pre-thesis-2026-07-29
```

Compare later thesis development against this baseline:

```bash
git diff revised-paper-pre-thesis-2026-07-29..dev
```
