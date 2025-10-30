import json
import os
from pathlib import Path


def extract_teacher_user_dialogues_with_splitline(data):
    """
    从数据中提取老师和用户的对话，并检测SplitLine消息类型
    """
    # 支持多种可能的作者名称
    valid_authors = ["老师", "用户", "teacher", "user", "家长"]
    
    dialogues = []
    splitline_count = 0

    # 如果数据是字典且包含context字段
    if isinstance(data, dict) and "context" in data:
        for msg in data.get("context", []):
            # 检测SplitLine消息类型
            if msg.get("msg_type") == "SplitLine":
                splitline_count += 1
                dialogues.append("通话结束")
            # 提取有效作者的对话
            elif msg.get("author") in valid_authors:
                dialogues.append(f"{msg['author']}：{msg['content']}")
    
    # 如果数据直接是对话列表
    elif isinstance(data, list):
        for msg in data:
            if isinstance(msg, dict):
                # 检测SplitLine消息类型
                if msg.get("msg_type") == "SplitLine":
                    splitline_count += 1
                    dialogues.append("通话结束")
                # 提取有效作者的对话
                elif msg.get("author") in valid_authors:
                    dialogues.append(f"{msg['author']}：{msg['content']}")
    
    # 如果数据是字典，寻找包含对话的字段
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                for msg in value:
                    if isinstance(msg, dict):
                        # 检测SplitLine消息类型
                        if msg.get("msg_type") == "SplitLine":
                            splitline_count += 1
                            dialogues.append("通话结束")
                        # 提取有效作者的对话
                        elif msg.get("author") in valid_authors:
                            dialogues.append(f"{msg['author']}：{msg['content']}")
                if dialogues:  # 找到第一个有效的对话列表就停止
                    break

    return dialogues, splitline_count


def extract_teacher_user_dialogues(data):
    """
    从数据中提取老师和用户的对话
    """
    # 支持多种可能的作者名称
    valid_authors = ["老师", "用户", "teacher", "user", "家长"]

    # 如果数据是字典且包含context字段
    if isinstance(data, dict) and "context" in data:
        dialogues = [
            f"{msg['author']}：{msg['content']}"
            for msg in data.get("context", [])
            if msg.get("author") in valid_authors
        ]
    # 如果数据直接是对话列表
    elif isinstance(data, list):
        dialogues = [
            f"{msg['author']}：{msg['content']}"
            for msg in data
            if isinstance(msg, dict) and msg.get("author") in valid_authors
        ]
    # 如果数据是字典，寻找包含对话的字段
    elif isinstance(data, dict):
        dialogues = []
        for key, value in data.items():
            if isinstance(value, list):
                temp_dialogues = [
                    f"{msg['author']}：{msg['content']}"
                    for msg in value
                    if isinstance(msg, dict) and msg.get("author") in valid_authors
                ]
                if temp_dialogues:
                    dialogues.extend(temp_dialogues)
                    break  # 找到第一个有效的对话列表就停止
    else:
        dialogues = []

    return dialogues


def process_single_file_with_splitline(input_file_path, output_file_path):
    """
    处理单个JSON文件，检测SplitLine并输出通话结束标记
    """
    try:
        # 读取JSON文件
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取对话（包含SplitLine检测）
        dialogues, splitline_count = extract_teacher_user_dialogues_with_splitline(data)

        if not dialogues:
            print(f"⚠️  {input_file_path} 中没有找到老师和用户的对话")
            return False

        # 只保存dialogues列表
        output_data = {"dialogues": dialogues}

        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # 保存结果
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(
            f"✅ 提取 {len(dialogues)} 条对话（包含{splitline_count}次通话结束标记）: {os.path.basename(input_file_path)} -> {os.path.basename(output_file_path)}")
        return True

    except Exception as e:
        print(f"❌ 处理文件 {input_file_path} 时出错: {str(e)}")
        return False


