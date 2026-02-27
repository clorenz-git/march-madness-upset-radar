import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

st.set_page_config(page_title="March Madness Upset Radar", layout="wide")

# Load local .env when running Streamlit without exported shell vars.
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")
DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("DB_URL is not set. Add it to your environment or local .env file.")
engine = create_engine(DB_URL)




# Streamlit Theme Helpers

def get_theme_colors():
    # Pull colors directly from Streamlit theme
    primary = st.get_option("theme.primaryColor") or "#FF4B4B"
    background = st.get_option("theme.backgroundColor") or "#0E1117"
    text = st.get_option("theme.textColor") or "#FAFAFA"
    secondary_bg = st.get_option("theme.secondaryBackgroundColor") or "#262730"

    return primary, background, text, secondary_bg


def apply_streamlit_theme(ax):
    primary, background, text, secondary_bg = get_theme_colors()

    ax.set_facecolor(background)
    ax.figure.set_facecolor(background)

    ax.tick_params(colors=text)
    ax.xaxis.label.set_color(text)
    ax.yaxis.label.set_color(text)
    ax.title.set_color(text)

    # gridlines that match Streamlit
    ax.grid(color=secondary_bg, linestyle='-', linewidth=0.6, alpha=0.6)

    for spine in ax.spines.values():
        spine.set_color(secondary_bg)

    return primary, background, text, secondary_bg



# Chart helpers with themes

def bar_chart(df, x_col, y_col, title, xlabel=None, ylabel=None, height=2.6):
    primary, background, text, secondary_bg = get_theme_colors()

    n = max(len(df), 1)
    width = min(9, max(5.5, n * 0.45))

    fig, ax = plt.subplots(figsize=(width, height), dpi=120)

    ax.bar(df[x_col].astype(str), df[y_col], color=primary)

    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel or x_col)
    ax.set_ylabel(ylabel or y_col)

    apply_streamlit_theme(ax)

    if n > 8:
        plt.xticks(rotation=45, ha="right")
    else:
        plt.xticks(rotation=0)

    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def hist_chart(series, title, xlabel=None, bins=20, height=2.6):
    primary, background, text, secondary_bg = get_theme_colors()

    fig, ax = plt.subplots(figsize=(7, height), dpi=120)

    ax.hist(series.dropna(), bins=bins, color=primary, edgecolor=secondary_bg)

    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xlabel or series.name or "value")
    ax.set_ylabel("count")

    apply_streamlit_theme(ax)

    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# Queries

@st.cache_data(ttl=300)
def get_seasons():
    q = """
    SELECT DISTINCT season
    FROM mart.tourney_upsets
    WHERE season >= 2019
    ORDER BY season;
    """
    return pd.read_sql(q, engine)["season"].tolist()


@st.cache_data(ttl=300)
def upset_margins(season: int):
    q = """
    SELECT margin
    FROM mart.tourney_upsets
    WHERE is_upset = TRUE
      AND season = :season
      AND margin IS NOT NULL;
    """
    return pd.read_sql(text(q), engine, params={"season": season})


@st.cache_data(ttl=300)
def biggest_upsets(season: int, limit: int):
    q = """
    SELECT
      season,
      winner_team_name,
      winner_seed,
      loser_team_name,
      loser_seed,
      seed_diff,
      margin
    FROM mart.tourney_upsets
    WHERE is_upset = TRUE
      AND season = :season
    ORDER BY seed_diff DESC, margin DESC
    LIMIT :limit;
    """
    return pd.read_sql(text(q), engine, params={"season": season, "limit": limit})


@st.cache_data(ttl=300)
def chaos_teams(season: int, limit: int):
    q = """
    SELECT
      winner_team_name AS team,
      COUNT(*) AS upset_wins,
      ROUND(AVG(seed_diff::numeric), 2) AS avg_seed_diff
    FROM mart.tourney_upsets
    WHERE is_upset = TRUE
      AND season = :season
    GROUP BY winner_team_name
    ORDER BY upset_wins DESC, avg_seed_diff DESC
    LIMIT :limit;
    """
    return pd.read_sql(text(q), engine, params={"season": season, "limit": limit})


@st.cache_data(ttl=300)
def upset_rate_by_winner_seed(season: int):
    q = """
    SELECT
      winner_seed,
      COUNT(*) AS wins,
      SUM(CASE WHEN is_upset THEN 1 ELSE 0 END) AS upset_wins,
      ROUND(
        100.0 * SUM(CASE WHEN is_upset THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
        2
      ) AS upset_win_pct
    FROM mart.tourney_upsets
    WHERE winner_seed IS NOT NULL
      AND loser_seed IS NOT NULL
      AND season = :season
    GROUP BY winner_seed
    ORDER BY winner_seed;
    """
    return pd.read_sql(text(q), engine, params={"season": season})


