# YouTube Channel Doctor - Project Status Report

**Last updated:** 29/09/2026  
**Workspace:** `G:\Other computers\My Computer\Project\youtube`  
**External data folder referenced:** `C:\Users\Admin\youtube`  
**Goal:** giup VSCode/Codex nam ro du an de nang cap MCP Apify, YouTube API, tele gateway va multi-agent.

---

## 1. Project Overview

Du an gom hai lop cong viec:

1. **Knowledge repo hien tai**: luu ghi chu, workflow va checklist tu video Hermes dashboard cho chan doan kenh YouTube.
2. **YouTube Channel Doctor data workspace**: thu muc `C:\Users\Admin\youtube` dang co report cu va JSON search data cho kenh minh/doi thu.

Trong video, Hermes duoc dung nhu mot dashboard/tro ly AI ca nhan:

- Cai Hermes, mo dashboard local, go lenh `H` de kiem tra.
- Dua URL kenh YouTube cho Hermes doc du lieu cong khai.
- Neu can phan tich sau, cap them YouTube Data API.
- Bien ket qua thanh dashboard, hinh anh, dan y, tieu de, checklist va hanh dong tiep theo.
- Co the ket noi Telegram de lam viec qua tin nhan.
- Co the ghi nho thoi quen, quy trinh va lua chon cong cu cua nguoi dung.

---

## 2. Current Repo Map

| File | Vai tro |
|------|---------|
| `README.md` | Tong quan du an ghi chu Hermes dashboard cho kenh YouTube. |
| `knowledge/video-notes/cho-ai-xem-kenh-youtube-cua-minh.md` | Ghi chu theo moc thoi gian tu 06:44 den het video. |
| `knowledge/distilled/hermes-dashboard-youtube-workflow.md` | Quy trinh Hermes dashboard: cai dat, dashboard, YouTube Data API, tao tai san noi dung. |
| `knowledge/distilled/youtube-ai-channel-ops.md` | Khung van hanh kenh YouTube bang Hermes/dashboard. |
| `knowledge/reusable-assets/youtube-channel-diagnosis-checklist.md` | Checklist de chay lai quy trinh chan doan kenh. |
| `azzam_search.json` | Ket qua YouTube search cho kenh chinh, dong bo tu `C:\Users\Admin\youtube`. |
| `gta_search.json` | Ket qua YouTube search cho kenh doi thu, dong bo tu `C:\Users\Admin\youtube`. |
| `PROJECT_STATUS_REPORT.md` | File bao cao tong hop cho Codex/VSCode. |

---

## 3. Timeline - Nhung viec da lam

### 28/09/2026 - Knowledge Extraction

| Cong viec | Ket qua |
|-----------|---------|
| Doc transcript video "Cho AI Xem Kenh YouTube Cua Minh - No Noi Gi?" | Hoan tat ghi chu phan trong tam tu 06:44 den het video. |
| Chon pham vi phan tich | Tap trung vao Hermes dashboard, YouTube channel doctor, YouTube Data API, Telegram va tri nho quy trinh. |
| Tao video notes | Co file ghi chu theo moc thoi gian. |
| Tao distilled workflow | Co workflow rieng cho Hermes dashboard chan doan kenh. |
| Tao khung van hanh kenh | Co vong lap: du lieu -> chan doan -> de xuat -> tai san noi dung -> ghi nho quy trinh. |
| Tao checklist tai su dung | Co checklist de lan sau chay lai quy trinh an toan. |

### 28/09/2026 - YouTube Data & Competitor Research

Thong tin duoc tong hop tu report cu tai `C:\Users\Admin\youtube\PROJECT_STATUS_REPORT.md`.

| Cong viec | Ket qua |
|-----------|---------|
| Clone repo `model-trader` | Hoan tat theo report cu. |
| Scaffold trader `azzam_master` | Hoan tat theo report cu. |
| Cai dependency pipeline | Hoan tat theo report cu. |
| Goi YouTube Data API cho kenh @Azzammastertradinggold | Lay channel info va 288 video theo report cu. |
| Dung Apify scrape @GoldTraderAlliance | Actor Apify da chay theo report cu. |
| Tao `video_inventory.csv` | Report cu ghi 288 row cho inventory/remake. |
| Tao template `pain_points_master.csv` | San sang cho research agent. |
| Tao template `remake_plan.csv` | San sang cho remake planning. |
| Tao SOP research -> video -> remake | Hoan tat theo report cu. |

### 29/09/2026 - Workspace Consolidation

