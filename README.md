# 🏀 March Madness Upset Radar

Local **Postgres-first data engineering project** built around NCAA March Madness data.

I wanted a hands-on pipeline project that was actually fun to work on, so naturally… we’re analyzing tournament chaos.

This project ingests historical NCAA data, models it using a classic **raw → staging → mart** warehouse pattern, and produces analytics focused on **modern era tournament upsets (2019+)**.

---

## 🚀 What this project does

This pipeline takes raw Kaggle CSVs and turns them into clean, queryable analytics tables.

**Ingestion**

* Loads Kaggle NCAA CSVs into a Postgres database running in Docker
* Raw data lands in the `raw` schema

**Transformation**

* Builds cleaned staging models in the `stg` schema
* Normalizes teams, games, and tournament seeds

**Analytics Marts**

* `mart.team_season_stats`
  Regular season performance metrics per team and season

* `mart.tourney_upsets`
  Tournament games with automatic upset detection
  *(Modern era only — seasons ≥ 2019)*

AKA: the “who busted brackets the hardest” table 😈

---

## ⚙️ Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make up
make run
```

This will:

1. Start Postgres in Docker
2. Create schemas and tables
3. Load raw data
4. Build staging + mart models

One command rebuilds the whole pipeline.

---

## 📂 Required raw files

Download the Kaggle March Machine Learning Mania dataset and place these files in:

```
data/raw/
```

Required files:

* `MTeams.csv`
* `MRegularSeasonCompactResults.csv`
* `MNCAATourneyCompactResults.csv`
* `MNCAATourneySeeds.csv`

These are intentionally **not committed** to the repo.

---

## 🔎 Example queries

### Biggest modern-era upsets

```sql
SELECT season, winner_team_name, winner_seed, loser_team_name, loser_seed, seed_diff, margin
FROM mart.tourney_upsets
WHERE is_upset = TRUE
ORDER BY seed_diff DESC, margin DESC
LIMIT 15;
```

---

### Upset win rate by seed

```sql
SELECT
  winner_seed,
  COUNT(*) AS wins,
  SUM(CASE WHEN is_upset THEN 1 ELSE 0 END) AS upset_wins,
  ROUND(100.0 * SUM(CASE WHEN is_upset THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS upset_win_pct
FROM mart.tourney_upsets
WHERE winner_seed IS NOT NULL AND loser_seed IS NOT NULL
GROUP BY winner_seed
ORDER BY winner_seed;
```

---

## 🧠 Why I built this

I wanted a beginner-friendly but realistic data engineering project that shows:

* SQL modeling (raw → stg → mart)
* Local warehouse setup with Docker + Postgres
* Working with real world datasets
* Building analytics that actually tell a story

Also… March Madness is chaotic and perfect for data exploration.

---

## 📌 Next steps / future ideas

* Add dbt for testing + documentation
* Add orchestration (Prefect or Dagster)
* Deploy dashboard publicly
* Add a “Chaos Score” metric across seasons

---

If you love basketball and data, this was a blast to build.
