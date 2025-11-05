from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel, constr
from datetime import date, time
import sqlite3
from typing import Any, Dict, List


attendance_router = APIRouter()
DB_PATH = "attendance.db"


# 전역 커넥션 생성 (애플리케이션 시작 시 1회)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

cmd1 ='''CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    student_name TEXT NOT NULL,
    timestamp DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, '+9 hours'))
    );
'''
def init_db():
    cursor = conn.cursor()
    cursor.execute(cmd1)
    conn.commit()
    conn.close()
init_db()


@attendance_router.post("/attendance_debug")
def query_attendance_debug(    
    student_id: str = Form(...),
):
    """
    요청: { "student_id": "..." }
    응답: { "count": n, "rows": [ {col: val, ...}, ... ] }
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # dict로 변환 쉽게
            cur = conn.execute(
                f"""
                SELECT *
                FROM attendance
                WHERE student_id = {student_id}
                """,
            )
            rows: List[Dict[str, Any]] = [dict(r) for r in cur.fetchall()]

        return {"count": len(rows), "rows": rows}

    except sqlite3.Error as e:
        raise HTTPException(500, f"DB error: {e}")

@attendance_router.post("/attendance_month")
def query_attendance(
    student_id: str = Form(...),
    start_date: str = Form(...),  # "YYYY-MM-DD"
    end_date:   str = Form(...),  # "YYYY-MM-DD"
    start_time: str = Form(...),  # "HH:MM[:SS]"
    end_time:   str = Form(...),  # "HH:MM[:SS]"
):
    try:
        # 문자열 → 타입 변환 (형식 오류시 ValueError)
        sd = date.fromisoformat(start_date)
        ed = date.fromisoformat(end_date)
        st = time.fromisoformat(start_time)
        et = time.fromisoformat(end_time)
    except ValueError:
        raise HTTPException(400, "날짜 또는 시간 형식이 올바르지 않습니다.")
    if ed < sd:
        raise HTTPException(400, "종료 날짜가 시작 날짜보다 빠릅니다.")

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # dict로 변환 쉽게
            if st <= et:
                # 일반 구간 (예: 09:10 ~ 10:07)
                sql = """
                SELECT *
                FROM attendance
                WHERE student_id = ?
                  AND date(timestamp) BETWEEN date(?) AND date(?)
                  AND time(timestamp) BETWEEN time(?) AND time(?)
                ORDER BY timestamp ASC
                """
                params = (student_id, sd.isoformat(), ed.isoformat(),
                          st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"))
            else:
                # 자정을 가로지르는 구간 (예: 22:00 ~ 02:00)
                sql = """
                SELECT *
                FROM attendance
                WHERE student_id = ?
                  AND date(timestamp) BETWEEN date(?) AND date(?)
                  AND (
                        time(timestamp) >= time(?)
                        OR
                        time(timestamp) <= time(?)
                      )
                ORDER BY timestamp ASC
                """
                params = (student_id, sd.isoformat(), ed.isoformat(),
                          st.strftime("%H:%M:%S"), et.strftime("%H:%M:%S"))

            cur = conn.execute(sql, params)
            rows: List[Dict[str, Any]] = [dict(r) for r in cur.fetchall()]
        return {"count": len(rows), "rows": rows}

    except sqlite3.Error as e:
        raise HTTPException(500, f"DB error: {e}")


def insert_data(student_id, student_name):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """
                INSERT INTO attendance (student_id, student_name)
                VALUES (?, ?)
                """,
                (student_id, student_name),
            )
            conn.commit()

            # 방금 넣은 행 반환(선택)
            # conn.row_factory = sqlite3.Row
            # inserted_id = cur.lastrowid
            # row = conn.execute(
            #     "SELECT * FROM attendance WHERE id = ?", (inserted_id,)
            # ).fetchone()
            # return {
            #     "status": "success",
            #     "row": dict(row) if row else None,
            #     "time": datetime.now().isoformat(),
            # }

            return {"status": "success", "student_id": student_id}
    except sqlite3.Error as e:
        raise HTTPException(500, f"DB error: {e}")