| Cong viec | Ket qua |
|-----------|---------|
| Kiem tra repo hien tai | Repo gom README, `knowledge/`, 2 file JSON search va report nay. |
| Kiem tra report cu tren o C | Co report cu nhung bi loi encoding khi xem trong terminal va co chua API key/token. |
| Tao report tong hop moi trong workspace | File nay la ban doc duoc, sach hon, phu hop cho Codex/VSCode. |
| Redact secrets | Khong dua YouTube API key, Apify token hay credential truc tiep vao report moi. |

---

## 4. Data Summary

### Kenh chinh: @Azzammastertradinggold

| Metric | Gia tri theo report cu |
|--------|------------------------|
| Channel ID | `UCBZ7LaffmEPv91sWcfroJdQ` |
| Subscribers | 1,970 |
| Total views | 233,031 |
| Videos | 288 |
| Created | 15/05/2024 |
| Country | GB |

### Kenh doi thu: @GoldTraderAlliance

| Metric | Gia tri theo report cu |
|--------|------------------------|
| Channel ID | `UCdS8VXFlNvVohM09qzZGCkA` |
| Subscribers | 14,100 |
| Total views | 1,389,242 |
| Videos | 733 |
| Created | 22/10/2016 |
| Country | GB |

### Video Performance - kenh chinh

| Metric | Gia tri theo report cu |
|--------|------------------------|
| Shorts | 144 video, 50% tong so video |
| Long videos | 144 video, 50% tong so video |
| Shorts views | 226,306, xap xi 97% tong views |
| Long views | 6,906, xap xi 3% tong views |
| Top short | "Don't joking with me" - 113,199 views |
| Top short #2 | "Small steps daily..." - 44,026 views |
| Avg views/short | 1,572 |
| Avg views/long | 48 |
| Like rate | 3.17% |
| Videos co like | 188/288 |
| Videos co comment | 7/288 |

---

## 5. Technical Stack

| Tool / API | Vai tro | Trang thai |
|------------|---------|------------|
| Hermes CLI / Hermes dashboard | Dashboard dieu phoi, chan doan kenh, tao tai san noi dung. | Da duoc mo ta trong knowledge repo; transcript chua co lenh cai chinh xac. |
| YouTube Data API v3 | Lay channel info, danh sach video va statistics. | Report cu ghi da dung thanh cong; credential phai de ngoai repo. |
| YouTube Analytics API | Lay retention, traffic source, demographics neu can phan tich sau hon. | Chua thay artifact da implement trong repo nay. |
| Apify API / Apify Actor | Scrape kenh doi thu va phu tro competitor research. | Report cu ghi da dung actor Apify; token phai de ngoai repo. |
| Google Sheets | Hop nhat `pain_points`, `video_inventory`, `remake_plan`. | Report cu ghi da co sheet tong hop; link nen de private neu chua muon cong khai. |
| Telegram / Tele Gateway | Kenh dieu khien Hermes qua tin nhan, nhac bao cao, trigger workflow. | Da duoc nhac trong video/knowledge; chua thay bot config/token trong repo hien tai. |
| Multi-agent / Hermes delegate | Tach research, planning, script va publish optimization thanh agent rieng. | Moi o muc roadmap/kien truc, chua thay code trong repo hien tai. |

**Security note:** khong luu API key, bot token, OAuth token, Apify token, Google credential hay du lieu analytics rieng trong Markdown hoac repo.

---

## 6. Tele Gateway - Nhung viec da ghi nhan

Trong repo hien tai, "tele gateway" nen hieu la lop Telegram/Hermes gateway phuc vu dieu khien dashboard va workflow qua tin nhan. Nhung viec da duoc ghi nhan:

| Hang muc | Da lam / da ghi nhan | Trang thai |
|----------|----------------------|------------|
| Telegram la kenh lam viec voi Hermes | Video notes ghi Hermes co the ket noi Telegram va lam viec qua Telegram. | Da ghi nhan trong knowledge repo. |
| Bao cao/nhac viec hang ngay | README va distilled docs ghi Hermes co the nhac bao cao hang ngay. | Da ghi nhan tu transcript. |
| Dieu phoi cong viec qua gateway | Workflow mo ta nguoi dung -> Hermes -> skill/dashboard -> output/tai san noi dung. | Da co khung van hanh. |
| Ket noi quy trinh YouTube doctor | Gateway co the nhan URL kenh, yeu cau Hermes chan doan, tao dashboard va de xuat hanh dong. | Da co checklist/quy trinh. |
| Ghi nho quy trinh nguoi dung | Hermes co the ghi nho cong cu, thoi quen va lua chon lap lai. | Da ghi nhan trong notes. |
| Token/bot Telegram | Chua thay credential hoac file cau hinh Telegram trong workspace nay. | Chua xac minh. |
| Gateway production-ready | Chua thay test, log, service file, webhook config hoac deployment artifact trong workspace nay. | Chua xac minh. |

