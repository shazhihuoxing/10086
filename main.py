from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# 跨域配置，等价原来 CORS(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接
def get_db_conn():
    conn = sqlite3.connect("pomodoro.db")
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库表
def init_database():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS setting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tomatoCount INTEGER DEFAULT 0,
            workMin INTEGER DEFAULT 25,
            breakMin INTEGER DEFAULT 5
        )
    ''')
    res = cursor.execute("SELECT * FROM setting WHERE id=1").fetchone()
    if not res:
        cursor.execute("INSERT INTO setting(tomatoCount, workMin, breakMin) VALUES (0, 25, 5)")
    conn.commit()
    conn.close()

init_database()

# 定义POST请求接收的JSON模型（替代request.get_json()）
class TomatoBody(BaseModel):
    tomatoCount: int = 0

class TimeBody(BaseModel):
    workMin: int = 25
    breakMin: int = 5


# 获取保存的数据 GET /api/getData
@app.get("/api/getData")
def get_data():
    conn = get_db_conn()
    row = conn.execute("SELECT * FROM setting WHERE id=1").fetchone()
    conn.close()
    return {
        "tomatoCount": row["tomatoCount"],
        "workMin": row["workMin"],
        "breakMin": row["breakMin"]
    }


# 保存番茄数量 POST /api/saveTomato
@app.post("/api/saveTomato")
def save_tomato(body: TomatoBody):
    count = body.tomatoCount
    conn = get_db_conn()
    conn.execute("UPDATE setting SET tomatoCount=? WHERE id=1", (count,))
    conn.commit()
    conn.close()
    return {"ok": True}


# 保存专注/休息时间 POST /api/saveTime
@app.post("/api/saveTime")
def save_time(body: TimeBody):
    work = body.workMin
    br = body.breakMin
    conn = get_db_conn()
    conn.execute("UPDATE setting SET workMin=?, breakMin=? WHERE id=1", (work, br))
    conn.commit()
    conn.close()
    return {"ok": True}
