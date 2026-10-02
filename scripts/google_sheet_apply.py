"""Apply a prepared Google Sheets batchUpdate payload and verify read-back."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

SHEETS_API_BASE = "https://sheets.googleapis.com/v4/spreadsheets"
TARGET_SHEET_TITLE_ALIASES = {
    "Video Inventory": ["video_inventory", "Video Inventory"],
    "Remake Candidates": ["remake_plan", "remake_candidates", "Remake Candidates"],
    "Shorts Pipeline": ["shorts_pipeline", "Shorts Pipeline", "content_calendar"],
}


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
    values = load_env_file(root / ".env")
    values.update({key: value for key, value in os.environ.items() if value})
    return values


def resolve_google_credentials_path(env: dict[str, str]) -> str:
    return env.get("GOOGLE_SHEETS_CREDENTIALS_PATH") or env.get("GOOGLE_APPLICATION_CREDENTIALS", "")


def column_letter(column_count: int) -> str:
    if column_count < 1:
        raise ValueError("column_count must be positive")
    letters = ""
    value = column_count
    while value:
        value, remainder = divmod(value - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def build_readback_range(summary_item: dict) -> str:
    row_count = int(summary_item.get("written_rows") or 0) + 1
    column_count = int(summary_item.get("column_count") or 0)
    target = str(summary_item.get("actual_sheet_title") or summary_item["target"]).replace("'", "''")
    return f"'{target}'!A1:{column_letter(column_count)}{row_count}"


def request_json(method: str, url: str, token: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/json")
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def describe_google_http_error(error: HTTPError) -> str:
    body = error.read().decode("utf-8", errors="replace")
    try:
        parsed = json.loads(body)
        body = json.dumps(parsed, ensure_ascii=False)
    except json.JSONDecodeError:
        pass
    return f"HTTP {error.code} {error.reason}: {body}"


def get_access_token(env: dict[str, str]) -> str:
    if env.get("GOOGLE_ACCESS_TOKEN"):
        return env["GOOGLE_ACCESS_TOKEN"]

    credentials_path = resolve_google_credentials_path(env)
    if credentials_path:
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request as GoogleAuthRequest
        except ImportError as exc:
            raise RuntimeError(
                "Google credentials path is configured, but google-auth is not installed. "
                "Install google-auth or set GOOGLE_ACCESS_TOKEN."
            ) from exc
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        credentials.refresh(GoogleAuthRequest())
        return credentials.token

    try:
        completed = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            "No Google access token available. Set GOOGLE_ACCESS_TOKEN, "
            "GOOGLE_SHEETS_CREDENTIALS_PATH, or GOOGLE_APPLICATION_CREDENTIALS."
        ) from exc
    return completed.stdout.strip()


def fetch_spreadsheet_metadata(
    spreadsheet_id: str,
    token: str,
    request_func: Callable[[str, str, str, dict | None], dict] = request_json,
) -> dict:
    url = f"{SHEETS_API_BASE}/{spreadsheet_id}?fields=sheets(properties(sheetId,title))"
    return request_func("GET", url, token, None)


def sheet_id_map_from_metadata(metadata: dict) -> dict[str, int]:
    sheet_ids: dict[str, int] = {}
    for sheet in metadata.get("sheets", []):
        properties = sheet.get("properties", {})
        title = properties.get("title")
        sheet_id = properties.get("sheetId")
        if title and sheet_id is not None:
            sheet_ids[str(title)] = int(sheet_id)
    return sheet_ids


def candidate_sheet_titles(target: str) -> list[str]:
    candidates = TARGET_SHEET_TITLE_ALIASES.get(target, [target])
    unique_candidates: list[str] = []
    for candidate in [*candidates, target]:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)
    return unique_candidates


def preferred_sheet_title(target: str) -> str:
    return candidate_sheet_titles(target)[0]


def resolve_sheet_title(target: str, sheet_ids_by_title: dict[str, int]) -> str:
    for candidate in candidate_sheet_titles(target):
        if candidate in sheet_ids_by_title:
            return candidate

    normalized = {title.lower(): title for title in sheet_ids_by_title}
    for candidate in candidate_sheet_titles(target):
        match = normalized.get(candidate.lower())
        if match:
            return match

    return ""


def create_missing_sheets(
    spreadsheet_id: str,
    token: str,
    payload: dict,
    metadata: dict,
    request_func: Callable[[str, str, str, dict | None], dict] = request_json,
) -> list[dict]:
    if "sheets" not in metadata:
        return []

    sheet_ids_by_title = sheet_id_map_from_metadata(metadata)
    created: list[dict] = []
    for item in payload.get("summary", []):
        target = str(item.get("target", ""))
        if not target or resolve_sheet_title(target, sheet_ids_by_title):
            continue
        title = preferred_sheet_title(target)
        url = f"{SHEETS_API_BASE}/{spreadsheet_id}:batchUpdate"
        request_func("POST", url, token, {"requests": [{"addSheet": {"properties": {"title": title}}}]})
        sheet_ids_by_title[title] = -1
        created.append({"target": target, "title": title})
    return created


def refresh_payload_sheet_ids(payload: dict, sheet_ids_by_title: dict[str, int]) -> list[dict]:
    refresh_log: list[dict] = []
    for request, summary_item in zip(payload.get("requests", []), payload.get("summary", [])):
        paste_data = request.get("pasteData")
        if not paste_data:
            continue
        target = str(summary_item.get("target", ""))
        matched_title = resolve_sheet_title(target, sheet_ids_by_title)
        if not matched_title:
            continue
        coordinate = paste_data.setdefault("coordinate", {})
        old_sheet_id = coordinate.get("sheetId")
        new_sheet_id = sheet_ids_by_title[matched_title]
        coordinate["sheetId"] = new_sheet_id
        summary_item["sheet_id"] = new_sheet_id
        summary_item["actual_sheet_title"] = matched_title
        refresh_log.append(
            {
                "target": target,
                "matched_title": matched_title,
                "old_sheet_id": old_sheet_id,
                "new_sheet_id": new_sheet_id,
                "status": "updated" if old_sheet_id != new_sheet_id else "unchanged",
            }
        )
    return refresh_log


def apply_and_read_back(
    payload_path: Path,
    spreadsheet_id: str,
    token: str,
    request_func: Callable[[str, str, str, dict | None], dict] = request_json,
    refresh_sheet_ids: bool = True,
) -> dict:
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    refresh_log: list[dict] = []
    if refresh_sheet_ids:
        metadata = fetch_spreadsheet_metadata(spreadsheet_id, token, request_func)
        created_sheets = create_missing_sheets(spreadsheet_id, token, payload, metadata, request_func)
        if created_sheets:
            metadata = fetch_spreadsheet_metadata(spreadsheet_id, token, request_func)
        refresh_log = refresh_payload_sheet_ids(payload, sheet_id_map_from_metadata(metadata))
    else:
        created_sheets = []

    apply_url = f"{SHEETS_API_BASE}/{spreadsheet_id}:batchUpdate"
    apply_response = request_func("POST", apply_url, token, {"requests": payload["requests"]})

    read_back = []
    for item in payload.get("summary", []):
        range_name = build_readback_range(item)
        encoded_range = quote(range_name, safe="'!:")
        read_url = f"{SHEETS_API_BASE}/{spreadsheet_id}/values/{encoded_range}"
        values_response = request_func("GET", read_url, token, None)
        values = values_response.get("values", [])
        expected_rows = int(item.get("written_rows") or 0) + 1
        status = "ok" if len(values) >= expected_rows else "mismatch"
        read_back.append(
            {
                "target": item.get("target", ""),
                "range": range_name,
                "expected_rows": expected_rows,
                "actual_rows": len(values),
                "status": status,
            }
        )

    return {
        "apply_status": "ok",
        "apply_response": apply_response,
        "created_sheets": created_sheets,
        "sheet_id_refresh": refresh_log,
        "read_back": read_back,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply and verify Google Sheets sync payload")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--payload", type=Path, default=Path("outputs/sheets/sheet_sync_payload.json"))
    parser.add_argument("--sheet-id", default="")
    parser.add_argument("--access-token", default="")
    parser.add_argument("--output", type=Path, default=Path("outputs/sheets/sheet_apply_report.json"))
    parser.add_argument("--approve", default="", help="Must be APPLY to write to the live Sheet")
    args = parser.parse_args()

    if args.approve != "APPLY":
        raise SystemExit("Refusing live Sheet write without --approve APPLY")

    root = args.root.resolve()
    env = merged_env(root)
    spreadsheet_id = args.sheet_id or env.get("GOOGLE_SHEETS_ID", "")
    if not spreadsheet_id:
        raise SystemExit("Missing Google spreadsheet id. Set GOOGLE_SHEETS_ID or pass --sheet-id.")

    token = args.access_token or get_access_token(env)
    try:
        report = apply_and_read_back(root / args.payload, spreadsheet_id, token)
    except HTTPError as exc:
        raise SystemExit(describe_google_http_error(exc)) from exc
    output_path = root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    failures = [item for item in report["read_back"] if item["status"] != "ok"]
    print(f"wrote {output_path}")
    if failures:
        print(f"read-back mismatches: {len(failures)}")
        return 1
    print("read-back ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
