DROP TABLE IF EXISTS mart.team_season_stats;
CREATE TABLE mart.team_season_stats AS
WITH team_games AS (
  SELECT
    season,
    winner_team_id AS team_id,
    1 AS win,
    0 AS loss,
    winner_score AS points_for,
    loser_score AS points_against,
    game_type
  FROM stg.games

  UNION ALL

  SELECT
    season,
    loser_team_id AS team_id,
    0 AS win,
    1 AS loss,
    loser_score AS points_for,
    winner_score AS points_against,
    game_type
  FROM stg.games
),
agg AS (
  SELECT
    season,
    team_id,
    COUNT(*) AS games_played,
    SUM(win) AS wins,
    SUM(loss) AS losses,
    SUM(points_for) AS points_for,
    SUM(points_against) AS points_against,
    ROUND(AVG(points_for::numeric), 2) AS avg_points_for,
    ROUND(AVG(points_against::numeric), 2) AS avg_points_against,
    ROUND(AVG((points_for - points_against)::numeric), 2) AS avg_margin
  FROM team_games
  WHERE game_type = 'regular'
  GROUP BY season, team_id
)
SELECT
  a.season,
  a.team_id,
  t.team_name,
  a.games_played,
  a.wins,
  a.losses,
  ROUND((a.wins::numeric / NULLIF(a.games_played, 0))::numeric, 3) AS win_pct,
  a.points_for,
  a.points_against,
  a.avg_points_for,
  a.avg_points_against,
  a.avg_margin
FROM agg a
JOIN stg.teams t ON t.team_id = a.team_id;

CREATE INDEX IF NOT EXISTS idx_mart_team_season_stats_season ON mart.team_season_stats(season);
