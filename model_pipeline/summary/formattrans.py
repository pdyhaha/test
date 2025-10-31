import json
import os
import random
import time
from datetime import datetime, timedelta
import uuid
import threading


class GlobalMsgIdGenerator:
    """全局msg_id生成器，确保跨文件唯一性"""

    def __init__(self):
        self._current_id = random.randint(1000000000000000000, 9999999999999999999)
        self._lock = threading.Lock()

    def get_next_id(self):
        with self._lock:
            self._current_id += random.randint(1, 100)  # 增加随机间隔避免过于规律
            return self._current_id


# 全局msg_id生成器实例
global_msg_id_generator = GlobalMsgIdGenerator()


def generate_random_data():
    """生成随机数据"""
    teacher_ids = [str(random.randint(10000, 99999)) for _ in range(100)]
    user_ids = [str(random.randint(10000000, 99999999)) for _ in range(100)]
    corp_ids = ['wwc58c804b152b2e7f', 'ww1234567890abcdef', 'ww9876543210fedcba']
    departments = [
        '销售中心-新项目销售部-初中语文-初中语文_北京-初中语文_北京_一组',
        '销售中心-新项目销售部-小学数学-小学数学_上海-小学数学_上海_二组',
        '教学中心-课程研发部-高中英语-高中英语_广州-高中英语_广州_三组',
        '运营中心-客服部-综合服务-综合服务_深圳-综合服务_深圳_四组'
    ]

    return {
        'teacher_id': random.choice(teacher_ids),
        'user_id': random.choice(user_ids),
        'corp_id': random.choice(corp_ids),
        'department_name': random.choice(departments),
        'teacher_wx_id': str(random.randint(13000000000, 13999999999)),
        'class_id': str(random.randint(50000, 99999)),
        'course_id': str(random.randint(1000, 9999))
    }


def generate_unique_ids(class_id, teacher_id, user_id, chat_time_start, chat_time_end):
    """根据指定规则生成s_id"""
    s_id = f"{class_id}-{teacher_id}-{user_id}-{chat_time_start}-{chat_time_end}"
    return s_id


def convert_json_file(input_file, output_file):
    """转换单个JSON文件"""
    try:
        # 读取原始JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 生成随机数据
        random_data = generate_random_data()

        # 获取原始数据中的字段
        third_user_id = data.get('third_user_id', f"wmKzPhXQAA{uuid.uuid4().hex[:20]}")
        business_wx_user_id = data.get('business_wx_user_id', random_data['teacher_wx_id'])
        user_id = data.get('user_id', random_data['user_id'])
        class_id = data.get('class_id', random_data['class_id'])
        teacher_wx_id = random_data['teacher_wx_id']

        # 获取第一个对话的时间作为send_time
        conversations = data.get('conversations', [])
        first_time = datetime.now().isoformat() + '+08:00'
        chat_time_start = str(int(time.time() * 1000) - random.randint(86400000, 604800000))
        chat_time_end = str(int(chat_time_start) + random.randint(10000, 99999))

        if conversations:
            first_conversation = conversations[0]
            first_time_raw = first_conversation.get('time', '')
            # 转换时间格式
            try:
                dt = datetime.strptime(first_time_raw, '%Y-%m-%d %H:%M:%S')
                first_time = dt.isoformat() + '+08:00'
            except:
                first_time = datetime.now().isoformat() + '+08:00'

        # 生成s_id
        s_id = generate_unique_ids(
            class_id,
            random_data['teacher_id'],
            user_id,
            chat_time_start,
            chat_time_end
        )

        # 生成session_id，格式为user_wx_id_teacher_wx_id
        session_id = f"{third_user_id}_{teacher_wx_id}"

        # 生成基础chat_time
        base_chat_time = int(time.time() * 1000) - random.randint(86400000, 604800000)  # 1-7天前

        # 转换conversations为context格式
        context = []
        for i, conversation in enumerate(data.get('conversations', [])):
            # 提取author, msg_type, text
            author = conversation.get('author', '用户')
            msg_type = conversation.get('msg_type', 'text')
            text = conversation.get('text', '')

            # 使用全局生成器获取唯一的msg_id
            unique_msg_id = global_msg_id_generator.get_next_id()
            current_chat_time = base_chat_time + i * random.randint(1000, 10000)  # 每条消息间隔1-10秒

            msg_id = f"{unique_msg_id}_{current_chat_time}_external"
            chat_time = str(current_chat_time)

            # 处理if_sop_bi字段，确保值为0或1
            is_sop_bi = conversation.get('is_sop_bi', 0)
            if is_sop_bi is None:
                if_sop_bi = 0
            else:
                # 转换为整数并限制在0或1
                if_sop_bi = 1 if float(is_sop_bi) > 0 else 0

            # 构造context条目
            context_item = {
                'msg_id': str(msg_id),  # 转换为字符串
                'session_id': str(session_id),
                'msg_type': str(msg_type),
                'author': str(author),
                'content': str(text),
                'chat_time': str(chat_time),
                'if_sop_bi': "0",  # 强制字符串
                'valid': 1,  # 保持整数
                'if_sop_strict': 0  # 保持整数
            }
            context.append(context_item)

        output_data = {
            'teacher_id': str(random_data['teacher_id']),
            'user_id': str(user_id),
            's_id': str(s_id),
            'corp_id': str(random_data['corp_id']),
            'session_type': str(data.get('session_type', 1)),
            'ip_position': str(data.get('ip_position', '运营')),
            'user_wx_id': str(third_user_id),
            'teacher_wx_id': str(random_data['teacher_wx_id']),
            'send_time': str(first_time),
            'department_name': str(random_data['department_name']),
            'class_id': str(class_id),
            'context': context,
            'chat_time_start': str(chat_time_start),
            'chat_time_end': str(chat_time_end)
        }

        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        return True, f"成功转换: {input_file} -> {output_file} (处理了 {len(context)} 条对话)"

    except Exception as e:
        return False, f"转换失败 {input_file}: {str(e)}"