@st.cache_data(ttl=300)
def top_regular_season_teams(season: int, limit: int):
    q = """
    SELECT team_name, wins, losses, win_pct, avg_margin
    FROM mart.team_season_stats
    WHERE season = :season
    ORDER BY win_pct DESC, avg_margin DESC
    LIMIT :limit;
    """
    return pd.read_sql(text(q), engine, params={"season": season, "limit": limit})

@st.cache_data(ttl=300)
def tourney_odds_by_win_range():
    q = """
    SELECT
      CASE
        WHEN win_pct < 0.55 THEN '<55%'
        WHEN win_pct < 0.60 THEN '55-60%'
        WHEN win_pct < 0.65 THEN '60-65%'
        WHEN win_pct < 0.70 THEN '65-70%'
        WHEN win_pct < 0.75 THEN '70-75%'
        WHEN win_pct < 0.80 THEN '75-80%'
        ELSE '80%+'
      END AS win_range,
      ROUND(100.0 * SUM(made_tournament)/COUNT(*),1) AS pct_made_tourney
    FROM mart.team_tourney_training_data
    GROUP BY win_range
    ORDER BY win_range;
    """
    return pd.read_sql(text(q), engine)
# UI for Streamlit app

st.title("March Madness Upset Radar (Modern Era)")

seasons = get_seasons()
default_season = seasons[-1] if seasons else 2023

with st.sidebar:
    st.header("Filters")
    season = st.selectbox(
        "Season",
        seasons,
        index=seasons.index(default_season) if default_season in seasons else 0,
    )
    limit = st.slider("Rows to show", 5, 50, 15)

# Top tables
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("Biggest Upsets")
    st.dataframe(biggest_upsets(season, limit), use_container_width=True)

with col2:
    st.subheader("Chaos Teams (Most Upset Wins)")
    st.dataframe(chaos_teams(season, limit), use_container_width=True)

# Compact charts row (two columns)
g1, g2 = st.columns(2)

with g1:
    st.subheader("Chaos Teams Chart")
    df_chaos = chaos_teams(season, limit)
    bar_chart(
        df_chaos,
        x_col="team",
        y_col="upset_wins",
        title=f"Top Chaos Teams by Upset Wins ({season})",
        xlabel="Team",
        ylabel="Upset Wins",
        height=2.6
    )

with g2:
    st.subheader("Upset Margins")
    df_margin = upset_margins(season)
    hist_chart(
        df_margin["margin"],
        title=f"Upset Margins Distribution ({season})",
        xlabel="Margin of Victory (points)",
        bins=15,
        height=2.6
    )

st.divider()
st.subheader("Historical Tournament Odds by Win Percentage")

df_odds = tourney_odds_by_win_range()

primary = "#E03A3E"      # NCAA red vibe
secondary = "#17408B"    # NCAA blue vibe

fig, ax = plt.subplots(figsize=(6.2, 2.2), dpi=120)

bars = ax.bar(df_odds["win_range"], df_odds["pct_made_tourney"])

# Color gradient red → blue
colors = [primary, "#f25c5f", "#f78c6b", "#ffd166", "#9ad1d4", "#5fa8d3", secondary]
for bar, color in zip(bars, colors):
    bar.set_color(color)

ax.set_title("Chance of Making March Madness by Win %")
ax.set_ylabel("Probability (%)")
ax.set_xlabel("Regular Season Win %")

ax.grid(alpha=0.3)
fig.tight_layout()

st.pyplot(fig, use_container_width=False)
st.divider()

# Bottom section: seed performance plus regular season context
c3, c4 = st.columns([1, 1])

with c3:
    st.subheader("Upset Rate by Winner Seed")
    df_seed = upset_rate_by_winner_seed(season)
    st.dataframe(df_seed, use_container_width=True)

    bar_chart(
        df_seed,
        x_col="winner_seed",
        y_col="upset_win_pct",
        title=f"Upset Win % by Winner Seed ({season})",
        xlabel="Winner Seed",
        ylabel="Upset Win %",
        height=2.6
    )

with c4:
    st.subheader("Regular Season Top Teams (by Win%)")
    st.dataframe(top_regular_season_teams(season, limit), use_container_width=True)

st.caption("Data source: Kaggle NCAA results. Pipeline: raw → stg → mart in Postgres.")
