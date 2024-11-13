import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random
from database import get_db_connection
from config import EXERCISE_TYPES, INTENSITY_LEVELS, FOOD_CATEGORIES, INTENSITY_CALORIES

def show(page):
    if not st.session_state.logged_in:
        st.warning("请先登录！")
        return
        
    st.title("用户中心")
    
    if page == "个人资料":
        show_profile()
    elif page == "锻炼记录":
        show_exercise_form()
    elif page == "锻炼推荐":
        show_recommendations()
    elif page == "数据统计":
        show_progress()
        show_analysis()

def show_profile():
    """显示和编辑个人资料"""
    st.header("个人资料")
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE user_id = ?', 
        (st.session_state.user_id,)
    ).fetchone()
    
    with st.form("profile_form"):
        username = st.text_input("用户名", value=user['username'], disabled=True)
        age = st.number_input("年龄", value=user['age'], min_value=1, max_value=120)
        gender = st.selectbox("性别", ["男", "女"], index=0 if user['gender']=="男" else 1)
        fitness_goal = st.selectbox("健身目标", options=["减重", "增肌", "提高耐力", "增强力量", "改善灵活性", "保持健康"], index=0)
        preferred_exercises = st.multiselect("偏好的运动类型", EXERCISE_TYPES, default=user['preferred_exercise'].split(','))
        
        if st.form_submit_button("更新资料"):
            try:
                conn.execute('''
                    UPDATE users 
                    SET age=?, gender=?, fitness_goal=?, preferred_exercise=?
                    WHERE user_id=?
                ''', (age, gender, fitness_goal, ','.join(preferred_exercises), st.session_state.user_id))
                conn.commit()
                st.success("资料更新成功！")
            except Exception as e:
                st.error(f"更新失败：{str(e)}")
    
    conn.close()

