DROP TABLE IF EXISTS stg.tourney_seeds;
CREATE TABLE stg.tourney_seeds AS
SELECT
  season,
  team_id,
  seed AS seed_code,
  LEFT(seed, 1) AS region,
  CAST(SUBSTRING(seed FROM 2 FOR 2) AS INT) AS seed_num
FROM raw.mncaa_tourney_seeds
WHERE season >= 2019;

CREATE INDEX IF NOT EXISTS idx_stg_tourney_seeds_season ON stg.tourney_seeds(season);
CREATE INDEX IF NOT EXISTS idx_stg_tourney_seeds_team ON stg.tourney_seeds(team_id);
