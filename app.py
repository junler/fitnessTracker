import streamlit as st
from database import init_database
import pages.auth as auth
import pages.user as user
import pages.admin as admin

def main():
    # 初始化数据库
    init_database()
    
    # 设置页面配置
    st.set_page_config(
        page_title="健身追踪系统",
        page_icon="🏃‍♂️",
        layout="wide"
    )
    
    # 初始化会话状态
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "锻炼推荐"
    
    # 自定义CSS样式
    st.markdown("""
        <style>
            /* 隐藏默认元素 */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* 未登录时隐藏侧边栏 */
            section[data-testid="stSidebar"] {
                display: none !important;
            }
            
            /* 侧边栏样式 */
            .css-1d391kg {
                padding: 0;
            }
            
            /* 侧边栏标题样式 */
            .sidebar-title {
                text-align: center;
                color: white;
                background-color: #262730;
                padding: 1rem;
                margin: 0;
            }
            
            /* 用户信息样式 */
            .user-info {
                padding: 1rem;
                background-color: #f8f9fa;
                border-bottom: 1px solid #e0e2e6;
            }
            
            /* 导航菜单样式 */
            .nav-menu {
                padding: 0.5rem 0;
            }
            
            .nav-item {
                padding: 0.8rem 1rem;
                text-decoration: none;
                color: #262730;
                display: block;
                border-left: 4px solid transparent;
                transition: all 0.2s;
                cursor: pointer;
            }
            
            .nav-item:hover {
                background-color: #f0f2f6;
                border-left-color: #1f77b4;
            }
            
            .nav-item.active {
                background-color: #e6e9ef;
                border-left-color: #1f77b4;
                font-weight: bold;
            }
            
            /* 退出按钮样式 */
            .logout-button {
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 1rem;
                background-color: #f8f9fa;
                border-top: 1px solid #e0e2e6;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # 登录后显示侧边栏的样式
    if st.session_state.logged_in:
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] {
                    display: flex !important;
                }
            </style>
        """, unsafe_allow_html=True)
    
    # 只在登录后显示侧边栏导航
    if st.session_state.logged_in:
        with st.sidebar:
            # 系统标题
            st.markdown('<h1 class="sidebar-title">健身追踪系统</h1>', unsafe_allow_html=True)
            
            # 用户信息
            st.markdown(
                f'<div class="user-info">👤 {st.session_state.username}</div>',
                unsafe_allow_html=True
            )
            
            # 导航菜单
            st.markdown('<div class="nav-menu">', unsafe_allow_html=True)
            
            if st.session_state.is_admin:
                menu_items = ["用户管理", "数据分析", "系统设置"]
            else:
                menu_items = ["个人资料", "锻炼记录", "锻炼推荐", "数据统计"]
            
            for item in menu_items:
                is_active = st.session_state.current_page == item
                if st.button(
                    item,
                    key=f"nav_{item}",
                    use_container_width=True,
                    type="secondary" if not is_active else "primary"
                ):
                    st.session_state.current_page = item
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 退出按钮
            st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
            if st.button("退出系统", key="logout_button", type="secondary", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.rerun()
    else:
        page = "登录/注册"
    
    # 页面路由
    if not st.session_state.logged_in:
        auth.show()
    elif st.session_state.is_admin:
        admin.show(st.session_state.current_page)
    else:
        user.show(st.session_state.current_page)

if __name__ == "__main__":
    main() 
