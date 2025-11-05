from attendance import insert_data, conn
import sqlite3
from datetime import datetime, timedelta

# === 조건: 2025년 9월~10월 ===
start_date = datetime(2025, 9, 1)
end_date = datetime(2025, 10, 31)

# 요일 매핑 (월=0, 화=1, ..., 일=6)
morning_times = {
    0: "09:10:00",  # 월
    1: "10:07:00",  # 화
    2: "09:10:00",  # 수
    3: "10:07:00",  # 목
    4: "09:10:00",  # 금
}
DB_PATH = "attendance.db"
conn = sqlite3.connect(DB_PATH)
current = start_date
while current <= end_date:
    weekday = current.weekday()
    if weekday in morning_times:
        ts = f"{current.strftime('%Y-%m-%d')} {morning_times[weekday]}"
        cur = conn.execute(
        """
        INSERT INTO attendance (student_id, student_name,timestamp)
        VALUES (?, ?, ?)
        """,
        ("1111", "test", ts),
    )
    conn.commit()
    current += timedelta(days=1)
