import sqlite3
from pathlib import Path

# مسیر دیتابیس (همون فایلی که قبلاً ساختیم)
DB_PATH = Path(__file__).with_name("weather_5y_milan.db")


def create_monthly_table():
    print("Using DB:", DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # اگر قبلاً ساختیم، پاک کن تا از نو بسازیم
    cur.execute("DROP TABLE IF EXISTS weather_monthly")

    # ساخت جدول ماهانه از روی daily_weather_point
    cur.execute(
        """
        CREATE TABLE weather_monthly AS
        SELECT
            substr(date, 1, 7) AS month,        -- مثل 2020-01
            AVG(tavg)        AS avg_temp,
            SUM(prcp)        AS total_rain,
            SUM(snow)        AS total_snow,
            AVG(wspd)        AS avg_wind_speed
        FROM daily_weather_point
        GROUP BY substr(date, 1, 7)
        ORDER BY month
        """
    )

    conn.commit()
    conn.close()

    print("✅ weather_monthly table created successfully.")


if __name__ == "__main__":
    create_monthly_table()
