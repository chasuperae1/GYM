#!/usr/bin/env python3
"""训练记录技能测试"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from training_skill import TrainingSkill

logger = TrainingSkill()

test_messages = [
    "开始今天训练",
    "推日",
    "很好",
    "杠铃卧推 60×10",
    "杠铃卧推 65×8 rpe8",
    "上斜哑铃卧推 22×12 3组",
    "绳索夹胸 25×15 3组",
    "训练结束",
]

print("🏋️  训练记录技能测试\n")

for msg in test_messages:
    print(f"用户: {msg}")
    result = logger.process(msg)
    print(f"助手: {result}")
    print()

print("✅ 测试完成！")
