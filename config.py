# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 19:07:02 2025

@author: 33952
"""

# config.py
INITIAL_GROUPS = {
    "第一组": ["学生1", "学生2", "学生3", "学生4", "学生5"],
    "第二组": ["学生6", "学生7", "学生8", "学生9", "学生10"],
    "第三组": ["学生11", "学生12", "学生13", "学生14", "学生15"]
}

INITIAL_USERS = [
    {"nickname": name, "name": name, "role": "学生", "group": group, "password": "1234"}
    for group, members in INITIAL_GROUPS.items()
    for name in members
] + [
    {"nickname": "老师1", "name": "老师1", "role": "老师", "group": "未定义组", "password": "1234"},
    {"nickname": "管理员1", "name": "管理员1", "role": "管理员", "group": "未定义组", "password": "1234"}
]