def show_exercise_form():
    """添加锻炼记录表单"""
    st.header("添加锻炼记录")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        with st.form("exercise_form"):
            exercise_type = st.selectbox("运动类型", EXERCISE_TYPES)
            duration = st.number_input("运动时长(分钟)", min_value=1, value=30)
            intensity = st.select_slider("运动强度", INTENSITY_LEVELS)
            calories = st.number_input("消耗卡路里", min_value=0, value=100)
            notes = st.text_area("备注")
            date = st.date_input("日期", datetime.now())
            
            if st.form_submit_button("添加记录"):
                conn = get_db_connection()
                try:
                    conn.execute('''
                        INSERT INTO exercise_records 
                        (user_id, exercise_type, duration, intensity, calories_burned, notes, date)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        st.session_state.user_id,
                        exercise_type,
                        duration,
                        intensity,
                        calories,
                        notes,
                        date.strftime('%Y-%m-%d')
                    ))
                    conn.commit()
                    st.success("记录添加成功！")
                except Exception as e:
                    st.error(f"添加失败：{str(e)}")
                finally:
                    conn.close()
    
    with col2:
        if st.button("生成随机记录"):
            generate_random_record()

def generate_random_record():
    """生成随机锻炼记录"""
    record = {
        'exercise_type': random.choice(EXERCISE_TYPES),
        'duration': random.randint(15, 120),
        'intensity': random.choice(INTENSITY_LEVELS),
        'calories_burned': random.randint(50, 500),
        'notes': "自动生成的记录",
        'date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
    }
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO exercise_records 
            (user_id, exercise_type, duration, intensity, calories_burned, notes, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            st.session_state.user_id,
            record['exercise_type'],
            record['duration'],
            record['intensity'],
            record['calories_burned'],
            record['notes'],
            record['date']
        ))
        conn.commit()
        st.success("随机记录生成成功！")
    except Exception as e:
        st.error(f"生成失败：{str(e)}")
    finally:
        conn.close()

def show_recommendations():
    """显示锻炼和饮食推荐"""
    st.header("今日推荐")
    
    # 获取用户信息和锻炼记录
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE user_id = ?', 
        (st.session_state.user_id,)
    ).fetchone()
    
    # 获取最近7天的运动记录
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    records = pd.read_sql_query('''
        SELECT * FROM exercise_records 
        WHERE user_id = ? AND date >= ?
        ORDER BY date DESC
    ''', conn, params=(st.session_state.user_id, seven_days_ago))
    
    # 计算最近的运动强度和消耗
    total_calories = 0
    if len(records) > 0:
        for _, record in records.iterrows():
            total_calories += INTENSITY_CALORIES.get(record['intensity'], 0)
        avg_daily_calories = total_calories / 7
    else:
        avg_daily_calories = 0
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("运动建议")
        preferred_exercises = user['preferred_exercise'].split(',')
        
        # 根据最近的运动强度调整建议
        if avg_daily_calories < 300:
            intensity = "中"
            duration = "30-45"
        elif avg_daily_calories < 500:
            intensity = "中到高"
            duration = "45-60"
        else:
            intensity = "低到中"
            duration = "30"
        
        st.write(f"建议运动: {random.choice(preferred_exercises)}")
        st.write(f"建议强度: {intensity}")
        st.write(f"建议时长: {duration}分钟")
    
    with col2:
        st.subheader("饮食建议")
        
        # 获取用户的健身目标
        goal = user['fitness_goal']
        if goal not in FOOD_CATEGORIES:
            goal = "保持健康"
        
        # 根据当前时间推荐餐点
        current_hour = datetime.now().hour
        if 5 <= current_hour < 10:
            meal_type = "早餐"
        elif 10 <= current_hour < 15:
            meal_type = "午餐"
        else:
            meal_type = "晚餐"
        
        # 显示推荐的食物
        st.write(f"当前时段: {meal_type}")
        recommended_food = random.choice(FOOD_CATEGORIES[goal][meal_type])
        
        # 使用卡片样式显示推荐食物
        st.markdown(
            f"""
            <div style="
                padding: 20px;
                border-radius: 10px;
                background-color: #f0f2f6;
                margin: 10px 0;
            ">
                <h4 style="margin: 0;">推荐食谱</h4>
                <p style="font-size: 1.2em; margin: 10px 0;">{recommended_food}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # 添加刷新按钮
        if st.button("换一个推荐"):
            st.rerun()
    
    # 显示营养建议
    st.subheader("营养建议")
    if goal == "增肌":
        st.info("🥩 注意补充优质蛋白，每天蛋白质摄入建议达到体重(kg)×2克")
    elif goal == "减重":
        st.info("🥗 控制碳水化合物摄入，增加蔬菜摄入，保证适量蛋白质")
    else:
        st.info("🥜 均衡饮食，适量多样，注意营养搭配")
    
    conn.close()

def show_progress():
    """显示进度追踪"""
    st.header("进度追踪")
    
    conn = get_db_connection()
    records = pd.read_sql_query('''
        SELECT * FROM exercise_records 
        WHERE user_id = ? 
        ORDER BY date DESC
    ''', conn, params=(st.session_state.user_id,))
    
    if len(records) == 0:
        st.info("还没有锻炼记录，开始添加吧！")
        return
    
    # 显示最近的运动记录
    st.subheader("最近的运动记录")
    st.dataframe(
        records[['date', 'exercise_type', 'duration', 'intensity', 'calories_burned']]
        .head(5)
    )
    
    # 绘制运动时长趋势图
    fig_duration = px.line(
        records, 
        x='date', 
        y='duration',
        title='运动时长趋势'
    )
    st.plotly_chart(fig_duration)
    
    # 绘制运动类型分布
    fig_types = px.pie(
        records, 
        names='exercise_type',
        title='运动类型分布'
    )
    st.plotly_chart(fig_types)
    
    conn.close()

def show_analysis():
    """显示数据分析"""
    st.header("数据分析")
    
    conn = get_db_connection()
    records = pd.read_sql_query('''
        SELECT * FROM exercise_records 
        WHERE user_id = ? 
        ORDER BY date DESC
    ''', conn, params=(st.session_state.user_id,))
    
    if len(records) == 0:
        st.info("还没有足够的数据进行分析，请先添加一些锻炼记录！")
        return
    
    # 计算统计数据
    total_workouts = len(records)
    total_duration = records['duration'].sum()
    total_calories = records['calories_burned'].sum()
    avg_duration = records['duration'].mean()
    
    # 显示统计数据
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总运动次数", total_workouts)
    col2.metric("总运动时长(分钟)", int(total_duration))
    col3.metric("总消耗卡路里", int(total_calories))
    col4.metric("平均每次时长", f"{int(avg_duration)}分钟")
    
    # 按周分析
    records['date'] = pd.to_datetime(records['date'])
    records['week'] = records['date'].dt.isocalendar().week
    weekly_stats = records.groupby('week').agg({
        'duration': 'sum',
        'calories_burned': 'sum'
    }).reset_index()
    
    # 绘制每周运动时长趋势
    fig_weekly = px.bar(
        weekly_stats,
        x='week',
        y='duration',
        title='每周运动时长统计'
    )
    st.plotly_chart(fig_weekly)
    
    conn.close() 
