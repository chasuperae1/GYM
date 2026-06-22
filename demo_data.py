#!/usr/bin/env python3
"""示例：如何使用数据库录入一次训练，并查询进度"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from init_db import init_database
from fitness_tool import (
    add_workout, add_set, add_measurement,
    print_workout, print_progress, list_exercises,
    get_volume_by_day,
)

init_database()

# ---------- 1. 录入一次「推日」训练 ----------
wid = add_workout(
    workout_date="2026-06-20",
    split="推日",
    duration_min=75,
    overall_rpe=7.5,
    mood="状态不错，睡眠充足",
    notes="第 4 周 第 2 次",
)
# 卧推 4 组
for idx, (w, r, rpe) in enumerate([(60, 10, 7), (65, 8, 7.5), (70, 6, 8.5), (65, 8, 9)], 1):
    add_set(wid, "杠铃卧推", idx, w, r, rpe=rpe)
# 上斜哑铃卧推 3 组
for idx, (w, r) in enumerate([(22, 12), (24, 10), (24, 10)], 1):
    add_set(wid, "上斜哑铃卧推", idx, w, r, rpe=8)
# 绳索夹胸 3 组
for idx, (w, r) in enumerate([(25, 15), (25, 15), (22, 12)], 1):
    add_set(wid, "绳索夹胸", idx, w, r)
# 坐姿推举 3 组
for idx, (w, r) in enumerate([(40, 10), (45, 8), (45, 8)], 1):
    add_set(wid, "坐姿推举", idx, w, r, rpe=8)
# 侧平举 3 组
for idx, (w, r) in enumerate([(8, 15), (8, 15), (8, 12)], 1):
    add_set(wid, "哑铃侧平举", idx, w, r)
# 绳索下压 3 组
for idx, (w, r) in enumerate([(30, 12), (32, 10), (32, 10)], 1):
    add_set(wid, "绳索下压", idx, w, r)

print("=" * 60)
print_workout(wid)

# ---------- 2. 再录一次「拉日」，前几天的 ----------
wid2 = add_workout(workout_date="2026-06-18", split="拉日", duration_min=80,
                   overall_rpe=8, mood="感觉背部发力比上周好")
for idx, (w, r, rpe) in enumerate([(60, 8, 7), (65, 6, 7.5), (70, 5, 8.5)], 1):
    add_set(wid2, "杠铃划船", idx, w, r, rpe=rpe)
for idx, (w, r) in enumerate([(55, 10), (55, 10), (52, 8)], 1):
    add_set(wid2, "高位下拉", idx, w, r)
for idx, (w, r, rpe) in enumerate([(80, 8, 9)], 1):
    add_set(wid2, "硬拉", idx, w, r, rpe=rpe, to_failure=1)

print("\n" + "=" * 60)
print_workout(wid2)

# ---------- 3. 录入身体测量 ----------
add_measurement("2026-06-20", weight_kg=72.5, body_fat=16.2,
                chest_cm=102, waist_cm=78, arm_cm=36, thigh_cm=58,
                calf_cm=38, neck_cm=39, notes="晨起空腹测量")
add_measurement("2026-06-13", weight_kg=72.1, body_fat=16.5,
                chest_cm=101.5, waist_cm=78.2, arm_cm=35.8, thigh_cm=57.8,
                calf_cm=38)

# ---------- 4. 查询进步与统计 ----------
print("\n" + "=" * 60)
print_progress("杠铃卧推", limit=5)

print("\n" + "=" * 60)
print("📊 最近 30 天训练容量统计")
rows = get_volume_by_day(30)
if rows:
    print(f"   {'日期':<12} {'组数':>6} {'总容量':>12}")
    for r in rows:
        print(f"   {r['workout_date']:<12} {r['total_sets']:>6} {(r['total_volume'] or 0):>10.0f} kg")
else:
    print("   暂无数据")

print("\n" + "=" * 60)
print("📚 动作库（胸/背/腿/肩/臂/核心）")
for e in list_exercises()[:6]:
    print(f"   [{e['id']:>2}] ({e['category']}) {e['name']}")
print("   ... 完整列表见 fitness_tool.py exercises")

print("\n✅ 示例数据已录入。数据库文件位于: fitness.db")
