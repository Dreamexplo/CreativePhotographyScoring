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

db = Database()

# 初始化数据库
if not db.data["users"]:
    for user in INITIAL_USERS:
        db.add_user(user)

# 登录状态
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "register_success" not in st.session_state:
    st.session_state.register_success = False

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
    nickname = st.text_input("昵称", key="login_nickname")
    password = st.text_input("密码", type="password", key="login_password")
    if st.button("登录"):
        user = db.get_user(nickname, password)
        if user:
            st.session_state.user = user
            st.success(f"登录成功！当前用户：{user['nickname']}")
        else:
            st.error("昵称或密码错误！")

    if st.button("注册", key="to_register"):
        st.session_state.page = "register"
        st.session_state.register_success = False

def register_page():
    st.title("注册")
    if not st.session_state.register_success:
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
                st.session_state.register_success = True
                st.success("注册成功！初始密码为1234")
            else:
                st.error("请填写昵称和姓名！")

    if st.session_state.register_success:
        with st.form(key="change_password_form"):
            new_password = st.text_input("新密码（可选）", type="password", key="register_new_password")
            change_password_button = st.form_submit_button(label="确认更改密码")
            if change_password_button and new_password:
                db.update_password(nickname, new_password)
                st.success("密码已更改！")
        if st.button("返回登录", key="back_to_login"):
            st.session_state.page = "login"
            st.session_state.register_success = False

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
    scores = {}
    for student in students:
        scores[student["nickname"]] = st.slider(f"给 {student['nickname']} 打分", 1, 15, 1, key=f"teacher_{student['nickname']}")
    if st.button("提交分数"):
        if all(scores.values()):
            st.write("请确认您的打分：")
            st.json(scores)
            if st.button("确认提交吗？", key="confirm_teacher"):
                db.save_scores(st.session_state.user["nickname"], scores)
                st.success(f"提交成功！评分已保存为 {st.session_state.user['nickname']} 的记录")
                st.write(f"已保存的评分数据：{scores}")
                st.write("请检查 database.json 的 scores_history 是否更新")
            elif st.button("再想想", key="rethink_teacher"):
                st.write("请返回修改分数")
        else:
            st.error("请为所有学生打分！")

def student_scoring():
    st.subheader("学生互评")
    group = st.session_state.user["group"]
    other_students = [s for s in db.get_users_by_role("学生") if s["group"] != group]
    scores = {}
    for student in other_students:
        scores[student["nickname"]] = st.slider(f"给 {student['nickname']} 打分", 1, 10, 1, key=f"student_{student['nickname']}")
    if st.button("提交分数"):
        if all(scores.values()):
            st.write("请确认您的打分：")
            st.json(scores)
            if st.button("确认提交吗？", key="confirm_student"):
                db.save_scores(st.session_state.user["nickname"], scores)
                st.success(f"提交成功！评分已保存为 {st.session_state.user['nickname']} 的记录")
                st.write(f"已保存的评分数据：{scores}")
                st.write("请检查 database.json 的 scores_history 是否更新")
            elif st.button("再想想", key="rethink_student"):
                st.write("请返回修改分数")
        else:
            st.error("请为所有其他组学生打分！")

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