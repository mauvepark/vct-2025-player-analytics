# VCT 2025 Player Analytics

An interactive Power BI dashboard analyzing professional VALORANT play across the 2025 VALORANT Champions Tour (VCT): which agents dominate the meta, which players perform best, and how teams build their compositions.

Built to practice the full analytics workflow: cleaning messy real-world data, modeling it, writing DAX measures, and designing reports a stakeholder can explore on their own.

![Agent Meta page](screenshots/agent-meta.png)

## Data

- **Source:** [Valorant Champion Tour 2021–2026 Data](https://www.kaggle.com/datasets/ryanluong1/valorant-champion-tour-2021-2023-data) (Kaggle), 2025 player stats file
- **Scope:** 15 tournaments, from the four regional Kickoffs through Masters Bangkok, Masters Toronto and Champions 2025
- **Grain after cleaning:** one row per player, per agent, per match (9,805 rows, 313 players, 58 teams, 27 agents)

## Data cleaning

The raw file had three problems that would have produced wrong numbers if left in. The fixes are in [`clean_data.py`](clean_data.py) (output: [`data/vct2025_players_clean.csv`](data/vct2025_players_clean.csv)) (Python, pandas).

| Issue | Impact | Fix |
|---|---|---|
| **Rollup rows mixed with detail rows.** "All Stages" rows total a whole tournament, and multi-agent rows (e.g. `astra, omen`) total a player's agents for one match. | Every stat would be double- or triple-counted. | Removed both, cutting the file from 17,996 to 9,805 rows at a single consistent grain. |
| **Clutch records corrupted into dates.** About 6,200 values like `1/3` had been auto-converted to `03-Jan`. | Clutch stats unusable for a third of the data. | Decoded the month (wins) and day (attempts) back into two numeric columns. Validated against the reported Clutch Success %: 2,654 / 2,654 rows match. |
| **Percentages stored as text** (`"44%"`). | Can't aggregate or format. | Converted to decimals. |

## Data model and measures

Single fact table, plus an Agent → Role column (Duelist, Initiator, Controller, Sentinel) added in Power Query.

The measures recompute every rate from raw counts and never average the per-row averages. A player's ACS across 20 maps is weighted by rounds played, not a simple mean of 20 map-level ACS values.

| Measure | DAX logic |
|---|---|
| Rounds | `SUM(Rounds Played)` |
| K/D | `Total Kills ÷ Deaths` |
| KPR | `Total Kills ÷ Rounds` |
| ACS | Round-weighted: `SUMX(ACS × Rounds) ÷ Rounds` |
| Entry Success | `First Kills ÷ (First Kills + First Deaths)` |
| Clutch % | `Clutches Won ÷ Clutches Played` |
| Agent Pick % | Agent's rounds ÷ all rounds in the current filter context |

## Report pages

1. **Agent Meta:** pick rate by agent, filterable by tournament
2. **Player Leaderboard:** ACS, K/D, entry success and clutch % for players over a minimum-rounds threshold
3. **Team Scouting:** a team's agent pool and player performance

## Key findings

- **Omen was the backbone of the 2025 meta.** He was played in about 13% of all player-rounds, ahead of Viper (8%) and Sova (8%). Omen was the most-played agent in every region and at international events.
- **The meta was remarkably uniform across regions.** Americas, EMEA, Pacific and China all shared the same top agents, with only EMEA swapping Viper for Cypher in its top three.
- **Some agents were nearly absent from pro play.** Reyna (0.1%), Phoenix (0.2%) and Clove (0.3%) barely appeared.
- **Duelists win their opening duels most often.** Duelists won 51.5% of the round-opening duels they took, compared with 47.1% for Initiators, which fits their role as the team's entry players.
- **Top performers (500+ rounds):** ZmjjKK (EDward Gaming) led all qualifying players in round-weighted ACS at 247. Kai (Trace Esports) and aspas (MIBR) had the best entry success, winning about 62% of their opening duels.

## Tools

Power BI (web): semantic model, DAX, reports · Python (pandas): data cleaning
