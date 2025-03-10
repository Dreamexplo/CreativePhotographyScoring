# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 19:15:57 2025

@author: 33952
"""

# visualization.py
import streamlit as st
from scoring import calculate_scores

# 增强版CSS注入（在main.py开头添加）
st.markdown('''
<style>
/* 强制全局字体 */
*:not(code):not(.code-font):not(.ace_editor):not(.streamlit-expanderHeader):not(.st-emotion-cache-1qg05tj) {
    font-family: 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'SimHei', sans-serif !important;
}

/* 解决部分组件字体覆盖问题 */
.stSelectbox label, .stSlider label, .stRadio label, .stTextInput label {
    font-family: 'Microsoft YaHei' !important;
}
</style>
''', unsafe_allow_html=True)

import matplotlib
matplotlib.use("agg")  # 强制使用无GUI的绘图后端

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 确认字体文件路径
font_path = "fonts/SimHei/SimHei.ttf"
if os.path.exists(font_path):
    print(f"字体文件存在：{font_path}")
else:
    print(f"字体文件不存在：{font_path}")

# 加载字体
prop = fm.FontProperties(fname=font_path)

# 设置字体
plt.rcParams["font.family"] = prop.get_name()




def plot_group_comparison(db):
    _, group_avg_scores = calculate_scores(db)
    fig, ax = plt.subplots()
    ax.bar(group_avg_scores.keys(), group_avg_scores.values())
    ax.set_title("组间比较")
    ax.set_xlabel("组别")
    ax.set_ylabel("平均成绩")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def plot_all_students(db):
    final_scores, _ = calculate_scores(db)
    names, scores = zip(*final_scores.items())
    fig, ax = plt.subplots()
    ax.bar(names, scores)
    ax.set_title("所有成员比较")
    ax.set_xlabel("学生")
    ax.set_ylabel("最终成绩")
    ax.tick_params(axis='x', rotation=90)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def plot_individual_details(db):
    scores_history = db.get_scores_history()
    all_users = db.data["users"]
    st.write(f"调试信息：当前 scores_history 记录数：{len(scores_history)}")
    if not scores_history:
        st.warning("暂无评分记录！")
        return
    for user in all_users:
        st.write(f"{user['nickname']} 的打分详情：")
        details = {}
        has_scores = False
        for entry in scores_history:
            scorer = entry["scorer"]
            score = entry["scores"].get(user["nickname"], "-")
            details[f"{scorer} ({entry['timestamp']})"] = score
            if score != "-":
                has_scores = True
        if has_scores:
            st.table(details)
        else:
            st.write("暂未收到评分")

def plot_history_trend(db):
    scores_history = db.get_scores_history()
    timestamps = [entry["timestamp"] for entry in scores_history]
    if not timestamps:
        st.write("暂无历史数据")
        return

    students = db.get_users_by_role("学生")
    fig, ax = plt.subplots()
    for student in students:
        history_scores = []
        for timestamp in timestamps:
            final_scores, _ = calculate_scores(db, timestamp)
            history_scores.append(final_scores.get(student["nickname"], 0))
        ax.plot(timestamps, history_scores, label=student["nickname"])
    ax.set_title("个人成绩历史变化趋势")
    ax.set_xlabel("时间")
    ax.set_ylabel("最终成绩")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    groups = db.get_groups()
    fig, ax = plt.subplots()
    for group in groups:
        history_scores = []
        for timestamp in timestamps:
            _, group_avg_scores = calculate_scores(db, timestamp)
            history_scores.append(group_avg_scores.get(group, 0))
        ax.plot(timestamps, history_scores, label=group)
    ax.set_title("小组成绩历史变化趋势")
    ax.set_xlabel("时间")
    ax.set_ylabel("平均成绩")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

def plot_cumulative_scores(db):
    scores_history = db.get_scores_history()
    all_users = db.data["users"]
    cumulative_scores = {}

    for user in all_users:
        total_score = 0
        for entry in scores_history:
            score = entry["scores"].get(user["nickname"], 0)
            total_score += score
        cumulative_scores[user["nickname"]] = total_score

    if not cumulative_scores:
        st.write("暂无累计分数数据")
        return

    names, scores = zip(*cumulative_scores.items())
    fig, ax = plt.subplots()
    ax.bar(names, scores)
    ax.set_title("所有成员历史累计分数")
    ax.set_xlabel("成员")
    ax.set_ylabel("累计分数")
    ax.tick_params(axis='x', rotation=90)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
