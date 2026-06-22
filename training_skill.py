#!/usr/bin/env python3
"""
训练记录技能 - 对话式接口

使用方式:
1. 创建实例: logger = TrainingSkill()
2. 发送消息: logger.process("开始今天训练")
3. 持续发送动作记录
4. 发送"训练结束"完成记录

示例对话流程:
用户: 开始今天训练
助手: 训练类型？
用户: 推日
助手: 今天状态？
用户: 很好
助手: 请输入动作（格式: 动作名 重量×次数）
用户: 杠铃卧推 60×10
用户: 杠铃卧推 65×8 rpe8
用户: 上斜哑铃卧推 22×12 3组
用户: 训练结束
助手: 训练记录保存成功！
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from fitness_tool import (
    add_workout, add_set, add_measurement, list_exercises,
    add_meal, add_meal_item, list_foods, get_daily_nutrition
)

class TrainingSkill:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.state = "idle"
        self.workout_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "split": None,
            "mood": None,
            "notes": None,
        }
        self.workout_id = None
        self.start_time = None
        self.exercises = {}
        self.foods = {}
        self.load_data()
    
    def load_data(self):
        for e in list_exercises():
            self.exercises[e["name"]] = e["category"]
        for f in list_foods():
            self.foods[f["name"]] = {k: v for k, v in f.items()}
    
    def parse_set_input(self, text):
        text = text.strip()
        parts = text.split()
        
        if len(parts) < 2:
            return None
        
        exercise = parts[0]
        for i in range(1, len(parts)):
            if "×" in parts[i] or "x" in parts[i]:
                break
            exercise += " " + parts[i]
        
        weight = None
        reps = None
        rpe = None
        sets_count = None
        
        for part in parts:
            if "×" in part or "x" in part:
                w, r = part.replace("×", "x").split("x")
                weight = float(w)
                reps = int(r)
            elif part.lower().startswith("rpe"):
                rpe = float(part[3:])
            elif part.endswith("组"):
                sets_count = int(part[:-1])
        
        return {
            "exercise": exercise,
            "weight": weight,
            "reps": reps,
            "rpe": rpe,
            "sets_count": sets_count or 1,
        }
    
    def process(self, message):
        message = message.strip()
        
        if message == "开始今天训练":
            self.state = "asking_split"
            self.start_time = datetime.now()
            self.workout_data["date"] = self.start_time.strftime("%Y-%m-%d")
            return "好的！开始记录今天的训练。请告诉我训练类型（推日/拉日/腿日/全身/上半身/下半身）？"
        
        if self.state == "asking_split":
            self.workout_data["split"] = message
            self.state = "asking_mood"
            return f"训练类型: {message}。今天状态如何（很好/一般/疲劳）？"
        
        if self.state == "asking_mood":
            self.workout_data["mood"] = message
            self.workout_id = add_workout(
                workout_date=self.workout_data["date"],
                split=self.workout_data["split"],
                mood=self.workout_data["mood"],
            )
            self.state = "recording"
            return f"状态: {message}。训练记录已创建！\n\n请输入动作记录（格式: 动作名 重量×次数），例如：\n杠铃卧推 60×10\n也可以加 rpe 和组数：\n杠铃卧推 65×8 rpe8 4组"
        
        if self.state == "recording":
            if message == "训练结束":
                return self.finish_workout()
            
            parsed = self.parse_set_input(message)
            if not parsed:
                return "❌ 格式不正确，请输入：动作名 重量×次数\n示例：杠铃卧推 60×10"
            
            exercise = parsed["exercise"]
            weight = parsed["weight"]
            reps = parsed["reps"]
            rpe = parsed["rpe"]
            sets_count = parsed["sets_count"]
            
            results = []
            for i in range(sets_count):
                add_set(
                    workout_id=self.workout_id,
                    exercise_name=exercise,
                    set_number=i + 1,
                    weight_kg=weight,
                    reps=reps,
                    rpe=rpe,
                )
                line = f"✓ {exercise} 第{i+1}组: {weight}kg × {reps}"
                if rpe:
                    line += f" (RPE {rpe})"
                results.append(line)
            
            if exercise not in self.exercises:
                results.append(f"⚠️  动作「{exercise}」已作为自定义动作添加")
            
            return "\n".join(results)
        
        if message.startswith("我吃了") or message.startswith("吃了"):
            return self.record_meal(message)
        
        if message == "记录饮食":
            self.state = "recording_meal"
            return "好的！请告诉我吃了什么（格式: 食物名XX克 食物名XX克），例如：鸡胸肉100克 米饭200克"
        
        if self.state == "recording_meal":
            if message == "完成":
                self.state = "idle"
                return "✅ 饮食记录完成！"
            return self.record_meal(message)
        
        if message == "今日饮食":
            return self.show_today_nutrition()
        
        if message == "训练结束":
            return "还没有开始训练呢，请先输入「开始今天训练」"
        
        return "输入「开始今天训练」开始记录，或输入「训练结束」保存退出"
    
    def finish_workout(self):
        end_time = datetime.now()
        duration = int((end_time - self.start_time).total_seconds() // 60)
        
        result = f"\n⏱️ 训练结束，总时长: {duration} 分钟\n\n📝 本次训练记录:\n"
        
        result += print_workout_str(self.workout_id)
        
        sync_result = self.sync_to_github()
        result += "\n\n" + sync_result
        
        result += "\n🎉 训练记录保存成功！\n\n是否需要更新身体数据？（是/否）"
        self.state = "asking_measurement"
        
        return result
    
    def sync_to_github(self):
        """自动同步数据库到 GitHub"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "add", "fitness.db"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return f"⚠️  Git add 失败: {result.stderr}"
            
            result = subprocess.run(
                ["git", "commit", "-m", f"训练记录: {self.workout_data['date']} {self.workout_data['split']}"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0 and "nothing to commit" not in result.stderr:
                return f"⚠️  Git commit 失败: {result.stderr}"
            
            result = subprocess.run(
                ["git", "push", "origin", "trae/solo-agent-1hq0no"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return "✅ 已自动同步到 GitHub"
            else:
                return f"⚠️  Git push 失败: {result.stderr}"
        except Exception as e:
            return f"⚠️  同步失败: {str(e)}"
    
    def add_measurement(self, weight, chest=None, waist=None, arm=None, thigh=None):
        add_measurement(
            measure_date=self.workout_data["date"],
            weight_kg=weight,
            chest_cm=chest,
            waist_cm=waist,
            arm_cm=arm,
            thigh_cm=thigh,
        )
        self.sync_to_github()
        self.reset()
        return "✅ 身体数据已更新！"
    
    def record_meal(self, message):
        """记录饮食"""
        text = message.replace("我吃了", "").replace("吃了", "").strip()
        items = []
        
        foods_list = list(self.foods.keys())
        remaining = text
        
        while remaining:
            matched = False
            for food_name in foods_list:
                if remaining.startswith(food_name):
                    remaining = remaining[len(food_name):].strip()
                    
                    import re
                    match = re.match(r"(\d+\.?\d*)(g|克)", remaining)
                    if match:
                        quantity = float(match.group(1))
                        remaining = remaining[match.end():].strip()
                    else:
                        quantity = 100
                        remaining = ""
                    
                    items.append({"name": food_name, "quantity": quantity})
                    matched = True
                    break
            
            if not matched:
                break
        
        if not items:
            return "❌ 未识别到食物，请使用格式：食物名XX克\n示例：鸡胸肉100克 米饭200克"
        
        meal_id = add_meal()
        
        total_carbs = 0
        total_protein = 0
        total_fat = 0
        total_calories = 0
        food_list = []
        
        for item in items:
            food_name = item["name"]
            quantity = item["quantity"]
            
            if food_name not in self.foods:
                return f"❌ 未找到食物「{food_name}」，请先告诉我它的营养成分"
            
            food_info = self.foods[food_name]
            add_meal_item(meal_id, food_name, quantity)
            
            carbs = (food_info["carbs_g"] * quantity) / 100
            protein = (food_info["protein_g"] * quantity) / 100
            fat = (food_info["fat_g"] * quantity) / 100
            calories = (food_info["calories"] * quantity) / 100
            
            total_carbs += carbs
            total_protein += protein
            total_fat += fat
            total_calories += calories
            
            food_list.append(f"{food_name}{quantity}g")
        
        self.sync_to_github()
        meal_type = self.get_meal_type()
        
        return (f"✅ 已记录{meal_type}：{' + '.join(food_list)}\n"
                f"   营养: 碳水{round(total_carbs,1)}g 蛋白质{round(total_protein,1)}g "
                f"脂肪{round(total_fat,1)}g 热量{round(total_calories,0)}kcal")
    
    def get_meal_type(self):
        hour = datetime.now().hour
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
    
    def show_today_nutrition(self):
        """显示今日营养摄入"""
        meals, totals = get_daily_nutrition()
        
        if not meals:
            return "📊 今日还没有饮食记录"
        
        result = "📊 今日营养摄入\n"
        result += "-" * 40 + "\n"
        
        for meal_time, items in meals.items():
            result += f"\n🍽️ {meal_time}\n"
            for item in items:
                result += f"   {item['food']} {item['quantity']}g\n"
        
        result += "\n📈 今日总计:\n"
        result += f"   碳水: {totals['carbs']}g\n"
        result += f"   蛋白质: {totals['protein']}g\n"
        result += f"   脂肪: {totals['fat']}g\n"
        result += f"   热量: {totals['calories']}kcal"
        
        return result
        

def print_workout_str(workout_id):
    from fitness_tool import get_workout
    from collections import defaultdict
    
    w, sets = get_workout(workout_id)
    
    lines = []
    lines.append(f"📅 {w['workout_date']} | {w['split'] or '未分类'} | 时长 {w['duration_min'] or '--'} 分钟")
    if w["mood"]:
        lines.append(f"   状态: {w['mood']}")
    
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
        lines.append(line)
    lines.append(f"   总容量: {total_volume:.0f} kg")
    
    return "\n".join(lines)

if __name__ == "__main__":
    logger = TrainingSkill()
    print("🏋️  训练记录技能测试")
    print("输入 '开始今天训练' 开始，'训练结束' 保存\n")
    
    while True:
        msg = input("> ").strip()
        if msg in ["退出", "quit", "exit"]:
            break
        result = logger.process(msg)
        print(result)
        if "训练记录保存成功" in result:
            meas = input("是否更新身体数据？(是/否): ")
            if meas == "是":
                weight = float(input("体重(kg): "))
                logger.add_measurement(weight)
            break
