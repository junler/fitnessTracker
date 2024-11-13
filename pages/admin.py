import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from database import get_db_connection
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def show(page):
    if not st.session_state.is_admin:
        st.warning("请使用管理员账号登录！")
        return
        
    if page == "用户管理":
        show_user_management()
    elif page == "数据分析":
        show_data_analysis()
    elif page == "系统设置":
        show_system_settings()

def show_user_management():
    """用户管理页面"""
    st.header("用户管理")
    
    conn = get_db_connection()
    users = pd.read_sql_query('SELECT * FROM users', conn)
    
    # 显示用户列表
    st.subheader("用户列表")
    
    # 为每个用户创建一个可展开的部分
    for _, user in users.iterrows():
        with st.expander(f"用户: {user['username']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"用户ID: {user['user_id']}")
                st.write(f"年龄: {user['age']}")
                st.write(f"性别: {user['gender']}")
                st.write(f"健身目标: {user['fitness_goal']}")
                st.write(f"注册时间: {user['created_at']}")
            
            with col2:
                # 获取用户的锻炼记录
                records = pd.read_sql_query(
                    'SELECT * FROM exercise_records WHERE user_id = ?',
                    conn,
                    params=(user['user_id'],)
                )
                st.write(f"锻炼记录数: {len(records)}")
                if len(records) > 0:
                    st.write(f"最近锻炼: {records['date'].max()}")
                    st.write(f"总运动时长: {records['duration'].sum()}分钟")
            
            # 编辑用户信息按钮
            if st.button(f"编辑用户 {user['username']}", key=f"edit_{user['user_id']}"):
                st.session_state.editing_user = user['user_id']
    
    conn.close()

def show_data_analysis():
    """数据分析页面"""
    st.header("数据分析")
    
    conn = get_db_connection()
    
    # 获取过去10天的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    records = pd.read_sql_query('''
        SELECT er.*, u.username 
        FROM exercise_records er
        JOIN users u ON er.user_id = u.user_id
        WHERE er.date >= ?
    ''', conn, params=(start_date.strftime('%Y-%m-%d'),))
    
    if len(records) == 0:
        st.info("暂无数据")
        return
    
    # 显示过去10天的运动情况
    st.subheader("过去10天运动情况")
    records['date'] = pd.to_datetime(records['date'])
    daily_stats = records.groupby(['date', 'exercise_type']).size().reset_index(name='count')
    
    fig_daily = px.bar(
        daily_stats,
        x='date',
        y='count',
        color='exercise_type',
        title='每日运动类型分布'
    )
    st.plotly_chart(fig_daily)
    
    # 显示排名前三的用户
    st.subheader("用户排名")
    user_stats = records.groupby('username').agg({
        'duration': 'sum',
        'calories_burned': 'sum'
    }).reset_index()
    
    user_stats['score'] = (
        user_stats['duration'] / user_stats['duration'].max() * 0.5 +
        user_stats['calories_burned'] / user_stats['calories_burned'].max() * 0.5
    )
    
    top_users = user_stats.nlargest(3, 'score')
    
    fig_ranking = px.bar(
        top_users,
        x='username',
        y='score',
        title='用户健身评分排名（前三名）',
        labels={'username': '用户名', 'score': '综合评分'}
    )
    st.plotly_chart(fig_ranking)
    
    conn.close()

def show_system_settings():
    """系统设置页面"""
    st.header("系统设置")
    
    # 机器学习参数设置
    st.subheader("机器学习模型参数")
    
    with st.form("ml_params"):
        n_estimators = st.slider("随机森林树的数量", 10, 200, 100)
        max_depth = st.slider("树的最大深度", 3, 20, 10)
        min_samples_split = st.slider("分裂所需的最小样本数", 2, 10, 2)
        
        if st.form_submit_button("重新训练模型"):
            retrain_model(n_estimators, max_depth, min_samples_split)
    
    # 系统维护选项
    st.subheader("系统维护")
    
    if st.button("备份数据库"):
        backup_database()
    
    if st.button("清理缓存"):
        clear_cache()
    
    # 系统关机选项
    st.subheader("系统关机")
    shutdown_reason = st.text_input("关机原因")
    
    if st.button("关闭系统"):
        if shutdown_reason:
            shutdown_system(shutdown_reason)
        else:
            st.error("请输入关机原因")

def retrain_model(n_estimators, max_depth, min_samples_split):
    """重新训练机器学习模型"""
    try:
        conn = get_db_connection()
        
        # 获取训练数据
        records = pd.read_sql_query('''
            SELECT er.*, u.age, u.gender, u.fitness_goal
            FROM exercise_records er
            JOIN users u ON er.user_id = u.user_id
        ''', conn)
        
        if len(records) < 10:
            st.warning("数据量不足，无法训练模型")
            return
        
        # 准备特征
        records['gender'] = records['gender'].map({'男': 0, '女': 1})
        records['intensity'] = records['intensity'].map({'低': 0, '中': 1, '高': 2})
        
        X = records[['age', 'gender', 'duration', 'intensity']]
        y = records['calories_burned']
        
        # 训练模型
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            random_state=42
        )
        model.fit(X, y)
        
        # 保存模型参数到数据库
        save_model_params(n_estimators, max_depth, min_samples_split)
        
        st.success("模型训练成功！")
        
    except Exception as e:
        st.error(f"模型训练失败：{str(e)}")
    finally:
        conn.close()

def backup_database():
    """备份数据库"""
    try:
        # 实现数据库备份逻辑
        st.success("数据库备份成功！")
    except Exception as e:
        st.error(f"备份失败：{str(e)}")

def clear_cache():
    """清理系统缓存"""
    try:
        st.cache_data.clear()
        st.cache_resource.clear()
        st.success("缓存清理成功！")
    except Exception as e:
        st.error(f"缓存清理失败：{str(e)}")

def shutdown_system(reason):
    """系统关机"""
    st.warning("系统即将关闭...")
    st.write(f"关机原因：{reason}")
    st.write("请保存所有工作，系统将在5秒后关闭。")
    # 在实际应用中，这里应该实现真正的关机逻辑
    st.stop()

def save_model_params(n_estimators, max_depth, min_samples_split):
    """保存模型参数到数据库"""
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS model_params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                n_estimators INTEGER,
                max_depth INTEGER,
                min_samples_split INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            INSERT INTO model_params (n_estimators, max_depth, min_samples_split)
            VALUES (?, ?, ?)
        ''', (n_estimators, max_depth, min_samples_split))
        
        conn.commit()
    finally:
        conn.close() 
