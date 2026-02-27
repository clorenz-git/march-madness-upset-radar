DROP TABLE IF EXISTS stg.games;
CREATE TABLE stg.games AS
WITH reg AS (
  SELECT
    season,
    day_num,
    'regular'::text AS game_type,
    w_team_id AS winner_team_id,
    l_team_id AS loser_team_id,
    w_score AS winner_score,
    l_score AS loser_score,
    w_loc,
    num_ot
  FROM raw.mregular_season_compact_results
),
tourn AS (
  SELECT
    season,
    day_num,
    'tourney'::text AS game_type,
    w_team_id AS winner_team_id,
    l_team_id AS loser_team_id,
    w_score AS winner_score,
    l_score AS loser_score,
    w_loc,
    num_ot
  FROM raw.mncaa_tourney_compact_results
)
SELECT
  season,
  day_num,
  game_type,
  winner_team_id,
  loser_team_id,
  winner_score,
  loser_score,
  (winner_score - loser_score) AS margin,
  w_loc,
  COALESCE(num_ot, 0) AS num_ot
FROM reg
UNION ALL
SELECT
  season,
  day_num,
  game_type,
  winner_team_id,
  loser_team_id,
  winner_score,
  loser_score,
  (winner_score - loser_score) AS margin,
  w_loc,
  COALESCE(num_ot, 0) AS num_ot
FROM tourn;

CREATE INDEX IF NOT EXISTS idx_stg_games_season ON stg.games(season);
CREATE INDEX IF NOT EXISTS idx_stg_games_type ON stg.games(game_type);
