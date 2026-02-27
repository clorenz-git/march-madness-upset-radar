DROP TABLE IF EXISTS mart.team_tourney_training_data;

CREATE TABLE mart.team_tourney_training_data AS
WITH seeds AS (
    SELECT
        season,
        team_id,
        1 AS made_tournament
    FROM stg.tourney_seeds
),

base AS (
    SELECT
        tss.season,
        tss.team_id,
        tss.team_name,
        tss.games_played,
        tss.wins,
        tss.losses,
        tss.win_pct,
        tss.avg_points_for,
        tss.avg_points_against,
        tss.avg_margin
    FROM mart.team_season_stats tss
    WHERE tss.season >= 2015
)

SELECT
    b.*,
    COALESCE(s.made_tournament, 0) AS made_tournament
FROM base b
LEFT JOIN seeds s
    ON b.team_id = s.team_id
    AND b.season = s.season;
