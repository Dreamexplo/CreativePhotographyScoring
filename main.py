# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 19:16:25 2025

@author: 33952
"""

# main.py
import streamlit as st
from database import Database
from scoring import calculate_scores
from visualization import plot_group_comparison, plot_all_students, plot_individual_details, plot_history_trend, plot_cumulative_scores
from config import INITIAL_USERS
import matplotlib.font_manager as fm

import matplotlib
matplotlib.use("agg")  # 在导入其他模块之前设置后端
import matplotlib.pyplot as plt


# 设置字体路径
font_path = "fonts/SimHei/SimHei.ttf"
prop = fm.FontProperties(fname=font_path)

# 设置字体
plt.rcParams["font.family"] = prop.get_name()

db = Database()

# 初始化数据库
if not db.data["users"]:
    for user in INITIAL_USERS:
        db.add_user(user)

# 会话状态
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# 主页面逻辑
def main():
    if st.session_state.user:
        if st.session_state.user["role"] == "管理员" and st.sidebar.text_input("后台密码", type="password", key="admin_password") == "OK":
            admin_page()
        elif st.session_state.user["role"] in ["老师", "学生"]:
            user_page()
        else:
            st.write("请以管理员身份登录后台！")
    else:
        if st.session_state.page == "login":
            login_page()
        elif st.session_state.page == "register":
            register_page()

def login_page():
    st.title("登录")
    with st.form(key="login_form"):
        nickname = st.text_input("昵称", key="login_nickname")
        password = st.text_input("密码", type="password", key="login_password")
        submit_button = st.form_submit_button(label="登录")
        if submit_button:
            user = db.get_user(nickname, password)
            if user:
                st.session_state.user = user
                st.success(f"登录成功！当前用户：{user['nickname']}")
            else:
                st.error("昵称或密码错误！")
    
    if st.button("前往注册", key="to_register"):
        st.session_state.page = "register"

def register_page():
    st.title("注册")
    with st.form(key="register_form"):
        nickname = st.text_input("昵称", key="register_nickname")
        name = st.text_input("姓名", key="register_name")
        role = st.selectbox("身份", ["学生", "老师", "管理员"], key="register_role")
        group_options = db.get_groups() + ["未定义组"] if role != "学生" else db.get_groups()
        group = st.selectbox("组别", group_options, key="register_group")
        submit_button = st.form_submit_button(label="提交注册")
        if submit_button:
            if nickname and name:
                user = {"nickname": nickname, "name": name, "role": role, "group": group, "password": "1234"}
                db.add_user(user)
                st.success("注册成功！初始密码为1234")
                st.session_state.page = "login"  # 直接返回登录页面
            else:
                st.error("请填写昵称和姓名！")

def user_page():
    st.title(f"欢迎，{st.session_state.user['nickname']}")
    
    if st.session_state.user["role"] == "老师":
        teacher_scoring()
    elif st.session_state.user["role"] == "学生":
        student_scoring()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("查看当前结果"):
            st.subheader("组间比较")
            plot_group_comparison(db)
            st.subheader("所有成员比较")
            plot_all_students(db)
    with col2:
        if st.button("查看历史变化"):
            st.subheader("历史变化趋势")
            plot_history_trend(db)

    if st.button("更改密码"):
        new_password = st.text_input("请输入新密码", type="password", key="user_new_password")
        if st.button("确认更改密码"):
            db.update_password(st.session_state.user["nickname"], new_password)
            st.success("密码已更改！")

def teacher_scoring():
    st.subheader("老师打分")
    students = db.get_users_by_role("学生")
    with st.form(key="teacher_form"):
        scores = {student["nickname"]: st.slider(f"给 {student['nickname']} 打分", 1, 15, 1, key=f"teacher_{student['nickname']}") for student in students}
        submit_button = st.form_submit_button(label="提交分数")
        if submit_button and all(scores.values()):
            st.write("请确认您的打分：")
            st.json(scores)
            if st.button("确认提交吗？", key="confirm_teacher"):
                db.save_scores(st.session_state.user["nickname"], scores)
                st.success(f"提交成功！评分已保存为 {st.session_state.user['nickname']} 的记录")

def student_scoring():
    st.subheader("学生互评")
    group = st.session_state.user["group"]
    other_students = [s for s in db.get_users_by_role("学生") if s["group"] != group]
    with st.form(key="student_form"):
        scores = {student["nickname"]: st.slider(f"给 {student['nickname']} 打分", 1, 10, 1, key=f"student_{student['nickname']}") for student in other_students}
        submit_button = st.form_submit_button(label="提交分数")
        if submit_button and all(scores.values()):
            st.write("请确认您的打分：")
            st.json(scores)
            if st.button("确认提交吗？", key="confirm_student"):
                db.save_scores(st.session_state.user["nickname"], scores)
                st.success(f"提交成功！评分已保存为 {st.session_state.user['nickname']} 的记录")

def admin_page():
    st.title("管理员后台")
    option = st.sidebar.selectbox("功能", ["重置密码", "编辑组别", "查看可视化", "查看打分详情", "查看历史变化", "查看累计分数"], key="admin_option")
    if option == "重置密码":
        nickname = st.text_input("要重置密码的用户昵称", key="admin_reset_nickname")
        if st.button("重置"):
            if db.reset_password(nickname):
                st.success("密码已重置为1234")
            else:
                st.error("用户不存在")
    elif option == "编辑组别":
        new_group = st.text_input("新建组别", key="admin_new_group")
        if st.button("添加组别"):
            db.add_group(new_group)
            st.success("组别已添加")
    elif option == "查看可视化":
        st.subheader("组间比较")
        plot_group_comparison(db)
        st.subheader("所有成员比较")
        plot_all_students(db)
    elif option == "查看打分详情":
        st.subheader("打分详情")
        plot_individual_details(db)
    elif option == "查看历史变化":
        st.subheader("历史变化趋势")
        plot_history_trend(db)
    elif option == "查看累计分数":
        st.subheader("历史累计分数")
        plot_cumulative_scores(db)

if __name__ == "__main__":
    main()
