from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

import sqlite3
from pydantic import BaseModel
from datetime import datetime


attendance_router = APIRouter()
DB_PATH = "attendance.db"

# 전역 커넥션 생성 (애플리케이션 시작 시 1회)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

cmd1 ='''CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
'''
def init_db():
    cursor = conn.cursor()
    cursor.execute(cmd1)
    conn.commit()
    conn.close()
init_db()


# 입력용 모델
class AttendanceIn(BaseModel):
    student_id: str
    student_name: str


@attendance_router.post("/attendance")
def record_attendance(data: AttendanceIn):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO attendance (student_id, student_name)
        VALUES (?, ?, ?)
    """, (data.student_id, data.student_name))
    conn.commit()
    conn.close()
    return {"status": "success", "student_id": data.student_id, "time": datetime.now()}