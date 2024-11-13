import streamlit as st
import sqlite3
import uuid
import time
from database import add_user, get_user
from config import FITNESS_GOALS, EXERCISE_TYPES, ADMIN_USERNAME, ADMIN_PASSWORD

def show():
    # 创建三列布局，使用中间列来居中显示内容
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <style>
                div.block-container {
                    text-align: center;
                }
                h1 {
                    text-align: center;
                }
            </style>
        """, unsafe_allow_html=True)
        st.title("欢迎使用健身追踪系统")
        
        # 初始化session state
        if 'active_tab' not in st.session_state:
            st.session_state.active_tab = 0  # 使用数字索引来控制标签页
        
        # 创建标签页
        tab1, tab2, tab3 = st.tabs(["用户登录", "用户注册", "管理员登录"])
        
        # 用户登录标签页
        with tab1:
            st.header("用户登录")
            with st.form("login_form", clear_on_submit=False):
                login_username = st.text_input("用户名")
                login_password = st.text_input("密码", type="password")
                
                if st.form_submit_button("登录", use_container_width=True):
                    user = get_user(login_username)
                    if user and user[2] == login_password:  # 检查密码
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.username = user[1]
                        st.session_state.current_page = "锻炼推荐"
                        st.success("登录成功！")
                        st.rerun()
                    else:
                        st.error("用户名或密码错误！")
        
        # 用户注册标签页
        with tab2:
            st.header("用户注册")
            
            # 注册表单
            with st.form("registration_form", clear_on_submit=True):
                username = st.text_input("用户名")
                password = st.text_input("密码", type="password")
                age = st.number_input("年龄", min_value=1, max_value=120, value=25)
                gender = st.selectbox("性别", ["男", "女"])
                fitness_goal = st.selectbox("健身目标", FITNESS_GOALS)
                preferred_exercise = st.multiselect("偏好的运动类型", EXERCISE_TYPES)
                
                if st.form_submit_button("注册", use_container_width=True):
                    if not username or not password:
                        st.error("用户名和密码不能为空！")
                        return
                    
                    # 检查用户名是否已存在
                    existing_user = get_user(username)
                    if existing_user:
                        st.error("用户名已存在！")
                        return
                    
                    # 创建新用户
                    user_data = {
                        'user_id': str(uuid.uuid4()),
                        'username': username,
                        'password': password,
                        'age': age,
                        'gender': gender,
                        'fitness_goal': fitness_goal,
                        'preferred_exercise': ','.join(preferred_exercise)
                    }
                    
                    try:
                        add_user(user_data)
                        st.success("注册成功！正在跳转到登录页面...")
                        # 设置要显示的用户名和密码
                        st.session_state.temp_username = username
                        st.session_state.temp_password = password
                        # 切换到登录标签页
                        st.session_state.active_tab = 0
                        time.sleep(1)  # 给用户一点时间看到成功消息
                        st.rerun()
                    except Exception as e:
                        st.error(f"注册失败：{str(e)}")
        
        # 管理员登录标签页
        with tab3:
            st.header("管理员登录")
            with st.form("admin_login_form", clear_on_submit=False):
                admin_username = st.text_input("管理员用户名")
                admin_password = st.text_input("管理员密码", type="password")
                
                if st.form_submit_button("管理员登录", use_container_width=True):
                    if admin_username == ADMIN_USERNAME and admin_password == ADMIN_PASSWORD:
                        st.session_state.logged_in = True
                        st.session_state.is_admin = True
                        st.session_state.current_page = "用户管理"
                        st.success("管理员登录成功！")
                        st.rerun()
                    else:
                        st.error("管理员用户名或密码错误！")
        
        # 根据active_tab切换标签页
        if st.session_state.active_tab == 0:
            tab1.active = True
            # 如果有临时保存的用户名和密码，自动填充到登录表单
            if hasattr(st.session_state, 'temp_username'):
                st.session_state.login_username = st.session_state.temp_username
                st.session_state.login_password = st.session_state.temp_password
                # 使用完后清除临时数据
                del st.session_state.temp_username
                del st.session_state.temp_password
