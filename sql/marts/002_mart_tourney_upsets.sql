DROP TABLE IF EXISTS mart.tourney_upsets;
CREATE TABLE mart.tourney_upsets AS
WITH tg AS (
  SELECT
    season,
    day_num,
    winner_team_id,
    loser_team_id,
    winner_score,
    loser_score,
    margin
  FROM stg.games
  WHERE game_type = 'tourney'
    AND season >= 2019
),
joined AS (
  SELECT
    g.season,
    g.day_num,
    g.winner_team_id,
    wt.team_name AS winner_team_name,
    ws.seed_num AS winner_seed,
    g.loser_team_id,
    lt.team_name AS loser_team_name,
    ls.seed_num AS loser_seed,
    g.winner_score,
    g.loser_score,
    g.margin
  FROM tg g
  JOIN stg.teams wt ON wt.team_id = g.winner_team_id
  JOIN stg.teams lt ON lt.team_id = g.loser_team_id
  LEFT JOIN stg.tourney_seeds ws
    ON ws.season = g.season AND ws.team_id = g.winner_team_id
  LEFT JOIN stg.tourney_seeds ls
    ON ls.season = g.season AND ls.team_id = g.loser_team_id
)
SELECT
  season,
  day_num,
  winner_team_id,
  winner_team_name,
  winner_seed,
  loser_team_id,
  loser_team_name,
  loser_seed,
  winner_score,
  loser_score,
  margin,
  (winner_seed - loser_seed) AS seed_diff,
  CASE
    WHEN winner_seed IS NULL OR loser_seed IS NULL THEN NULL
    WHEN winner_seed > loser_seed THEN TRUE
    ELSE FALSE
  END AS is_upset
FROM joined;

CREATE INDEX IF NOT EXISTS idx_mart_upsets_season ON mart.tourney_upsets(season);
CREATE INDEX IF NOT EXISTS idx_mart_upsets_is_upset ON mart.tourney_upsets(is_upset);
