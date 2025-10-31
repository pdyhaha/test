# -*- coding: UTF-8 -*-
import pandas as pd
import time
import os
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from doubao_enterprise_v2 import get_result
from datetime import datetime


import pandas as pd

def load_sessions_from_excel(csv_file):
    """
    从单个 Excel 文件加载数据：
    - 按月份升序拼接所有 "op_tags: message"
    - 返回一个字符串
    """
    # Excel 文件无需尝试多种编码，直接读取
    try:
        df = pd.read_excel(csv_file, dtype=str)  # 替换 pd.read_csv 为 pd.read_excel
        print(f"成功读取 Excel 文件: {csv_file}")
    except Exception as e:
        print(f"读取 Excel 文件失败: {e}")
        raise ValueError("无法读取 Excel 文件，请确认文件格式")

    required_cols = {"message", "op_tags", "reply"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"文件 {csv_file} 缺少必要列: {required_cols - set(df.columns)}")

    # 提取月份数字用于排序（保持不变）
    df["month_num"] = df["op_tags"].str.extract(r"M(\d+)").astype(float)
    df = df.sort_values("month_num")

    # 拼接 "op_tags: message"（保持不变）
    combined_text = "\n".join(
        f"{row['op_tags']}-月度总结:\n {row['reply'].strip('{}')}"
        for _, row in df.iterrows() if pd.notna(row["message"])
    )
    print(combined_text)
    print(f"成功拼接 {len(df)} 条记录，结果长度 {len(combined_text)} 字符")
    return combined_text


def load_sum_content_text(csv_file):
    """
    从 CSV 文件中按月份递增顺序加载 sum_content_text
    只返回 sum_content_text 的拼接结果（按月份分组）
    """
    encodings_to_try = ["utf-8-sig", "utf-8", "gbk", "ansi"]

    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(csv_file, encoding=enc, dtype=str)
            print(f"使用编码 {enc} 成功读取")
            break
        except Exception as e:
            print(f"尝试编码 {enc} 失败: {e}")

    if df is None:
        raise ValueError("无法读取 CSV，请确认文件编码")

    if not {"op_tags", "sum_content_text"}.issubset(df.columns):
        raise ValueError("CSV 缺少必要列: op_tags 或 sum_content_text")
# 确保操作的是 DataFrame
    df = df.copy()
        # 提取月份数字
    df["month_num"] = df["op_tags"].str.extract(r"M(\d+)").astype(int)

    # 按月份升序排序
    df = df.sort_values("month_num")

    # 拼接所有 sum_content_text
    all_texts = "\n".join(df["sum_content_text"].dropna())

    print(f"成功加载并拼接 {df['month_num'].nunique()} 个月份的 sum_content_text")
    return all_texts


def load_sessions_from_csv(csv_file):
    """
    从单个 CSV 文件加载数据：
    - 按月份升序拼接所有 "op_tags: message"
    - 返回一个字符串
    """
    encodings_to_try = ["utf-8-sig", "utf-8", "gbk", "ansi"]

    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(csv_file, encoding=enc, dtype=str)
            print(f"使用编码 {enc} 成功读取")
            break
        except Exception as e:
            print(f"尝试编码 {enc} 失败: {e}")

    if df is None:
        raise ValueError("无法读取 CSV，请确认文件编码")

    required_cols = {"message", "op_tags","reply"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"文件 {csv_file} 缺少必要列: {required_cols - set(df.columns)}")

    # 提取月份数字用于排序
    df["month_num"] = df["op_tags"].str.extract(r"M(\d+)").astype(float)
    df = df.sort_values("month_num")

    # 拼接 "op_tags: message"
    combined_text = "\n".join(
        f"{row['op_tags']}-月度总结:\n {row['reply']}"
        for _, row in df.iterrows() if pd.notna(row["message"])
    )
    # 拼接所有非空 message（每行独立）
    # messages = [
    #     row["message"]
    #     for _, row in df.iterrows()
    #     if pd.notna(row["message"])
    # ]
    # print(combined_text)
    print(f"成功拼接 {len(df)} 条记录，结果长度 {len(combined_text)} 字符")
    return combined_text


