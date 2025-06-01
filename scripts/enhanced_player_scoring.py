#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
增强版NBA球员能力评分系统
新增体能属性，为12人轮换阵容建模做准备
"""

import pandas as pd
import numpy as np

# 读取数据集，指定分隔符和编码
try:
    data = pd.read_csv('initial_dataset/2023-2024 NBA Player Stats - Regular.csv',sep=";", encoding='ISO-8859-1')
except UnicodeDecodeError:
    data = pd.read_csv('initial_dataset/2023-2024 NBA Player Stats - Regular.csv',sep=";",encoding='Windows-1252')


# 1. 合并相同球员的数据
numeric_columns = ['G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%',
                   '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%',
                   'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

# 定义加权平均函数
def weighted_avg(group, cols, weight_col):
    result = {}
    for col in cols:
        if col in ['FG%', '3P%', '2P%', 'eFG%', 'FT%']:  # 百分比列
            valid_data = group.dropna(subset=[col, weight_col])
            if len(valid_data) > 0 and valid_data[weight_col].sum() > 0:
                result[col] = (valid_data[col] * valid_data[weight_col]).sum() / valid_data[weight_col].sum()
            else:
                result[col] = 0
        else:  # 其他数值列
            valid_data = group.dropna(subset=[col, weight_col])         
            if len(valid_data) > 0 and valid_data[weight_col].sum() > 0:
                result[col] = (valid_data[col] * valid_data[weight_col]).sum() / valid_data[weight_col].sum()
            else:
                result[col] = 0
    return pd.Series(result)

# 按球员姓名分组，合并数据
merged_data = data.groupby('Player').apply(
    lambda x: weighted_avg(x, numeric_columns, 'G')
).reset_index()

# 保留非数值列（Pos, Age），取最后一条记录的值
non_numeric = data[['Player', 'Pos', 'Age']].drop_duplicates(subset='Player', keep='last')
merged_data = merged_data.merge(non_numeric, on='Player')

# 2. 计算四个维度的能力评分

# 进攻能力评分 (考虑得分效率、投篮准确性、失误控制)
def calculate_offensive_score(row):
    try:
        # 基础得分效率
        scoring_efficiency = row['PTS'] * row['eFG%'] if pd.notna(row['eFG%']) and row['eFG%'] > 0 else 0
        
        # 投篮稳定性 (综合各种投篮方式)
        total_attempts = row['3PA'] + row['2PA'] + row['FTA']
        if total_attempts > 0:
            shooting_stability = (row['3P%'] * row['3PA'] + row['2P%'] * row['2PA'] + row['FT%'] * row['FTA']) / total_attempts
        else:
            shooting_stability = 0
            
        # 失误控制 (降低因失误造成的负面影响)
        turnover_control = max(0, 1 - (row['TOV'] / max(row['FGA'], 1)))
        
        return 0.5 * scoring_efficiency + 0.3 * shooting_stability * 100 + 0.2 * turnover_control * 100
    except:
        return 0

# 防守能力评分 (篮板、抢断、盖帽、犯规控制)
def calculate_defensive_score(row):
    try:
        # 防守贡献 (篮板、抢断、盖帽)
        defensive_stats = row['DRB'] + 2 * row['STL'] + 2 * row['BLK']
        
        # 犯规控制 (减少不必要犯规)
        foul_control = max(0, 1 - (row['PF'] / 6)) * 20
        
        return 0.8 * defensive_stats + 0.2 * foul_control
    except:
        return 0

# 团队合作能力评分 (助攻、进攻篮板、失误控制、上场时间稳定性)
def calculate_teamwork_score(row):
    try:
        # 助攻和进攻篮板贡献
        team_contribution = row['AST'] + 0.5 * row['ORB']
        
        # 球权保护 (助攻失误比)
        total_possessions = row['AST'] + row['FGA'] + row['TOV']
        ball_security = (1 - (row['TOV'] / max(total_possessions, 1))) * 50 if total_possessions > 0 else 0
        
        # 出场时间稳定性 (反映教练信任度)
        playing_time_factor = min(row['MP'] / 48, 1) * 30
        
        return 0.4 * team_contribution + 0.3 * ball_security + 0.3 * playing_time_factor
    except:
        return 0

# 新增：体能属性评分 (基于出场时间、出场次数、年龄、效率维持)
def calculate_stamina_score(row):
    try:
        # 出场持久性 (场均上场时间 * 出场场次比例)
        games_played_ratio = min(row['G'] / 82, 1.0)  # 假设赛季82场，最高为1
        playing_time_normalized = min(row['MP'] / 48, 1.0)  # 标准化到0-1
        endurance = playing_time_normalized * games_played_ratio * 40
        
        # 年龄因子 (分层次评分，避免阶跃)
        age = row['Age'] if pd.notna(row['Age']) else 27  # 默认年龄27岁
        if age <= 23:
            age_factor = 25  # 年轻球员，体能充沛
        elif age <= 27:
            age_factor = 30  # 黄金年龄，体能与经验平衡
        elif age <= 31:
            age_factor = 20  # 经验丰富，体能略有下降
        else:
            age_factor = 15  # 老将，体能下降但经验丰富
            
        # 效率维持 (分层次评分，避免阶跃函数)
        mp = row['MP']
        if mp >= 35:  # 核心球员级别
            load_tier = 4
            efficiency_base = 25
        elif mp >= 30:  # 主力球员级别  
            load_tier = 3
            efficiency_base = 20
        elif mp >= 20:  # 轮换球员级别
            load_tier = 2
            efficiency_base = 15
        else:  # 替补球员级别
            load_tier = 1
            efficiency_base = 10
            
        # 基于得分效率调整
        points_per_minute = row['PTS'] / max(row['MP'], 1)
        efficiency_adjustment = min(points_per_minute * 3, 10)  # 最高10分奖励
        efficiency_maintenance = efficiency_base + efficiency_adjustment
        
        # 首发稳定性 (连续性评分)
        starting_rate = row['GS'] / max(row['G'], 1) if row['G'] > 0 else 0
        starting_consistency = starting_rate * 20
        
        # 健康度 (基于出场比例)
        health_factor = games_played_ratio * 15
        
        return 0.25 * endurance + 0.2 * age_factor + 0.25 * efficiency_maintenance + 0.15 * starting_consistency + 0.15 * health_factor
    except:
        return 20  # 默认中等体能

# 应用评分函数
merged_data['Offensive_Score'] = merged_data.apply(calculate_offensive_score, axis=1)
merged_data['Defensive_Score'] = merged_data.apply(calculate_defensive_score, axis=1)
merged_data['Teamwork_Score'] = merged_data.apply(calculate_teamwork_score, axis=1)
merged_data['Stamina_Score'] = merged_data.apply(calculate_stamina_score, axis=1)

# 3. 标准化评分到0-100范围
def standardize_score(series):
    # 处理可能的异常值和NaN
    series = series.fillna(series.median())
    
    # 使用四分位数方法处理异常值
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # 限制异常值
    series_clipped = series.clip(lower_bound, upper_bound)
    
    min_score = series_clipped.min()
    max_score = series_clipped.max()
    
    if max_score == min_score:  # 防止除零错误
        return pd.Series([50] * len(series))  # 如果得分无差异，赋中值50
    
    standardized = (series_clipped - min_score) / (max_score - min_score) * 100
    return standardized.round(2)

# 标准化所有评分
merged_data['Offensive_Score'] = standardize_score(merged_data['Offensive_Score'])
merged_data['Defensive_Score'] = standardize_score(merged_data['Defensive_Score'])
merged_data['Teamwork_Score'] = standardize_score(merged_data['Teamwork_Score'])
merged_data['Stamina_Score'] = standardize_score(merged_data['Stamina_Score'])

# 计算综合评分
merged_data['Overall_Score'] = (
    0.3 * merged_data['Offensive_Score'] + 
    0.25 * merged_data['Defensive_Score'] + 
    0.25 * merged_data['Teamwork_Score'] + 
    0.2 * merged_data['Stamina_Score']
).round(2)

# 4. 筛选所需列并保存
output_data = merged_data[[
    'Player', 'Pos', 'Age', 'G', 'MP',
    'Offensive_Score', 'Defensive_Score', 'Teamwork_Score', 'Stamina_Score', 'Overall_Score'
]]

# 按综合评分排序
output_data = output_data.sort_values('Overall_Score', ascending=False)

# 保存结果
output_data.to_csv('second_dataset/nba_player_enhanced_scores.csv', index=False)

print("增强版球员能力评分计算完成!")
print(f"共处理 {len(output_data)} 名球员")
print("\n评分维度说明:")
print("- Offensive_Score: 进攻能力 (得分效率、投篮稳定性、失误控制)")
print("- Defensive_Score: 防守能力 (篮板、抢断、盖帽、犯规控制)")
print("- Teamwork_Score: 团队合作 (助攻、球权保护、上场时间)")
print("- Stamina_Score: 体能属性 (耐力、年龄因素、效率维持)")
print("- Overall_Score: 综合评分 (四个维度的加权平均)")

# 计算字符串的显示宽度（中文字符占 2 宽度，英文字符占 1 宽度）
def get_display_width(s):
    width = 0
    for char in str(s):
        # 中文字符（Unicode 范围大致为中文字符）
        if ord(char) >= 0x4E00 and ord(char) <= 0x9FFF:
            width += 2
        else:
            width += 1
    return width

# 显示前 10 名球员
print("\n综合评分前 10 名球员:")
print("=" * 100)

# 定义列宽（考虑中文字符和最大内容长度）
col_widths = {
    '排名': 6,    # 4（中文“排名”占 4 宽度） + 2（间距）
    '球员': 24,   # 适应最长球员姓名（如 "Giannis Antetokounmpo"，约 22 字符）
    '位置': 10,   # 8（中文“位置”占 4 宽度 + 英文如 "PF-C"） + 2（间距）
    '年龄': 6,    # 4（中文“年龄”占 4 宽度） + 2（间距）
    '进攻': 8,    # 6（数字如 100.00） + 2（间距）
    '防守': 8,    # 6（数字如 100.00） + 2（间距）
    '配合': 8,    # 6（数字如 100.00） + 2（间距）
    '体能': 8,    # 6（数字如 100.00） + 2（间距）
    '综合': 8     # 6（数字如 100.00） + 2（间距）
}

# 打印表头
header = (f"{'排名':<{col_widths['排名']}}"
          f"{'球员':<{col_widths['球员']}}"
          f"{'位置':<{col_widths['位置']}}"
          f"{'年龄':<{col_widths['年龄']}}"
          f"{'进攻':<{col_widths['进攻']}}"
          f"{'防守':<{col_widths['防守']}}"
          f"{'配合':<{col_widths['配合']}}"
          f"{'体能':<{col_widths['体能']}}"
          f"{'综合':<{col_widths['综合']}}")
print(header)
print("-" * 100)

# 打印球员数据
for i, (_, row) in enumerate(output_data.head(10).iterrows(), 1):
    # 格式化球员姓名，确保显示宽度适应
    player_name = row['Player']
    player_width = col_widths['球员'] - (get_display_width(player_name) - len(player_name))
    
    # 格式化年龄（处理 NaN）
    age = int(row['Age']) if pd.notna(row['Age']) else 'N/A'
    
    # 格式化评分（保留两位小数）
    print(f"{i:<{col_widths['排名']}}"
          f"{player_name:<{player_width}}"
          f"{row['Pos']:<{col_widths['位置']}}"
          f"{age:<{col_widths['年龄']}}"
          f"{row['Offensive_Score']:<6.2f}{''.ljust(col_widths['进攻'] - 6)}"
          f"{row['Defensive_Score']:<6.2f}{''.ljust(col_widths['防守'] - 6)}"
          f"{row['Teamwork_Score']:<6.2f}{''.ljust(col_widths['配合'] - 6)}"
          f"{row['Stamina_Score']:<6.2f}{''.ljust(col_widths['体能'] - 6)}"
          f"{row['Overall_Score']:<6.2f}{''.ljust(col_widths['综合'] - 6)}")