import sqlite3
import datetime

class DatabaseManager:
    def __init__(self, db_name="sentinel.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        """初始化数据表"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cve_id TEXT,
                category TEXT,
                component TEXT,
                summary TEXT,
                url TEXT UNIQUE,
                discovered_at TIMESTAMP
            )
        ''')
        self.conn.commit()

    def insert_intel(self, data, url):
        """插入新情报，如果 URL 已存在则忽略"""
        try:
            self.cursor.execute('''
                INSERT INTO intelligence (cve_id, category, component, summary, url, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('cve_id'),
                data.get('category'),
                data.get('affected_component'),
                data.get('summary_zh'),
                url,
                datetime.datetime.now()
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 捕获 URL 重复的错误（双重保险）
            return False

    def close(self):
        self.conn.close()
