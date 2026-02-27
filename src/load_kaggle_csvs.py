import os
import re

import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL")
RAW_DIR = os.getenv("RAW_DIR", "data/raw")

FILES = [
    ("MTeams.csv", "raw.mteams"),
    ("MRegularSeasonCompactResults.csv", "raw.mregular_season_compact_results"),
    ("MNCAATourneyCompactResults.csv", "raw.mncaa_tourney_compact_results"),
    ("MNCAATourneySeeds.csv", "raw.mncaa_tourney_seeds"),
]


def load_csv(engine, filename: str, table: str) -> None:
    path = os.path.join(RAW_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Put {filename} in {RAW_DIR}/")

    df = pd.read_csv(path)
    # Convert Kaggle CamelCase/PascalCase headers to snake_case for easier querying in SQL and pandas 
    normalized_cols = []
    for c in df.columns:
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", c.strip())
        s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
        normalized_cols.append(s2.lower())
    df.columns = normalized_cols

    schema, table_name = table.split(".")
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE {table};"))
        df.to_sql(
            table_name,
            conn,
            schema=schema,
            if_exists="append",
            index=False,
            method="multi",
        )
    print(f"Loaded {len(df):,} rows into {table}")


def main() -> None:
    if not DB_URL:
        raise ValueError("DB_URL is not set. Add it to your environment or local .env file.")
    engine = create_engine(DB_URL)
    for filename, table in FILES:
        load_csv(engine, filename, table)


if __name__ == "__main__":
    main()