def batch_convert_json_files(input_folder, output_folder):
    """批量转换JSON文件"""
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)

    # 获取所有JSON文件
    json_files = [f for f in os.listdir(input_folder) if f.endswith('.json')]

    if not json_files:
        print(f"在 {input_folder} 中没有找到JSON文件")
        return

    print(f"找到 {len(json_files)} 个JSON文件，开始转换...")
    print(f"使用全局唯一msg_id生成器，确保跨文件唯一性")

    success_count = 0
    failed_count = 0
    total_conversations = 0

    for i, filename in enumerate(json_files, 1):
        input_path = os.path.join(input_folder, filename)
        output_filename = f"converted_{filename}"
        output_path = os.path.join(output_folder, output_filename)

        success, message = convert_json_file(input_path, output_path)

        if success:
            success_count += 1
            print(f"[{i}/{len(json_files)}] ✓ {message}")

            # 统计conversation数量
            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_conversations += len(data.get('conversations', []))
            except:
                pass
        else:
            failed_count += 1
            print(f"[{i}/{len(json_files)}] ✗ {message}")

        # 每处理50个文件显示一次进度
        if i % 50 == 0:
            print(f"进度: {i}/{len(json_files)} ({i / len(json_files) * 100:.1f}%)")

    print(f"\n转换完成!")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {failed_count} 个文件")
    print(f"总计处理对话: {total_conversations} 条")
    print(f"输出目录: {output_folder}")
    print(f"所有msg_id都是全局唯一的")


def verify_msg_id_uniqueness(output_folder):
    """验证生成的msg_id是否唯一"""
    print(f"\n开始验证msg_id唯一性...")

    all_msg_ids = set()
    duplicate_count = 0
    total_msg_count = 0

    json_files = [f for f in os.listdir(output_folder) if f.endswith('.json')]

    for filename in json_files:
        file_path = os.path.join(output_folder, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                context = data.get('context', [])

                for item in context:
                    msg_id = item.get('msg_id', '')
                    total_msg_count += 1

                    if msg_id in all_msg_ids:
                        duplicate_count += 1
                        print(f"发现重复msg_id: {msg_id} 在文件 {filename}")
                    else:
                        all_msg_ids.add(msg_id)
        except Exception as e:
            print(f"验证文件 {filename} 时出错: {e}")

    print(f"验证完成:")
    print(f"总计msg_id数量: {total_msg_count}")
    print(f"唯一msg_id数量: {len(all_msg_ids)}")
    print(f"重复msg_id数量: {duplicate_count}")

    if duplicate_count == 0:
        print("✓ 所有msg_id都是唯一的!")
    else:
        print(f"✗ 发现 {duplicate_count} 个重复的msg_id")


# 使用示例
if __name__ == "__main__":
    # 设置输入和输出文件夹路径
    input_folder = r"C:\Users\JOJO\Desktop\外呼数据SP164\session"  # 包含500个JSON文件的文件夹
    output_folder = "./dataset/waihudata/1"  # 转换后的文件输出文件夹

    # 如果要测试单个文件转换，可以使用：
    # success, message = convert_json_file("test_input.json", "test_output.json")
    # print(message)

    # 批量转换所有文件
    batch_convert_json_files(input_folder, output_folder)

    # 可选：验证msg_id唯一性
    # verify_msg_id_uniqueness(output_folder)
