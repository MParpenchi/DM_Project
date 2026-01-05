import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("weather_5y_milan.db")

def join_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # حذف اگر قبلاً ساخته شده بود
    cur.execute("DROP TABLE IF EXISTS final_weather_accidents")

    # ساخت جدول JOIN
    cur.execute("""
        CREATE TABLE final_weather_accidents AS
        SELECT
            a.*,
            w.avg_temp,
            w.total_rain,
            w.total_snow,
            CASE
                WHEN w.total_snow > 0 THEN 'snow'
                WHEN w.total_rain > 0 THEN 'rain'
                ELSE 'dry'
            END AS weather_condition
        FROM accidents_monthly a
        LEFT JOIN weather_monthly w
        ON a.month = w.month
        ORDER BY a.month;
    """)

    conn.commit()
    conn.close()
    print("✅ final_weather_accidents table created successfully.")

if __name__ == "__main__":
    join_tables()
