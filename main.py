from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# 数据库连接
def get_db_conn():
    conn = sqlite3.connect("pomodoro.db")
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库表
def init_database():
    conn = get_db_conn()
    cursor = conn.cursor()
    # 创建配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS setting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tomatoCount INTEGER DEFAULT 0,
            workMin INTEGER DEFAULT 25,
            breakMin INTEGER DEFAULT 5
        )
    ''')
    # 检查是否有初始数据，没有就插入
    res = cursor.execute("SELECT * FROM setting WHERE id=1").fetchone()
    if not res:
        cursor.execute("INSERT INTO setting(tomatoCount, workMin, breakMin) VALUES (0, 25, 5)")
    conn.commit()
    conn.close()

# 获取保存的数据
@app.route("/api/getData", methods=["GET"])
def get_data():
    conn = get_db_conn()
    row = conn.execute("SELECT * FROM setting WHERE id=1").fetchone()
    conn.close()
    return jsonify({
        "tomatoCount": row["tomatoCount"],
        "workMin": row["workMin"],
        "breakMin": row["breakMin"]
    })

# 保存番茄数量
@app.route("/api/saveTomato", methods=["POST"])
def save_tomato():
    json_data = request.get_json()
    count = json_data.get("tomatoCount", 0)
    conn = get_db_conn()
    conn.execute("UPDATE setting SET tomatoCount=? WHERE id=1", (count,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# 保存专注/休息时间
@app.route("/api/saveTime", methods=["POST"])
def save_time():
    json_data = request.get_json()
    work = json_data.get("workMin", 25)
    br = json_data.get("breakMin", 5)
    conn = get_db_conn()
    conn.execute("UPDATE setting SET workMin=?, breakMin=? WHERE id=1", (work, br))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

if __name__ == "__main__":
    init_database()
    app.run(debug=True, host="127.0.0.1", port=3000)
