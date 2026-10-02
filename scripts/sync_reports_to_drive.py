#!/usr/bin/env python3
"""Đẩy toàn bộ báo cáo lên Google Drive, có tổ chức thư mục.

Folder đích: youtube_hermes (1AzIiixGpZ4miW7ht7snpz7D5-4RZDycc)

QUAN TRỌNG — dùng OAuth token của user, KHÔNG dùng service account:
    Service account không có dung lượng Drive (`Service Accounts do not have
    storage quota`) → mọi file SA tạo đều bị Google chặn, dù folder đã share
    Editor. Phải upload bằng token của chính chủ Drive.

    Lấy token: python scripts/gdrive_oauth_login.py

Cấu trúc tạo ra:
    youtube_hermes/
    ├── 01_DASHBOARDS/    HTML
    ├── 02_REPORTS_WORD/  .docx
    ├── 03_REPORTS_EXCEL/ .xlsx
    ├── 04_DATA/          .csv / .json
    ├── 05_DOCS/          .md
    └── 06_ARCHIVE/       file cũ

Upload idempotent: file cùng tên trong folder đích sẽ được UPDATE (giữ link),
không tạo bản trùng.

Usage:
    python scripts/sync_reports_to_drive.py            # dry-run
    python scripts/sync_reports_to_drive.py --apply    # upload thật
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2 import service_account

sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402

ensure_utf8_console()

ROOT = Path(__file__).resolve().parents[1]
SA_KEY = ROOT / "secrets" / "hermess-503014-service-account.json"
OAUTH_TOKEN = ROOT / "secrets" / "gdrive_token.json"
CLIENT_SECRET = ROOT / "vendor" / "youtube-analytics-dashboard" / "client_secret.json"
PARENT = "1AzIiixGpZ4miW7ht7snpz7D5-4RZDycc"   # youtube_hermes

FOLDER_MAP = {
    "01_DASHBOARDS": [
        "outputs/dashboard/REPORT_HUB.html",
        "outputs/dashboard/ops.html",
        "outputs/dashboard/youtube-analytics-real.html",
    ],
    "02_REPORTS_WORD": [
        "outputs/reports/AZZAM_MRBEAST_AUDIT.docx",
        "outputs/reports/AZZAM_EVERGREEN_PLAN.docx",
        "outputs/reports/AZZAM_ANALYTICS_DIEM_MU.docx",
        "outputs/reports/AZZAM_BAOCAO_PHAN_TICH_DOI_THU.docx",
        "outputs/reports/AZZAM_SOP_FINAL.docx",
        "outputs/reports/AZZAM_SOP_EDITOR.docx",
        "outputs/reports/AZZAM_ACTION_PLAN_EDITOR.docx",
    ],
    "03_REPORTS_EXCEL": [
        "outputs/reports/AZZAM_MRBEAST_AUDIT.xlsx",
        "outputs/reports/AZZAM_EVERGREEN_PLAN.xlsx",
        "outputs/reports/AZZAM_ANALYTICS_DIEM_MU.xlsx",
        "outputs/reports/AZZAM_PHAN_TICH_DOI_THU.xlsx",
        "outputs/reports/AZZAM_SOP_FINAL.xlsx",
        "outputs/reports/AZZAM_SOP_EDITOR.xlsx",
        "outputs/reports/AZZAM_ACTION_PLAN_EDITOR.xlsx",
    ],
    "04_DATA": [
        "outputs/strategy/EVERGREEN_PLAN.csv",
        "outputs/strategy/content_backlog.csv",
        "outputs/strategy/keywords_longtail.json",
        "outputs/strategy/keywords_main.json",
        "outputs/strategy/keywords_title_patterns.json",
        "outputs/reports/blindspots.json",
        "outputs/mrbeast_audit/azzam_videos.json",
        "outputs/mrbeast_audit/gta_videos.json",
        "vendor/youtube-analytics-dashboard/history.csv",
    ],
    "05_DOCS": [
        "outputs/reports/MRBEAST_AUDIT.md",
        "outputs/strategy/MRBEAST_PLAN_ACTION.md",
        "outputs/strategy/MRBEAST_SOP.md",
        "outputs/strategy/MRBEAST_BUILD_TO_SELL.md",
        "outputs/strategy/EVERGREEN_PLAN.md",
        "outputs/reports/blindspots.md",
    ],
}

FOLDER_MIME = "application/vnd.google-apps.folder"


class Drive:
    """Drive client dùng OAuth token của user (bắt buộc — SA không có quota)."""

    def __init__(self, token_path: Path, client_secret: Path):
        if not token_path.exists():
            raise SystemExit(
                f"Thiếu {token_path}\n"
                "Chạy: python scripts/gdrive_oauth_login.py")
        self.token_path = token_path
        self.client_secret = client_secret
        self.token = self._refresh()

    def _refresh(self) -> str:
        tok = json.loads(self.token_path.read_text(encoding="utf-8"))
        if not tok.get("refresh_token"):
            raise SystemExit("gdrive_token.json thiếu refresh_token — login lại.")
        cs = json.loads(self.client_secret.read_text(encoding="utf-8"))
        node = cs.get("installed") or cs.get("web") or {}
        req = urllib.request.Request(
            "https://oauth2.googleapis.com/token",
            data=urllib.parse.urlencode({
                "client_id": node["client_id"],
                "client_secret": node["client_secret"],
                "refresh_token": tok["refresh_token"],
                "grant_type": "refresh_token",
            }).encode())
        with urllib.request.urlopen(req, timeout=30) as r:
            fresh = json.load(r)
        fresh.setdefault("refresh_token", tok["refresh_token"])
        # ghi lại access_token mới
        self.token_path.write_text(json.dumps(fresh, indent=2), encoding="utf-8")
        self.email = self._whoami(fresh["access_token"])
        return fresh["access_token"]

    def _whoami(self, token: str) -> str:
        req = urllib.request.Request(
            "https://www.googleapis.com/drive/v3/about?fields=user",
            headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                u = json.load(r).get("user", {})
            return f"{u.get('emailAddress')} ({u.get('displayName')})"
        except Exception:
            return "(không đọc được)"

    def _req(self, url, data=None, method="GET", ctype=None):
        hdr = {"Authorization": f"Bearer {self.token}"}
        if ctype:
            hdr["Content-Type"] = ctype
        req = urllib.request.Request(url, data=data, method=method, headers=hdr)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
            return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            b = e.read().decode("utf-8", "replace")
            raise RuntimeError(f"HTTP {e.code}: {b[:300]}") from None

    def find_child(self, parent: str, name: str, mime: str | None = None):
        q = f"'{parent}' in parents and name = '{name}' and trashed=false"
        if mime:
            q += f" and mimeType = '{mime}'"
        u = ("https://www.googleapis.com/drive/v3/files?q="
             + urllib.parse.quote(q)
             + "&fields=files(id,name,mimeType)&supportsAllDrives=true")
        fs = self._req(u).get("files", [])
        return fs[0] if fs else None

    def ensure_folder(self, parent: str, name: str) -> str:
        found = self.find_child(parent, name, FOLDER_MIME)
        if found:
            return found["id"]
        meta = {"name": name, "mimeType": FOLDER_MIME, "parents": [parent]}
        u = ("https://www.googleapis.com/drive/v3/files"
             "?fields=id&supportsAllDrives=true")
        d = self._req(u, data=json.dumps(meta).encode(), method="POST",
                      ctype="application/json")
        return d["id"]

    def upload(self, parent: str, path: Path) -> tuple[str, bool]:
        """Trả (file_id, created). Update nếu đã có file cùng tên."""
        existing = self.find_child(parent, path.name)
        mime = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if existing:
            u = (f"https://www.googleapis.com/upload/drive/v3/files/{existing['id']}"
                 "?uploadType=media&supportsAllDrives=true")
            self._req(u, data=path.read_bytes(), method="PATCH", ctype=mime)
            return existing["id"], False
        boundary = "----hermesdriveboundary"
        meta = {"name": path.name, "parents": [parent]}
        payload = (
            f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
            f"{json.dumps(meta)}\r\n"
            f"--{boundary}\r\nContent-Type: {mime}\r\n\r\n"
        ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        u = ("https://www.googleapis.com/upload/drive/v3/files"
             "?uploadType=multipart&fields=id&supportsAllDrives=true")
        d = self._req(u, data=payload, method="POST",
                      ctype=f"multipart/related; boundary={boundary}")
        return d["id"], True

    def move(self, file_id: str, new_parent: str, old_parent: str) -> None:
        u = (f"https://www.googleapis.com/drive/v3/files/{file_id}"
             f"?addParents={new_parent}&removeParents={old_parent}"
             "&fields=id&supportsAllDrives=true")
        self._req(u, data=b"", method="PATCH")

    def list_children(self, parent: str) -> list[dict]:
        q = f"'{parent}' in parents and trashed=false"
        u = ("https://www.googleapis.com/drive/v3/files?q=" + urllib.parse.quote(q)
             + "&fields=files(id,name,mimeType)&pageSize=200&supportsAllDrives=true")
        return self._req(u).get("files", [])

    def share(self, file_id: str, email: str, role="reader") -> None:
        u = (f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions"
             "?sendNotificationEmail=false&supportsAllDrives=true")
        body = {"type": "user", "role": role, "emailAddress": email}
        self._req(u, data=json.dumps(body).encode(), method="POST",
                  ctype="application/json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="upload thật")
    ap.add_argument("--archive-old", action="store_true",
                    help="chuyển file cũ ở root vào 06_ARCHIVE")
    args = ap.parse_args()

    if not OAUTH_TOKEN.exists():
        print(f"Thiếu OAuth token: {OAUTH_TOKEN}", file=sys.stderr)
        print("Chạy: python scripts/gdrive_oauth_login.py", file=sys.stderr)
        return 1

    d = Drive(OAUTH_TOKEN, CLIENT_SECRET)
    print(f"Tài khoản Drive: {d.email}")
    print(f"Folder đích: youtube_hermes ({PARENT})")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}\n")

    # kiểm tra quyền
    try:
        root_meta = d._req(
            f"https://www.googleapis.com/drive/v3/files/{PARENT}"
            "?fields=id,name&supportsAllDrives=true")
        print(f"✓ Truy cập folder OK: {root_meta.get('name')}\n")
    except RuntimeError as e:
        print(f"✗ Không truy cập được folder: {e}", file=sys.stderr)
        return 1

    # tạo cấu trúc thư mục
    folders = {}
    for name in list(FOLDER_MAP) + ["06_ARCHIVE"]:
        if args.apply:
            fid = d.ensure_folder(PARENT, name)
        else:
            found = d.find_child(PARENT, name, FOLDER_MIME)
            fid = found["id"] if found else "(sẽ tạo)"
        folders[name] = fid
        print(f"  {'✓' if args.apply or fid != '(sẽ tạo)' else '·'} {name:20} {fid}")

    print()
    total_new = total_upd = total_missing = 0
    for fname, rels in FOLDER_MAP.items():
        print(f"--- {fname} ---")
        for rel in rels:
            p = ROOT / rel
            if not p.exists():
                print(f"  ✗ THIẾU  {rel}")
                total_missing += 1
                continue
            kb = p.stat().st_size / 1024
            if args.apply:
                try:
                    fid, created = d.upload(folders[fname], p)
                    print(f"  {'＋' if created else '↻'} {p.name:44} {kb:>8,.1f} KB")
                    total_new += created
                    total_upd += (not created)
                except RuntimeError as e:
                    print(f"  ✗ {p.name}: {e}")
            else:
                print(f"  · {p.name:44} {kb:>8,.1f} KB")

    if args.archive_old and args.apply:
        print("\n--- Chuyển file cũ ở root vào thư mục phù hợp ---")
        known = {p.name for rels in FOLDER_MAP.values()
                 for rel in rels for p in [ROOT / rel]}
        # Không bao giờ đụng vào: sheet chính, file đang được dùng, folder
        NEVER_MOVE = {"youtube", "TIM-NGACH.xlsx"}
        for f in d.list_children(PARENT):
            if f["mimeType"] == FOLDER_MIME:
                continue
            if f["name"] in known or f["name"] in NEVER_MOVE:
                if f["name"] in NEVER_MOVE:
                    print(f"  · giữ nguyên {f['name']} (file đang dùng)")
                continue
            # đoán thư mục theo phần mở rộng
            ext = f["name"].rsplit(".", 1)[-1].lower() if "." in f["name"] else ""
            dest = {"docx": "02_REPORTS_WORD", "xlsx": "03_REPORTS_EXCEL",
                    "csv": "04_DATA", "json": "04_DATA",
                    "md": "05_DOCS", "html": "01_DASHBOARDS"}.get(ext, "06_ARCHIVE")
            try:
                d.move(f["id"], folders[dest], PARENT)
                print(f"  → {dest}/{f['name']}")
            except RuntimeError as e:
                print(f"  ✗ {f['name']}: {e}")

    print(f"\n{'='*60}")
    print(f"  Tạo mới: {total_new} | Cập nhật: {total_upd} | Thiếu: {total_missing}")
    print(f"  Folder: https://drive.google.com/drive/folders/{PARENT}")
    if not args.apply:
        print("  (dry-run — thêm --apply để upload thật)")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
