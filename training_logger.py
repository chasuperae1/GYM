#!/usr/bin/env python3
"""
训练记录技能 - 对话式训练日志录入

使用方式:
1. 运行脚本: python training_logger.py
2. 输入"开始今天训练"开始记录
3. 依次回答问题或直接输入动作（格式: 动作名 重量×次数）
4. 输入"训练结束"保存并退出

示例对话:
> 开始今天训练
> 推日
> 杠铃卧推 60×10
> 杠铃卧推 65×8 rpe8
> 上斜哑铃卧推 22×12 3组
> 训练结束
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from fitness_tool import add_workout, add_set, add_measurement, list_exercises

class TrainingLogger:
    def __init__(self):
        self.workout = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "split": None,
            "duration": None,
            "mood": None,
            "notes": None,
        }
        self.sets = []
        self.workout_id = None
        self.start_time = None
        self.exercises = {}
        self.load_exercises()
    
    def load_exercises(self):
        for e in list_exercises():
            self.exercises[e["name"]] = e["category"]
    
    def ask(self, prompt, default=None):
        if default:
            resp = input(f"{prompt} (回车使用默认: {default}): ").strip()
        else:
            resp = input(f"{prompt}: ").strip()
        return resp if resp else default
    
    def parse_set_input(self, text):
        """解析用户输入的动作记录"""
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
    
    def run(self):
        print("🏋️  训练记录器已启动")
        print("输入 '开始今天训练' 开始记录，'训练结束' 保存退出")
        print("动作格式: 动作名 重量×次数 [rpeX] [N组]")
        print("示例: 杠铃卧推 60×10 rpe8 4组\n")
        
        while True:
            line = input("> ").strip()
            
            if line == "开始今天训练":
                self.start_session()
            elif line == "训练结束":
                self.end_session()
                break
            elif line in ["退出", "quit", "exit"]:
                print("已退出，未保存")
                break
            elif self.workout_id is not None:
                self.handle_input(line)
            else:
                print("请先输入 '开始今天训练'")
    
    def start_session(self):
        print("\n📅 开始记录今天的训练")
        self.start_time = datetime.now()
        self.workout["date"] = self.start_time.strftime("%Y-%m-%d")
        
        self.workout["split"] = self.ask("训练类型（推日/拉日/腿日/全身/上半身/下半身）")
        self.workout["mood"] = self.ask("今天状态（很好/一般/疲劳）", "一般")
        
        self.workout_id = add_workout(
            workout_date=self.workout["date"],
            split=self.workout["split"],
            mood=self.workout["mood"],
        )
        
        print(f"\n✅ 训练记录已创建，ID: {self.workout_id}")
        print("请输入动作记录（格式: 动作名 重量×次数）")
    
    def handle_input(self, line):
        parsed = self.parse_set_input(line)
        if not parsed:
            print("❌ 格式不正确，请输入: 动作名 重量×次数")
            print("示例: 杠铃卧推 60×10")
            return
        
        exercise = parsed["exercise"]
        weight = parsed["weight"]
        reps = parsed["reps"]
        rpe = parsed["rpe"]
        sets_count = parsed["sets_count"]
        
        if exercise not in self.exercises:
            print(f"⚠️  动作「{exercise}」不在预置列表中，将作为自定义动作添加")
        
        for i in range(sets_count):
            add_set(
                workout_id=self.workout_id,
                exercise_name=exercise,
                set_number=i + 1,
                weight_kg=weight,
                reps=reps,
                rpe=rpe,
            )
            print(f"  ✓ {exercise} 第{i+1}组: {weight}kg × {reps}", end="")
            if rpe:
                print(f" (RPE {rpe})", end="")
            print()
    
    def end_session(self):
        end_time = datetime.now()
        duration = int((end_time - self.start_time).total_seconds() // 60)
        
        print(f"\n⏱️  训练结束，总时长: {duration} 分钟")
        
        notes = self.ask("训练备注（可选）")
        body_update = self.ask("是否更新身体数据？(是/否)", "否")
        
        if body_update == "是":
            weight = float(self.ask("体重(kg)"))
            chest = float(self.ask("胸围(cm)", "0")) or None
            waist = float(self.ask("腰围(cm)", "0")) or None
            arm = float(self.ask("臂围(cm)", "0")) or None
            thigh = float(self.ask("腿围(cm)", "0")) or None
            
            add_measurement(
                measure_date=self.workout["date"],
                weight_kg=weight,
                chest_cm=chest,
                waist_cm=waist,
                arm_cm=arm,
                thigh_cm=thigh,
            )
            print("✅ 身体数据已更新")
        
        from fitness_tool import print_workout
        print("\n📝 本次训练记录:")
        print_workout(self.workout_id)
        print("\n🎉 训练记录保存成功！")

if __name__ == "__main__":
    logger = TrainingLogger()
    logger.run()
