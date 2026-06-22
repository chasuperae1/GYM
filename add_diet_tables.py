#!/usr/bin/env python3
"""添加饮食记录相关的数据表"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "fitness.db")


def add_diet_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript(
        """
        -- 食物库：记录常见食物的营养成分
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,             -- 食物名称
            category TEXT,                  -- 类别：主食/蛋白质/蔬菜/水果/油脂/零食
            carbs_g REAL,                   -- 碳水化合物(g)
            protein_g REAL,                 -- 蛋白质(g)
            fat_g REAL,                     -- 脂肪(g)
            calories REAL,                  -- 卡路里(kcal)
            serving_size_g REAL,            -- 标准份量(g)
            notes TEXT,                     -- 备注
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        -- 饮食记录：每餐吃了什么
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_time TEXT NOT NULL,        -- 时间戳 YYYY-MM-DD HH:MM
            meal_type TEXT,                 -- 餐次：早餐/午餐/晚餐/宵夜
            notes TEXT,                     -- 备注（如照片描述）
            photo_ref TEXT,                 -- 照片引用
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        -- 餐食明细：每餐包含的食物
        CREATE TABLE IF NOT EXISTS meal_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_id INTEGER NOT NULL,
            food_id INTEGER NOT NULL,
            quantity_g REAL NOT NULL,       -- 食用量(g)
            notes TEXT,                     -- 备注
            FOREIGN KEY (meal_id) REFERENCES meals(id) ON DELETE CASCADE,
            FOREIGN KEY (food_id) REFERENCES foods(id)
        );

        CREATE INDEX IF NOT EXISTS idx_meals_time ON meals(meal_time);
        CREATE INDEX IF NOT EXISTS idx_meal_items_meal ON meal_items(meal_id);
        CREATE INDEX IF NOT EXISTS idx_meal_items_food ON meal_items(food_id);
        """
    )

    # 预置常见食物数据
    seed_foods = [
        # 主食类
        ("白米饭", "主食", 28, 2.7, 0.3, 130, 100, "熟米饭"),
        ("糙米饭", "主食", 23, 2.6, 1.1, 111, 100, "熟糙米饭"),
        ("燕麦", "主食", 66, 17, 7, 389, 100, "干燕麦片"),
        ("全麦面包", "主食", 47, 10, 3, 260, 100, ""),
        ("面条", "主食", 25, 7, 1, 130, 100, "煮熟"),
        ("红薯", "主食", 20, 1.6, 0.2, 86, 100, "蒸熟"),
        ("玉米", "主食", 22, 3.4, 1.2, 106, 100, "煮熟"),
        ("土豆", "主食", 17, 2.7, 0.1, 77, 100, "煮熟"),

        # 蛋白质类
        ("鸡胸肉", "蛋白质", 1, 24, 3.6, 130, 100, "煮熟"),
        ("瘦牛肉", "蛋白质", 0, 26, 5, 150, 100, "煮熟"),
        ("鱼肉", "蛋白质", 0, 22, 2, 116, 100, "煮熟"),
        ("虾", "蛋白质", 0, 23, 0.8, 100, 100, "煮熟"),
        ("鸡蛋", "蛋白质", 1.1, 6.3, 5, 78, 50, "一个中等大小"),
        ("豆腐", "蛋白质", 2, 8, 4.8, 70, 100, "嫩豆腐"),
        ("希腊酸奶", "蛋白质", 6, 10, 0.5, 59, 100, "无糖"),
        ("蛋白粉", "蛋白质", 3, 80, 3, 370, 30, "一勺约30g"),

        # 蔬菜类
        ("西兰花", "蔬菜", 7, 3.6, 0.4, 34, 100, ""),
        ("菠菜", "蔬菜", 4, 2.9, 0.4, 23, 100, ""),
        ("黄瓜", "蔬菜", 2, 0.8, 0.1, 15, 100, ""),
        ("番茄", "蔬菜", 4, 1.2, 0.2, 18, 100, ""),
        ("生菜", "蔬菜", 2, 1.4, 0.2, 16, 100, ""),
        ("芦笋", "蔬菜", 5, 2.2, 0.2, 27, 100, ""),
        ("蘑菇", "蔬菜", 4, 2.5, 0.3, 22, 100, ""),

        # 水果类
        ("苹果", "水果", 14, 0.3, 0.2, 52, 100, ""),
        ("香蕉", "水果", 22, 1.1, 0.3, 91, 100, ""),
        ("蓝莓", "水果", 12, 0.7, 0.3, 57, 100, ""),
        ("橙子", "水果", 9, 1.2, 0.2, 47, 100, ""),
        ("葡萄", "水果", 18, 0.7, 0.2, 69, 100, ""),

        # 油脂类
        ("橄榄油", "油脂", 0, 0, 100, 900, 10, "10g约1小勺"),
        ("牛油果", "油脂", 9, 2, 15, 160, 100, ""),
        ("坚果", "油脂", 16, 15, 49, 575, 30, "一小把"),
        ("花生酱", "油脂", 22, 25, 50, 600, 20, "一勺"),

        # 零食类
        ("巧克力", "零食", 47, 7.5, 30, 539, 100, "黑巧克力"),
        ("薯片", "零食", 53, 7, 35, 536, 100, ""),
        ("饼干", "零食", 70, 7, 17, 473, 100, ""),
    ]

    cursor.execute("SELECT COUNT(*) FROM foods")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.executemany(
            "INSERT INTO foods (name, category, carbs_g, protein_g, fat_g, calories, serving_size_g, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            seed_foods,
        )
        print(f"   预置食物: {len(seed_foods)} 种")

    conn.commit()
    conn.close()
    print("✅ 饮食数据表添加完成")


def get_meal_type(hour):
    """根据时间判断餐次"""
    if 6 <= hour < 10:
        return "早餐"
    elif 10 <= hour < 14:
        return "午餐"
    elif 14 <= hour < 18:
        return "下午茶"
    elif 18 <= hour < 22:
        return "晚餐"
    else:
        return "宵夜"


if __name__ == "__main__":
    add_diet_tables()
