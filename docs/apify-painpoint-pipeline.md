# Apify Comments → Pain-Point Pipeline

## Status

- MCP integration: local configuration; official `@apify/actors-mcp-server`.
- Actor scope: allowlist only.
- Token: must be supplied via YouTube profile/project `.env`; never committed.
- Paid/bulk run: requires Alan's approval.
- First real scrape: not executed until token, source list and item limit are approved.

## Allowed Actors

- YouTube: `streamers/youtube-comments-scraper`
- TikTok: `clockworks/tiktok-comments-scraper`
- Instagram: `apify/instagram-comment-scraper`
- Facebook: `apify/facebook-comments-scraper`

Actor availability, input schema, pricing and platform terms must be checked again before each first production run. A configured Actor is not proof that a scrape succeeded.

## Secure token setup

Run locally in the YouTube profile only:

```bash
hermes config env-path
```

Open that file and add:

```text
APIFY_TOKEN=<token entered locally by Alan>
```

Do not paste the token into chat, MCP config, Run Record, source code or Git.

## Commands

```bash
hermes mcp list
hermes mcp test apify
python scripts/extract_painpoints.py <apify-json-or-jsonl> --output-dir outputs/painpoints/<run-id>
```

## Data flow

```text
Approved source list + per-source limit
→ Apify Actor
→ raw immutable JSON/JSONL
→ normalize + deduplicate
→ privacy hash author identifier
→ deterministic pain-point candidates
→ content_bridge semantic review/clustering
→ Alan review
→ approved backlog
→ optional Channel Brain update
```

## Required raw evidence

Every candidate must preserve:

- Platform.
- Content URL/ID.
- Comment ID/text.
- Engagement when available.
- Timestamp when available.
- Actor and Actor run ID.

Unsupported/missing fields are marked missing; they are never invented.

## Outputs

- `normalized_comments.csv`: normalized, deduplicated comments.
- `painpoint_candidates.csv`: source-backed candidate rows with transparent scoring.
- `painpoint_report.md`: category counts, top evidence and missing-data notes.

The local extractor is a deterministic triage stage, not a claim that it understands intent perfectly. `content_bridge` must review ambiguous language before a topic is promoted to the backlog.

## Guardrails

- Public content only unless explicit authorization exists.
- Respect platform terms, applicable privacy law and Actor policy.
- Minimize author data; store only a SHA-256 hash when an identifier is available.
- No private messages, login-wall bypass, fake engagement or seeding.
- No paid/bulk run without approval containing platform, sources, maximum items and budget cap.
- Raw comments do not automatically update Channel Brain, Sheet or published content.
- Trading claims from comments are audience statements, not verified financial facts.

## Approval request format

```text
Workflow: WF02
Mode: L1 external read / potentially paid
Platforms: YouTube, TikTok, Instagram, Facebook
Sources: <exact URLs/accounts>
Maximum items: <per source and total>
Estimated cost: <Actor pricing evidence>
Purpose: pain-point research
Retention: <raw/normalized retention period>
Approval required: YES
```