def load_sessions_from_csv1(csv_file):
    """
    从单个 CSV 文件加载数据：
    - 按月份升序返回包含 user_id、class_id、op_tags、message 的字典列表
    """
    encodings_to_try = ["utf-8-sig", "utf-8", "gbk", "ansi"]

    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(csv_file, encoding=enc, dtype=str)
            print(f"使用编码 {enc} 成功读取")
            break
        except Exception as e:
            print(f"尝试编码 {enc} 失败: {e}")

    if df is None:
        raise ValueError("无法读取 CSV，请确认文件编码")

    # 新增：检查必要列是否包含 user_id 和 class_id
    required_cols = {"message", "op_tags", "user_id", "class_id"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"文件 {csv_file} 缺少必要列: {required_cols - set(df.columns)}")

    # 提取月份数字用于排序
    df["month_num"] = df["op_tags"].str.extract(r"M(\d+)").astype(float)
    df = df.sort_values("month_num")

    # 收集完整字段（包含 user_id、class_id、op_tags、message）
    sessions_data = [
        {
            "user_id": row["user_id"],
            "class_id": row["class_id"],
            "op_tags": row["op_tags"],
            "message": row["message"]
        }
        for _, row in df.iterrows()
        if pd.notna(row["message"])  # 过滤空消息
    ]

    print(f"成功提取 {len(sessions_data)} 条记录（包含 user_id、class_id、op_tags）")
    return sessions_data

def process_session(session, idx):
    """处理一个 session"""
    try:
        input_conv = {
            "sum_content_text": session.get("sum_content_text", ""),
            # "op_tags": session.get("op_tags", ""),
            # "message": session.get("message", ""),

        }
        # print(input_conv)
        agent2 = "yy"
        result = get_result(input_conv, agent2)
        return idx, result.get("reply", "")
    except Exception as e:
        return idx, f"ERROR: {e}"


def process_csv1(csv_file, max_workers=30):
    """处理单个 CSV 文件，返回包含 user_id、class_id、op_tags、message、reply 的 DataFrame"""
    # 加载包含完整字段的会话数据（user_id、class_id、op_tags、message）
    sessions = load_sessions_from_csv1(csv_file)

    if not sessions:
        return pd.DataFrame()

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 直接提交原始会话数据（已包含 user_id 等字段）
        futures = [executor.submit(process_session, session, idx) for idx, session in enumerate(sessions)]
        for future in as_completed(futures):
            idx, reply = future.result()
            # 将 reply 存入会话（覆盖 sum_content_text 的逻辑通过列名映射实现）
            sessions[idx]["reply"] = reply

    logger.info(f"文件 {csv_file} 处理完成，共处理 {len(sessions)} 条记录，用时 {time.time() - start_time:.2f} 秒")

    # 直接转换为 DataFrame，自动包含所有字段：user_id、class_id、op_tags、message、reply
    df = pd.DataFrame(sessions)
    return df


def process_csv(csv_file, max_workers=30):
    """处理单个 CSV 文件，返回 DataFrame"""
    combined_text = load_sessions_from_excel(csv_file)
    # combined_text = load_sessions_from_csv(csv_file)
    # print(combined_text)
    if not combined_text:
        return pd.DataFrame()

    # 这里封装成一个 dict（单条 session）
    sessions = [{"sum_content_text": combined_text}]
    print(sessions)
    # sessions = [{"message": msg} for msg in combined_text]

    start_time = time.time()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_session, session, idx) for idx, session in enumerate(sessions)]
        for future in as_completed(futures):
            idx, reply = future.result()
            sessions[idx]["reply"] = reply

    logger.info(f"文件 {csv_file} 处理完成，用时 {time.time()-start_time:.2f} 秒")

    df = pd.DataFrame(sessions)
    return df


if __name__ == "__main__":
    input_csv = r"C:\Users\JOJO\Desktop\app\model_pipeline\summary\danyue_session_result\73728443_extract20251030_163743.xlsx" # 只处理一个 CSV
    # print(input_csv)
    # 创建session_result文件夹
    output_dir = "duoyue_session_result"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建文件夹: {output_dir}")
    
    output_excel = os.path.join(output_dir, f"73728443_extract{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

    df = process_csv(input_csv, max_workers=30)
    if not df.empty:
        df.to_excel(output_excel, index=False)

    print(f"结果已保存到 {output_excel}")



