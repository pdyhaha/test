# -*- coding: UTF-8 -*-
import pandas as pd
import time
import concurrent
import os
from data_merge import merge_data
from functools import partial
from doubao_enterprise_v2 import get_result as get_result_from_doubao
# from result_anal_asv_L3 import result_anal_staff_agent_label_L3
# from result_anal.result_anal_asv_L3_v2 import result_anal_staff_agent_label_L3
# from result_anal.result_anal_asv_L3_v3 import result_anal_staff_agent_label_L3


# def get_result(input,agent_name):
#     result = get_result_from_doubao(input,agent_name)
#     return result

def get_result(input,brand,agent_name):
    result = get_result_from_doubao(input,brand,agent_name)
    return result

# def llm_pre_v2(df,agent_name,output_root,cols,input_col):
#
#     output_dir = f'{output_root}/{agent_name}/'
#
#     # 使用os.makedirs创建新目录
#     os.makedirs(output_dir, exist_ok=True)
#     print(f'Directory {output_dir} created successfully')
#
#     # 使用 partial 将 get_result 包装成只接受一个参数的函数
#     get_result_partial = partial(get_result, agent_name=agent_name)
#
#
#     #############################################################
#     # 按顺序分组，每组包含    max_workers    个元素
#     group_size = 50
#     groups = [df.iloc[i:i + group_size] for i in range(0, len(df), group_size)]
#     len_groups = len(groups)
#
#     output_start = 0
#     output_end = len_groups
#     output_group_size = 10
#     output_groups = [list(range(i, min(i + output_group_size, output_end))) for i in
#                      range(output_start, output_end, output_group_size)]
#
#     print(f'count_data:{len(df)}')
#     print(f'group_size:{group_size}')
#     print(f'count_groups:{len_groups}')
#     print('count_iters:', len(output_groups))
#     print()
#
#     total_time = 0
#     for _, output_group in enumerate(output_groups):
#         # if _ < 8:
#         #     continue
#
#
#         outs = {col:[] for col in cols}
#         outs['reply'] = []
#         outs['cost'] = []
#
#         for i in output_group:
#             data_chat = groups[i]
#             start_time = time.time()
#
#             for col in cols:
#                 outs[col].extend(list(data_chat[col]))
#
#             group_input = list(data_chat[input_col])
#
#             # 使用 ThreadPoolExecutor 并行发起请求
#             with concurrent.futures.ThreadPoolExecutor(max_workers=group_size) as executor:
#                 results = list(executor.map(get_result_partial, group_input))
#
#             end_time = time.time()
#             elapsed_time = end_time - start_time
#             print(f"iter {_} group {i} 运行时间: {elapsed_time} 秒")
#
#             total_time += elapsed_time
#             time.sleep(2)
#
#             # 获取每个元组中的第一个和第二个元素
#             group_reply = [item['reply'] for item in results]
#             group_cost = [item['cost'] for item in results]
#
#
#             outs['reply'].extend(group_reply)
#             outs['cost'].extend(group_cost)
#
#         output_data = pd.DataFrame(outs)
#
#         output_data.to_csv(f'{output_dir}result_{_}.csv', index=False)
#
#         print()
#     print()
#     print(f"total_time:{total_time}")
#     merge_data(output_dir)



def llm_pre_v3(df, agent_name, output_root, cols, input_col, brand_col):
    output_dir = f'{output_root}/{agent_name}/'

    # 使用os.makedirs创建新目录
    os.makedirs(output_dir, exist_ok=True)
    print(f'Directory {output_dir} created successfully')

    #############################################################
    # 按顺序分组，每组包含 max_workers 个元素
    group_size = 50
    groups = [df.iloc[i:i + group_size] for i in range(0, len(df), group_size)]
    len_groups = len(groups)

    output_start = 0
    output_end = len_groups
    output_group_size = 10
    output_groups = [list(range(i, min(i + output_group_size, output_end))) for i in
                     range(output_start, output_end, output_group_size)]

    print(f'count_data:{len(df)}')
    print(f'group_size:{group_size}')
    print(f'count_groups:{len_groups}')
    print('count_iters:', len(output_groups))
    print()

    total_time = 0
    for _, output_group in enumerate(output_groups):
        outs = {col: [] for col in cols}
        outs['reply'] = []
        outs['cost'] = []

        for i in output_group:
            data_chat = groups[i]
            start_time = time.time()

            for col in cols:
                outs[col].extend(list(data_chat[col]))

            group_inputs = list(data_chat[input_col])
            group_brands = list(data_chat[brand_col])

            # 使用 ThreadPoolExecutor 并行发起请求
            with concurrent.futures.ThreadPoolExecutor(max_workers=group_size) as executor:
                # 使用 lambda 函数将三个参数传递给 get_result
                results = list(executor.map(
                    lambda input, brand: get_result(input, brand, agent_name),
                    group_inputs,
                    group_brands
                ))

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"iter {_} group {i} 运行时间: {elapsed_time} 秒")

            total_time += elapsed_time
            time.sleep(2)

            # 获取每个元组中的第一个和第二个元素
            group_reply = [item['reply'] for item in results]
            group_cost = [item['cost'] for item in results]

            outs['reply'].extend(group_reply)
            outs['cost'].extend(group_cost)

        output_data = pd.DataFrame(outs)
        output_data.to_csv(f'{output_dir}result_{_}.csv', index=False)
        print()

    print()
    print(f"total_time:{total_time}")
    merge_data(output_dir)

if __name__ == "__main__":


    df = pd.read_excel('data/jingping.xlsx')
    df = df[df['if_valid'] == 1]
    # df = df[df['tag'] != '夏令营']
    df = df[df['tag'] == '夏令营']

    print(len(df))
    brands = list(set(df['tag']))
    # df = df[:1000]

    for brand in brands:
        print(f'-------brand:{brand}--------')
        df_brand = df[df['tag'] == brand]
        if len(df_brand) > 5000:
            df_brand = df_brand.sample(n=5000, random_state=42)  # 设置random_state保证可重复性
        print(f'len df brand : {len(df_brand)}')
        # agent_names = ['jp']
        agent_names = ['jp_summer']
        for agent in agent_names:
            llm_pre_v3(df_brand,agent,output_root=f'output/jp_summer/{brand}',cols = ['科目','会话ID','会话日期','用户ID','老师ID','text','tag'],input_col='text',brand_col='tag')
        print(f'-------brand:{brand} done--------')
        print()



    # # df = pd.read_csv('output/l3/staff_agent_L3/result_total.csv')
    # df = pd.read_csv('output/l3_v3/staff_agent_L3/result_total.csv')
    # df['label_results'] = df['reply'].apply(result_anal_staff_agent_label_L3)
    #
    # df_exploded = df.explode('label_results')
    # # 假设 df_exploded 是已展开的 DataFrame
    # df_exploded = df_exploded.reset_index(drop=True)  # 关键步骤：重置索引
    #
    # # 标准化 JSON 数据并合并
    # df_normalized = pd.json_normalize(df_exploded['label_results'])
    # df_final = pd.concat([
    #     df_exploded.drop('label_results', axis=1),
    #     df_normalized
    # ], axis=1)
    #
    # cols_to_keep = ['s_id', 'input',  'reply', 'l1', 'l2', 'l3']
    # df_final = df_final[cols_to_keep]
    #
    # df_final.to_excel('output/l3_v3/test3.xlsx')
