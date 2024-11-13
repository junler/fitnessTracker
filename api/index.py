from app import main
import streamlit as st

# Vercel 需要一个 WSGI 应用
def app(environ, start_response):
    # 设置响应头
    headers = [
        ('Content-Type', 'text/html; charset=utf-8'),
    ]
    start_response('200 OK', headers)
    
    # 运行 Streamlit 应用
    main()
    
    # 返回响应
    return [b'']

# 为了本地开发
if __name__ == "__main__":
    main()
