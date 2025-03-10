# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 19:15:23 2025

@author: 33952
"""

# scoring.py
from database import Database

def calculate_scores(db, timestamp=None):
    scores_history = db.get_scores_history()
    students = db.get_users_by_role("学生")
    groups = db.get_groups()

    if timestamp:
        scores = next((entry["scores"] for entry in scores_history if entry["timestamp"] == timestamp), {})
    else:
        scores = {entry["scorer"]: entry["scores"] for entry in scores_history}

    teacher_scores = scores.get("老师1", {}) if timestamp else scores.get("老师1", {})
    personal_teacher_scores = {student["nickname"]: teacher_scores.get(student["nickname"], 0) * (10 / 15) for student in students}

    peer_scores = {}
    for student in students:
        peer_total = 0
        peer_count = 0
        for scorer, score_dict in scores.items():
            if scorer != student["nickname"] and scorer != "老师1" and db.get_user(scorer)["group"] != student["group"]:
                peer_total += score_dict.get(student["nickname"], 0)
                peer_count += 1
        peer_scores[student["nickname"]] = peer_total / peer_count if peer_count > 0 else 0

    personal_scores = {
        student["nickname"]: personal_teacher_scores.get(student["nickname"], 0) * 0.5 + peer_scores.get(student["nickname"], 0) * 0.5
        for student in students
    }

    group_avg_scores = {}
    for group in groups:
        group_students = db.get_users_by_group(group)
        group_total = sum(personal_scores.get(student["nickname"], 0) for student in group_students)
        group_avg_scores[group] = group_total / len(group_students) if group_students else 0

    final_scores = {
        student["nickname"]: personal_scores[student["nickname"]] * 0.5 + group_avg_scores[student["group"]] * 0.5
        for student in students
    }

    sorted_scores = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    normalized_scores = {}
    for i, (name, score) in enumerate(sorted_scores):
        rank_score = 10 - min(i // 2, 7)
        normalized_scores[name] = rank_score

    return normalized_scores, group_avg_scores