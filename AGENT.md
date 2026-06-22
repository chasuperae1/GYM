# 健身追踪 Agent 使用指南

## 📋 项目概述

这是一个基于 TRAE 的健身数据追踪 Agent，用于记录训练和饮食数据，自动同步到 GitHub 进行持久化存储。

### 核心功能
- **训练记录**：记录动作、重量、次数、RPE
- **饮食记录**：拍照分析食物营养成分
- **营养统计**：每日碳水/蛋白质/脂肪/热量统计
- **自动同步**：数据自动同步到 GitHub

---

## 🚀 快速开始

### 环境要求
- Python 3.8+
- SQLite 数据库
- GitHub 仓库（用于数据持久化）

### 初始化

```bash
# 克隆仓库
git clone https://github.com/chasuperae1/GYM.git
cd GYM

# 初始化数据库
python3 init_db.py
```

### 配置 GitHub 同步

```bash
# 配置 git 用户信息
git config user.email "your_email@example.com"
git config user.name "Your Name"

# 设置 co-author 禁用（可选）
git config trae.coauthor false
```

---

## 🎯 使用方法

### 命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `开始今天训练` | 开始记录训练 | 开始今天训练 |
| `训练结束` | 结束训练并同步 | 训练结束 |
| `我吃了XX` | 快速记录饮食 | 我吃了鸡胸肉100克 米饭200克 |
| `记录饮食` | 开始饮食记录 | 记录饮食 |
| `今日饮食` | 查看今日营养摄入 | 今日饮食 |
| `今日训练` | 查看今日训练记录 | 今日训练 |

### 训练记录示例

```
用户: 开始今天训练
助手: 请告诉我训练类型（推日/拉日/腿日/全身/上半身/下半身）？
用户: 推日
助手: 今天状态如何（很好/一般/疲劳）？
用户: 很好
用户: 杠铃卧推 60×10
用户: 杠铃卧推 65×8 rpe8
用户: 上斜哑铃卧推 22×12 3组
用户: 训练结束
```

### 饮食记录示例

```
用户: 我吃了大虾150克 鸡蛋50克 面条150克
助手: ✅ 已记录午餐：大虾150g + 鸡蛋50g + 面条150g
      营养: 碳水39.5g 蛋白质48.1g 脂肪5.2g 热量384kcal
```

---

## 🗄️ 数据库结构

### 表结构

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `exercises` | 动作库 | name, category, equipment, target_muscles |
| `workouts` | 训练日记录 | date, split, duration, overall_rpe, mood |
| `sets` | 每组动作记录 | exercise, set_number, weight_kg, reps, rpe |
| `body_measurements` | 身体数据 | weight_kg, body_fat, chest_cm, waist_cm, arm_cm |
| `foods` | 食物营养库 | name, category, carbs_g, protein_g, fat_g, calories |
| `meals` | 餐次记录 | meal_time, meal_type, notes |
| `meal_items` | 每餐食物明细 | meal_id, food_name, quantity_g |
| `training_cycles` | 训练周期计划 | name, start_date, end_date, goal |

### 预置数据

- **34 个常用训练动作**（胸/背/腿/肩/臂/核心）
- **35 种常见食物**（主食/蛋白质/蔬菜/水果/油脂）

---

## 🔧 API 接口

### Python 函数调用

```python
from fitness_tool import (
    add_workout,    # 添加训练日
    add_set,        # 添加每组记录
    add_meal,       # 添加餐次
    add_measurement, # 添加身体数据
    get_today_workout, # 获取今日训练
    get_today_meals   # 获取今日饮食
)

# 添加训练日
workout_id = add_workout(
    workout_date="2026-06-22",
    split="推日",
    duration_min=75,
    overall_rpe=8,
    mood="很好"
)

# 添加动作组
add_set(workout_id, "杠铃卧推", 1, 60, 10, rpe=8)

# 添加饮食
meal_id = add_meal(meal_type="午餐")
add_meal_item(meal_id, "鸡胸肉", 100)
```

### 时间判断规则（北京时间 UTC+8）

| 时间段 | 餐次 |
|--------|------|
| 06:00 - 10:00 | 早餐 |
| 10:00 - 14:00 | 午餐 |
| 14:00 - 18:00 | 下午茶 |
| 18:00 - 22:00 | 晚餐 |
| 其他时间 | 宵夜 |

---

## 🔄 数据同步

### 自动同步机制

每次训练或饮食记录完成后，系统自动执行：

```bash
git add fitness.db
git commit -m "训练记录: YYYY-MM-DD 类型"
git push origin trae/solo-agent-1hq0no
```

### 手动同步

```bash
python3 -c "from training_skill import TrainingSkill; ts = TrainingSkill(); ts.sync_to_github()"
```

---

## 📁 项目结构

```
GYM/
├── fitness.db              # SQLite 数据库
├── fitness_tool.py         # 数据工具函数
├── training_skill.py       # 训练记录技能主入口
├── init_db.py              # 数据库初始化脚本
├── add_diet_tables.py      # 饮食数据表初始化
├── backup_restore.py       # 备份恢复工具
├── training_logger.py      # 命令行训练记录器
└── AGENT.md                # 本文档
```

---

## 📊 数据分析

### 可用查询

```python
from fitness_tool import (
    get_progress,           # 获取动作进步曲线
    get_volume_by_day,      # 获取每日训练容量
    get_weekly_nutrition,   # 获取每周营养统计
    print_workout           # 打印训练详情
)

# 查看深蹲进步曲线（最近10次）
get_progress("杠铃深蹲", limit=10)

# 查看最近30天训练容量
get_volume_by_day(30)

# 查看本周营养摄入
get_weekly_nutrition()
```

---

## 🔒 安全注意事项

1. **数据库备份**：定期使用 `backup_restore.py` 备份数据
2. **GitHub 权限**：确保使用的 token 只有仓库读写权限
3. **敏感数据**：不要在 notes 中记录个人敏感信息
4. **依赖管理**：保持 Python 依赖更新

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-06-22 | v1.0 | 初始版本，训练记录功能 |
| 2026-06-22 | v1.1 | 添加饮食记录功能 |
| 2026-06-22 | v1.2 | 修复北京时间判断 |

---

## 🤝 维护说明

### 新增食物/动作

```python
from fitness_tool import add_food, add_exercise

# 添加新食物
add_food(
    name="三文鱼",
    category="蛋白质",
    carbs_g=0,
    protein_g=25,
    fat_g=10,
    calories=200,
    notes="熟三文鱼"
)

# 添加新动作
add_exercise(
    name="哑铃侧平举",
    category="肩部",
    equipment="哑铃",
    target_muscles="三角肌中束"
)
```

### 常见问题

**Q: 数据库文件丢失怎么办？**
A: 使用 `backup_restore.py` 从 GitHub 恢复或使用 CSV 导出文件。

**Q: 时间判断错误？**
A: 检查系统时区设置，确保使用北京时间（UTC+8）。

**Q: GitHub 同步失败？**
A: 检查网络连接和 GitHub token 权限。

---

## 📬 联系方式

如有问题或建议，请联系项目维护者。