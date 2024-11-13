import sqlite3
import pandas as pd
from datetime import datetime
from config import DATABASE_PATH

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """初始化数据库"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # 创建用户表
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            fitness_goal TEXT,
            preferred_exercise TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建锻炼记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS exercise_records (
            record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            exercise_type TEXT,
            duration INTEGER,
            intensity TEXT,
            calories_burned FLOAT,
            notes TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # 创建用户设置表
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id TEXT PRIMARY KEY,
            daily_exercise_goal INTEGER,
            weekly_exercise_goal INTEGER,
            reminder_time TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_data):
    """添加新用户"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO users (
                user_id, username, password, age, 
                gender, fitness_goal, preferred_exercise
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            user_data['username'],
            user_data['password'],
            user_data['age'],
            user_data['gender'],
            user_data['fitness_goal'],
            user_data['preferred_exercise']
        ))
        
        # 初始化用户设置
        c.execute('''
            INSERT INTO user_settings (
                user_id, daily_exercise_goal, 
                weekly_exercise_goal, reminder_time
            )
            VALUES (?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            30,  # 默认每日运动30分钟
            3,   # 默认每周运动3次
            "08:00"
        ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_user(username):
    """获取用户信息"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    
    conn.close()
    return user if user else None

def get_user_by_id(user_id):
    """通过ID获取用户信息"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    
    conn.close()
    return user if user else None 
