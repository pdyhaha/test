# -*- coding: UTF-8 -*-
import os
import pandas as pd
import time




def merge_data(folder_path):

    # 获取文件夹下所有 xlsx 文件的文件名
    # xlsx_files = [file for file in os.listdir(folder_path) if file.endswith('.xlsx') and 'total' not in file]
    xlsx_files = [file for file in os.listdir(folder_path) if file.endswith('.csv') and 'total' not in file]
    # print(xlsx_files)

    # 初始化一个空的 DataFrame 用于存储合并后的数据
    merged_df = pd.DataFrame()

    # 遍历所有 xlsx 文件并合并到一个 DataFrame 中
    for file in xlsx_files:
        file_path = os.path.join(folder_path, file)
        # print(file_path)
        # df = pd.read_excel(file_path)
        df = pd.read_csv(file_path)

        merged_df = pd.concat([merged_df, df], ignore_index=True)

    # 将合并后的 DataFrame 写入新的 xlsx 文件
    output_file_path = '{}result_total.csv'.format(folder_path)
    # output_file_path = '{}result_total.xlsx'.format(folder_path)
    merged_df.to_csv(output_file_path, index=False)
    # merged_df.to_excel(output_file_path, index=False)

    print(f'Merged data written to {output_file_path},the length of merged data is {len(merged_df)}')


def delete_data(folder_path):
    xlsx_files = [file for file in os.listdir(folder_path) if file.endswith('.xlsx') and 'total' not in file]

    # 删除原始文件
    for file in xlsx_files:
        file_path = os.path.join(folder_path, file)
        os.remove(file_path)


if __name__ == "__main__":
    # # 文件夹路径
    folder_path = 'output/gpt/学习能力欠缺 或 培养目标/'
    merge_data(folder_path)


    # df1 = pd.read_excel(r'/Users/pai/PycharmProjects/pythonProject/jojo/KB/query_extract/output/0103/result_total.xlsx')
    # df2 = pd.read_excel(r'/Users/pai/PycharmProjects/pythonProject/jojo/KB/query_extract/客服data_process/output/231115-231215_query&answer_queryLen8-50.xlsx')
    # df2 = df2.drop_duplicates(subset = 'conversation')
    #
    # # 使用 merge 将 df2 的 answer 列的值替换 df1 中相应 conversation 的行
    # merged_df = pd.merge(df1, df2[['conversation', 'answer']], on='conversation', how='left')
    #
    # # 如果 df1 中的 conversation 在 df2 中没有对应项，保留原始的 answer 列的值
    # merged_df['answer'] = merged_df['answer_y'].fillna(merged_df['answer_x'])
    #
    # # 删除多余的列
    # merged_df = merged_df.drop(columns=['answer_x', 'answer_y'])
    # print(len(merged_df))
    #
    # merged_df.to_excel('output/0104/result_total.xlsx')

