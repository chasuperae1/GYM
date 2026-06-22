#!/usr/bin/env python3
"""
TRAE Skill: 健身追踪器
功能：记录训练与饮食，自动同步到 GitHub

使用方法：
- 开始今天训练 → 记录训练
- 我吃了XX → 记录饮食
- 今日饮食 → 查看今日营养摄入
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from training_skill import TrainingSkill

class FitnessSkill:
    def __init__(self):
        self.logger = TrainingSkill()
    
    def handle_message(self, message):
        return self.logger.process(message)
    
    def handle_measurement(self, weight, chest=None, waist=None, arm=None, thigh=None):
        return self.logger.add_measurement(weight, chest, waist, arm, thigh)

def main():
    skill = FitnessSkill()
    print("🏋️  健身追踪器 Skill 已加载")
    
    while True:
        try:
            msg = input("> ").strip()
            if msg in ["退出", "quit", "exit"]:
                break
            
            result = skill.handle_message(msg)
            print(result)
            
            if "是否需要更新身体数据" in result:
                resp = input("请输入：").strip()
                if resp == "是":
                    weight = float(input("体重(kg): "))
                    skill.handle_measurement(weight)
                    print("✅ 身体数据已更新！")
                    
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
