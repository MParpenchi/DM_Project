import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("weather_5y_milan.db")

def import_accidents():
    df = pd.read_csv("accidents_milan_monthly.csv")

    # اگر لازم بود نام ستون ماه رو تغییر بده به month
    # df = df.rename(columns={"اسم_ستون_ماه": "month", "اسم_ستون_تعداد": "accidents"})

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("accidents_monthly", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ accidents_monthly table created/updated.")

if __name__ == "__main__":
    import_accidents()
