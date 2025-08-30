# MARKET MUSE — TRADING DESK 📈

*Owner: Assistant (full ops). User never runs commands or modifies the canvas in any way. Clock: All times in ET (12‑hour).*

---

## Meta • Ops Notes (read‑only) 🔧

- **Config discovery:** `MUSE_DC_CONFIG_DIR` → `./configs` (packaged defaults)
- **Canvas writes:** anchor‑only; dry‑run → minimal‑diff → verify → rollback on failure.
- **Anchor locks & throttle:** single‑writer per anchor; ≤1 write/min per live dashboard row; global 750 ms coalesce.
- **Integrity ping:** tiny HUD note if any write is rolled back or rejected.
- **Schema discipline:** headers versioned; non‑table anchors are free‑form; never *reflow*.
- **Post‑ship notes:** **archive-only** — append to **ARCHIVE** (and **CHANGELOG** if major); no System Health rows.
- **Pro‑Prepend — Market Muse:** atomic patches; no networking (unless Deep Research explicitly set); Python 3.10+; 12‑hour ET in outputs; strict schemas/enums; idempotent publishers; deterministic tests/fixtures.

---

## Dashboard (quick view) 🎛️ — DASHBOARD

### Dashboard Status (compact) — DASHBOARD\_STATUS

| Metric                | Value                          |
| --------------------- | ------------------------------ |
| Risk Sizer Multiplier | 0.95x (regime=NEUTRAL, vix=17) |

### SmartPricing — Summary (30d) — SMARTPRICING\_SUMMARY   &#x20;

| Structure        | Fast bps | Normal bps | Patient bps | Samples |
| ---------------- | -------- | ---------- | ----------- | ------- |
| VERTICAL\_CREDIT | —        | 400        | 100         | 2       |

*Risk Posture & SmartPricing:* prefer **REGIME\_CAL** (Market Regime) when present; otherwise use baseline defaults.

- **Session:** [Pre | **RTH** | Post]
- **Risk posture:** Aggressive entries allowed; **−25% premium stop guideline** unless level invalidation first.
- **SmartPricing:** Mid (default). Dynamic: **Normal** (default); **Fast** on liquid/tight/momentum; **Patient** on wider credits/IC‑IB or non‑urgent.

---

## 1) Mission & Operating Mode 🎯

**Goal:** Aggressive, options‑first *intraday*/short‑swing trading with strict risk controls; equity fallback only when options are sub‑optimal.

**Scope:** Index ETFs (**SPY/QQQ**) + Playbook tickers (**UNH, RDDT, PLTR, TTD, SNAP**) + earnings plays.

**Automation:** All monitors run server‑side; alerts obey the Final Outbound Filter; the app/browser isn’t required.

---

## 2) Alerts & Silence Rules 🔔

- **Outbound tags allowed:** `[ENTRY NOW ✅]`, `[EXIT NOW 🛑]`, `[NEWS 📰]`, `[MARKET ⬆️/⬇️]`.
- **Silence rule:** If nothing actionable, send nothing (no “no signal” pings).
- **Heads‑up (auto):** Off by default; auto‑enabled only on Tier‑1 days during **8:20–9:50 AM** and **1:45–2:30 PM**.
- **Controls respected everywhere:** `HALT_UNTIL`, `QUIET_UNTIL`, `HEADSUP_ON`.

---

## 3) ETF Market Pulse (overview) 📊

- **Tracked:** SPY, QQQ, IWM, DIA, VIX, HYG, TLT, UUP.
- **Primary entries:** Break‑retest through **PDH/PDL** (10‑min hold); default options idea 0.35–0.45Δ expiring next Friday.
- **Momentum path (indices only):** 5‑min close past PDH/PDL + **VIX** trend + breadth; auto‑size by **VIX**; stop = last 5‑min swing or \~20%; targets 1.5R → ATR trail.
- **Beacon:** Risk‑On/Off one‑liner on state change only (**VWAP** + breadth + **VIX** 15‑min cooldown).
- **VIX Shock Guard:** If **abs(ΔVIX) ≥ 5%** in 3 min → pause momentum entries for 15 min (retest path still allowed).

---

## 4) Risk, Structure & OA Exits (summary) 🛡️

- **Liquidity guards:** Bid‑ask ≤ **5%** of mid; **OI ≥ 500** (else alternate Δ/expiry or shares).
- **IVR → structure:** <30 single‑leg (or **LCS/LPS** if fair); 30–50 favor **LCS/LPS**; >50 **SPS/SCS**, **IC/IB** if neutral.
- **Stops/targets:** Stop = last 5–15m swing or **−25% premium** (\~20% for index momentum). Targets **0.5x/1.0x/EM**; runners ATR trail.
- **Exit types:** Profit Taking, Stop %, Trailing, Price Target, Expiration, Earnings approach (**never “Touch”**).
- **Equity fallback:** Long‑only when options inefficient; Late‑Day Equity Guard bars new **overnight** equity after **3:30 PM ET** unless Drift Watch is active.

### OA Policy — Defaults (v1.0) 📝 — OA\_POLICY

- Global stop guideline: −25% premium unless technical invalidation first.
- Profit‑taking ladder per trade (e.g., **30%/50%/70%**) or as specified in alert.
- Trailing: optional, defined per trade; default **off**.
- **Expiration:** choose expiries that support **1–10 trading‑day** holds; minimum hold guideline ≥ **1 day**. Baseline: **weeklies (next Friday)** for momentum; **1–2 weeks (≤10 sessions)** for drift/plays; always exit sooner on invalidation.
- **Earnings:** do **not** hold through earnings unless explicitly noted.
- **SmartPricing:** Mid default; Dynamic (Normal/Fast/Patient) per liquidity/momentum; IC/IB and broad credits default **Patient**.
- **Never** use OA “Touch”.
- *Changes to v propagate automatically to new alerts.*

---

### SmartPricing — Rules (spread/IVR/ATR) 🧮 — SMART\_PRICING\_CAL

**SmartPricing v2 — Calibration Rules (deterministic)**

| Structure | Spread% ≤ | IVR band | ATR/Price ≤ | Mode    | Notes                                        |
| --------- | --------- | -------- | ----------- | ------- | -------------------------------------------- |
| SINGLE    | 0.50      | Any      | 1.0         | Fast    | Tight market; prefer limit near mid          |
| SINGLE    | 1.25      | Any      | 2.0         | Normal  | Typical liquid names                         |
| SINGLE    | 2.50      | Any      | —           | Patient | Wider market; step orders                    |
| LCS/LPS   | 0.75      | Any      | 1.0         | Fast    | Debit spread; allow small chase              |
| LCS/LPS   | 1.50      | Any      | 2.0         | Normal  | Standard                                     |
| LCS/LPS   | 2.50      | Any      | —           | Patient | Wide; staggered entries                      |
| SPS/SCS   | 0.75      | 50+      | 1.5         | Fast    | Credit; strong IVR (50+)                     |
| SPS/SCS   | 1.50      | 20–50    | 2.0         | Normal  | Credit; mid IVR (20–50)                      |
| SPS/SCS   | 2.50      | Any      | —           | Patient | Credit; wide market                          |
| IC/IB     | 0.50      | 50+      | 1.0         | Fast    | Tight condor/fly; high IVR                   |
| IC/IB     | 1.25      | 40–70    | 2.0         | Normal  | IVR in 40–70 sweet spot                      |
| IC/IB     | 1.75      | Any      | —           | Patient | Wider; conservative pricing                  |
| ANY       | —         | Any      | —           | Patient | Guardrail: spread% > 3.00 → Patient or avoid |

## 5) Playbook Watchlist (live) 📋

| Ticker   | Bias                           | Notes                                                  |
| -------- | ------------------------------ | ------------------------------------------------------ |
| **SPY**  | Tactical per Beacon & triggers | Momentum path + break‑retest; OA exits auto; no equity |
| **QQQ**  | Tactical per Beacon & triggers | Momentum path + break‑retest; OA exits auto; no equity |
| **UNH**  | Calls bias                     | A+B triggers; equity fallback allowed (long‑only)      |
| **RDDT** | Puts bias                      | A+B triggers; equity fallback allowed (long‑only)      |
| **PLTR** | Puts bias                      | A+B triggers; equity fallback allowed (long‑only)      |
| **TTD**  | Calls bias                     | A+B triggers; equity fallback allowed (long‑only)      |
| **SNAP** | Calls bias                     | A+B triggers; equity fallback allowed (long‑only)      |

---

## Playbook Table (ops table) 🗃️ — PLAYBOOK\_TABLE&#x20;

**Schema (header synonyms allowed):**

