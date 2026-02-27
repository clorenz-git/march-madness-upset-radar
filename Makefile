DB ?= postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@localhost:5432/$(POSTGRES_DB)
DB_URL ?= postgresql+psycopg2://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@localhost:5432/$(POSTGRES_DB)

up:
	docker compose up -d

down:
	docker compose down

ddl:
	psql $(DB) -f sql/ddl/001_raw_tables.sql

load:
	DB_URL="$(DB_URL)" .venv/bin/python src/load_kaggle_csvs.py

staging:
	psql $(DB) -f sql/staging/001_stg_teams.sql
	psql $(DB) -f sql/staging/002_stg_games.sql
	psql $(DB) -f sql/staging/003_stg_tourney_seeds.sql

marts:
	psql $(DB) -f sql/marts/001_mart_team_season_stats.sql
	psql $(DB) -f sql/marts/002_mart_tourney_upsets.sql

run: ddl load staging marts
	@echo "Pipeline complete"
