#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将薪资数据整合到增强版球员评分系统中
为12人轮换阵容优化做准备
"""

import pandas as pd
import numpy as np

# 读取增强版球员评分数据和薪资数据
try:
    scores_df = pd.read_csv('second_dataset/nba_player_enhanced_scores.csv', encoding='utf-8-sig')
    salaries_df = pd.read_csv('initial_dataset/NBA Player Salaries_2024-25_1.csv', encoding='utf-8')
except UnicodeDecodeError:
    try:
        scores_df = pd.read_csv('second_dataset/nba_player_enhanced_scores.csv', encoding='Windows-1252')
        salaries_df = pd.read_csv('initial_dataset/NBA Player Salaries_2024-25_1.csv', encoding='Windows-1252')
    except:
        print("请确保文件路径正确，并检查文件编码")
        exit()

print(f"球员评分数据: {len(scores_df)} 条记录")
print(f"薪资数据: {len(salaries_df)} 条记录")

# 处理薪资数据
# 清理薪资列，移除美元符号和逗号，转换为数值
if 'Salary' in salaries_df.columns:
    salaries_df['Salary_Clean'] = salaries_df['Salary'].astype(str).str.replace('[\$,]', '', regex=True)
    # 处理可能的空值和非数值
    salaries_df['Salary_Clean'] = pd.to_numeric(salaries_df['Salary_Clean'], errors='coerce')
    salaries_df = salaries_df.dropna(subset=['Salary_Clean'])
    salaries_df['Salary_2023_2024'] = salaries_df['Salary_Clean'].astype('Int64')
else:
    print("警告: 薪资数据中未找到 'Salary' 列")
    print("可用列:", salaries_df.columns.tolist())

# 处理球员姓名匹配问题（去除多余空格，统一格式）
def clean_player_name(name):
    if pd.isna(name):
        return ""
    return str(name).strip().replace("'", "'")

scores_df['Player_Clean'] = scores_df['Player'].apply(clean_player_name)
salaries_df['Player_Clean'] = salaries_df['Player'].apply(clean_player_name)

# 处理重复球员记录，保留薪资最高的
salaries_df = salaries_df.sort_values(by='Salary_2023_2024', ascending=False).drop_duplicates(subset=['Player_Clean'], keep='first')

# 合并数据集（内连接，只保留有薪资数据的球员）
merged_df = scores_df.merge(
    salaries_df[['Player_Clean', 'Salary_2023_2024']],
    on='Player_Clean',
    how='inner'  # 改为内连接，只保留有薪资数据的球员
)

# 删除临时列
merged_df = merged_df.drop('Player_Clean', axis=1)

print(f"\n有完整薪资数据的球员: {len(merged_df)} 名")
print(f"移除了 {len(scores_df) - len(merged_df)} 名没有薪资数据的球员")

# 计算性价比指标
merged_df['Value_Score'] = (merged_df['Overall_Score'] / (merged_df['Salary_2023_2024'] / 1000000)).round(2)

# 按位置分类
def categorize_position(pos):
    if pd.isna(pos):
        return 'Unknown'
    pos_str = str(pos).upper()
    if 'PG' in pos_str:
        return 'PG'
    elif 'SG' in pos_str:
        return 'SG'
    elif 'SF' in pos_str:
        return 'SF'
    elif 'PF' in pos_str:
        return 'PF'
    elif 'C' in pos_str:
        return 'C'
    else:
        return 'Unknown'

merged_df['Primary_Position'] = merged_df['Pos'].apply(categorize_position)

# 选择输出列
output_df = merged_df[[
    'Player', 'Primary_Position', 'Pos', 'Age', 'G', 'MP',
    'Offensive_Score', 'Defensive_Score', 'Teamwork_Score', 'Stamina_Score', 'Overall_Score',
    'Salary_2023_2024', 'Value_Score'
]]

# 按综合评分排序
output_df = output_df.sort_values('Overall_Score', ascending=False)

# 保存结果
output_df.to_csv('second_dataset/nba_player_enhanced_scores_with_salary.csv', index=False, encoding='utf-8-sig')

print(f"\n数据整合完成!")
print(f"最终数据集包含 {len(output_df)} 名球员")

# 显示各位置球员数量分布
print("\n各位置球员数量分布:")
position_counts = output_df['Primary_Position'].value_counts()
for pos, count in position_counts.items():
    print(f"{pos}: {count} 名球员")

# 显示薪资统计
print(f"\n薪资统计:")
print(f"平均薪资: ${output_df['Salary_2023_2024'].mean():,.2f}")
print(f"中位数薪资: ${output_df['Salary_2023_2024'].median():,.2f}")
print(f"最高薪资: ${output_df['Salary_2023_2024'].max():,.2f}")
print(f"最低薪资: ${output_df['Salary_2023_2024'].min():,.2f}")

# 显示性价比最高的前10名球员
print("\n性价比最高的前10名球员:")
print("=" * 120)
print(f"{'排名':<4} {'球员':<20} {'位置':<8} {'综合评分':<8} {'薪资(百万)':<12} {'性价比':<8}")
print("-" * 120)
top_value_players = output_df.nlargest(10, 'Value_Score')
for i, (_, row) in enumerate(top_value_players.iterrows(), 1):
    print(f"{i:<4} {row['Player']:<20} {row['Primary_Position']:<8} {row['Overall_Score']:<8} "
          f"${row['Salary_2023_2024']/1000000:<11.2f} {row['Value_Score']:<8}")

print("\n文件已保存至: 'second_dataset/nba_player_enhanced_scores_with_salary.csv'")
