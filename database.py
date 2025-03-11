# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 19:14:57 2025

@author: 33952
"""

# database.py
import json
import os
from datetime import datetime

class Database:
    def __init__(self, db_file="database.json"):
        self.db_file = db_file
        if not os.path.exists(db_file):
            self.data = {"users": [], "scores_history": []}
            self.save()
        else:
            self.load()
            if "scores" in self.data and "scores_history" not in self.data:
                self.data["scores_history"] = [
                    {"scorer": scorer, "scores": scores, "timestamp": "未知时间"}
                    for scorer, scores in self.data["scores"].items()
                ]
                del self.data["scores"]
                self.save()

    def load(self):
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            print(f"数据库加载成功，当前 scores_history 记录数：{len(self.data['scores_history'])}")
        except Exception as e:
            print(f"加载数据库失败：{e}")
            self.data = {"users": [], "scores_history": []}

    def save(self):
        try:
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"数据库已保存至 {self.db_file}，scores_history 记录数：{len(self.data['scores_history'])}")
        except Exception as e:
            print(f"保存数据库失败：{e}")

    def add_user(self, user):
        self.data["users"].append(user)
        self.save()

    def get_user(self, nickname, password=None):
        for user in self.data["users"]:
            if user["nickname"] == nickname:
                if password is None or user["password"] == password:
                    return user
        return None

    def update_password(self, nickname, new_password):
        user = self.get_user_by_nickname(nickname)
        if user:
            user["password"] = new_password  # 更新密码
            self.save_data()  # 保存数据库
            return True
        return False


    def reset_password(self, nickname):
        return self.update_password(nickname, "1234")

    def add_group(self, group_name):
        if group_name not in self.get_groups():
            self.save()

    def get_groups(self):
        return list(set(user["group"] for user in self.data["users"] if user["role"] == "学生"))

    def get_users_by_role(self, role):
        return [user for user in self.data["users"] if role in user["role"]]

    def get_users_by_group(self, group):
        return [user for user in self.data["users"] if user["group"] == group]

    def save_scores(self, scorer, scores):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "scorer": scorer,
            "scores": scores,
            "timestamp": timestamp
        }
        self.data["scores_history"].append(entry)
        self.save()
        print(f"评分已保存：{entry}")

    def get_scores_history(self):
        return self.data["scores_history"]