Ket luan: tele gateway da duoc chuan hoa o muc workflow va yeu cau san pham, nhung trong workspace hien tai chua co bang chung day du ve implementation production. Buoc tiep theo la tao cau truc config/log/test rieng neu muon nang cap thanh gateway that.

---

## 7. Key Insights

1. **Shorts la kenh growth chinh**  
   144 shorts tao gan nhu toan bo views. Nen uu tien shorts, hook va CTA comment-specific.

2. **Long-form dang underperform**  
   Long videos co avg view thap hon nhieu. Nen remake hoac bien long-form thanh shorts/tutorial ngan.

3. **Engagement gap nam o comment**  
   Like rate tam on, nhung comment rat thap. Can CTA dang cau hoi, trigger tai lieu, hoac "comment keyword".

4. **Pain point research la nut that tiep theo**  
   Template da co, nhung can research agent thu thap pain points tu X, YouTube comments, trends va doi thu.

5. **Hermes dashboard huu ich khi co vong lap**  
   Gia tri nam o du lieu -> chan doan -> hanh dong -> tai san noi dung -> review -> ghi nho.

---

## 8. Upgrading Roadmap

### 8.1 MCP Apify

**Muc tieu:** bien Apify thanh cong cu co the goi lai on dinh tu Codex/Hermes de cap nhat competitor/video data.

Next work:

1. Chon actor phu hop cho channel-level va video-level scraping.
2. Chuan hoa input: channel URL, handle, max videos, date range.
3. Chuan hoa output schema: title, URL, views, likes, comments, published_at, duration, tags, description.
4. Ghi output vao CSV/JSON va Google Sheets.
5. Them error handling cho quota, actor timeout, empty result va duplicate videos.

### 8.2 YouTube Data API

**Muc tieu:** lay du lieu performance theo thoi gian de quyet dinh remake/publish.

Next work:

1. Tach credential ra `.env` hoac secret manager.
2. Viet script fetch channel/video stats co cache va quota tracking.
3. Lay snapshot sau 24h, 7 ngay, 30 ngay cho video moi publish.
4. Neu can retention/traffic source, tich hop YouTube Analytics API voi OAuth dung cach.
5. Xuat dashboard summary cho views, likes, comments, CTR/retention neu co.

### 8.3 Tele Gateway

**Muc tieu:** dung Telegram lam remote control cho Hermes/YouTube doctor.

Next work:

1. Dinh nghia command: `/diagnose`, `/remake`, `/painpoints`, `/report`, `/next`.
2. Thiet ke gateway service nhan message, xac thuc user, goi workflow tuong ung.
3. Luu log task: request, input, output, status, error.
4. Tra ve ket qua ngan gon qua Telegram, luu ban day du vao file/sheet.
5. Them guardrail: khong gui secret, khong publish tu dong khi chua co approval.

### 8.4 Multi-Agent

**Muc tieu:** tach quy trinh research -> planning -> script -> publish optimization.

| Agent | Input | Output |
|-------|-------|--------|
| Research Agent | X trends, YouTube comments, competitor videos, Google/Apify data. | `pain_points_master.csv` voi pain point, intent, source, evidence. |
| Content Planning Agent | Pain points + video inventory + competitor patterns. | Ideas, format, priority, remake candidates. |
| Script Agent | Pain point + target format + sample video. | Hook, script, CTA, visual notes. |
| Publish Optimizer Agent | Script + niche + target audience. | Title, description, tags, thumbnail angle, pinned comment. |
| Review Agent | Post-publish metrics. | Lessons, next iteration, stop/scale/remake decision. |

---

## 9. Blockers & Risks

| Risk | Status | Recommended fix |
|------|--------|-----------------|
| Secrets in old report | Found in `C:\Users\Admin\youtube\PROJECT_STATUS_REPORT.md`. | Rotate exposed keys if they were real; move secrets to `.env`/vault; never paste into Markdown. |
| Encoding issue in old report terminal output | Old report displays mojibake in PowerShell output. | Keep this new report clean UTF-8/ASCII-friendly; use VSCode UTF-8. |
| Repo hien tai chua co code/API scripts | Workspace mostly docs + JSON search exports. | Neu muon nang cap MCP/API, can add scripts/config structure. |
| Tele gateway chua co implementation artifact | Chua thay bot config, webhook, service file, logs. | Tao gateway spec + minimal service + test log. |
| YouTube Analytics depth | Data API stats khong bang Analytics retention/traffic. | Dung OAuth Analytics API neu can du lieu sau. |
| Manual workflow | Nhieu buoc dang duoc ghi la manual/template. | Chuan hoa thanh CLI scripts va agent tasks. |

---

## 10. Next Actions

### Lam ngay

