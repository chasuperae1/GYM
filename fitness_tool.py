#!/usr/bin/env python3
"""健身数据录入与查询工具"""
import sqlite3
import os
from datetime import datetime, date
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(__file__), "fitness.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ---------------- 录入功能 ----------------

def add_workout(workout_date, split=None, duration_min=None,
                overall_rpe=None, mood=None, notes=None):
    """新增一个训练日，返回 workout_id"""
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO workouts (workout_date, split, duration_min, overall_rpe, mood, notes) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (workout_date, split, duration_min, overall_rpe, mood, notes),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def add_set(workout_id, exercise_name, set_number, weight_kg, reps,
            rpe=None, to_failure=0, notes=None):
    """为某次训练添加一组记录；通过动作名自动查找 exercise_id"""
    conn = _connect()
    cur = conn.cursor()
    row = cur.execute("SELECT id FROM exercises WHERE name = ?", (exercise_name,)).fetchone()
    if not row:
        cur.execute("INSERT INTO exercises (name, category, notes) VALUES (?, '自定义', '手动添加')",
                    (exercise_name,))
        exercise_id = cur.lastrowid
    else:
        exercise_id = row["id"]
    cur.execute(
        "INSERT INTO sets (workout_id, exercise_id, set_number, weight_kg, reps, rpe, to_failure, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (workout_id, exercise_id, set_number, weight_kg, reps, rpe, to_failure, notes),
    )
    conn.commit()
    conn.close()


def add_measurement(measure_date, weight_kg=None, body_fat=None,
                    chest_cm=None, waist_cm=None, arm_cm=None,
                    thigh_cm=None, calf_cm=None, neck_cm=None, notes=None):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO body_measurements "
        "(measure_date, weight_kg, body_fat, chest_cm, waist_cm, arm_cm, thigh_cm, calf_cm, neck_cm, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (measure_date, weight_kg, body_fat, chest_cm, waist_cm,
         arm_cm, thigh_cm, calf_cm, neck_cm, notes),
    )
    conn.commit()
    conn.close()


# ---------------- 查询功能 ----------------

def list_exercises(category=None):
    """列出动作库"""
    conn = _connect()
    cur = conn.cursor()
    if category:
        rows = cur.execute(
            "SELECT id, name, category, equipment FROM exercises WHERE category = ? ORDER BY id",
            (category,),
        ).fetchall()
    else:
        rows = cur.execute(
            "SELECT id, name, category, equipment FROM exercises ORDER BY category, id"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_workout(workout_id):
    """获取某次训练的完整记录（包含所有组）"""
    conn = _connect()
    cur = conn.cursor()
    workout = cur.execute("SELECT * FROM workouts WHERE id = ?", (workout_id,)).fetchone()
    sets = cur.execute(
        "SELECT s.set_number, s.weight_kg, s.reps, s.rpe, s.to_failure, e.name AS exercise, e.category "
        "FROM sets s JOIN exercises e ON s.exercise_id = e.id "
        "WHERE s.workout_id = ? ORDER BY e.id, s.set_number",
        (workout_id,),
    ).fetchall()
    conn.close()
    return dict(workout), [dict(s) for s in sets]


def get_progress(exercise_name, limit=10):
    """追踪某个动作的历史进步（按日期看最大重量/总容量）"""
    conn = _connect()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT w.workout_date,
               MAX(s.weight_kg)         AS top_weight,
               MAX(s.reps)              AS top_reps,
               SUM(s.weight_kg * s.reps) AS total_volume
        FROM sets s
        JOIN exercises e ON s.exercise_id = e.id
        JOIN workouts  w ON w.id = s.workout_id
        WHERE e.name = ?
        GROUP BY w.workout_date
        ORDER BY w.workout_date DESC
        LIMIT ?
        """,
        (exercise_name, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_volume_by_day(days=30):
    """最近 N 天每天的训练总容量（重量*次数）"""
    conn = _connect()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT w.workout_date,
               COUNT(DISTINCT w.id) AS workouts,
               SUM(s.weight_kg * s.reps) AS total_volume,
               COUNT(s.id) AS total_sets
        FROM workouts w
        LEFT JOIN sets s ON s.workout_id = w.id
        WHERE w.workout_date >= date('now', ?)
        GROUP BY w.workout_date
        ORDER BY w.workout_date DESC
        """,
        (f"-{days} days",),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_measurement_trend(days=90):
    conn = _connect()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT * FROM body_measurements "
        "WHERE measure_date >= date('now', ?) "
        "ORDER BY measure_date DESC",
        (f"-{days} days",),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- 打印工具 ----------------

def print_workout(workout_id):
    w, sets = get_workout(workout_id)
    print(f"\n📅 {w['workout_date']} | {w['split'] or '未分类'} | 时长 {w['duration_min'] or '--'} 分钟")
    if w["mood"] or w["notes"]:
        print(f"   状态: {w['mood'] or ''} | 备注: {w['notes'] or ''}")

    grouped = defaultdict(list)
    for s in sets:
        grouped[s["exercise"]].append(s)

    total_volume = 0
    for ex, ss in grouped.items():
        line = f"   🏋️ {ex}:"
        for s in ss:
            line += f"  {s['weight_kg']}kg × {s['reps']}"
            if s["rpe"]:
                line += f" (RPE {s['rpe']})"
            if s["to_failure"]:
                line += " 💀"
            total_volume += s["weight_kg"] * s["reps"]
        print(line)
    print(f"   总容量: {total_volume:.0f} kg")


def print_progress(exercise_name, limit=8):
    rows = get_progress(exercise_name, limit)
    if not rows:
        print(f"⚠️ 还没有「{exercise_name}」的训练记录")
        return
    print(f"\n📈 {exercise_name} 最近进步")
    print(f"   {'日期':<12} {'最大重量':>10} {'最高次数':>10} {'总容量':>12}")
    for r in rows:
        print(f"   {r['workout_date']:<12} {r['top_weight']:>10.1f}kg {r['top_reps']:>10} {r['total_volume']:>10.0f}kg")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "exercises":
        for e in list_exercises():
            print(f"  [{e['id']:>2}] ({e['category']}) {e['name']} - {e['equipment']}")
    else:
        print("用法:")
        print("  python fitness_tool.py exercises   # 列出所有动作")
        print("  # 在代码中调用 add_workout / add_set 来添加训练记录")
