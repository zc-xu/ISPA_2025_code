# Integrity Recheck, 2026-07-29

The archived payload was rechecked while establishing the revised-paper
baseline before thesis development.

- Source snapshot: `9721bec21bfb9bf5f2cb619849d163f4b451309b`
- Files listed in the source snapshot's `SHA256SUMS.txt`: 128
- Entries that already matched: 114
- Stale checksum entries corrected: 14
- Archived code, data, figures, manuscripts, and other payload files changed:
  none
- Final manifest entries, including this recheck record: 129
- Result after correcting the checksum metadata: 129 of 129 entries match

The corrected entries covered CSV evidence files, two duplicate SVG exports,
and one Markdown response audit. Duplicate copies produced identical actual
hashes. This confirms that the mismatch was in the checksum metadata rather
than a partial checkout or inconsistent duplicate payload.

Verification command:

```bash
cd research_archive/2026-07-22_round1
shasum -a 256 -c SHA256SUMS.txt
```
