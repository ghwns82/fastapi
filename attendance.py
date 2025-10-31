from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel, constr
from datetime import datetime
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
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
'''
def init_db():
    cursor = conn.cursor()
    cursor.execute(cmd1)
    conn.commit()
    conn.close()
init_db()


@attendance_router.post("/attendance")
def query_attendance(    
    student_id: str = Form(...),
    student_name: str = Form(...)
):
    """
    요청: { "student_id": "...", "student_name": "..." }
    응답: { "count": n, "rows": [ {col: val, ...}, ... ] }
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # dict로 변환 쉽게
            cur = conn.execute(
                """
                SELECT *
                FROM attendance
                WHERE student_id = ?
                  AND student_name = ?
                -- 필요하면 아래처럼 대소문자 무시:
                -- WHERE student_id = ?
                --   AND UPPER(student_name) = UPPER(?)
                """,
                (student_id, student_name),
            )
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
