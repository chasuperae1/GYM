#!/usr/bin/env python3
"""肌肥大健身数据数据库初始化脚本"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fitness.db")


def init_database():
    if os.path.exists(DB_PATH):
        print(f"数据库已存在: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript(
        """
        -- 动作库：记录所有训练动作
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,                 -- 动作名，如「杠铃卧推」
            category TEXT NOT NULL,             -- 主要肌群：胸/背/腿/肩/臂/核心
            equipment TEXT,                     -- 器械：杠铃/哑铃/器械/自由
            target_muscles TEXT,                -- 目标肌群详细
            notes TEXT,                         -- 备注
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        -- 训练日：一次完整训练
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_date TEXT NOT NULL,         -- 训练日期 YYYY-MM-DD
            split TEXT,                         -- 训练划分：推/拉/腿/全身/上半身/下半身
            duration_min INTEGER,               -- 训练时长（分钟）
            overall_rpe REAL,                   -- 整体 RPE 主观感受
            mood TEXT,                          -- 当天状态/心情
            notes TEXT,                         -- 训练备注
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        -- 单组记录：每个动作的每一组
        CREATE TABLE IF NOT EXISTS sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            set_number INTEGER NOT NULL,        -- 第几组
            weight_kg REAL NOT NULL,            -- 重量（kg）
            reps INTEGER NOT NULL,              -- 次数
            rpe REAL,                           -- RPE 1-10
            to_failure INTEGER DEFAULT 0,       -- 是否力竭 0/1
            notes TEXT,                         -- 该组感受
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES exercises(id)
        );

        -- 身体数据：体重与围度
        CREATE TABLE IF NOT EXISTS body_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            measure_date TEXT NOT NULL,
            weight_kg REAL,                     -- 体重
            body_fat REAL,                      -- 体脂率（可选）
            chest_cm REAL,                      -- 胸围
            waist_cm REAL,                      -- 腰围
            arm_cm REAL,                        -- 臂围
            thigh_cm REAL,                      -- 腿围
            calf_cm REAL,                       -- 小腿围
            neck_cm REAL,                       -- 颈围
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        -- 训练周期计划
        CREATE TABLE IF NOT EXISTS training_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cycle_name TEXT NOT NULL,           -- 计划名称，如「8周肌肥大周期」
            start_date TEXT,
            end_date TEXT,
            target TEXT,                        -- 目标：增肌/减脂/力量
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE INDEX IF NOT EXISTS idx_sets_workout  ON sets(workout_id);
        CREATE INDEX IF NOT EXISTS idx_sets_exercise ON sets(exercise_id);
        CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(workout_date);
        CREATE INDEX IF NOT EXISTS idx_measure_date  ON body_measurements(measure_date);
        """
    )

    # 预置常用动作
    seed_exercises = [
        ("杠铃卧推",        "胸", "杠铃", "胸大肌、三角肌前束、肱三头肌"),
        ("哑铃卧推",        "胸", "哑铃", "胸大肌、三角肌前束"),
        ("上斜哑铃卧推",    "胸", "哑铃", "上胸、三角肌前束"),
        ("绳索夹胸",        "胸", "器械", "胸大肌中缝"),
        ("双杠臂屈伸",      "胸", "自由", "下胸、肱三头肌"),

        ("引体向上",        "背", "自由", "背阔肌、肱二头肌"),
        ("高位下拉",        "背", "器械", "背阔肌、大圆肌"),
        ("杠铃划船",        "背", "杠铃", "背阔肌、菱形肌、二头"),
        ("坐姿划船",        "背", "器械", "中背、斜方肌中下部"),
        ("单臂哑铃划船",    "背", "哑铃", "单侧背阔肌"),
        ("硬拉",            "背", "杠铃", "后链肌群、核心"),

        ("杠铃深蹲",        "腿", "杠铃", "股四头肌、臀大肌"),
        ("哈克深蹲",        "腿", "器械", "股四头肌"),
        ("腿举",            "腿", "器械", "股四头肌、臀大肌"),
        ("罗马尼亚硬拉",    "腿", "杠铃", "腘绳肌、臀大肌"),
        ("腿弯举",          "腿", "器械", "腘绳肌"),
        ("腿屈伸",          "腿", "器械", "股四头肌"),
        ("站姿提踵",        "腿", "自由", "小腿"),
        ("坐姿提踵",        "腿", "器械", "比目鱼肌"),

        ("坐姿推举",        "肩", "器械", "三角肌前/中束"),
        ("哑铃推举",        "肩", "哑铃", "三角肌"),
        ("哑铃侧平举",      "肩", "哑铃", "三角肌中束"),
        ("哑铃前平举",      "肩", "哑铃", "三角肌前束"),
        ("绳索面拉",        "肩", "器械", "三角肌后束、上背"),
        ("反向飞鸟",        "肩", "器械", "三角肌后束"),

        ("杠铃弯举",        "臂", "杠铃", "肱二头肌"),
        ("哑铃弯举",        "臂", "哑铃", "肱二头肌"),
        ("牧师凳弯举",      "臂", "器械", "肱二头肌短头"),
        ("窄距卧推",        "臂", "杠铃", "肱三头肌"),
        ("绳索下压",        "臂", "器械", "肱三头肌外侧头"),
        ("仰卧臂屈伸",      "臂", "杠铃", "肱三头肌长头"),

        ("平板支撑",        "核心", "自由", "核心肌群"),
        ("卷腹",            "核心", "自由", "腹直肌"),
        ("悬垂举腿",        "核心", "自由", "腹直肌下部、髋屈肌"),
    ]

    cursor.executemany(
        "INSERT INTO exercises (name, category, equipment, target_muscles) VALUES (?, ?, ?, ?)",
        seed_exercises,
    )

    conn.commit()
    conn.close()
    print(f"✅ 数据库创建成功: {DB_PATH}")
    print(f"   预置动作: {len(seed_exercises)} 个")


if __name__ == "__main__":
    init_database()
