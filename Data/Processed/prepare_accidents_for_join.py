import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("weather_5y_milan.db")

def prepare_accidents():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # اگر قبلاً month ساخته شده بود پاکش کنیم
    try:
        cur.execute("ALTER TABLE accidents_monthly DROP COLUMN month;")
    except:
        pass  # اگر وجود ندارد مشکلی نیست

    # اضافه کردن ستون month
    cur.execute("ALTER TABLE accidents_monthly ADD COLUMN month TEXT;")

    # پر کردن month با فرمت YYYY-MM
    cur.execute("""
        UPDATE accidents_monthly
        SET month = printf('%04d-%02d', Anno, Mese);
    """)

    conn.commit()
    conn.close()
    print("✅ month column created successfully.")

if __name__ == "__main__":
    prepare_accidents()
