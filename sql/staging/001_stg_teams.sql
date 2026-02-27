DROP TABLE IF EXISTS stg.teams;
CREATE TABLE stg.teams AS
SELECT
  team_id,
  team_name,
  first_d1_season,
  last_d1_season
FROM raw.mteams;

CREATE UNIQUE INDEX IF NOT EXISTS ux_stg_teams ON stg.teams(team_id);
