CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS stg;
CREATE SCHEMA IF NOT EXISTS mart;

-- Teams
DROP TABLE IF EXISTS raw.mteams;
CREATE TABLE raw.mteams (
  team_id INT PRIMARY KEY,
  team_name TEXT NOT NULL,
  first_d1_season INT,
  last_d1_season INT
);

-- Regular season compact results
DROP TABLE IF EXISTS raw.mregular_season_compact_results;
CREATE TABLE raw.mregular_season_compact_results (
  season INT NOT NULL,
  day_num INT NOT NULL,
  w_team_id INT NOT NULL,
  w_score INT NOT NULL,
  l_team_id INT NOT NULL,
  l_score INT NOT NULL,
  w_loc TEXT,
  num_ot INT
);

-- Tourney compact results
DROP TABLE IF EXISTS raw.mncaa_tourney_compact_results;
CREATE TABLE raw.mncaa_tourney_compact_results (
  season INT NOT NULL,
  day_num INT NOT NULL,
  w_team_id INT NOT NULL,
  w_score INT NOT NULL,
  l_team_id INT NOT NULL,
  l_score INT NOT NULL,
  w_loc TEXT,
  num_ot INT
);

-- Tourney seeds
DROP TABLE IF EXISTS raw.mncaa_tourney_seeds;
CREATE TABLE raw.mncaa_tourney_seeds (
  season INT NOT NULL,
  seed TEXT NOT NULL,
  team_id INT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reg_season_season ON raw.mregular_season_compact_results(season);
CREATE INDEX IF NOT EXISTS idx_tourney_season ON raw.mncaa_tourney_compact_results(season);
CREATE INDEX IF NOT EXISTS idx_seeds_season ON raw.mncaa_tourney_seeds(season);