def process_single_file(input_file_path, output_file_path):
    """
    处理单个JSON文件，只保存dialogues
    """
    try:
        # 读取JSON文件
        with open(input_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取对话
        dialogues = extract_teacher_user_dialogues(data)

        if not dialogues:
            print(f"⚠️  {input_file_path} 中没有找到老师和用户的对话")
            return False

        # 只保存dialogues列表
        output_data = {"dialogues": dialogues}

        # 创建输出目录（如果不存在）
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

        # 保存结果
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        print(
            f"✅ 提取 {len(dialogues)} 条对话: {os.path.basename(input_file_path)} -> {os.path.basename(output_file_path)}")
        return True

    except Exception as e:
        print(f"❌ 处理文件 {input_file_path} 时出错: {str(e)}")
        return False


def process_folder_with_splitline(input_folder, output_folder):
    """
    处理单个文件夹下的所有JSON文件（包含SplitLine检测）
    """
    if not os.path.exists(input_folder):
        print(f"❌ 输入文件夹不存在: {input_folder}")
        return 0

    # 获取文件夹中的所有JSON文件
    json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    if not json_files:
        print(f"⚠️  文件夹 {input_folder} 中没有找到JSON文件")
        return 0

    success_count = 0
    total_dialogues = 0
    total_splitlines = 0

    print(f"📂 处理文件夹: {input_folder} ({len(json_files)} 个文件)")

    for json_file in json_files:
        input_path = os.path.join(input_folder, json_file)
        output_path = os.path.join(output_folder, json_file)

        if process_single_file_with_splitline(input_path, output_path):
            success_count += 1
            # 统计对话数量和SplitLine数量
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    dialogues = result.get('dialogues', [])
                    total_dialogues += len(dialogues)
                    total_splitlines += sum(1 for d in dialogues if d == "通话结束")
            except:
                pass

    print(f"   ✅ 成功处理 {success_count}/{len(json_files)} 个文件，共提取 {total_dialogues} 条对话（包含{total_splitlines}次通话结束标记）")
    return success_count


def process_folder(input_folder, output_folder):
    """
    处理单个文件夹下的所有JSON文件
    """
    if not os.path.exists(input_folder):
        print(f"❌ 输入文件夹不存在: {input_folder}")
        return 0

    # 获取文件夹中的所有JSON文件
    json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    if not json_files:
        print(f"⚠️  文件夹 {input_folder} 中没有找到JSON文件")
        return 0

    success_count = 0
    total_dialogues = 0

    print(f"📂 处理文件夹: {input_folder} ({len(json_files)} 个文件)")

    for json_file in json_files:
        input_path = os.path.join(input_folder, json_file)
        output_path = os.path.join(output_folder, json_file)

        if process_single_file(input_path, output_path):
            success_count += 1
            # 统计对话数量
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    result = json.load(f)
                    total_dialogues += len(result.get('dialogues', []))
            except:
                pass

    print(f"   ✅ 成功处理 {success_count}/{len(json_files)} 个文件，共提取 {total_dialogues} 条对话")
    return success_count


def batch_process_folders_with_splitline(root_directory=r"C:\Users\JOJO\Desktop\app\dataset\waihudata\1", output_root=r"C:\Users\JOJO\Desktop\app\dataset\waihudata\extracted"):
    """
    批量处理多个文件夹下的JSON文件（包含SplitLine检测）
    """
    if not os.path.exists(root_directory):
        print(f"❌ 根目录不存在: {root_directory}")
        return

    # 获取所有子文件夹
    subfolders = [d for d in os.listdir(root_directory)
                  if os.path.isdir(os.path.join(root_directory, d)) and not d.startswith('.')]

    # 也检查根目录本身是否有JSON文件
    root_json_files = [f for f in os.listdir(root_directory) if f.endswith('.json')]

    total_folders = len(subfolders)
    if root_json_files:
        total_folders += 1

    if total_folders == 0:
        print("❌ 没有找到包含JSON文件的文件夹")
        return

    print(f"🚀 开始处理 {total_folders} 个文件夹（包含SplitLine检测）...")
    print("=" * 60)

    total_success = 0
    total_dialogues = 0
    total_splitlines = 0

    # 处理根目录的JSON文件
    if root_json_files:
        success = process_folder_with_splitline(root_directory, output_root)
        total_success += success
        print()

    # 处理子文件夹
    for subfolder in subfolders:
        input_folder = os.path.join(root_directory, subfolder)
        output_folder = os.path.join(output_root, subfolder)

        success = process_folder_with_splitline(input_folder, output_folder)
        total_success += success
        print()

    print("=" * 60)
    print(f"🎉 处理完成！总共成功处理了 {total_success} 个文件")
    print(f"📊 统计信息：共提取 {total_dialogues} 条对话，检测到 {total_splitlines} 次通话结束标记")
    print(f"📁 结果保存在: {output_root} 目录下")


def batch_process_folders(root_directory=r"C:\Users\JOJO\Desktop\app\dataset\waihudata\1", output_root=r"C:\Users\JOJO\Desktop\app\dataset\waihudata\extracted"):
    """
    批量处理多个文件夹下的JSON文件
    """
    if not os.path.exists(root_directory):
        print(f"❌ 根目录不存在: {root_directory}")
        return

    # 获取所有子文件夹
    subfolders = [d for d in os.listdir(root_directory)
                  if os.path.isdir(os.path.join(root_directory, d)) and not d.startswith('.')]

    # 也检查根目录本身是否有JSON文件
    root_json_files = [f for f in os.listdir(root_directory) if f.endswith('.json')]

    total_folders = len(subfolders)
    if root_json_files:
        total_folders += 1

    if total_folders == 0:
        print("❌ 没有找到包含JSON文件的文件夹")
        return

    print(f"🚀 开始处理 {total_folders} 个文件夹...")
    print("=" * 60)

    total_success = 0

    # 处理根目录的JSON文件
    if root_json_files:
        success = process_folder(root_directory, output_root)
        total_success += success
        print()

    # 处理子文件夹
    for subfolder in subfolders:
        input_folder = os.path.join(root_directory, subfolder)
        output_folder = os.path.join(output_root, subfolder)

        success = process_folder(input_folder, output_folder)
        total_success += success
        print()

    print("=" * 60)
    print(f"🎉 处理完成！总共成功处理了 {total_success} 个文件")
    print(f"📁 结果保存在: {output_root} 目录下")


def process_specific_folders(folder_list, output_root="extracted"):
    """
    处理指定的文件夹列表
    """
    print(f"🚀 开始处理指定的 {len(folder_list)} 个文件夹...")
    print("=" * 60)

    total_success = 0

    for folder_path in folder_list:
        folder_name = os.path.basename(folder_path)
        output_folder = os.path.join(output_root, folder_name)

        success = process_folder(folder_path, output_folder)
        total_success += success
        print()

    print("=" * 60)
    print(f"🎉 处理完成！总共成功处理了 {total_success} 个文件")
    print(f"📁 结果保存在: {output_root} 目录下")


# 使用示例
if __name__ == "__main__":
    print("🚀 批量处理多文件夹JSON对话提取...")

    # 方式1: 自动处理当前目录下的所有子文件夹（包含SplitLine检测）
    # batch_process_folders_with_splitline()

    # 方式2: 自动处理当前目录下的所有子文件夹（原始功能）
    batch_process_folders()

    # 方式3: 指定根目录和输出目录（取消注释使用）
    # batch_process_folders(root_directory="data", output_root="extracted_dialogues")

    # 方式4: 处理指定的文件夹列表（取消注释使用）
    # folder_list = ["folder1", "folder2", "folder3"]
    # process_specific_folders(folder_list, "extracted_dialogues")

    # 方式5: 处理单个文件夹（取消注释使用）
    # process_folder("input_folder", "output_folder")


# 创建测试数据结构（包含SplitLine）
def create_test_structure_with_splitline():
    """
    创建测试文件夹结构和数据（包含SplitLine消息）
    """
    test_data = {
        "context": [
            {"author": "用户", "content": "老师好，我想了解孩子的学习情况", "msg_type": "text"},
            {"author": "老师", "content": "您好！孩子最近表现很好", "msg_type": "text"},
            {"author": "老师", "content": "通话结束", "msg_type": "SplitLine"},
            {"author": "用户", "content": "数学成绩怎么样？", "msg_type": "text"},
            {"author": "老师", "content": "数学进步很大", "msg_type": "text"},
            {"author": "老师", "content": "通话结束", "msg_type": "SplitLine"}
        ]
    }

    # 创建测试文件夹结构
    folders = ["test_folder1", "test_folder2", "test_folder3"]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

        # 在每个文件夹中创建2个测试文件
        for i in range(1, 3):
            file_path = os.path.join(folder, f"dialogue_{i}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)

    print("📝 已创建测试文件夹结构（包含SplitLine消息）:")
    print("   test_folder1/dialogue_1.json, dialogue_2.json")
    print("   test_folder2/dialogue_1.json, dialogue_2.json")
    print("   test_folder3/dialogue_1.json, dialogue_2.json")


# 创建测试数据结构
def create_test_structure():
    """
    创建测试文件夹结构和数据
    """
    test_data = {
        "context": [
            {"author": "用户", "content": "老师好，我想了解孩子的学习情况"},
            {"author": "老师", "content": "您好！孩子最近表现很好"},
            {"author": "system", "content": "系统消息"},
            {"author": "用户", "content": "数学成绩怎么样？"},
            {"author": "老师", "content": "数学进步很大"}
        ]
    }

    # 创建测试文件夹结构
    folders = ["test_folder1", "test_folder2", "test_folder3"]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

        # 在每个文件夹中创建2个测试文件
        for i in range(1, 3):
            file_path = os.path.join(folder, f"dialogue_{i}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)

    print("📝 已创建测试文件夹结构:")
    print("   test_folder1/dialogue_1.json, dialogue_2.json")
    print("   test_folder2/dialogue_1.json, dialogue_2.json")
    print("   test_folder3/dialogue_1.json, dialogue_2.json")

# 如果需要创建测试数据，取消注释下面这行
# create_test_structure_with_splitline()