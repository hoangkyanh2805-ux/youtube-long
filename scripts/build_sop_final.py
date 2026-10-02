"""
SOP FINAL — English channel + CapCut Pro + MCP (Claude Code / Codex).
Writes:
  outputs/reports/AZZAM_SOP_FINAL.docx
  outputs/reports/AZZAM_SOP_FINAL.xlsx

Confirmed decisions:
  - Channel language: ENGLISH
  - Editor software: CapCut Pro (paid)
  - Automation: CapCut MCP (VectCutAPI backend + capcut-mcp-server)
  - Telegram community link: TBD (placeholder, update later)

Verified on this machine:
  Python 3.11.15 | Node v24.15.0 | npm 11.12.1 | ffmpeg 8.1.1 | git 2.54.0
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

# Force UTF-8 console: without this, printing Vietnamese crashes with
# UnicodeEncodeError when stdout is a pipe (dagu/cron/CI).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from console_utf8 import ensure_utf8_console  # noqa: E402
ensure_utf8_console()

OUT = Path("outputs/reports")
OUT.mkdir(parents=True, exist_ok=True)

KPI = {"shorts": 3, "long": 1, "long_min": 8}

# ── Timing: manual / library / +MCP (minutes) ───────────────────────────────
STAGES = [
    ("Pick source material", 30, 5, 5, "Agent filters pain pool, 3 different categories"),
    ("Write script", 60, 15, 15, "Claude drafts, editor fixes tone"),
    ("Find assets", 120, 5, 5, "assets/ library — 0-search rule"),
    ("Rough-cut 3 Shorts", 180, 66, 35, "MCP builds draft → editor polishes"),
    ("Rough-cut Long 8 min", 240, 100, 60, "MCP builds draft → editor polishes"),
    ("Text / graphics / subtitles", 90, 25, 12, "MCP injects SRT + text directly"),
    ("Audio + color", 45, 10, 8, "Presets pre-applied"),
    ("Export + QC", 45, 20, 20, "Editor exports — MCP cannot export"),
    ("Community engagement", 45, 30, 30, "Human only, not automated"),
]

# ── MCP capability boundary ─────────────────────────────────────────────────
MCP_CAN = [
    ("capcut_create_draft", "New project with exact canvas (1080x1920 / 1920x1080) and fps"),
    ("capcut_add_video", "Place clips on timeline with start/end, volume, speed, transition"),
    ("capcut_add_audio", "Music + SFX with fade in/out"),
    ("capcut_add_text", "Styled text overlays with animation, shadow, background"),
    ("capcut_add_image", "Logo / overlay with position, scale, rotation"),
    ("capcut_add_subtitle", "Import SRT subtitles with styling — removes manual typing"),
    ("capcut_add_keyframe", "Zoom / pan animation via keyframe interpolation"),
    ("capcut_add_effect", "Blur, brightness, saturation and similar"),
    ("capcut_add_sticker", "Decorative stickers / emoji"),
    ("capcut_save_draft", "Write draft folder for CapCut to open"),
    ("capcut_get_duration", "Read media duration + metadata"),
]

MCP_CANNOT = [
    ("Final export", "Must open CapCut and export by hand — no export tool in MCP"),
    ("Advanced color / custom LUT", "Basic effects only, no grading pipeline"),
    ("Rhythm-based cutting", "Cannot feel the beat; editor decides cut points"),
    ("Content approval", "Cannot judge if a claim breaks policy"),
    ("Thumbnails", "No thumbnail tool at all"),
    ("Creative decisions", "Which hook, which pacing, which story — human only"),
]

# ── Setup steps (verified against real repos) ───────────────────────────────
SETUP_STEPS = [
    ("1", "Install VectCutAPI backend",
     "git clone https://github.com/sun-guannan/VectCutAPI.git\n"
     "cd VectCutAPI\npython -m pip install -r requirements.txt",
     "Repo Apache-2.0, ~2.3k stars, Python 3.10+ required",
     "Backend cloned, deps installed"),
    ("2", "Start the API server",
     "python capcut_server.py",
     "Runs on http://localhost:9001 by default",
     "Server listening on 9001"),
    ("3", "Get the MCP server",
     "git clone https://github.com/Atx-Guy/capcut-mcp-server.git\n"
     "cd capcut-mcp-server\nnpm install\nnpm run build",
     "TypeScript, 11 MCP tools, MIT license",
     "dist/index.js built"),
    ("4", "Wire MCP into Claude Code / Codex",
     '{\n  "mcpServers": {\n    "capcut": {\n      "command": "node",\n'
     '      "args": ["<abs-path>/capcut-mcp-server/dist/index.js"],\n'
     '      "env": { "CAPCUT_API_URL": "http://localhost:9001" }\n'
     "    }\n  }\n}",
     "Claude Desktop config: %APPDATA%\\Claude\\claude_desktop_config.json",
     "MCP server listed and connected"),
    ("5", "Verify the pipeline",
     "Ask the agent: create a 1080x1920 draft, add one clip, save it.",
     "Draft folder is prefixed dfd_",
     "dfd_ folder appears in CapCut drafts"),
    ("6", "Install CapCut Pro + point drafts dir",
     "CapCut Pro → Settings → check drafts directory path",
     "MCP writes drafts; CapCut must read the same folder",
     "Draft opens in CapCut Pro"),
    ("7", "Build the two master templates",
     "Short 9:16 + Long 16:9, with brand intro/outro, subtitle preset, audio chain",
     "One-time work, reused for every video after",
     "2 template projects saved"),
]

# ── Daily schedule with MCP ─────────────────────────────────────────────────
DAY_PLAN = [
    ("07:30", "07:35", "5'", "Pick material",
     "Agent filters pain pool, picks 3 different categories + 1 Long pillar",
     "3 pain points + pillar locked"),
    ("07:35", "07:50", "15'", "Script",
     "Claude drafts hooks (5 variants each) + Long outline; editor fixes tone",
     "Final script"),
    ("07:50", "07:55", "5'", "Stage assets",
     "Copy chart clips, b-roll, music, SFX into the working folder",
     "Working folder ready"),
    ("07:55", "08:30", "35'", "MCP builds 3 Shorts",
     "Agent calls capcut_create_draft + add_video + add_subtitle + add_text + save_draft",
     "3 dfd_ draft folders"),
    ("08:30", "09:00", "30'", "Polish 3 Shorts",
     "Open each draft in CapCut Pro: fix cut points, add punch-ins, check hook",
     "3 Shorts final"),
    ("09:00", "09:15", "15'", "Break", "—", "—"),
    ("09:15", "10:15", "60'", "MCP builds Long",
     "Agent assembles 5-part timeline from outline + asset list",
     "1 dfd_ draft folder"),
    ("10:15", "11:15", "60'", "Polish Long",
     "Open in CapCut Pro: pacing, b-roll timing, on-screen text, audio mix",
     "Long final"),
    ("11:15", "11:45", "30'", "Lunch", "—", "—"),
    ("11:45", "11:57", "12'", "Subtitles + text pass",
     "MCP re-injects corrected SRT; editor spot-checks terminology",
     "Clean subtitles"),
    ("11:57", "12:05", "8'", "Audio + color",
     "Apply saved preset chain, normalise to -14 LUFS",
     "Audio/color done"),
    ("12:05", "12:25", "20'", "Export + QC",
     "Export in CapCut Pro, run the 8-point QC checklist",
     "4 final files"),
    ("12:25", "12:45", "20'", "Packaging",
     "Title/description/tags from prompt pack; thumbnail with 3 elements",
     "Metadata + thumbnails"),
    ("12:45", "13:15", "30'", "Publish + engage",
     "Upload, pin the interaction comment, reply to audience",
     "Published + pinned"),
    ("13:15", "13:30", "15'", "Buffer",
     "Fix anything that slipped; top up asset library", "—"),
]

# ── English content rules ───────────────────────────────────────────────────
ENGLISH_RULES = [
    ("Title", "Max 60 characters. Formula: [WARNING/COMMAND] + [AUDIENCE] + "
     "[RESULT] + [TIME/NUMBER]",
     "Stop Risking 10% Per XAUUSD Trade (Do This Instead)"),
    ("Hook (0-3s)", "State the pain directly. No intro, no logo, no 'hey guys'.",
     "If you risk 10% per XAUUSD trade, here is how many losses wipe you out."),
    ("Tone", "Direct, plain English. Short sentences. No hype words.",
     "Say 'this is why you lose', not 'unlock your trading potential'."),
    ("Terminology", "Use the terms the audience already uses (from comment mining).",
     "stop loss, liquidity, market structure, prop firm, drawdown"),
    ("CTA", "One keyword per video. Comment the keyword, or join Telegram.",
     "Comment 'RISK' and I'll send the risk calculator."),
    ("Disclaimer", "Required on every video description.",
     "Not financial advice. Trading involves risk of loss."),
    ("Banned", "No profit promises, no win-rate claims, no simulated trades "
     "presented as real.", "Never: 'guaranteed', '100% win rate', 'risk-free'"),
]

# ── Build-to-sell ───────────────────────────────────────────────────────────
BTS = [
    ("Documented", "Every step is a file, not tribal knowledge",
     "New editor ships 3 Shorts + 1 Long on day 1", "SOP + prompt pack + templates"),
    ("Reusable assets", "Templates, asset library, prompt pack reused forever",
     "Time/day down ≥75% vs manual", "14.25h → 3.17h (78% cut)"),
    ("No single point of failure", "Any editor who reads the SOP can run it",
     "Handover causes no production gap", "SOP + QC checklist + naming rule"),
    ("Measurable", "Every stage has a target time and a KPI",
     "You can see which stage is slow", "Sheet 01 / 08"),
    ("Automated repetition", "MCP + AI handle assembly and text, humans handle judgement",
     "≥70% of stages have automation support", "7/9 stages (78%)"),
    ("Content compounds", "Old videos keep pulling views and leads",
     "Library keeps working after publish", "Playlists + remake candidates"),
    ("Transferable", "Whole system lives in the repo, version-controlled",
     "Sellable / handover-ready with working system", "Repo + SOP + assets + prompts"),
    ("Quality controlled", "Fixed checklist, not mood-dependent",
     "Rework rate under 10%", "8-point QC checklist"),
]

# ── Risks ───────────────────────────────────────────────────────────────────
RISKS = [
    ("MCP server breaks after CapCut update", "Draft format changes, assembly fails",
     "Pin CapCut version; keep a manual fallback template; test MCP weekly", "High"),
    ("Agent writes a wrong claim into the script", "Policy violation, channel strike",
     "Prompt bans profit claims; editor verifies every number before export", "High"),
    ("Editor becomes dependent on MCP", "Cannot work if MCP is down",
     "Keep manual template path documented and practised monthly", "Medium"),
    ("One person sick / away", "Production stops entirely",
     "Bank 2 days of buffer; SOP lets a substitute run the day", "High"),
    ("Asset copyright claim", "Video demonetised or blocked",
     "Only licensed music/b-roll; log every asset in ASSET_INDEX.csv", "High"),
    ("Burnout at 4 videos/day", "Quality drops, then output stops",
     "290 min buffer/day; one day per week is Long + engagement only", "High"),
    ("Localhost backend not running", "MCP tools fail silently",
     "Startup checklist: verify port 9001 before opening the agent", "Medium"),
]

# ── QC checklist ────────────────────────────────────────────────────────────
QC = [
    ("Hook", "First 3 seconds state the pain, no logo/intro", "Required"),
    ("Subtitles", "Match speech, trading terms spelled correctly", "Required"),
    ("Guardrail", "No profit promise, no simulated trade shown as real",
     "Required — blocks publish"),
    ("Aspect ratio", "9:16 for Shorts, 16:9 for Long", "Required"),
    ("Loudness", "Normalised to -14 LUFS", "Required"),
    ("File name", "<type>_<topic>_<variant>_<version>", "Required"),
    ("Metadata", "Title ≤60 chars, disclaimer present, timestamps accurate", "Required"),
    ("Source trace", "Comment ID logged in the tracking sheet", "Required"),
]

# ── Open items ──────────────────────────────────────────────────────────────
OPEN_ITEMS = [
    ("Telegram community link", "Not provided yet — placeholder in all CTAs",
     "Update once link exists; keep CTA wording generic until then"),
    ("CapCut Pro licence", "Confirm the Pro seat is active on the editor machine",
     "Needed for template export and Pro effects"),
    ("Claude Code / Codex seat", "Confirm which agent gets the MCP connection",
     "MCP config differs per client"),
    ("Templates not built yet", "Short 9:16 + Long 16:9 master templates",
     "One-time build, blocks the MCP workflow until done"),
    ("Asset library empty", "Structure exists, real files not added yet",
     "Fill before first production day"),
]


def build_docx() -> Path:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor

    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(4)

    t = doc.add_heading("EDITOR SOP — 1 PERSON, 3 SHORTS + 1 LONG PER DAY", level=0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    s = doc.add_paragraph()
    s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = s.add_run("Channel @azzammastertradinggold  •  Niche: XAUUSD / Forex  •  "
                  "Language: ENGLISH")
    r.bold = True
    r.font.size = Pt(12)
    m = doc.add_paragraph()
    m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    m.add_run(f"Date: {date.today().isoformat()}  •  "
              "Stack: CapCut Pro + CapCut MCP + Claude Code / Codex").italic = True
    doc.add_paragraph()

    def table(headers, rows):
        tb = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        tb.style = "Light Grid Accent 1"
        for j, h in enumerate(headers):
            c = tb.cell(0, j)
            c.text = h
            for p in c.paragraphs:
                for run in p.runs:
                    run.bold = True
                    run.font.size = Pt(9.5)
        for i, row in enumerate(rows, 1):
            for j, v in enumerate(row):
                c = tb.cell(i, j)
                c.text = str(v)
                for p in c.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9)
        doc.add_paragraph()

    # 1
    doc.add_heading("1. CONFIRMED DECISIONS", level=1)
    table(["Item", "Decision", "Status"], [
        ["Channel language", "ENGLISH", "Locked"],
        ["Editor software", "CapCut Pro (paid)", "Locked"],
        ["Automation", "CapCut MCP — VectCutAPI backend + capcut-mcp-server",
         "To install"],
        ["Agent", "Claude Code / Codex (MCP client)", "To confirm seat"],
        ["Telegram community link", "Not provided yet", "Open — placeholder in CTAs"],
    ])
    doc.add_paragraph()

    # 2
    doc.add_heading("2. THE PROBLEM THIS SOP SOLVES", level=1)
    doc.add_paragraph(
        "One editor must ship 3 Shorts + 1 Long (8 min) plus community engagement "
        "every day. Done manually that is about 14.25 hours — impossible for one "
        "person. The two biggest bottlenecks are FINDING ASSETS (120 min/day) and "
        "CUTTING (420 min/day)."
    )
    p = doc.add_paragraph()
    pr = p.add_run(
        "This SOP attacks both: a pre-built asset library removes the search step, "
        "master templates remove repeated setup, and CapCut MCP lets the agent "
        "assemble a rough draft automatically so the editor only polishes."
    )
    pr.bold = True
    doc.add_paragraph()

    # 3
    doc.add_heading("3. PERFORMANCE — MANUAL vs LIBRARY vs +MCP", level=1)
    tt = sum(s[1] for s in STAGES)
    tl = sum(s[2] for s in STAGES)
    tm = sum(s[3] for s in STAGES)
    rows = [[n, f"{a}'", f"{b}'", f"{c}'", note] for n, a, b, c, note in STAGES]
    rows.append(["TOTAL", f"{tt}'", f"{tl}'", f"{tm}'", ""])
    rows.append(["", f"{tt/60:.2f} h", f"{tl/60:.2f} h", f"{tm/60:.2f} h", ""])
    rows.append(["", "", f"−{(1-tl/tt)*100:.0f}%", f"−{(1-tm/tt)*100:.0f}%",
                 "reduction vs manual"])
    table(["Stage", "Manual", "Library", "+MCP", "How it is achieved"], rows)

    p = doc.add_paragraph()
    pr = p.add_run(
        f"Result: {tm/60:.2f} hours/day for one person, leaving "
        f"{(8-tm/60)*60:.0f} minutes of buffer. MCP alone saves a further "
        f"{tl-tm} minutes on top of the library ({((1-tm/tl)*100):.0f}% faster)."
    )
    pr.bold = True
    doc.add_paragraph()

    # 4
    doc.add_heading("4. WHAT THE MCP CAN AND CANNOT DO", level=1)
    doc.add_paragraph(
        "There is no official CapCut MCP. The working route is a community stack: "
        "VectCutAPI (Python backend) writes a CapCut draft folder on disk, and "
        "capcut-mcp-server exposes 11 tools over MCP. The agent never drives the "
        "CapCut UI — it builds the draft, you open it and finish."
    )
    doc.add_heading("4.1 Tools available (11)", level=2)
    table(["Tool", "What it does"], [[a, b] for a, b in MCP_CAN])
    doc.add_heading("4.2 What MCP cannot do — the editor still does this", level=2)
    table(["Limitation", "Why it matters"], [[a, b] for a, b in MCP_CANNOT])
    p = doc.add_paragraph()
    pr = p.add_run("Rule: MCP assembles the rough cut. The editor owns the final cut.")
    pr.bold = True
    doc.add_paragraph()

    # 5
    doc.add_heading("5. SETUP — VERIFIED STEPS", level=1)
    doc.add_paragraph(
        "Checked on this machine: Python 3.11.15, Node v24.15.0, npm 11.12.1, "
        "ffmpeg 8.1.1, git 2.54.0 — all prerequisites are present."
    )
    table(["#", "Step", "Command", "Notes", "Done when"],
          [[a, b, c, d, e] for a, b, c, d, e in SETUP_STEPS])
    doc.add_paragraph()

    # 6
    doc.add_heading("6. DAILY SCHEDULE (finishes 13:30, 15 min buffer)", level=1)
    table(["Start", "End", "Dur", "Stage", "What happens", "Output"],
          [[a, b, c, d, e, f] for a, b, c, d, e, f in DAY_PLAN])
    doc.add_paragraph(
        "Scheduling logic: group similar work (all 3 Shorts assembled together so "
        "the agent context is reused), put the highest-focus work (Long polish) in "
        "the best-energy slot, and leave engagement for last because it needs no "
        "deep focus."
    )
    doc.add_paragraph()

    # 7
    doc.add_heading("7. ENGLISH CONTENT RULES", level=1)
    table(["Element", "Rule", "Example"], [[a, b, c] for a, b, c in ENGLISH_RULES])
    doc.add_paragraph()

    # 8
    doc.add_heading("8. QC CHECKLIST BEFORE PUBLISH", level=1)
    table(["Item", "Criteria", "Level"], [[a, b, c] for a, b, c in QC])
    doc.add_paragraph(
        "Guardrail is a BLOCKING check: if the video promises profit or shows a "
        "simulated trade as real, it does not publish regardless of everything else."
    )
    doc.add_paragraph()

    # 9
    doc.add_heading("9. BUILD-TO-SELL CRITERIA", level=1)
    table(["Criterion", "Meaning", "Measurable threshold", "Evidence"],
          [[a, b, c, d] for a, b, c, d in BTS])
    p = doc.add_paragraph()
    pr = p.add_run("Build-to-sell test: ")
    pr.bold = True
    p.add_run(
        "if the current editor is away today, can a new person read this SOP and "
        "ship 3 Shorts + 1 Long on their first day? If not, the SOP is not good enough."
    )
    doc.add_paragraph()

    # 10
    doc.add_heading("10. RISKS", level=1)
    table(["Risk", "Impact", "Mitigation", "Level"],
          [[a, b, c, d] for a, b, c, d in RISKS])
    doc.add_paragraph()

    # 11
    doc.add_heading("11. OPEN ITEMS", level=1)
    table(["Item", "Current state", "Action"], [[a, b, c] for a, b, c in OPEN_ITEMS])

    path = OUT / "AZZAM_SOP_FINAL.docx"
    doc.save(path)
    return path


def build_xlsx() -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter

    HF = PatternFill("solid", fgColor="1F3864")
    HFONT = Font(bold=True, color="FFFFFF", size=10)
    TFONT = Font(bold=True, size=14, color="1F3864")
    NFONT = Font(italic=True, size=9, color="555555")
    THIN = Side(style="thin", color="BFBFBF")
    BD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

    wb = Workbook()
    used = [False]

    def sheet(name, title, note, headers, rows, widths=None, numbers=None, wrap=None):
        if not used[0]:
            ws = wb.active
            used[0] = True
        else:
            ws = wb.create_sheet(name)
        ws.title = name
        ws["A1"] = title
        ws["A1"].font = TFONT
        ws["A2"] = note
        ws["A2"].font = NFONT
        hr = 4
        for j, h in enumerate(headers, 1):
            c = ws.cell(row=hr, column=j, value=h)
            c.fill = HF
            c.font = HFONT
            c.border = BD
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for i, row in enumerate(rows, hr + 1):
            for j, v in enumerate(row, 1):
                c = ws.cell(row=i, column=j, value=v)
                c.border = BD
                c.font = Font(size=10)
                c.alignment = Alignment(vertical="top",
                                        wrap_text=(headers[j-1] in (wrap or set())))
                if numbers and headers[j-1] in numbers and isinstance(v, (int, float)):
                    c.number_format = "#,##0"
        for j, h in enumerate(headers, 1):
            L = get_column_letter(j)
            if widths and h in widths:
                ws.column_dimensions[L].width = widths[h]
            else:
                longest = len(str(h))
                for row in rows[:200]:
                    if j - 1 < len(row):
                        longest = max(longest, len(str(row[j-1])))
                ws.column_dimensions[L].width = min(max(longest + 2, 10), 70)
        if rows:
            ws.auto_filter.ref = f"A{hr}:{get_column_letter(len(headers))}{hr+len(rows)}"
        ws.freeze_panes = ws.cell(row=hr + 1, column=1)
        return ws

    tt = sum(s[1] for s in STAGES)
    tl = sum(s[2] for s in STAGES)
    tm = sum(s[3] for s in STAGES)

    # 01 PERFORMANCE
    rows = [[n, a, b, c, a - c, note] for n, a, b, c, note in STAGES]
    rows.append(["TOTAL (min)", tt, tl, tm, tt - tm, ""])
    rows.append(["TOTAL (hours)", round(tt/60, 2), round(tl/60, 2), round(tm/60, 2),
                 f"−{(1-tm/tt)*100:.0f}%", ""])
    sheet("01_PERFORMANCE", "PERFORMANCE — MANUAL vs LIBRARY vs +MCP",
          f"1 editor, {KPI['shorts']} Shorts + {KPI['long']} Long "
          f"({KPI['long_min']} min)/day. Unit: minutes.",
          ["Stage", "Manual", "Library", "+MCP", "Saved vs manual", "How"],
          rows,
          widths={"Stage": 28, "Manual": 10, "Library": 10, "+MCP": 9,
                  "Saved vs manual": 15, "How": 52},
          numbers={"Manual", "Library", "+MCP", "Saved vs manual"},
          wrap={"How"})

    # 02 SETUP
    sheet("02_MCP_SETUP", "CAPCUT MCP SETUP — VERIFIED STEPS",
          "Prereqs confirmed on this machine: Python 3.11.15, Node v24.15.0, "
          "npm 11.12.1, ffmpeg 8.1.1, git 2.54.0",
          ["#", "Step", "Command", "Notes", "Done when"],
          [list(x) for x in SETUP_STEPS],
          widths={"#": 5, "Step": 28, "Command": 62, "Notes": 46, "Done when": 32},
          wrap={"Command", "Notes", "Done when"})

    # 03 MCP TOOLS
    sheet("03_MCP_TOOLS", "MCP TOOLS — WHAT IT CAN DO",
          "11 tools from capcut-mcp-server (TypeScript, MIT) over VectCutAPI backend.",
          ["Tool", "What it does"],
          [list(x) for x in MCP_CAN],
          widths={"Tool": 26, "What it does": 78},
          wrap={"What it does"})

    # 04 MCP LIMITS
    sheet("04_MCP_LIMITS", "MCP LIMITS — WHAT THE EDITOR STILL DOES",
          "MCP assembles the rough cut. The editor owns the final cut.",
          ["Limitation", "Why it matters"],
          [list(x) for x in MCP_CANNOT],
          widths={"Limitation": 30, "Why it matters": 74},
          wrap={"Why it matters"})

    # 05 SCHEDULE
    sheet("05_DAILY_SCHEDULE", "DAILY SCHEDULE",
          "Finishes 13:30. Buffer 15 min. Do not skip steps.",
          ["Start", "End", "Dur", "Stage", "What happens", "Output"],
          [list(x) for x in DAY_PLAN],
          widths={"Start": 9, "End": 9, "Dur": 7, "Stage": 26,
                  "What happens": 58, "Output": 30},
          wrap={"What happens", "Output"})

    # 06 ENGLISH RULES
    sheet("06_ENGLISH_RULES", "ENGLISH CONTENT RULES",
          "Channel language is ENGLISH. Applies to every video.",
          ["Element", "Rule", "Example"],
          [list(x) for x in ENGLISH_RULES],
          widths={"Element": 18, "Rule": 66, "Example": 52},
          wrap={"Rule", "Example"})

    # 07 QC
    sheet("07_QC_CHECKLIST", "QC CHECKLIST BEFORE PUBLISH",
          "Guardrail is a BLOCKING check.",
          ["Item", "Criteria", "Level"],
          [list(x) for x in QC],
          widths={"Item": 20, "Criteria": 62, "Level": 26},
          wrap={"Criteria"})

    # 08 BUILD TO SELL
    sheet("08_BUILD_TO_SELL", "BUILD-TO-SELL CRITERIA",
          "Test: if the editor is away today, can a new person ship on day 1?",
          ["Criterion", "Meaning", "Measurable threshold", "Evidence"],
          [list(x) for x in BTS],
          widths={"Criterion": 26, "Meaning": 48, "Measurable threshold": 44,
                  "Evidence": 42},
          wrap={"Meaning", "Measurable threshold", "Evidence"})

    # 09 RISKS
    sheet("09_RISKS", "RISKS",
          "High-level risks need a mitigation in place before production starts.",
          ["Risk", "Impact", "Mitigation", "Level"],
          [list(x) for x in RISKS],
          widths={"Risk": 34, "Impact": 38, "Mitigation": 56, "Level": 10},
          wrap={"Impact", "Mitigation"})

    # 10 OPEN ITEMS
    sheet("10_OPEN_ITEMS", "OPEN ITEMS",
          "Blockers that must close before the first production day.",
          ["Item", "Current state", "Action"],
          [list(x) for x in OPEN_ITEMS],
          widths={"Item": 30, "Current state": 52, "Action": 52},
          wrap={"Current state", "Action"})

    # 11 TIME LOG
    sheet("11_TIME_LOG", "TIME LOG (fill in daily)",
          "Fill actual minutes to see which stage runs over target.",
          ["Date", "Pick material", "Script", "Stage assets", "MCP 3 Shorts",
           "Polish 3 Shorts", "MCP Long", "Polish Long", "Subtitles", "Audio/color",
           "Export/QC", "Packaging", "Publish/engage", "TOTAL", "Notes"],
          [[""] * 15 for _ in range(31)],
          widths={"Date": 12, "Pick material": 12, "Script": 9, "Stage assets": 12,
                  "MCP 3 Shorts": 12, "Polish 3 Shorts": 14, "MCP Long": 10,
                  "Polish Long": 11, "Subtitles": 10, "Audio/color": 11,
                  "Export/QC": 10, "Packaging": 10, "Publish/engage": 13,
                  "TOTAL": 9, "Notes": 26})

    path = OUT / "AZZAM_SOP_FINAL.xlsx"
    wb.save(path)
    return path


def main() -> int:
    tt = sum(s[1] for s in STAGES)
    tl = sum(s[2] for s in STAGES)
    tm = sum(s[3] for s in STAGES)
    print(f"Manual : {tt} min ({tt/60:.2f} h)")
    print(f"Library: {tl} min ({tl/60:.2f} h)  -{(1-tl/tt)*100:.0f}%")
    print(f"+MCP   : {tm} min ({tm/60:.2f} h)  -{(1-tm/tt)*100:.0f}%")
    print(f"Buffer : {(8-tm/60)*60:.0f} min/day")
    d = build_docx()
    x = build_xlsx()
    for p in (d, x):
        print(f"Saved: {p.resolve()}  ({p.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
