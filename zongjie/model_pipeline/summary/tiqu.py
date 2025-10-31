import pandas as pd
import json
import ast
import re
import argparse


def parse_message_cell(x):
    """解析message字段提取user_id和class_id"""
    if pd.isna(x):
        return {}
    s = str(x).strip()

    # 尝试JSON解析
    try:
        return json.loads(s)
    except:
        pass

    # 尝试Python literal
    try:
        return ast.literal_eval(s)
    except:
        pass

    # 正则表达式提取
    res = {}
    m = re.search(r"""['"]?user_id['"]?\s*:\s*['"]?([^'",}\]\s]+)['"]?""", s)
    if m:
        res['user_id'] = m.group(1)
    m = re.search(r"""['"]?class_id['"]?\s*:\s*['"]?([^'",}\]\s]+)['"]?""", s)
    if m:
        res['class_id'] = m.group(1)
    return res


def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='数据筛选工具')
    parser.add_argument('--user_id', type=str, default='19126754', help='要筛选的user_id，留空则不筛选')
    parser.add_argument('--class_id', type=str, default='', help='要筛选的class_id，留空则不筛选')
    parser.add_argument('--input_file', type=str, default='运营总结存量.csv', help='输入文件路径')
    parser.add_argument('--output_file', type=str, default='19126754.csv', help='输出文件路径')
    parser.add_argument('--no_filter', action='store_true', help='不进行筛选，输出所有数据')

    args = parser.parse_args()

    # 只读取message列
    df = pd.read_csv(args.input_file, usecols=['message'], dtype={"message": str})

    # 提取user_id和class_id
    df["message_parsed"] = df["message"].apply(parse_message_cell)
    df["user_id"] = df["message_parsed"].apply(lambda d: d.get("user_id", "")).astype(str).str.strip()
    df["class_id"] = df["message_parsed"].apply(lambda d: d.get("class_id", "")).astype(str).str.strip()

    # 根据参数决定是否筛选
    if args.no_filter:
        # 不筛选，输出所有数据
        filtered_df = df
        print("不进行筛选，输出所有数据")
    elif args.user_id or args.class_id:
        # 构建筛选条件
        conditions = []
        if args.user_id:
            conditions.append(df["user_id"] == args.user_id)
        if args.class_id:
            conditions.append(df["class_id"] == args.class_id)

        # 应用筛选条件
        if conditions:
            filtered_df = df[pd.concat(conditions, axis=1).all(axis=1)]
        else:
            filtered_df = df
    else:
        # 默认不筛选
        filtered_df = df
        print("未指定筛选条件，输出所有数据")

    # 保存结果
    filtered_df[['message', 'user_id', 'class_id']].to_csv(args.output_file, index=False)

    print(f"找到 {len(filtered_df)} 条记录")
    print(f"结果已保存到: {args.output_file}")


if __name__ == "__main__":
    main()