- Enabled (On)
- Side (Long/Short)
- Ticker
- Setup (Pattern/Thesis)
- Trigger (If/Level/Condition)
- Entry Plan (Call/Put/**LCS/LPS/SPS/SCS** strikes + expiry)
- Stop (Level **or** Premium%)
- Targets (T1/T2/T3; levels or premium%)
- Confirm (VIX/Rates/Credit filters)
- Size (Risk Sizer notes)
- Notes

**Template row**

| Enabled | Side | Ticker | Setup   | Trigger   | Entry Plan   | Stop                   | Targets  | Confirm              | Size         | Notes   |
| ------- | ---- | ------ | ------- | --------- | ------------ | ---------------------- | -------- | -------------------- | ------------ | ------- |
| Y       | Long | SPY    | [setup] | [trigger] | [leg detail] | Level **or** −25% prem | T1/T2/T3 | VIX / Rates / Credit | [risk units] | [notes] |

*Rules:* Drives **intraday** playbook; explicit vertical names; single‑leg baseline unless spreads clearly superior.

---

### Playbook Audit (read‑only) 🔍 — PLAYBOOK\_AUDIT

*Initial audit populated. Add/edit rows in ****PLAYBOOK\_TABLE**** and I'll refresh this report.*

#### Summary

- Rows audited: 0
- Issues flagged: 0
- Rows needing attention: 0
- Non‑destructive fixes applied: 0

#### Per‑Row Findings

| # | Ticker | Enabled | Side | Setup | Trigger OK | Entry OK | Stop OK | Targets OK | Warnings |
| - | ------ | ------- | ---- | ----- | ---------- | -------- | ------- | ---------- | -------- |
| — | —      | —       | —    | —     | —          | —        | —       | —          | —        |

## Active Trades (live) 🧾 — ACTIVE\_TRADES

*User‑confirmed positions only; signals are not auto‑logged.*

| Opened (ET) | Ticker | Direction | Contract(s) | Avg Price | Current | Invalidation | Premium Stop     | Targets  | Status |
| ----------- | ------ | --------- | ----------- | --------- | ------- | ------------ | ---------------- | -------- | ------ |
| —           | —      | —         | —           | —         | —       | —            | **−25% default** | T1/T2/T3 | —      |

---

## 6) Playbook & Rules 📘

### Market Regime — Calibration Report 🧭 — REGIME\_CAL

*Auto-updated by Weekend Catalyst Scan tools; Dashboard Risk Posture + SmartPricing consume automatically when present. Baseline is used until a report exists.*

### Playbook Bias Handling 🧭 — PLAYBOOK\_BIAS

*Bias is user-selected and never auto-modified. Scanners, gates, and alerts respect the selected bias but do not change it.*

### Index Momentum — Calibration Report 📈 — MOMENTUM\_CAL&#x20;

*Auto-updated by Weekend Catalyst Scan tools; Dashboard Risk Posture + SmartPricing consume automatically when present. Baseline is used until a report exists.*

### Risk Sizer — Calibration Table ⚖️ — RISK\_SIZER\_CAL

| Regime      | VIX Band | Multiplier |
| ----------- | -------- | ---------- |
| TREND\_UP   | <15      | 1.20       |
| TREND\_UP   | 15-20    | 1.10       |
| TREND\_UP   | 20-25    | 1.00       |
| TREND\_UP   | 25-30    | 0.90       |
| TREND\_UP   | ≥30      | 0.80       |
| NEUTRAL     | <15      | 1.00       |
| NEUTRAL     | 15-20    | 0.95       |
| NEUTRAL     | 20-25    | 0.90       |
| NEUTRAL     | 25-30    | 0.85       |
| NEUTRAL     | ≥30      | 0.75       |
| CHOP        | <15      | 0.90       |
| CHOP        | 15-20    | 0.85       |
| CHOP        | 20-25    | 0.80       |
| CHOP        | 25-30    | 0.70       |
| CHOP        | ≥30      | 0.60       |
| TREND\_DOWN | <15      | 0.85       |
| TREND\_DOWN | 15-20    | 0.80       |
| TREND\_DOWN | 20-25    | 0.70       |
| TREND\_DOWN | 25-30    | 0.60       |
| TREND\_DOWN | ≥30      | 0.50       |

### Risk Sizer v3 — Δ by Time-of-Day — RISK\_SIZER\_CAL\_V2  &#x20;

| TOD    | Δ (mult) | Notes   |
| ------ | -------- | ------- |
| Open   | 1.00     | neutral |
| AM     | 1.00     | neutral |
| Midday | 1.00     | neutral |
| PM     | 1.00     | neutral |
| Close  | 1.00     | neutral |

### Momentum Wick — Calibration (False Break Guard) — MOMENTUM\_WICK\_CAL

| Setting                   | Value | Unit           | Notes                         |
| ------------------------- | ----- | -------------- | ----------------------------- |
| max\_retrace\_wick\_ratio | 0.25  | ratio of range | LONG: (H-C)/R; SHORT: (C-L)/R |
| min\_body\_ratio          | 0.35  | ratio of range | abs(C-O)/R                    |
| min\_volume\_multiple     | 1.40  | x avg          | vs avg last 20 bars           |
| volume\_lookback\_bars    | 20    | bars           | volume MA window              |
| atr\_lookback\_bars       | 14    | bars           | ATR window                    |
| max\_atr\_pct             | 3.5   | %              | ATR/close × 100               |
| cooldown\_minutes         | 10    | minutes        | min gap between entries       |

### Momentum Wick — Overrides (per-symbol × TOD) — MOMENTUM\_WICK\_OVERRIDES

| Symbol | TOD | WickMax% | BodyMinR | VolNormMin | RetestReq | Notes |
| ------ | --- | -------- | -------- | ---------- | --------- | ----- |

### News — Calibration (Signal Quality) — NEWS\_CAL&#x20;

| Cohort     | ConfirmMin | MinVolMult | MaxATR% | Notes    |
| ---------- | ---------- | ---------- | ------- | -------- |
| DEFAULT    | 5          | 0.50       | 10.00   | baseline |
| TECH       | 10         | 1.00       | 8.00    | baseline |
| HEALTHCARE | 10         | 1.00       | 9.00    | baseline |
| EARNINGS   | 5          | 1.50       | 9.00    | baseline |
| RUMOR      | 10         | 1.20       | 7.50    | baseline |

### Alert Throttle — Calibration (Entry Anti-Noise) — ALERT\_THROTTLE\_CAL

| Name    | Lookback (bars) | MinHits | Suppress (min) | Decay | MaxSuppress | Notes           |
| ------- | --------------- | ------- | -------------- | ----- | ----------- | --------------- |
| DEFAULT | 120             | 3       | 15             | 0.5   | 45          | —               |
| EXIT    | 120             | 3       | 10             | 0.5   | 45          | Exit alerts gap |

### Structure Recommender — Rules — STRUCTURE\_REC\_CAL

| Symbol | IVR Border | Spread Border (%) | Width×ATR | Credit OK | Notes |
| ------ | ---------- | ----------------- | --------- | --------- | ----- |

### Structure Recommender v2 — STRUCTURE\_REC\_CAL\_V2  &#x20;

| Symbol | TOD | IVR | Liquidity | Slippage (bps p50) | Suggested | Pricing | Notes |
| ------ | --- | --- | --------- | ------------------ | --------- | ------- | ----- |

### 6.4 Equity Fallback (long‑only, non‑ETF)

- **Scope:** Playbook stocks & earnings plays only. No ETFs. No short equity.
- **Use shares instead of options** when: liquidity poor after trying alt Δ/expiry; poor RR on debit (single‑leg or **LCS** breakeven > \~0.75× EM); post‑ER upside drift; etc.
- **Entry rules:** Same A+B triggers; use break‑retest (no single‑name momentum). Stops/targets per §4.
- **Late‑Day Equity Guard:** After **3:30 PM ET**, block new overnight equity unless Drift Watch active (Earnings T+2 or Playbook T+1).

### 6.5 Post‑ER Drift Watch (T+2)

- **When active:** If the Big Brain dossier flags a likely upside drift, enable a **T+2 drift window** by default.
- **Trigger (long‑only):** Break‑retest above ER‑day high or 1H high with sector confirmation and no vol conflict (**VIX** not spiking).
- **Structure:** Prefer single‑leg calls; if **IVR 30–50**, use **LCS**; if options inefficient per /\$/δ, use equity fallback.
- **Risk/Expiry:** Standard stops/targets; if using options, prefer **1–2 weeks (≤10 sessions)** to allow drift; trim into 0.5×/1.0× EM.

### 6.6 Playbook Drift Watch (non‑ER, T+1)

- **Activation:** When a Playbook name gets a **[NEWS 📰] Bullish** classification with price confirmation and aligned context, tag Drift Watch (**T+1**).
- **Window:** Next regular session (**T+1**) after the news; auto‑expires end of that session if no setup.
- **Trigger (long‑only):** Break‑retest above news‑day high or 1H high with context aligned.
- **Structure:** Options first (calls / **LCS** if **IVR 30–50**). If options are sub‑optimal, use equity fallback (long‑only).
- **Silence:** Only `[ENTRY NOW ✅]` may alert if it actually triggers; otherwise no messages.

---

## Market Beacon — Calibration Report 📐 — BEACON\_CAL

*Awaiting calibration report from BBP‑203…*

## Market Beacon — Calibration v2 (candidate) — BEACON\_CAL\_V2

| Symbol | Regime | Source | Lead (bars) | UpThresh (bps) | DownThresh (bps) | Hysteresis (bps) | Cooldown (bars) | Notes |
| ------ | ------ | ------ | ----------- | -------------- | ---------------- | ---------------- | --------------- | ----- |

## Beacon — Adapter Status 🧊 — BEACON\_ADAPTER

*Updated:* 2025-08-18 01:00 PM ET

## Effective cooldown: 15 min (candidate=15, ewma=0.00 fph, regime=n/a)

## 7) Controls (quick commands) 🎚️

- **Heads‑up on/off:** toggles pre‑alerts (*ACTIONABLE ⚠️*).
- **Timed heads‑up (auto):** On Tier‑1 days (**CPI/PPI/PCE/NFP/FOMC**), auto‑enable (*ACTIONABLE ⚠️*) during the windows above.
- **Halt until [time]:** pause all alerts.
- **Quiet until [time]:** log silently; send a single ⏳ Quiet mode summary when time ends.

### 7.5) Automations & Tasks (Live) 🤖 — AUTOMATIONS&#x20;

| Task                                                         | Cadence (ET)                                            | Last Run (ET) | Next Run (ET) | Status |
| ------------------------------------------------------------ | ------------------------------------------------------- | ------------- | ------------- | ------ |
| 🛠️ Update Intraday Dashboard (HUD + A+B + News)             | 9:30 AM–4:00 PM (RTH), every 15 min (@ :03/:18/:33/:48) | —             | —             | PAUSED |
| ⚡ Market Pulse — Open (SPY/QQQ)                              | 9:35 AM; retries to 9:40; backfill 9:41                 | —             | —             | PAUSED |
| 🧾 Close Orchestrator — Snapshot, Logs & Reliability         | Weekdays 4:05 & 4:11                                    | —             | —             | PAUSED |
| 🪨 Weekend Catalyst Scan                                     | Sunday 6:00 PM                                          | —             | —             | PAUSED |
| 📆 Earnings Orchestrator — Radar, Dossier & Drift (AM+Close) | 8:00 & 8:15 AM; 4:00 & 4:15 PM (trading days)           | —             | —             | PAUSED |
| 🚀 Burst Scan — AM Tier‑1 Window                             | 8:25 AM (±10 min window, actionable‑only)               | —             | —             | PAUSED |
| 🚀 Burst Scan — FOMC 2:00 Window                             | 1:55 PM (±10 min, actionable‑only)                      | —             | —             | PAUSED |
| 🚀 Burst Scan — FOMC 2:30 Window                             | 2:25 PM (±10 min, actionable‑only)                      | —             | —             | PAUSED |
| 🚀 Burst Scan — PM Window (Staggered)                        | 1:45 PM (±10 min, actionable‑only)                      | —             | —             | PAUSED |
| 🛡️ Position Guardian — Exit & Profit Lock                   | 9:30 AM–4:00 PM (RTH), every 15 min (@ :02/:17/:32/:47) | —             | —             | PAUSED |

---

## 8) Big Brain — Prompts (queue) 🧠 — BIG\_BRAIN

### Standing Charter — Pro Knowledge Usage *(never remove)*

- On completion, auto-archive to ARCHIVE and remove from Queue and Prompt Library.

- The Assistant may generate **BBPs** at any time to leverage GPT‑5 Pro’s knowledge for upgrades across the stack.

- **Scope:** canvas structure/content, automations & tasks, trading models & playbooks, risk/exit policy, data connectors, reliability/CI, and docs.

- Each **BBP** must specify **Pro mode(s)** and follow guardrails: atomic patches, minimal diffs, tests/fixtures, Safe‑Apply (preflight + diff budget + rollback), and **no networking** unless **Deep Research** is specified.

- **BBPs** must be concise, emoji‑free inside prompt blocks, and include an **acceptance** checklist.

- **Auto‑placement:** When a BBP creates a new report/log/section, the Assistant will create the anchor and place it under the most appropriate parent (e.g., **6.x Playbook & Rules**, **9.x Earnings**, **10.x Logs**), keep numbering consistent, and refresh **ANCHOR\_MAP**. The user never needs to move sections manually.

### Queue Ordering — Execution Policy *(do not remove)*

- Strict top‑down execution order. The Assistant sets priority and arranges items exactly in the order the user will submit them to **Pro**.
- The user will work through **BBPs** from the **top down** unless an item is explicitly tagged otherwise.
- **Timing tags (optional):** `[NOW]`, `[TODAY AM]`, `[TODAY PM]`, `[AFTER CLOSE]`, `[OVERNIGHT]`, `[LOW RISK]`, `[HEAVY]`.
- **Non‑timing labels (optional):** `[FOLLOW‑UP]`, `[SUGGESTION]`, `[NEEDS DATA]`, `[BLOCKED]`, `[HOTFIX]`.
- Assistant may reorder to optimize outcomes; any reordering is reflected immediately on the canvas.

### BBP Formatting Policy — Queue & Library *(DO NOT REMOVE)*

1. Queue bullets live only in **Queue** (priority & timing) — top‑down (compact cards).\
   **Format:** `- BBP‑### — short label [tag1, tag2]` — tags required; comma‑separated. (Parser also accepts • and will normalize to -.)
2. Prompt Library cards use one fenced block with the universal template:

```md
#### BBP-###: Title

Mode or Modes:
Goal: –
Requirements:
- –
Deliverables:
- –
Acceptance:
- –
```

3. Do **not** place **BBP** bullets under *Queue Ordering — Execution Policy*.
4. Dashes in `BBP‑###` are normalized automatically; keep the ASCII hyphen when writing.

### Pro Follow‑Up Suggestion Policy (triage + action)

1. **Decide:** *Accept / Modify / Defer / Reject* (brief rationale kept with the BBP or in **CHANGELOG** when executed).
2. **If Accept/Modify:** Convert into a **BBP** with modes, scope, deliverables, and acceptance; tag **[FOLLOW‑UP]** and add timing tag; insert into the queue in **top‑down** order.
3. **If Defer:** Keep out of the live queue; optionally tag **[LOW RISK]** and park for a low‑impact window.
4. **If Reject:** No action; rationale noted briefly.

*Guardrails remain: atomic diffs, Safe‑Apply, and no networking unless Deep Research is explicitly requested.*

### Ship handler (automatic)

When a **BBP** is marked **Shipped**:

- Run **FG Micro** (BBP‑326r3) post‑ship: `mm fg-micro apply` (anchor‑bounded, TableOps/RowOps only). Adds one SYSTEM\_HEALTH incident on anomaly; OPS\_VERIFY guard row enforced.

- Use **ship macros** (BBP‑314) for all ship flows: `mm ship remove-queue`, `mm ship remove-library`, `mm ship archive-append` (anchor-bounded, TableOps-only).

- Append a line to **ARCHIVE**; if the change is major/structural, also append to **CHANGELOG**.

- Remove the **BBP** card from **Prompt Library**.

- Remove the **BBP** from the live **Queue**.

- Avoid duplicates; operations are idempotent.

- **Archive table guard:** if the header is missing, auto‑recreate the standard header before appending.

### Queue (priority & timing) — top‑down (compact cards)  &#x20;

- BBP-333 — SmartPricing Slippage Profiler (per-symbol × TOD) [AFTER CLOSE, LOW RISK]
- BBP-335 — Playbook Outcome Attribution (WR×RR by setup/TOD) [LOW RISK]
- BBP-336 — Snapshot Consistency Auditor (open/close) [LOW RISK]
- BBP-337 — Level Mapper (PDH/PDL/AVWAP publisher) [LOW RISK]

### Prompt Library (full text; read‑only)   &#x20;

```md
#### BBP-333: SmartPricing Slippage Profiler (per-symbol × TOD)

Mode or Modes:
Agent

Goal:
Analyze SMARTPRICING_TELEM to publish per-symbol × time-of-day slippage medians and IQR, and recommend SmartPricing Mode overrides.

Requirements:
- No networking. Read SMARTPRICING_TELEM; compute per (symbol,TOD) medians/IQR; produce suggested mode.
- Append/update SMARTPRICING_SUMMARY_V2 and SMARTPRICING_SUGG_V2.

Deliverables:
- CLI (`mm slippage-profiler run`) and ops docs.

Acceptance:
- Deterministic results on fixtures; suggestions reduce median slippage by ≥10% on targeted symbols (A/B harness).
- No schema drift and idempotent writes.
```

```md
#### BBP-335: Playbook Outcome Attribution (WR×RR by setup/TOD)

Mode or Modes:
Agent

Goal:
Attribute outcomes (WR, median R, EV) by setup/TOD to identify where the playbook excels or lags, publishing a compact weekly report.

Requirements:
- No networking. Source POSITION_LOG + ENTRY_EVENTS; group by (setup, TOD).
- Compute WR, median R, EV, count; produce an attribution table and short notes.

Deliverables:
- CLI (`mm playbook-attrib run`), tests, ops docs.
- New table PLAYBOOK_ATTRIB (append weekly; idempotent) or add to ALERT_QSCORE note.

Acceptance:
- Reproducible metrics on fixtures; report covers ≥90% of labeled trades; no table shrink.
```

```md
#### BBP-336: Snapshot Consistency Auditor (open/close)

Mode or Modes:
Agent

Goal:
Continuously audit that OPENING_SNAPSHOT and CLOSE_SNAPSHOT have exactly one row per session and repair/backfill within policy windows.

Requirements:
- No networking. Read both snapshot tables; verify one-per-day; attempt safe backfill inside guard windows; log one SYSTEM_HEALTH incident on persistent failure.

Deliverables:
- CLI (`mm snapshot-audit run`) with dry-run flag; tests & ops docs.

Acceptance:
- Detects and repairs synthetic “missing row” cases in fixtures with ≥99% success inside the window.
- Writes are append-only; no duplicate-days introduced.
```

```md
#### BBP-337: Level Mapper (PDH/PDL/AVWAP publisher)

Mode or Modes:
Agent

Goal:
Publish key reference levels (PDH/PDL, 1H high/low, anchored VWAP from open) onto a small levels table for tasks to read, avoiding repeated ad-hoc calculations.

Requirements:
- No networking. Use internal price series proxies (where available) or cached series; compute levels at defined checkpoints.
- Idempotent writer updates LEVELS table (append/update block).

Deliverables:
- CLI (`mm levels publish`) + tests/fixtures; optional LEVELS table anchor.

Acceptance:
- Deterministic level values on fixture tapes; no lagged/duplicate level rows; tasks consume values without recomputation.
```

### Archive (shipped BBPs) 📦 — ARCHIVE *(See ****BBP Catalog**** for full BBP history)*

| Date | BBP | Title | Anchors | Notes |
| ---- | --- | ----- | ------- | ----- |











---

## 9) Earnings (Radar & Drift) 📆 — EARNINGS

### 9.1 Earnings Radar (Today → Next 3 days) — EARNINGS\_RADAR&#x20;

*Purpose:* track upside drift candidates after earnings. Auto-expires at end of T+2.

| Ticker | Date/Time (ET) | Bias | ±EM | Planned Structure | Notes | Status |
| ------ | -------------- | ---- | --- | ----------------- | ----- | ------ |
| —      | —              | —    | —   | —                 | —     | —      |

### 9.2 Drift Watch (post‑ER, T+2) — EARNINGS\_DRIFT\_WATCH

*Purpose:* track upside drift candidates after earnings. Auto-expires at end of T+2.

| Ticker | Directional Bias | Window  | Trigger                                  | Status | Updated |
| ------ | ---------------- | ------- | ---------------------------------------- | ------ | ------- |
| —      | —                | T+1/T+2 | Break‑retest above ER‑day high / 1H high | —      | —       |

### 9.3 Earnings Dossier (prepped tickers) — EARNINGS\_DOSSIER&#x20;

*Auto-maintained notes for prepped names; refresh ****IVR/EM****, liquidity, peers before ER; tag Drift Watch after if criteria hit.*

**Pre‑ER checklist**

- **IVR ≥ ?** • ±EM vs historical • Liquidity (spread ≤5%, OI ≥ 500)
- **Event time (BMO/AMC)** • Sector/peer context • **Plan** (structure & stops) • **Post‑ER** drift gates

| Ticker | ER Date/Time (ET) | IVR % | ±EM (%) | Liquidity (spread/OI) | Sector/Peers | Bias | Pre‑plan | Status | Post‑ER Drift Gate | Updated |
| ------ | ----------------- | ----- | ------- | --------------------- | ------------ | ---- | -------- | ------ | ------------------ | ------- |
| —      | —                 | —     | —       | —                     | —            | —    | —        | —      | —                  | —       |

### 9.4 Earnings Drift — Calibration Report 📈 — DRIFT\_CAL &#x20;

| Cohort | T+2 Gate | Bias | Confidence | Notes |
| ------ | -------- | ---- | ---------- | ----- |

*Awaiting first calibrator run (BBP‑245). T+2 drift thresholds & confidence will render here; Dashboard + Playbook helpers will consume when present.*

### 9.5 Earnings EM — Cohort v2 — EARNINGS\_EM\_COHORTS\_V2&#x20;

| Cohort | N | Median Move (%) | IQR (%) | Coverage\@band | Suggested ±EM (%) | Delta vs Baseline (%) | Confidence | Notes |
| ------ | - | --------------- | ------- | -------------- | ----------------- | --------------------- | ---------- | ----- |
| —      | — | —               | —       | —              | —                 | —                     | —          | —     |

### 9.6 Dossier Helpers — EARNINGS\_DOSSIER\_HELPERS&#x20;

| Ticker | Date | Session | Cohort | Suggested ±EM (%) | Confidence | Note |
| ------ | ---- | ------- | ------ | ----------------- | ---------- | ---- |

---

## 10) Logs & Journal (auto‑maintained) 📓 — LOGS

### Regime Log — REGIME\_LOG&#x20;

*Auto-appended by tools; compact one-liners only.*

2025-08-20 03:59 PM ET — [RiskSizer] v2 multiplier=0.95 (regime=NEUTRAL, vix=17)

### 10.1 Position Log (all trades) 📒 — POSITION\_LOG&#x20;

*Every trade entry with structure + exits. Immutable after close; errors corrected via addendum.*

*Note:* **Signals are not auto-logged.** I will only add/update rows when you explicitly confirm you entered/exited.

| ID | Time (ET) | Ticker | Strategy | Direction | Legs / Strikes | Expiry | Entry Type | Entry Px | Size | Stop @ entry | Targets | OA exits | Thesis (1‑line) | Catalyst | Status | P&L | R |
| -- | --------- | ------ | -------- | --------- | -------------- | ------ | ---------- | -------- | ---- | ------------ | ------- | -------- | --------------- | -------- | ------ | --- | - |
| —  | —         | —      | —        | —         | —              | —      | —          | —        | —    | —            | —       | —        | —               | —        | —      | —   | — |

### Post‑Trade Reviews — Drafts 🧠 — PTR\_DRAFTS&#x20;

*Auto-drafted review cards for recently closed trades. Edit/refine, then move to Journal when finalized. This writer never edits ****POSITION\_LOG****.*

### Post-Trade Journal (finalized) 📝 — POST\_TRADE\_JOURNAL

| Time (ET) | PTR\_ID | Ticker | Strategy | Thesis | Outcome | Notes |
| --------- | ------- | ------ | -------- | ------ | ------- | ----- |

### 10.1b Proposed Exit Ladders — PROPOSED\_LADDERS

| Ticker | Regime | Samples | Baseline | Base WR×RR | Base MAE p50 | Base MFE p50 | Proposed | Prop WR×RR | Prop MAE p50 | Prop MFE p50 | Rationale |
| ------ | ------ | ------- | -------- | ---------- | ------------ | ------------ | -------- | ---------- | ------------ | ------------ | --------- |

### 10.1c Entry Events (A+B features) — ENTRY\_EVENTS  &#x20;

| Time (ET) | Symbol | TOD | Side | Wick% | BodyR | VolRel | FirstRetest | RetestQuality | Actionable | EV (R) | BeaconConflict20m | Shock |
| --------- | ------ | --- | ---- | ----- | ----- | ------ | ----------- | ------------- | ---------- | ------ | ----------------- | ----- |

### 10.2 News/Catalyst Log (price‑confirmed only) 📰 — NEWS\_LOG&#x20;

*Only log when news is material and price‑confirmed; otherwise stays out of the log.*

| Time (ET) | Ticker/Index | Headline | Class | Price confirm | Bias change | Action taken |
| --------- | ------------ | -------- | ----- | ------------- | ----------- | ------------ |
| —         | —            | —        | —     | —             | —           | —            |

### 10.2a News Tuner — Weekly Report — NEWS\_TUNER\_REPORT&#x20;

| Date | Cohort | Before | After | Changes | Notes |
| ---- | ------ | ------ | ----- | ------- | ----- |
| —    | —      | —      | —     | —       | —     |

### 10.3 Market Beacon Log (state changes) 🔔 — MARKET\_BEACON\_LOG

*Risk‑On/Off flips only; includes lightweight context for auditability.*

| Time (ET) | State | SPY % | QQQ % | VIX % | HYG % | IWM % | Note |
| --------- | ----- | ----- | ----- | ----- | ----- | ----- | ---- |
| —         | —     | —     | —     | —     | —     | —     | —    |

### 10.4 Earnings Tracker (covered names) 📈 — EARNINGS\_TRACKER&#x20;

*Pre/post‑ER deltas, realized move, IV crush, and outcome vs. bias.*

| Ticker | Event (ET) | ±EM @ T‑0 | Realized (1D) | IV pre/post | Outcome vs bias | Notes |
| ------ | ---------- | --------- | ------------- | ----------- | --------------- | ----- |
| —      | —          | —         | —             | —           | —               | —     |

### 10.5 Opening Snapshot (daily) 🌅 — OPENING\_SNAPSHOT&#x20;

Logged \~9:35 AM ET after the first 5-minute bar closes; silent unless actionable.

| Date | SPY % | QQQ % | vs PDH/PDL | VIX % | HYG % | IWM % | TLT % | UUP % | Beacon | Notes |
| ---- | ----- | ----- | ---------- | ----- | ----- | ----- | ----- | ----- | ------ | ----- |
| —    | —     | —     | —          | —     | —     | —     | —     | —     | —      | —     |

### 10.6 Closing Snapshot (daily) 🌇 — CLOSE\_SNAPSHOT&#x20;

Logged \~4:11 PM ET. End-of-day context; pairs with Opening Snapshot for a clean tape diary.

| Date | SPY % | QQQ % | VIX % | HYG % | IWM % | UUP % | Beacon | Notes |
| ---- | ----- | ----- | ----- | ----- | ----- | ----- | ------ | ----- |
| —    | —     | —     | —     | —     | —     | —     | —      | —     |

**Rules:** `OPENING_SNAPSHOT` & `CLOSE_SNAPSHOT` are **append‑only**; **backfill** allowed within **9:41 AM / 4:11 PM ET** windows if a write fails.

---

### 10.7 Alert Quality — Scoreboard (weekly) 📈 — ALERT\_QSCORE  &#x20;

| week\_start | version | k | precision\_baseline | precision\_v2 | improvement\_pct | band\_counts | priors\_json | ctx\_regime | ctx\_beacon | notes |
| ----------- | ------- | - | ------------------- | ------------- | ---------------- | ------------ | ------------ | ----------- | ----------- | ----- |

### 10.8 SmartPricing Telemetry (append-only) 📏 — SMARTPRICING\_TELEM   &#x20;

| Time (ET)             | Ticker | Structure        | Side | Qty | Mid  | Fill | Slippage (bps) | Mode    |
| --------------------- | ------ | ---------------- | ---- | --- | ---- | ---- | -------------- | ------- |
| 2025-08-20 9:41 AM ET | AAPL   | VERTICAL\_CREDIT | SELL | 3   | 1.25 | 1.20 | 400            | Normal  |
| 2025-08-20 9:42 AM ET | AAPL   | VERTICAL\_CREDIT | BUY  | 5   | 2.00 | 2.02 | 100            | Patient |

### 10.8a SmartPricing Summary v2 (Symbol × TOD) — SMARTPRICING\_SUMMARY\_V2   &#x20;

| Symbol | TOD | N | Median (bps) | IQR (bps) | Suggested Mode | Expected (bps) |
| ------ | --- | - | ------------ | --------- | -------------- | -------------- |

### 10.8b SmartPricing Suggestions v2 — SMARTPRICING\_SUGG\_V2   &#x20;

| Symbol | TOD | Suggestion | Rationale |
| ------ | --- | ---------- | --------- |

### 10.9 Liquidity Sentinel — Report — LIQUIDITY\_SENTINEL&#x20;

| Ticker | Structure | Status | Reason | Last Checked |
| ------ | --------- | ------ | ------ | ------------ |

### 10.10 Time-of-Day Edge Map — TOD\_EDGE\_MAP&#x20;

| Bucket | Signals | Hit-Rate | Avg R | Median R | EV (R) | Confidence |
| ------ | ------- | -------- | ----- | -------- | ------ | ---------- |

### 10.11 Alert Throttle — A/B Results — THROTTLE\_AB\_RESULTS

| Week | Variant | Alerts | Suppressed | Actionable% | Hit-Rate | Decision |
| ---- | ------- | ------ | ---------- | ----------- | -------- | -------- |

### 10.12 Divergence Log — DIVERGENCE\_LOG&#x20;

| Time (ET) | Beacon | Regime | Decision | Note |
| --------- | ------ | ------ | -------- | ---- |

### 10.13 Alert Interlock — Decisions (append-only) — INTERLOCK\_LOG&#x20;

| Time (ET) | Symbol | Kind | Decision | Reason |
| --------- | ------ | ---- | -------- | ------ |

### 10.14 Simulator Scenarios — SIM\_SCENARIOS

| scenario\_id | name | seed | minutes | version | digest | notes |
| ------------ | ---- | ---- | ------- | ------- | ------ | ----- |
| ------------ | ---- | ---- | ------- | ------- | ------ | ----- |
| —            | —    | —    | —       | —       | —      | —     |

### 10.15 Simulator Coverage — SIM\_COVERAGE

| scenario\_id | version | name | seed | minutes | digest | status | branches | notes |
| ------------ | ------- | ---- | ---- | ------- | ------ | ------ | -------- | ----- |
| —            | —       | —    | —    | —       | —      | —      | —        | —     |

### 10.16 Risk Budget — RISK\_BUDGET

| date | regime | vix\_band | session | budget\_index | budget\_single | budget\_news\_exit | consumed\_index | consumed\_single | consumed\_news\_exit | remaining\_index | remaining\_single | remaining\_news\_exit | status | notes |
| ---- | ------ | --------- | ------- | ------------- | -------------- | ------------------ | --------------- | ---------------- | -------------------- | ---------------- | ----------------- | --------------------- | ------ | ----- |
| —    | —      | —         | —       | —             | —              | —                  | —               | —                | —                    | —                | —                 | —                     | —      | —     |

---

## System Health 🩺 — SYSTEM\_HEALTH  &#x20;

*Event-driven log; only rows with real timestamps appear here; static readiness lives in ARCHIVE/CHANGELOG.*

| Time (ET) | Check | Status | Note |
| --------- | ----- | ------ | ---- |

### Runtime Gates — RUNTIME\_GATES

| key | value | expires\_at | notes |
| --- | ----- | ----------- | ----- |

### FG Enforce State — FG\_ENFORCE\_STATE

| last\_incident\_hash | ts |
| -------------------- | -- |

---

## Anchor Map & Health 🌐 — ANCHOR\_MAP  &#x20;

*Index of anchors; sentinel for truncation. If this looks broken, run the Sweeper.*

| Anchor                     | Present | Notes |
| -------------------------- | ------- | ----- |
| DASHBOARD                  | ✅       | —     |
| OA\_POLICY                 | ✅       | —     |
| SMART\_PRICING\_CAL        | ✅       | —     |
| STRUCTURE\_REC\_CAL        | ✅       | —     |
| STRUCTURE\_REC\_CAL\_V2    | ✅       | —     |
| PLAYBOOK\_TABLE            | ✅       | —     |
| PLAYBOOK\_AUDIT            | ✅       | —     |
| ACTIVE\_TRADES             | ✅       | —     |
| MOMENTUM\_CAL              | ✅       | —     |
| PLAYBOOK\_BIAS             | ✅       | —     |
| REGIME\_CAL                | ✅       | —     |
| BEACON\_CAL                | ✅       | —     |
| BEACON\_CAL\_V2            | ✅       | —     |
| BEACON\_ADAPTER            | ✅       | —     |
| AUTOMATIONS                | ✅       | —     |
| BIG\_BRAIN                 | ✅       | —     |
| ARCHIVE                    | ✅       | —     |
| EARNINGS                   | ✅       | —     |
| EARNINGS\_EM\_COHORTS\_V2  | ✅       | —     |
| EARNINGS\_DOSSIER\_HELPERS | ✅       | —     |
| DRIFT\_CAL                 | ✅       | —     |
| LOGS                       | ✅       | —     |
| REGIME\_LOG                | ✅       | —     |
| POSITION\_LOG              | ✅       | —     |
| ENTRY\_EVENTS              | ✅       | —     |
| PTR\_DRAFTS                | ✅       | —     |
| POST\_TRADE\_JOURNAL       | ✅       | —     |
| NEWS\_LOG                  | ✅       | —     |
| NEWS\_TUNER\_REPORT        | ✅       | —     |
| MARKET\_BEACON\_LOG        | ✅       | —     |
| EARNINGS\_RADAR            | ✅       | —     |
| EARNINGS\_DOSSIER          | ✅       | —     |
| EARNINGS\_TRACKER          | ✅       | —     |
| OPENING\_SNAPSHOT          | ✅       | —     |
| CLOSE\_SNAPSHOT            | ✅       | —     |
| ALERT\_QSCORE              | ✅       | —     |
| RISK\_SIZER\_CAL           | ✅       | —     |
| RISK\_SIZER\_CAL\_V2       | ✅       | —     |
| MOMENTUM\_WICK\_CAL        | ✅       | —     |
| MOMENTUM\_WICK\_OVERRIDES  | ✅       | —     |
| NEWS\_CAL                  | ✅       | —     |
| ALERT\_THROTTLE\_CAL       | ✅       | —     |
| DASHBOARD\_STATUS          | ✅       | —     |
| SMARTPRICING\_SUMMARY      | ✅       | —     |
| SMARTPRICING\_TELEM        | ✅       | —     |
| SMARTPRICING\_SUMMARY\_V2  | ✅       | —     |
| SMARTPRICING\_SUGG\_V2     | ✅       | —     |
| PROPOSED\_LADDERS          | ✅       | —     |
| TOD\_EDGE\_MAP             | ✅       | —     |
| THROTTLE\_AB\_RESULTS      | ✅       | —     |
| DIVERGENCE\_LOG            | ✅       | —     |
| INTERLOCK\_LOG             | ✅       | —     |
| LIQUIDITY\_SENTINEL        | ✅       | —     |
| SYSTEM\_HEALTH             | ✅       | —     |
| ANCHOR\_MAP                | ✅       | —     |
| OPS\_KEYRING               | ✅       | —     |
| OPS\_AUTOMATIONS           | ✅       | —     |
| OPS\_SCHEMAS               | ✅       | —     |
| OPS\_DOCS                  | ✅       | —     |
| OPS\_VERIFY                | ✅       | —     |
| CHANGELOG                  | ✅       | —     |
| EARNINGS\_DRIFT\_WATCH     | ✅       | —     |
| OPS\_DOCS\_POLICY          | ✅       | —     |
| SIM\_SCENARIOS             | ✅       | —     |
| SIM\_COVERAGE              | ✅       | —     |
| RISK\_BUDGET               | ✅       | —     |

---

## OPS — Keyring & Automations 🔐

### Keyring (state) 🔒 — OPS\_KEYRING&#x20;

Rotate with BBP‑202 tools. Placeholder values shown.

| Name        | Value | Version |
| ----------- | ----- | ------- |
| API\_TOKEN  | —     | 1       |
| BOT\_SECRET | —     | 1       |

### Automations (literals) 🤖 — OPS\_AUTOMATIONS   &#x20;

*Canonical spec table (BBP‑237 normalized). All tasks default ****paused****; iCal lines are ET‑aligned. Anchor‑only update.*

*Runtime cadence offsets (q15m tasks):* **Position Guardian** → :02/:17/:32/:47; **Update Intraday Dashboard** → :03/:18/:33/:48.

| Task                                                         | Enabled | iCal (ET)                                                                            | Prompt                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Alert           |
| ------------------------------------------------------------ | ------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 🛠️ Update Intraday Dashboard (HUD + A+B + News)             | ⏸       | `RRULE:FREQ=MINUTELY;INTERVAL=15;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9,10,11,12,13,14,15,16` | Preflight: run `mm fg-enforce run` (light); if non-zero → log one SYSTEM\_HEALTH incident and skip this cycle. Update Live Automations Dashboard timestamps and maintain `DASHBOARD` HUD: Session toggle, plus Risk posture + SmartPricing driven by calibrated Beacon state and VIX Shock Guard (prefer `BEACON_CAL_V2` (Beacon v2) if present; else `BEACON_CAL` (Beacon v1), and `MOMENTUM_CAL` (Momentum §6.2); otherwise §6.3 baseline, cooldown ≥15m). Also: compute Risk Sizer multiplier each cycle — prefer v3 (`mm risk-sizer-v3 compute`) when `RISK_SIZER_CAL_V2` present; else run `risk-sizer` (regime from `REGIME_CAL` if present else NEUTRAL; VIX from scanner), upsert "Risk Sizer Multiplier" in `DASHBOARD_STATUS`, and append a timestamped line to `REGIME_LOG` only if the multiplier changed. Also: compute Risk Budget — run `mm risk-budget run --apply` to append/update `RISK_BUDGET` (day‑level caps); expose a gate to throttle non‑essential alerts when budgets are exceeded. Also: ensure `MOMENTUM_WICK_CAL` and `NEWS_CAL` defaults present (seed if empty; idempotent). Also acts as a Beacon flips notifier: on state change, append to `MARKET_BEACON_LOG` and send one `[MARKET ⬆️/⬇️]`. Additionally: at 9:30 AM update the Automations dashboard row for Playbook Open timestamps; each cycle scan `PLAYBOOK_TABLE` for A+B alignment; apply **Liquidity Sentinel v3** gate (depth/quote‑stale/widening/slippage tails): if `BLOCK` suppress; if `BORDERLINE` allow with SmartPricing='Patient'; run `mm liquidity-v3 scan --apply` to update `LIQUIDITY_SENTINEL` (append‑or‑replace by symbol); apply **Divergence Resolver** (Beacon vs Regime, side/quality): suppress low‑quality conflicts; run `mm divergence-resolver` to append to `DIVERGENCE_LOG` on conflict state change; when met, send `[ENTRY NOW ✅]` with explicit legs/expiry/stop/targets per §4/§6.1; pre‑alert throttle via `ALERT_THROTTLE_CAL`; apply Alert Quality Scorer v2 bands (HIGH/MED/LOW) in the Final Outbound Filter—allow HIGH by default; allow MED if Risk Budget (BBP‑331) has headroom; block LOW unless budget+interlock permit; HALT/QUIET‑aware. Classify news per `NEWS_CAL` and log to `NEWS_LOG`; run `mm news-cluster scan` (window\_min=20, ttl\_min=90) to append `cluster=<id>` into `NEWS_LOG` and de-duplicate alerts (one per active cluster); emit `[NEWS 📰]` (classification: **Bullish/Bearish/Neutral**; Bias impact: **No change/Lean/Flip**) only when gates pass; Healthboard: run `mm task-health scan` (cadence/miss\_slots/last\_run\_et) to log one SYSTEM\_HEALTH row per new incident and attempt one safe restart per incident (HALT suppresses; QUIET allows); include feed‑lag detection — if a feed is stale, log it and suppress alerts until healthy. Also: capture entry-event features and append to `ENTRY_EVENTS` (symbol×TOD; wick/body/vol; first-retest; actionable; EV; beacon\_conflict\_20m) — idempotent; HALT/QUIET aware. No auto trade logging. Enforce Interlock (`mm interlock run`) with this cycle’s candidate set (ENTRY/EXIT/NEWS) and append decisions to `INTERLOCK_LOG`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | quiet           |
| ⚡ Market Pulse — Open (SPY/QQQ)                              | ⏸       | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=35;BYSECOND=0`             | HARDEN OPENING SNAPSHOT: append to `OPENING_SNAPSHOT`; retries to 9:40; backfill 9:41; one system‑health alert on failure.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | notify‑on‑fail  |
| 🧾 Close Orchestrator — Snapshot, Logs & Reliability         | ⏸       | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=16;BYMINUTE=5,11;BYSECOND=0`          | Preflight: run `mm fg-enforce run` (strict) — if non-zero, set HALT\_UNTIL (short TTL), log one SYSTEM\_HEALTH incident, and skip this cycle. Branch by time (exit silently otherwise). Weekdays 4:05 PM → append `CLOSE_SNAPSHOT`; PTR handling; update 30‑day `SMARTPRICING_SUMMARY`; then run `mm smartpricing-tune` to refresh `SMARTPRICING_SUMMARY_V2` and `SMARTPRICING_SUGG_V2` (idempotent; no auto‑apply); then run `mm exits-optimize` to refresh `PROPOSED_LADDERS` (analysis-only; idempotent); then run `mm structure-rec-v2 apply` (idempotent; no networking); run `mm risk-sizer-v3 compute` at close and append to `REGIME_LOG` only on change; seed `MOMENTUM_WICK_CAL`/`NEWS_CAL` if missing; run OPS\_VERIFY + safe Auto‑Fix (TableOps/Selectors only); run `mm news-tune` → `NEWS_TUNER_REPORT`; run `mm tod-edge-map scan` to refresh `TOD_EDGE_MAP` (idempotent; no networking); run `mm anchor-health`. Then run `mm fg-micro apply` (idempotent; hard‑block EOF spill; one SYSTEM\_HEALTH incident only on anomalies). Weekdays 4:11 PM → reliability backfill only if today’s close row is missing; single System Health alert on failure.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | mixed           |
| 🪨 Weekend Catalyst Scan                                     | ⏸       | `RRULE:FREQ=WEEKLY;BYDAY=SU;BYHOUR=18;BYMINUTE=0;BYSECOND=0`                         | Sunday Weekly Wrap timestamp updater (silent unless failure). Also: run `mm fg-enforce run` (strict) before any writes; on non-zero exit set HALT\_UNTIL (short TTL), emit one SYSTEM\_HEALTH incident, and abort further writes; if `FG_ALLOW_REPAIR=1`, run `mm fg-repair apply` and re-verify. Also: run `mm fg-lock init` to (re)build `FENCE_LOCK.json` from the current canvas (idempotent). Also: run full OPS\_VERIFY sweep + safe Auto‑Fix (TableOps/Selectors only) — remove \$ artifacts; repair table bodies; canonicalize Opening/Close/Keyring notes; refresh OPS\_VERIFY; append one System Health summary if fixes applied. Also: run `mm beacon-calibrate` (bar\_sec=60) with the last week’s internal series to refresh `BEACON_CAL_V2` (candidate; idempotent; futures-optional with proxy fallback). Also: run `mm throttle-ab` (eligible low-risk weeks) to refresh `THROTTLE_AB_RESULTS` (idempotent; no networking). Also: run `mm canvas-watchdog` (v3) to scan/repair fences and append a SYSTEM\_HEALTH row only if issues are detected. Also: run `mm fg-micro audit` (no writes) and append a single SYSTEM\_HEALTH incident only on anomalies. Also: run `mm sim-ship-scenarios --apply` (append-only/idempotent). If `MM_STRICT_DIGESTS=1` and fixture digests are present, compute digests via `mm sim-gen <scenario> --digest-only` for each default scenario and append a SYSTEM\_HEALTH row on mismatch; also run `mm sim-cov run --scenario all` (append-only `SIM_COVERAGE`, idempotent); if regressions, append a SYSTEM\_HEALTH row (use `--strict-digests` when fixture digests are pinned);  Also: run `mm anchor-health` to validate ANCHOR\_MAP doc-order and dedupe. Also: preflight planned Anchor Map edits via `mm anchor-map lint` (row-ops-only enforcer); append one `OPS_VERIFY` ack (3-col) and a `SYSTEM_HEALTH` incident row on violations; abort risky plan. Also: run `mm entry-quality-opt` (last 7 calendar days of `ENTRY_EVENTS`) to write `MOMENTUM_WICK_OVERRIDES`; then run `mm alert-qscore run --apply` to update `ALERT_QSCORE` (append-or-replace by {week\_start, version=2}).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          Also: run `mm momentum-calibrate` (bar\_sec=60) to refresh `MOMENTUM_CAL` (idempotent; no networking). Also: run `mm regime-calibrate` to refresh `REGIME_CAL` (idempotent; no networking). Also: run `mm policy-harden guard-rows` (idempotent) to ensure OPS\_VERIFY policy guard rows; append one SYSTEM\_HEALTH row only on change/failure. Also: run `mm anchor-map sync --apply` (idempotent). | quiet           |
| 📆 Earnings Orchestrator — Radar, Dossier & Drift (AM+Close) | ⏸       | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8,16;BYMINUTE=0,15;BYSECOND=0`        | Branch by time (exit silently otherwise). 8:00 AM → refresh `EARNINGS_RADAR` (9.1) and `EARNINGS_DOSSIER` (9.3) for next 3 sessions; rebuild `EARNINGS_TRACKER` from Playbook∪Explicit; apply the Pre‑ER checklist; tag Drift Watch for fresh post‑ER names per rules. Then run `mm earnings-em-cal` to refresh `EARNINGS_EM_COHORTS_V2` and `EARNINGS_DOSSIER_HELPERS` (idempotent; no networking). 4:15 PM → clear expired Drift Watch tags in 9.2; update timestamps; then run `mm drift-v2 apply` to rewrite `DRIFT_CAL`; silent unless failure. Other scheduled ticks (8:15/4:00) → quick health/no‑op checks only.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | quiet           |
| 🚀 Burst Scan — AM Tier‑1 Window                             | ⏸       | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8;BYMINUTE=25;BYSECOND=0`             | If within ±10 min of AM Tier‑1 macro, run consolidated scan; alert only if actionable.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | actionable‑only |
| 🚀 Burst Scan — FOMC 2:00 Window                             | ⏸       | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=13;BYMINUTE=55;BYSECOND=0`            | If within ±10 min of 2:00 statement, run consolidated scan; alert only if actionable.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | actionable‑only |
| 🚀 Burst Scan — FOMC 2:30 Window                             | ⏸       | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=14;BYMINUTE=25;BYSECOND=0`            | If within ±10 min of 2:30 presser, run consolidated scan; alert only if actionable.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | actionable‑only |
| 🚀 Burst Scan — PM Window (Staggered)                        | ⏸       | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=13;BYMINUTE=45;BYSECOND=0`            | Staggered PM catalyst sweep; alert only if actionable.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | actionable‑only |
| 🛡️ Position Guardian — Exit & Profit Lock                   | ⏸       | `RRULE:FREQ=MINUTELY;INTERVAL=15;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9,10,11,12,13,14,15,16` | RTH-only sentinel. Monitor `ACTIVE_TRADES` (user-confirmed positions only) each cycle; ignore if empty. Do NOT emit alerts for hard-stop hits (assume stop order handles it). Focus on early danger and profit preservation with confirmation. For each open position, **Early-Danger (pre-stop)** — emit `[EXIT NOW 🛑]` when ANY of the following confirm: (1) Beacon flips against position **and** Divergence Resolver quality=LOW/CONFLICT ≥3 minutes; (2) VWAP or entry invalidation level lost on 1‑min close **and** retest fails within 3 minutes (guarded by `MOMENTUM_WICK_CAL` body/wick rules); (3) **VIX shock** against position: ΔVIX ≥ 3% in ≤3 minutes; (4) Adverse **news cluster** per `NEWS_CAL` with price confirmation. **Profit-Lock** — after T1/T2 (OA ladder) or MFE ≥ 1.0R, emit `[EXIT NOW 🛑]` — Lock Profit if: 5‑min close back inside range; VWAP fails (long) / recaptured (short); or Beacon turns neutral/contrary with wick deterioration. **Actions:** Close now / Trim 50% / Flatten to runner; never use OA “Touch”. **Guards:** HALT/QUIET aware; respect `ALERT_THROTTLE_CAL`; idempotent alerts; enforce Interlock (`mm interlock run`) against concurrent ENTRY/NEWS and append to `INTERLOCK_LOG`. **Logging:** No auto writes to `POSITION_LOG` (user-confirmed only). After user confirms action, append/update the row and draft PTR in `PTR_DRAFTS`. On internal errors, write one `SYSTEM_HEALTH` line (once per incident), no spam.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      Cadence: 15-min; if per-hour cap increases, consider 1–5 min during RTH.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | actionable‑only |

---

### Schemas (fixtures) 🧩 — OPS\_SCHEMAS

```yaml
EARNINGS_FEED:
  watchlist: [UNH, RDDT, PLTR, TTD, SNAP]
  horizon_days: 30
  explicit: []
```

### Docs (ops) 📚 — OPS\_DOCS&#x20;

### OPS Docs Policy — OPS\_DOCS\_POLICY&#x20;

| Policy Line                                                                                                                                                                                                   |   |   |   |   |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | - | - | - | - |
| Edit only inside `<!-- BB:QUEUE -->`/`<!-- /BB:QUEUE -->` and `<!-- BB:LIBRARY -->`/`<!-- /BB:LIBRARY -->`.                                                                                                   |   |   |   |   |
| **Selectors (preferred):** target `<!-- H3:BB_QUEUE -->` and `<!-- H3:BB_LIBRARY -->` sentinels; never match by the plain text of headings or phrases like "(compact cards)".                                 |   |   |   |   |
| Queue: one bullet per item, tags required, top-down order.                                                                                                                                                    |   |   |   |   |
| Library: one code-fenced card per BBP using the universal template.                                                                                                                                           |   |   |   |   |
| Do not touch surrounding policies/headings.                                                                                                                                                                   |   |   |   |   |
| If an updater run blocks (conflict/budget/struct), check **OPS\_VERIFY** and **SYSTEM\_HEALTH**, then re-run.                                                                                                 |   |   |   |   |
| Use `mm section move ...` to move/rename H3 sections safely within **BIG\_BRAIN**.                                                                                                                            |   |   |   |   |
| Moves bytes strictly within the anchor; never reflows content.                                                                                                                                                |   |   |   |   |
| Prefer `--renumber-level 3` when adjusting 9.x subsections.                                                                                                                                                   |   |   |   |   |
| Always dry-run first (`--dry-run --json`) and review the diff; then apply.                                                                                                                                    |   |   |   |   |
| ANCHOR\_MAP refreshes automatically after successful moves.                                                                                                                                                   |   |   |   |   |
| If Queue/Library bodies were pasted into **BBP Formatting Policy** by mistake, cut them back into their fenced slices and restore the policy text verbatim.                                                   |   |   |   |   |
| If **ARCHIVE** or **OPS** sections seem off, prefer restoring from the immediately prior version and rerunning the small, anchor‑scoped operation rather than mass pasting.                                   |   |   |   |   |
| **OPS\_VERIFY** for guard failures,                                                                                                                                                                           |   |   |   |   |
| **SYSTEM\_HEALTH** for recent blocked writes/rollbacks,                                                                                                                                                       |   |   |   |   |
| **CHANGELOG** for big structural changes.                                                                                                                                                                     |   |   |   |   |
| Delete **exactly one** table row at a time using line-anchored matches (`^…$`, multiline mode).                                                                                                               |   |   |   |   |
| **Never** use DOTALL/greedy patterns or multi-line spans for deletes; avoid `.*` across newlines.                                                                                                             |   |   |   |   |
| Match ASCII-literal text inside the target row; escape special chars; **no \`\` backrefs**.                                                                                                                   |   |   |   |   |
| Prefer TableOps/Selectors when available; otherwise use single-line regex anchored to the row.                                                                                                                |   |   |   |   |
| Dry-run + verify: expected diff ≤ 1 line per table.                                                                                                                                                           |   |   |   |   |
| The `ANCHOR_MAP` table is wrapped with `<!-- ANCHOR: ANCHOR_MAP START/END -->`.                                                                                                                               |   |   |   |   |
| Only **TableOps row ops** are allowed (append\_once / row\_after / update\_cell). Regex/multi-line edits are disallowed.                                                                                      |   |   |   |   |
| Inserts use `row_after(<nearby anchor>)`; deletes are single line-anchored; no greedy patterns.                                                                                                               |   |   |   |   |
| After any change, run `mm anchor-health` to validate document order and dedupe.                                                                                                                               |   |   |   |   |
| **Headings:** Every new H3 section that will be edited gets an inline sentinel on the heading — for example: `<!-- H3:ANCHOR_NAME -->`.                                                                       |   |   |   |   |
| **Fences:** Wrap the first Markdown table in the section with `<!-- ANCHOR: ANCHOR_NAME START -->` above the header row and `<!-- ANCHOR: ANCHOR_NAME END -->` immediately after the last body row.           |   |   |   |   |
| **Anchor Map:** When a new anchor is created, append a row to **ANCHOR\_MAP** with the anchor name; set **Present = ✅**, **Notes = —** (append-only).                                                         |   |   |   |   |
| **Verify row (schema):** Add/adjust a concise row in **OPS\_VERIFY** to assert presence/schema for the new table.                                                                                             |   |   |   |   |
| **Edits:** Use **RowOps DSL** only (`append_once`, `row_after`, `update_cell`) inside fenced tables; **ban** `line_replace_in_anchor` under table anchors.                                                    |   |   |   |   |
| **Ship:** Archive any structural BBP via `mm archive append` (BBP‑310); never hand‑edit the Archive table.                                                                                                    |   |   |   |   |
| **Idempotency:** All writers must be safe to re‑run (NOOP when already correct) and Unicode‑tolerant (NBSP/emoji/dash).                                                                                       |   |   |   |   |
| Ban line‑replace in **table anchors** (SYSTEM\_HEALTH, ARCHIVE, OPS\_VERIFY, ANCHOR\_MAP, AUTOMATIONS, NEWS\_LOG, PLAYBOOK\_TABLE, LIQUIDITY\_SENTINEL, ALERT\_QSCORE, ENTRY\_EVENTS) — RowOps/TableOps only. |   |   |   |   |
| Require **Postcheck++**: anchor‑span unchanged, next heading unchanged, and append‑only tbodies must not shrink.                                                                                              |   |   |   |   |
| **Soft rowkeys** default **ON** for row selection (NBSP/ZWSP/dash/emoji tolerant).                                                                                                                            |   |   |   |   |
| **Ship macros** required for Queue/Library/Archive: ARCHIVE append‑only; Queue/Library via RowOps (append/update), never freeform replace.                                                                    |   |   |   |   |
| **Fence Guardian (BBP‑316)** integrated with ZFEP: audit/apply fences & H3 sentinels; pre‑commit guard blocks any content/fences after `*End of canvas.*`.                                                    |   |   |   |   |
| **FG Enforcement (BBP‑319 + 326r3)**: ZFEP Postcheck++ **rejects** any fence/sentinel modification not executed via **Fence Guardian Autopilot** (e.g., `mm fg-micro apply`); ad‑hoc edits are blocked.       |   |   |   |   |
| CLI: `mm policy-harden guard-rows` and `mm policy-harden check-plan --plan-json …`.                                                                                                                           |   |   |   |   |
| Chat/Writer path (BBP-321/322/323): Chat- and writer-origin fence/sentinel edits are mandatory **FG Autopilot + Selector Cursor**; ZFEP hard gate blocks any non-FG route.                                    |   |   |   |   |
| SafeReplace v3 (BBP‑328): strict — block suspicious tokens everywhere; allow literals only in code/inline-code or escaped as \$1.                                                                             |   |   |   |   |

**Addendum — BBP‑340 (Fence Guardian v4):** Immutable fences & H3 sentinels are FG‑only. Any plan that touches `<!-- ANCHOR: NAME START/END -->`, `<!-- H3:NAME -->`, or `<!-- BB:QUEUE|/BB:QUEUE|BB:LIBRARY|/BB:LIBRARY -->` is **blocked** unless run via FG Autopilot with a valid one‑time, TTL‑limited, anchor‑scoped `fg_unlock` token (env: `MM_FG_AUTOPILOT=1`, `MM_FG_UNLOCK=<token>`). Postcheck++ verifies fence digests and fails/rolls back on drift. CLI: `mm fg-lock init|verify|rotate`. Policy v4.

**Addendum — BBP‑343 (Policy‑Harden):** Broadens policy to reject **multiline/DOTALL** regex anywhere and **line\_replace\_in\_anchor** globally (FG unlock token permits only the targeted anchor); any replacement that **touches sentinel literals** (`<!-- ANCHOR:* START/END -->`, `<!-- H3:* -->`, `<!-- BB:* -->`) is **always blocked**. CLI: `mm policy-harden guard-rows|check-plan|ci-lint`.

**Addendum — BBP‑344 (Selector Compiler & Heading Normalizer):** Compiles resilient selector sets (H3 sentinel → normalized heading fingerprint → nearby anchor/table header) and writes `SELECTOR_MAP.json`. CLI: `mm selectors compile` and `mm selectors locate`. Writers should prefer H3 names where available; otherwise use normalized slugs from the map.

**Addendum — BBP‑346 (Anchor Map Syncer):** Reads live H3/fence spans and updates `ANCHOR_MAP` using RowOps only; new rows use `row_after(<nearest existing row>)` to keep doc order; updates are in‑place; CLI: `mm anchor-map sync --dry-run/--apply`.

**Addendum — BBP‑348 (Writer Gateway v2 — FG‑Only Route):**

- **Never** attempt legacy or literal‑regex canvas edits (no header EOL matches, no DOTALL, no backrefs). All writes **must** go through the gateway path.
- **Mandatory route:** 343 (policy‑harden) → 340 (FG lock precommit) → 344 (selectors) → 347 (per‑section plan). H3+fence edits **via 345** only; `ANCHOR_MAP` updates **via 346** only. Anything else is **blocked**.
- **Per‑section commits only:** Dry‑run → verify → commit each section. If one section fails, stop that section, **do not retry with regex**, continue only via 347.
- **Loop‑breaker SOP:** On any block/mismatch → 1) compile selectors; 2) gateway **autopilot\_345** for the single section; 3) `anchor-map sync` (346); 4) if still blocked, log one SYSTEM\_HEALTH incident (342) and return a clear report — **do not** re‑attempt legacy edits.

**Fences & Sentinels — Practical Rule of Thumb**

- If a section will ever be touched by writers or tasks (insert, update, move, or reorder), use **both**:
  - H3 sentinel on the heading: `<!-- H3:ANCHOR_NAME -->` (use durable UPPER\_SNAKE\_CASE).
  - Table fence around each editable table: `<!-- ANCHOR: ANCHOR_NAME START -->` … `<!-- ANCHOR: ANCHOR_NAME END -->`.
- Static human-only prose: H3 sentinel optional; no table fence needed.
- Multiple editable tables under one heading: keep one H3 sentinel on the heading, and **one fence per table**.
- Sentinels/fences are FG-only (BBP‑340/343); avoid over-tagging ephemeral headings.

---

**Troubleshooting & Recovery**

*Quick helper:* run `mm fg-micro audit` (NO‑FAIL) to re‑assert fences/sentinels and check EOF guard.

*If a Big Brain edit wipes content or you see stray ****\`\`**** artifacts:*

**Quick checklist**

1. Roll back the last change (canvas history).
2. Verify Big Brain fences are present: `<!-- BB:QUEUE -->`/`<!-- /BB:QUEUE -->`, `<!-- BB:LIBRARY -->`/`<!-- /BB:LIBRARY -->`.
3. Confirm required H3 sentinels exist: Standing Charter, Queue Ordering, BBP Formatting, Pro Follow‑Up, Ship.
4. Check anchors are closed: every `START_TPL` has a matching `END_TPL` lines.
5. Run **OPS\_VERIFY** and review **SYSTEM\_HEALTH** for any alerts.
6. Re‑apply the intended Queue/Library edit **only through the hardened updater** (slice‑scoped). Avoid manual edits outside the fences.
7. If you saw \$1/\$2 artifacts, ensure single-line patterns use \g<1> style backrefs; **never** use \$1 (it inserts literally).
8. If content truncated at bottom, run the Sweeper (Anchor Map refresh) and re‑create any missing `END_TPL` lines.
9. Regex policy: Use CanvasSelectors/TableOps for all table edits; ad‑hoc regex is disallowed (Kill‑Switch blocks DOTALL/multi‑line/greedy).

**Manual repair tips**

- If Queue/Library bodies were pasted into **BBP Formatting Policy** by mistake, cut them back into **their** fenced slices and restore the policy text verbatim.
- If **ARCHIVE** or **OPS** sections seem off, prefer restoring from the immediately prior version and rerunning the small, anchor‑scoped operation rather than mass pasting.
- Keep edits **anchor‑scoped**; never reflow or mass‑format.

**Where to look**

- **OPS\_VERIFY** for guard failures,
- **SYSTEM\_HEALTH** for recent blocked writes/rollbacks,
- **CHANGELOG** for big structural changes.



---

### Verify (checks) ✅ — OPS\_VERIFY  &#x20;

| Check                                     | Status | Note                                                                 |
| ----------------------------------------- | ------ | -------------------------------------------------------------------- |
| BB Queue H3 sentinel present              | ✅      | `<!-- H3:BB_QUEUE -->` present on heading (inline)                   |
| BB Library H3 sentinel present            | ✅      | `<!-- H3:BB_LIBRARY -->` present on heading (inline)                 |
| BB\_QUEUE fences                          | ✅      | `<!-- BB:QUEUE -->`/`<!-- /BB:QUEUE -->` present                     |
| BB\_LIBRARY fences                        | ✅      | `<!-- BB:LIBRARY -->`/`<!-- /BB:LIBRARY -->` present                 |
| OPS\_DOCS (Updater usage)                 | ✅      | usage note present                                                   |
| OPS\_DOCS (Troubleshooting & Recovery)    | ✅      | quick checklist + tips present                                       |
| BIG\_BRAIN H3 sentinels                   | ✅      | Charter / Queue Ordering / Formatting / Pro Follow‑Up / Ship present |
| BEACON\_ADAPTER                           | ✅      | live status line present                                             |
| REGIME\_LOG                               | ✅      | —                                                                    |
| DRIFT\_CAL                                | ✅      | —                                                                    |
| MOMENTUM\_WICK\_OVERRIDES schema (7-col)  | ✅      | header present                                                       |
| Notes (Opening/Close/Keyring)             | ✅      | Canonical wording OK                                                 |
| RISK\_SIZER\_CAL present                  | ✅      | header present                                                       |
| RISK\_SIZER\_CAL\_V2 schema (3-col)       | ✅      | header present                                                       |
| DASHBOARD\_STATUS table (Metric/Value)    | ✅      | header present                                                       |
| SIM\_SCENARIOS schema (7-col)             | ✅      | header present                                                       |
| SIM\_COVERAGE schema (9-col)              | ✅      | header present                                                       |
| EARNINGS\_TRACKER freshness (≤ 7 days)    | ✅      | ok                                                                   |
| REGIME\_LOG timestamped format            | ✅      | pattern ok; no \$ artifacts                                          |
| SMARTPRICING\_TELEM schema (9-col)        | ✅      | header present                                                       |
| AUTOMATIONS live table header             | ✅      | header present                                                       |
| OPS\_AUTOMATIONS canonical schema (5-col) | ✅      | header present                                                       |
| Row-delete SOP present                    | ✅      | docs present                                                         |
| ANCHOR\_MAP fenced (comment model)        | ✅      | START/END present                                                    |
| ANCHOR\_MAP duplicates                    | ✅      | none                                                                 |
| ANCHOR\_MAP doc-order = actual            | ✅      | anchor-health ok                                                     |
| No \$ artifacts                           | ✅      | none present                                                         |
| NEWS\_CAL schema (5-col)                  | ✅      | header present                                                       |
| NEWS\_TUNER\_REPORT schema (7-col)        | ✅      | header present                                                       |
| STRICT\_MODE sentinel                     | ✅      | present                                                              |
| EARNINGS\_DOSSIER schema (11-col)         | ✅      | header present                                                       |
| EARNINGS\_RADAR schema (7-col)            | ✅      | header present                                                       |
| ALERT\_QSCORE schema (11-col)             | ✅      | header present                                                       |
| RUNTIME\_GATES schema (4-col)             | ✅      | header present                                                       |
| FG\_ENFORCE\_STATE schema (2-col)         | ✅      | header present                                                       |

---

## CHANGELOG 📁

*Major/structural changes only; routine BBPs live in ARCHIVE.*

- **2025‑08‑29 —** Fence Guardian v4: immutable fence/sentinel locks with FG‑only unlock tokens; Diff Scanner + Postcheck++ integration. *(BBP‑340)*

- **2025‑08‑29 —** Policy‑Harden: ban non‑FG multiline/DOTALL & line\_replace\_in\_anchor; hard‑block sentinel‑literal edits; CI lints. *(BBP‑343)*

- **2025‑08‑28 —** SafeReplace v3 & Diff Scanner enforcement (no-number artifacts). *(BBP‑328)*

- **2025‑08‑25 —** Policy Hardening: ZFEP defaults enforced (Postcheck++ / RowOps-only / soft rowkeys; ARCHIVE append-only). *(BBP‑315)*

- **2025‑08‑18 —** Enabled WriteGuard v2 (hash‑locked plan → verify → commit) for anchor‑safe commits. *(BBP‑260)*

- **2025‑08‑15 —** Global structural delta guard (hard‑fail): blocks anchor loss/overshrink; health note on block; wired into Safe‑Apply. *(BBP‑212)*

- **2025‑08‑15 —** Structural guardrails: BIG\_BRAIN schema guard + Safe‑Apply repair hook + split user vs backref diff budgets. *(BBP‑211, BBP‑215, BBP‑216)*

- **2025‑08‑15 —** Anchor Move & Reorder primitives (`mm anchor move`) with H1‑aware placement; idempotent reorders. *(BBP‑210)*

- **2025‑08‑15 —** Keyring Regenerator + `mm keyring` alias; backups, rollback, and audit lines. *(BBP‑202, BBP‑209)*

- **2025‑08‑15 —** Canvas recovery: restored Prompt Library/Queue; moved Dashboard under title; **CHANGELOG** relocated to bottom; Anchor Map re‑verified.

---

*End of canvas.*
