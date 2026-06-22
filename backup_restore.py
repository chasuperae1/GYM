#!/usr/bin/env python3
"""健身数据备份与恢复工具"""
import os
import shutil
import json
from datetime import datetime

BACKUP_DIR = "fitness_backups"
DB_FILE = "fitness.db"

def backup_data(description=""):
    """备份数据库和代码文件到压缩包"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"fitness_backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    os.makedirs(backup_path, exist_ok=True)
    
    files_to_backup = [
        "fitness.db",
        "fitness_tool.py",
        "init_db.py", 
        "training_skill.py",
        "training_logger.py",
    ]
    
    for f in files_to_backup:
        if os.path.exists(f):
            shutil.copy(f, backup_path)
    
    info = {
        "backup_time": datetime.now().isoformat(),
        "description": description,
        "files": files_to_backup,
        "database_size_mb": os.path.getsize(DB_FILE) / 1024 / 1024 if os.path.exists(DB_FILE) else 0,
    }
    
    with open(os.path.join(backup_path, "backup_info.json"), "w") as f:
        json.dump(info, f, indent=2)
    
    shutil.make_archive(backup_path, 'zip', backup_path)
    shutil.rmtree(backup_path)
    
    zip_path = f"{backup_path}.zip"
    print(f"✅ 备份完成！文件: {zip_path}")
    print(f"   描述: {description}")
    return zip_path

def list_backups():
    """列出所有备份"""
    if not os.path.exists(BACKUP_DIR):
        print("暂无备份")
        return []
    
    backups = []
    for f in os.listdir(BACKUP_DIR):
        if f.endswith(".zip"):
            parts = f.replace(".zip", "").split("_")
            date = parts[-2]
            time = parts[-1]
            backups.append({
                "filename": f,
                "date": date,
                "time": time,
                "size": os.path.getsize(os.path.join(BACKUP_DIR, f)) / 1024,
            })
    
    backups.sort(key=lambda x: f"{x['date']}_{x['time']}", reverse=True)
    
    if backups:
        print("\n📁 可用备份:")
        print(f"   {'文件名':<35} {'日期':<12} {'大小':>8}")
        print("   " + "-" * 55)
        for b in backups:
            print(f"   {b['filename']:<35} {b['date']} {b['size']:>8.1f} KB")
    
    return backups

def restore_backup(backup_file):
    """从备份恢复数据"""
    backup_path = os.path.join(BACKUP_DIR, backup_file)
    
    if not os.path.exists(backup_path):
        print(f"❌ 备份文件不存在: {backup_file}")
        return False
    
    temp_dir = f"restore_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.unpack_archive(backup_path, temp_dir, 'zip')
    
    files_to_restore = [
        "fitness.db",
        "fitness_tool.py",
        "init_db.py",
        "training_skill.py",
        "training_logger.py",
    ]
    
    for f in files_to_restore:
        src = os.path.join(temp_dir, f)
        if os.path.exists(src):
            shutil.copy(src, ".")
            print(f"   ✓ 恢复: {f}")
    
    shutil.rmtree(temp_dir)
    print(f"\n✅ 从 {backup_file} 恢复完成！")
    return True

def export_csv(table_name="all"):
    """导出数据为CSV格式"""
    import sqlite3
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if table_name == "all":
        tables = ["workouts", "sets", "body_measurements", "exercises"]
    else:
        tables = [table_name]
    
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        
        csv_path = f"{table}_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(csv_path, "w") as f:
            f.write(",".join(col_names) + "\n")
            for row in rows:
                f.write(",".join(str(v) for v in row) + "\n")
        
        print(f"   ✓ 导出: {csv_path}")
    
    conn.close()
    print("\n✅ CSV导出完成！")

def main():
    print("🏋️  健身数据备份工具")
    print("1. 创建备份")
    print("2. 列出备份")
    print("3. 恢复备份")
    print("4. 导出CSV")
    print("5. 退出")
    
    while True:
        choice = input("\n请选择操作 (1-5): ")
        
        if choice == "1":
            desc = input("备份描述（可选）: ")
            backup_data(desc)
        elif choice == "2":
            list_backups()
        elif choice == "3":
            list_backups()
            name = input("请输入要恢复的备份文件名: ")
            restore_backup(name)
        elif choice == "4":
            export_csv()
        elif choice == "5":
            break
        else:
            print("无效选项")

if __name__ == "__main__":
    main()
