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
    ID TEXT NOT NULL,
    name TEXT NOT NULL,
    timestamp DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, '+9 hours'))
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
    ID: str = Form(...),
    name: str = Form(...)
):
    """
    요청: { "ID": "...", "name": "..." }
    응답: { "count": n, "rows": [ {col: val, ...}, ... ] }
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row  # dict로 변환 쉽게
            cur = conn.execute(
                """
                SELECT *
                FROM attendance
                WHERE ID = ?
                  AND name = ?
                -- 필요하면 아래처럼 대소문자 무시:
                -- WHERE ID = ?
                --   AND UPPER(name) = UPPER(?)
                """,
                (ID, name),
            )
            rows: List[Dict[str, Any]] = [dict(r) for r in cur.fetchall()]

        return {"count": len(rows), "rows": rows}

    except sqlite3.Error as e:
        raise HTTPException(500, f"DB error: {e}")


def insert_data(ID, name):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """
                INSERT INTO attendance (ID, name)
                VALUES (?, ?)
                """,
                (ID, name),
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

            return {"status": "success", "ID": ID}
    except sqlite3.Error as e:
        raise HTTPException(500, f"DB error: {e}")
