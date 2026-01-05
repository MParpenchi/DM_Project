import requests
import sqlite3
from datetime import datetime, timedelta

API_KEY = "e465200b7cmsh5bee388637f4a94p1f54cfjsnd512dae625fe"

# Milan Malpensa Airport weather station
STATION_ID = "16059"

# Date range
START = "2020-01-01"
END = "2024-12-31"

def get_daily_data():
    url = "https://meteostat.p.rapidapi.com/stations/daily"
    query = {
        "station": STATION_ID,
        "start": START,
        "end": END
    }
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "meteostat.p.rapidapi.com"
    }

    print("Requesting data from API...")
    r = requests.get(url, headers=headers, params=query)
    r.raise_for_status()
    return r.json()["data"]


def save_to_sqlite(data):
    conn = sqlite3.connect("weather_5y_milan.db")
    cur = conn.cursor()

    # Create table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            tavg REAL,
            tmin REAL,
            tmax REAL,
            prcp REAL,
            snow REAL,
            wdir REAL,
            wspd REAL,
            wpgt REAL,
            pres REAL,
            tsun REAL
        )
        """
    )

    insert_sql = """
        INSERT INTO daily_weather (
            date, tavg, tmin, tmax, prcp, snow, wdir, wspd, wpgt, pres, tsun
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    rows = []
    for row in data:
        rows.append((
            row.get("date"),
            row.get("tavg"),
            row.get("tmin"),
            row.get("tmax"),
            row.get("prcp"),
            row.get("snow"),
            row.get("wdir"),
            row.get("wspd"),
            row.get("wpgt"),
            row.get("pres"),
            row.get("tsun")
        ))

    cur.executemany(insert_sql, rows)
    conn.commit()
    conn.close()

    print(f"Inserted {len(rows)} rows into SQLite!")


if __name__ == "__main__":
    data = get_daily_data()
    save_to_sqlite(data)
    print("Done.")
