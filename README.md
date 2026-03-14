Repository for March Machine Learning Mania Kaggle Competition

https://www.kaggle.com/competitions/march-machine-learning-mania-2026


# Data Section 5 — Supplementary Files

> Supporting data for the [March Machine Learning Mania 2026](https://www.kaggle.com/competitions/march-machine-learning-mania-2026/overview) Kaggle competition.
> This section covers coaches, conference affiliations, alternative team name spellings, bracket structure, and game results for NIT and other postseason tournaments.

---

## Table of Contents

1. [Reference Tables](#reference-tables)
   - [Conferences.csv](#conferencescsv)
   - [MTeamSpellings / WTeamSpellings](#mteamspellings--wteamspellings)
2. [Team Context Files](#team-context-files)
   - [MTeamCoaches.csv](#mteamcoachescsv)
   - [MTeamConferences / WTeamConferences](#mteamconferences--wteamconferences)
3. [Performance Signal Files](#performance-signal-files)
   - [MConferenceTourneyGames / WConferenceTourneyGames](#mconferencetourneygames--wconferencetourneygames)
   - [MSecondaryTourneyTeams / WSecondaryTourneyTeams](#msecondarytourneyteams--wsecondarytourneyteams)
   - [MSecondaryTourneyCompactResults / WSecondaryTourneyCompactResults](#msecondarytourneycompactresults--wsecondarytourneycompactresults)
4. [Bracket Structure Files](#bracket-structure-files)
   - [MNCAATourneySlots / WNCAATourneySlots](#mncaatourneyslots--wncaatourneyslots)
   - [MNCAATourneySeedRoundSlots.csv](#mncaatourneyseedroundslotscsv)
5. [Modelling Pipeline Overview](#modelling-pipeline-overview)

---

## Reference Tables

### Conferences.csv

**Purpose:** Lookup table mapping short conference abbreviations to their full names. Acts as the join key for all conference-related files.

| Column | Type | Description |
|--------|------|-------------|
| `ConfAbbrev` | string | Short abbreviation (e.g. `acc`, `big12`) — primary key used in all other files |
| `Description` | string | Full conference name (e.g. `Atlantic Coast Conference`) |

**Notes:**
- Covers Division I conferences since 1985.
- No attempt is made to link conferences that merged or renamed over time — each name change produces a new entry.
- **Modelling use:** join key only; use to derive conference-strength features when combined with `MTeamConferences`.

---

### MTeamSpellings / WTeamSpellings

**Purpose:** Maps alternative team name spellings to canonical `TeamID` values. Used exclusively for ingesting and aligning external datasets (e.g. KenPom, Bart Torvik) with this competition's identifiers.

| Column | Type | Description |
|--------|------|-------------|
| `TeamNameSpelling` | string | Alternate spelling in all lowercase |
| `TeamID` | int | Canonical team identifier (matches `MTeams.csv`) |

**Notes:**
- Not a modelling feature — ingestion helper only.
- Use this when merging external ratings or stats that use different team name conventions.

---

## Team Context Files

### MTeamCoaches.csv

**Purpose:** Records the head coach for each team in each season, with day-number ranges to capture mid-season coaching changes.

| Column | Type | Description |
|--------|------|-------------|
| `Season` | int | Year of the associated season (tournament year) |
| `TeamID` | int | Team identifier |
| `FirstDayNum` | int | First day the coach was head coach in this season |
| `LastDayNum` | int | Last day the coach was head coach in this season |
| `CoachName` | string | Coach full name in `first_last` format, all lowercase, spaces replaced with underscores |

**Notes:**
- For coaches with no mid-season change, `FirstDayNum = 0` and `LastDayNum = 154` (full season).
- Multiple rows per team-season indicate a coaching change; rows are non-overlapping within a season.
- **Modelling use:** derive features such as coach tournament experience, historical win rate, and tenure length.

---

### MTeamConferences / WTeamConferences

**Purpose:** Tracks conference membership for each team across every season. Captures historical conference realignment.

| Column | Type | Description |
|--------|------|-------------|
| `Season` | int | Year of the associated season |
| `TeamID` | int | Team identifier |
| `ConfAbbrev` | string | Conference the team belonged to that season (joins to `Conferences.csv`) |

**Notes:**
- One row per team per season.
- Conference membership can change year to year due to realignment.
- **Modelling use:** derive conference-strength features (average conference SRS, conference win %), and use as a grouping variable for strength-of-schedule calculations.

---

## Performance Signal Files

### MConferenceTourneyGames / WConferenceTourneyGames

**Purpose:** Flags which games in the regular season results files were played as part of a conference tournament. All conference tournament games finish on or before Selection Sunday.

| Column | Type | Description |
|--------|------|-------------|
| `ConfAbbrev` | string | Conference that hosted the tournament |
| `Season` | int | Season year |
| `DayNum` | int | Day the game was played |
| `WTeamID` | int | Winning team |
| `LTeamID` | int | Losing team |

**Notes:**
- The four columns `Season`, `DayNum`, `WTeamID`, `LTeamID` uniquely identify each game.
- Full game stats can be retrieved by joining to the Regular Season Compact or Detailed Results files.
- Men's data starts from the 2001 season; women's from 2002.
- **Modelling use:** isolate conference tournament performance separately from regular season performance — useful for capturing a team's form and pressure-game experience immediately before the NCAA bracket.

---

### MSecondaryTourneyTeams / WSecondaryTourneyTeams

**Purpose:** Lists teams that participated in postseason tournaments other than the NCAA Tournament (NIT, CBI, CIT, WNIT, etc.), which run in parallel with the NCAA Tournament.

| Column | Type | Description |
|--------|------|-------------|
| `Season` | int | Season year |
| `SecondaryTourney` | string | Tournament abbreviation (e.g. `NIT`, `CBI`, `CIT`, `WNIT`, `WBI`) |
| `TeamID` | int | Participating team identifier |

**Notes:**
- A team appearing here did not make the NCAA Tournament but was considered postseason-worthy.
- **Modelling use:** binary feature — "made a secondary postseason" — acts as a quality signal for borderline teams. Can also be used to filter teams from historical records when evaluating pre-tournament predictions.

---

### MSecondaryTourneyCompactResults / WSecondaryTourneyCompactResults

**Purpose:** Game-by-game results for secondary postseason tournaments (NIT, CBI, CIT, CBC, V16 [Vegas 16], TBC [The Basketball Classic] for men; WBI, WBIT, WNIT for women).

| Column | Type | Description |
|--------|------|-------------|
| `SecondaryTourney` | string | Tournament abbreviation |
| `Season` | int | Season year |
| `DayNum` | int | Day the game was played (always > 132) |
| `WTeamID` | int | Winning team |
| `WScore` | int | Winning team's score |
| `LTeamID` | int | Losing team |
| `LScore` | int | Losing team's score |
| `WLoc` | string | Location indicator for the winning team |
| `NumOT` | int | Number of overtime periods |

**Notes:**
- These games are played after `DayNum = 132` and are **not** included in the Regular Season Compact Results file.
- Not all tournaments are held every year or with the same bracket structure.
- **Modelling use:** late-season win/loss data for teams that did not make the NCAA Tournament; useful for training models on teams across a broader performance range.

---

## Bracket Structure Files

### MNCAATourneySlots / WNCAATourneySlots

**Purpose:** Defines how seeds are paired against each other as the tournament progresses through rounds, allowing reconstruction and simulation of any year's bracket.

| Column | Type | Description |
|--------|------|-------------|
| `Season` | int | Season year |
| `Slot` | string | Unique game identifier. Play-in games: 3-char (e.g. `W16`). Regular rounds: 4-char (e.g. `R1W1`, `R2W1`) |
| `StrongSeed` | string | Expected stronger seed for this game. In Round 1: a team seed (e.g. `W01`). In later rounds: a prior slot (e.g. `R1W1`) |
| `WeakSeed` | string | Expected weaker seed. Same format as `StrongSeed` |

**Round codes:**

| Code | Round |
|------|-------|
| Play-in | Play-in games (determines seed that enters Round 1) |
| `R1` | Round of 64 |
| `R2` | Round of 32 |
| `R3` | Sweet Sixteen |
| `R4` | Elite Eight |
| `R5` | Final Four |
| `R6` | Championship |

**Notes:**
- Round 1 references actual team seeds; subsequent rounds reference prior slot winners.
- **Modelling use:** simulate bracket paths for any given pair of seed predictions; compute expected number of rounds a team will advance; calculate "upset probability" for specific matchups.

---

### MNCAATourneySeedRoundSlots.csv

**Purpose:** Men's only. Maps each tournament seed to its expected game slot and possible day numbers for each round, assuming no upsets. Simplifies bracket simulation without needing to trace slot chains.

| Column | Type | Description |
|--------|------|-------------|
| `Seed` | string | Tournament seed (e.g. `W01`, `X12`) |
| `GameRound` | int | Round number (0 = play-in, 1–2 = first weekend, 3–4 = second weekend, 5 = Final Four, 6 = Championship) |
| `GameSlot` | string | The slot a team with this seed would play in during this round |
| `EarlyDayNum` | int | Earliest possible day the game could occur |
| `LateDayNum` | int | Latest possible day the game could occur |

**Notes:**
- No equivalent file exists for women's data due to greater scheduling variability.
- The 2021 men's tournament had unusual scheduling and did not follow the standard `DayNum` assignments.
- **Modelling use:** quickly look up which round/slot any seed occupies without tracing slot chains; use `EarlyDayNum`/`LateDayNum` to filter game records by round.

---

## Modelling Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        REFERENCE TABLES                             │
│   MTeams.csv (TeamID)  ·  MSeasons.csv (Season)  ·  Conferences    │
└──────────┬────────────────────┬─────────────────────────────────────┘
           │  join              │  join
           ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│  TEAM CONTEXT    │  │ PERF. SIGNALS    │  │ BRACKET STRUCTURE    │
│                  │  │                  │  │                      │
│ MTeamCoaches     │  │ MConference      │  │ MNCAATourneySlots    │
│ MTeamConferences │  │   TourneyGames   │  │ SeedRoundSlots       │
│                  │  │ MSecondary       │  │                      │
│                  │  │   TourneyTeams   │  │                      │
│                  │  │ MSecondary       │  │                      │
│                  │  │   TourneyResults │  │                      │
└────────┬─────────┘  └───────┬──────────┘  └──────────┬───────────┘
         │                    │                          │
         ▼                    ▼                          ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│ Team context     │  │ Performance      │  │ Bracket simulation   │
│ features         │  │ signal features  │  │ features             │
│                  │  │                  │  │                      │
│ · Coach exp.     │  │ · Conf-tourney   │  │ · Expected path      │
│ · Coach win rate │  │   W/L record     │  │ · Upset probability  │
│ · Conf strength  │  │ · NIT/secondary  │  │ · Round reach prob.  │
│ · SOS via conf   │  │   postseason flag│  │                      │
└────────┬─────────┘  └───────┬──────────┘  └──────────┬───────────┘
         │                    │                          │
         └────────────────────┴──────────────────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │   SUBMISSION PREDICTIONS  │
                     │  Win probability per      │
                     │  team-vs-team matchup     │
                     └──────────────────────────┘

Note: MTeamSpellings is an ingestion helper only — use it to
align external data sources (KenPom, Bart Torvik, etc.) to TeamID.
It does not contribute model features directly.
```

---

*Files prefixed `M` cover men's tournament data; files prefixed `W` cover women's. Where both exist, schema is identical unless noted.*
