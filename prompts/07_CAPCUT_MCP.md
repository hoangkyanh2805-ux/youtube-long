# PROMPT 7 — CAPCUT MCP DRAFT BUILD (English channel)

## Preconditions
- VectCutAPI backend running on http://localhost:9001
- capcut-mcp-server connected to the agent
- Master templates exist: Short 9:16 and Long 16:9

## Short build prompt (use once per Short)
```
Build a CapCut draft for a YouTube Short.

Canvas: 1080x1920, fps 30.
Working folder: assets/08_EXPORTS/shorts/<slug>/

Steps:
1. capcut_create_draft width=1080 height=1920 fps=30
2. capcut_add_video for each clip in order (chart clip -> b-roll -> chart clip)
   - set start/end from the shot list
   - volume 0.0 for b-roll under voice
3. capcut_add_subtitle with the SRT file (white text, background enabled)
4. capcut_add_text for the 0-3s hook (font_size 72, animation fade_in)
5. capcut_add_audio background music, volume 0.15, fade_in 0.5, fade_out 1.0
6. capcut_save_draft

Do NOT export. Do NOT add a profit claim. Do NOT show a simulated trade as real.

Shot list:
[paste shot list with file paths and timings]
SRT file: [path]
```

## Long build prompt (5-part timeline)
```
Build a CapCut draft for an 8-minute YouTube video.

Canvas: 1920x1080, fps 30.
Structure (must match):
00:00 Problem  |  01:30 Cause  |  03:30 Solution  |  06:30 Checklist  |  07:30 CTA

Steps:
1. capcut_create_draft width=1920 height=1080 fps=30
2. Add chart clips + b-roll per the shot list
3. capcut_add_text for section titles at each timestamp
4. capcut_add_subtitle with the full SRT
5. capcut_add_audio music bed, volume 0.12, ducking under voice
6. capcut_save_draft

Do NOT export. Keep every number exactly as written in the script — never invent figures.

Outline:
[paste outline]
Shot list: [paste]
SRT: [path]
```

## After the agent returns the draft
1. Open CapCut Pro.
2. Find the `dfd_` draft folder.
3. Polish: cut points, punch-ins, pacing, audio mix.
4. Export by hand (MCP cannot export).

## If MCP fails
Fall back to the manual master template. Log the failure in sheet 11_TIME_LOG
so you can see how often it breaks.
