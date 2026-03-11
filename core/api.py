from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Sentinel OSINT API")

# 允许跨域请求（方便前端直接调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect('sentinel.db')
    conn.row_factory = sqlite3.Row  # 让查询结果像字典一样可访问
    return conn

@app.get("/api/intelligence")
def get_intelligence(limit: int = 50):
    """获取最新的威胁情报列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # 按时间倒序获取最新情报
    cursor.execute('''
        SELECT id, cve_id, category, component, summary, url, discovered_at 
        FROM intelligence 
        ORDER BY discovered_at DESC 
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # 转换为字典列表
    return [dict(row) for row in rows]

@app.get("/api/stats")
def get_stats():
    """获取简单的统计数据供大屏展示"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM intelligence")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM intelligence WHERE category = 'PoC'")
    poc_count = cursor.fetchone()[0]
    conn.close()
    return {"total_intel": total, "poc_count": poc_count}

if __name__ == "__main__":
    import uvicorn
    # 启动 API 服务，运行在 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)