1. Tao `.env.example` cho YouTube, Apify, Telegram nhung khong dien secret that.
2. Tao `data/` hoac `exports/` trong workspace de gom `azzam_search.json`, `gta_search.json` neu can versioning.
3. Tao script `fetch_youtube_stats` co quota tracking va cache.
4. Tao schema cho `video_inventory.csv`, `pain_points_master.csv`, `remake_plan.csv`.
5. Viet gateway spec cho Telegram commands va response format.

### 1-2 tuan

1. Chon 5 shorts/long videos underperform de remake.
2. Tao 5 script remake dau tien voi hook, body, CTA comment-specific.
3. Chay research agent lan dau de lay 100 pain points.
4. Cap nhat Google Sheets tu file local hoac API.
5. Review ket qua sau 3 ngay, cap nhat lesson learned.

### 2-4 tuan

1. Nang MCP Apify thanh tool on dinh cho competitor/video scraping.
2. Them YouTube Analytics API neu can retention/traffic source.
3. Tach multi-agent pipeline thanh cac task co input/output ro.
4. Ket noi tele gateway de trigger diagnose/report/remake tu Telegram.
5. Tao weekly review routine cho content performance.

---

## 11. Acceptance Criteria For Next Upgrade

- Codex doc file nay va hieu ngay repo dang o trang thai nao.
- Khong co secret trong Markdown.
- Co duong di ro cho MCP Apify, YouTube API, tele gateway va multi-agent.
- Moi workflow co input/output schema ro rang.
- Moi phien chan doan ket thuc bang hanh dong cu the: remake, publish, research, review hoac stop.

---

**Current status:** knowledge/workflow da duoc tong hop; data report cu da duoc tham chieu; tele gateway moi o muc workflow/chua thay implementation trong repo nay.  
**Next priority:** chuan hoa data/config an toan, sau do implement YouTube API + Apify + Telegram gateway theo tung buoc.

---

## 12. Audit Update - 29/09/2026

### Hermes Gateway Folder Alignment

- Folder checked: `C:\Users\Admin\youtube`.
- Before alignment, folder only had `azzam_search.json`, `gta_search.json`, and `PROJECT_STATUS_REPORT.md`.
- Synced from workspace into gateway folder:
  - `README.md`
  - `knowledge/`
- Current interpretation: `/c/Users/Admin/youtube` is now aligned with the documentation/knowledge side of the active project. It still does not contain production gateway code, bot config, webhook service, logs, or tests.

### Repository Clone Check

- Exact requested repo `https://github.com/tonbistudio/model-trade.git` was checked with `git ls-remote` and returned `Repository not found`.
- Existing valid repo `https://github.com/tonbistudio/model-trader.git` was checked and exists.
- Local clone already exists at `C:\Users\Admin\model-trader` with remote `https://github.com/tonbistudio/model-trader.git`.
- Current `C:\Users\Admin\model-trader` has untracked local work: `pipeline/youtube_content_generator.py` and `traders/`.

### Status

- Do not clone `model-trade` unless the GitHub URL is corrected or the repo becomes available.
- Use existing local `model-trader` clone for pipeline work unless a separate clone location is explicitly needed.

---

## 13. Consolidation Update - 29/09/2026

### Source Of Truth

- Main project root is now `C:\Users\Admin\youtube`.
- VSCode, Codex and Hermes/tele gateway should use this same folder to avoid split-brain work between `C:\Users\Admin\youtube` and `G:\Other computers\My Computer\Project\youtube`.
- The `G:\Other computers\My Computer\Project\youtube` copy should be treated as an older mirror unless intentionally synced.

### Model Trader Integration

- `model-trader` has been copied into `C:\Users\Admin\youtube\vendor\model-trader` from the existing local clone at `C:\Users\Admin\model-trader`.
- The vendored repo keeps the remote `https://github.com/tonbistudio/model-trader.git`.
- The requested repo `https://github.com/tonbistudio/model-trade.git` was checked and does not exist on GitHub at the time of verification.
- Added `MODEL_TRADER_INTEGRATION.md` to explain how to apply `model-trader` to the YouTube channel doctor project.
- Added `.env.example` for YouTube, Apify, Telegram, Anthropic and Google Sheets configuration without secrets.

### How The Repo Applies

Use `vendor/model-trader` as the trading-content engine:

```text
trader videos/transcripts
-> model-trader strategy extraction
-> scanner/backtest/paper journal
-> youtube_content_generator.py
-> Shorts ideas, setup breakdowns, weekly recaps, hooks and CTAs
-> YouTube channel doctor remake/content plan
```

### Immediate Next Step

Open VSCode at `C:\Users\Admin\youtube`, then from `vendor/model-trader` install editable dependencies and decide whether to continue `traders/azzam_master`, `traders/azammaster_master`, or create a clean `traders/azzam_master_v2`.
