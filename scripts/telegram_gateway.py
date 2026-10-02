"""Minimal Telegram gateway for dry-run previews and approved sends."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TELEGRAM_API_BASE = "https://api.telegram.org"


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def merged_env(root: Path) -> dict[str, str]:
    values = {key: value for key, value in os.environ.items() if value}
    values.update(load_env_file(root / ".env"))
    return values


def first_bullets(markdown: str, heading: str, limit: int = 3) -> list[str]:
    lines = markdown.splitlines()
    in_section = False
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped.lower() == f"## {heading}".lower()
            continue
        if in_section and stripped.startswith("- "):
            bullets.append(stripped[2:])
            if len(bullets) >= limit:
                break
    return bullets


def render_command_response(command: str, daily_status: str) -> str:
    normalized = command.strip().lower()
    if normalized == "/report":
        snapshot = first_bullets(daily_status, "Snapshot", limit=4)
        actions = first_bullets(daily_status, "Today Next Actions", limit=3)
        lines = ["Azzam daily report"]
        if snapshot:
            lines.append("")
            lines.append("Snapshot:")
            lines.extend(f"- {item}" for item in snapshot)
        if actions:
            lines.append("")
            lines.append("Next:")
            lines.extend(f"- {item}" for item in actions)
        return "\n".join(lines)

    if normalized == "/next":
        actions = first_bullets(daily_status, "Today Next Actions", limit=3)
        if not actions:
            return "No next action found in daily status."
        return "Next actions:\n" + "\n".join(f"- {item}" for item in actions)

    if normalized in {"/remake", "checklist", "/checklist"}:
        return (
            "Educational XAUUSD CHECKLIST:\n"
            "1. Bias: what is the session direction?\n"
            "2. Liquidity: where can price sweep traders?\n"
            "3. Trigger: what confirms entry?\n"
            "4. Invalidation: where is the setup wrong?\n"
            "5. Risk: what is the planned loss?\n\n"
            "Use this before studying a setup.\n"
            "Educational only. No signal. No guaranteed result."
        )

    if normalized == "/painpoints":
        return "Pain point workflow: collect comments -> tag pain -> create Short angle -> review before publish."

    if normalized == "/diagnose":
        return "Diagnose workflow: fetch stats -> rank remake candidates -> review guardrails -> choose one next action."

    return "Supported commands: /report, /next, /remake, /painpoints, /diagnose, CHECKLIST"


def telegram_post(url: str, payload: dict) -> dict:
    data = urlencode(payload).encode("utf-8")
    request = Request(url, data=data, method="POST")
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def telegram_get(url: str) -> dict:
    with urlopen(url) as response:
        return json.loads(response.read().decode("utf-8"))


def describe_telegram_error(error: Exception) -> str:
    if isinstance(error, HTTPError):
        if error.code == 404:
            return "Telegram API returned HTTP 404. Check that TELEGRAM_BOT_TOKEN is a valid bot token."
        return f"Telegram API returned HTTP {error.code}. Check bot permissions and request parameters."
    if isinstance(error, URLError):
        return f"Telegram API network error: {error.reason}"
    return f"Telegram gateway error: {type(error).__name__}"


def send_message(
    bot_token: str,
    chat_id: str,
    text: str,
    *,
    thread_id: str = "",
    approval: str = "",
    request_func=telegram_post,
) -> dict:
    if approval != "APPROVE":
        raise PermissionError("Refusing Telegram send without approval=APPROVE")
    url = f"{TELEGRAM_API_BASE}/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": "true"}
    if thread_id:
        payload["message_thread_id"] = thread_id
    return request_func(url, payload)


def get_updates(bot_token: str, request_func=telegram_get) -> dict:
    return request_func(f"{TELEGRAM_API_BASE}/bot{bot_token}/getUpdates")


def resolve_thread_id(cli_thread_id: str, env: dict[str, str]) -> str:
    return cli_thread_id or env.get("TELEGRAM_THREAD_ID", "")


def extract_chat_ids(updates: dict) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in updates.get("result", []):
        message = item.get("message") or item.get("channel_post") or {}
        chat = message.get("chat", {})
        if not chat.get("id"):
            continue
        rows.append(
            {
                "chat_id": str(chat.get("id", "")),
                "thread_id": str(message.get("message_thread_id", "")),
                "title": str(chat.get("title") or chat.get("username") or chat.get("first_name") or ""),
                "type": str(chat.get("type", "")),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Telegram gateway dry-run and approved sender")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--command", default="/report")
    parser.add_argument("--daily-status", type=Path, default=Path("outputs/reports/daily_status.md"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--approve", default="")
    parser.add_argument("--discover-chat-id", action="store_true")
    parser.add_argument("--thread-id", default="")
    args = parser.parse_args()

    root = args.root.resolve()
    env = merged_env(root)
    bot_token = env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = env.get("TELEGRAM_CHAT_ID", "")

    if args.discover_chat_id:
        if not bot_token:
            raise SystemExit("Missing TELEGRAM_BOT_TOKEN")
        try:
            rows = extract_chat_ids(get_updates(bot_token))
        except (HTTPError, URLError) as exc:
            raise SystemExit(describe_telegram_error(exc)) from exc
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    daily_status = (root / args.daily_status).read_text(encoding="utf-8") if (root / args.daily_status).exists() else ""
    text = render_command_response(args.command, daily_status)

    if args.dry_run or not args.send:
        print(text)
        return 0

    if not bot_token or not chat_id:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
    try:
        result = send_message(
            bot_token,
            chat_id,
            text,
            thread_id=resolve_thread_id(args.thread_id, env),
            approval=args.approve,
        )
    except (HTTPError, URLError) as exc:
        raise SystemExit(describe_telegram_error(exc)) from exc
    print(json.dumps({"ok": result.get("ok", False)}, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
