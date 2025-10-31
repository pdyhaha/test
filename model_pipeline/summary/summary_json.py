# -*- coding: UTF-8 -*-
import json
import os
import glob
import time
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from doubao_enterprise_v2 import get_result
from datetime import datetime
import openpyxl
from openpyxl.styles import Alignment


def load_sessions_from_json_files(json_folder_path, max_files=None):
    """
    从JSON文件夹中加载所有session数据，将dialogues列表转换为带换行的字符串
    """
    sessions = []

    if not os.path.exists(json_folder_path):
        logger.error(f"文件夹不存在: {json_folder_path}")
        return sessions

    json_files = glob.glob(os.path.join(json_folder_path, "*.json"))
    if not json_files:
        logger.warning(f"在文件夹 {json_folder_path} 中未找到JSON文件")
        return sessions

    if max_files:
        json_files = json_files[:max_files]

    logger.info(f"找到 {len(json_files)} 个JSON文件，开始加载...")

    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'dialogues' in data:
                    session_data = {}
                    session_data.update(data)

                    # 将dialogues列表转换为带换行的字符串，增强可读性
                    dialogues_list = data['dialogues']
                    if isinstance(dialogues_list, list):
                        # 使用换行符连接每个对话条目
                        dialogues_text = '\n'.join([str(dialogue) for dialogue in dialogues_list])
                        session_data['dialogues'] = dialogues_text
                    else:
                        session_data['dialogues'] = str(dialogues_list)

                    sessions.append(session_data)
                else:
                    logger.warning(f"文件 {json_file} 中未找到dialogues字段")

            if i % 100 == 0:
                logger.info(f"已加载 {i}/{len(json_files)} 个文件")

        except Exception as e:
            logger.error(f"加载文件 {json_file} 时出错: {str(e)}")
            continue

    logger.info(f"成功加载 {len(sessions)} 个session")
    return sessions


def process_session(session, idx):
    """处理一个 session"""
    try:
        # 从session中获取dialogues（现在已经是带换行的字符串）
        dialogues_text = session.get('dialogues', "")

        # 如果需要将字符串转换回列表进行处理，可以这样做：
        if isinstance(dialogues_text, str) and dialogues_text:
            dialogues_list = dialogues_text.split('\n')
        else:
            dialogues_list = [""]

        input_conv = {
            'dialogues': dialogues_list
        }
        agent2 = 'AIS'
        result = get_result(input_conv, agent2)
        return idx, result['reply']
    except Exception as e:
        return idx, f"ERROR: {e}"


def process_folder(json_folder, max_files=None, max_workers=30):
    """处理单个文件夹，返回 DataFrame"""
    sessions = load_sessions_from_json_files(json_folder, max_files=max_files)
    if not sessions:
        return pd.DataFrame()

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_session, session, idx) for idx, session in enumerate(sessions)]
        for future in as_completed(futures):
            idx, reply = future.result()
            sessions[idx]['reply'] = reply

    logger.info(f"文件夹 {json_folder} 处理完成，用时 {time.time()-start_time:.2f} 秒")

    # 转成 DataFrame，保留原始信息 + reply
    df = pd.DataFrame(sessions)
    return df


if __name__ == "__main__":
    base_dir = r"C:\Users\JOJO\Desktop\app\dataset\waihudatanew\extracted"  # 根目录
    # sub_folders = ["L1","L2","L3","L4","L5","L6","L7", "L8","L9"]  # 要处理的子文件夹
    output_excel = f"waihu_summary/sessions_results_AI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    # output_excel = f"waihu_summary/sessions_results_HandSplit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        # for folder in sub_folders:
        # for folder in sub_folders:
            folder_path = os.path.join(base_dir)
            sheet_name = os.path.basename(folder_path)
            df = process_folder(folder_path, max_files=None, max_workers=30)
            if not df.empty:
                # 保存到Excel时配置格式，确保换行符正确显示
                df.to_excel(writer, sheet_name=sheet_name, index=False)


    print(f"所有结果已保存到 {output_excel}")