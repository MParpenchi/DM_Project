import requests
import sqlite3

API_KEY = "e465200b7cmsh5bee388637f4a94p1f54cfjsnd512dae625fe"

# مختصات میلان (خود شهر، نه صرفاً فرودگاه)
LAT = 45.4643
LON = 9.1895

START = "2020-01-01"
END = "2024-12-31"

def get_daily_point_data():
    url = "https://meteostat.p.rapidapi.com/point/daily"
    params = {
        "lat": LAT,
        "lon": LON,
        "start": START,
        "end": END,
        # "alt": 120  # می‌تونی اضافه کنی، اجباری نیست
    }
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "meteostat.p.rapidapi.com"
    }

    print("Requesting point daily data from API...")
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["data"]


def save_point_to_sqlite(data):
    conn = sqlite3.connect("weather_5y_milan.db")
    cur = conn.cursor()

    # جدول جدا برای point data
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_weather_point (
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
        INSERT INTO daily_weather_point (
            date, tavg, tmin, tmax, prcp, snow, wdir, wspd, wpgt, pres, tsun
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    print(f"Inserted {len(rows)} point-rows into SQLite!")


if __name__ == "__main__":
    data = get_daily_point_data()
    save_point_to_sqlite(data)
    print("Done.")
