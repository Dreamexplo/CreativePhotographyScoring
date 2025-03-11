# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 19:07:02 2025

@author: 33952
"""

# config.py
INITIAL_GROUPS = {
    "group1": ["student1", "student2", "student3", "student4", "student5"],
    "group2": ["student6", "student7", "student8", "student9", "student10"],
    "group3": ["student11", "student12", "student13", "student14", "student15"]
}

INITIAL_USERS = [
    {"nickname": name, "name": name, "role": "学生", "group": group, "password": "1234"}
    for group, members in INITIAL_GROUPS.items()
    for name in members
] + [
    {"nickname": "老师1", "name": "老师1", "role": "老师", "group": "未定义组", "password": "1234"},
    {"nickname": "管理员1", "name": "管理员1", "role": "管理员", "group": "未定义组", "password": "1234"}
]
