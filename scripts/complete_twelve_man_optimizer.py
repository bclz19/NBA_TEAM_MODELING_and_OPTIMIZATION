# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# """
# NBA 12人轮换阵容优化模型
# 支持多种战术风格：攻击型、防守型、均衡型
# """

# import pandas as pd
# import numpy as np
# from pulp import *

# class TeamOptimizer:
#     def __init__(self, data_file='second_dataset/nba_player_enhanced_scores_with_salary.csv'):
#         """初始化优化器"""
#         try:
#             self.df = pd.read_csv(data_file)
#             print(f"成功加载数据: {len(self.df)} 名球员")
#         except FileNotFoundError:
#             print(f"错误: 找不到文件 {data_file}")
#             print("请先运行数据预处理脚本")
#             return
        
#         # 确保Primary_Position列存在
#         if 'Primary_Position' not in self.df.columns:
#             self.df['Primary_Position'] = self.df['Pos'].apply(self._categorize_position)
        
#         # 过滤掉综合评分过低的球员（提高求解效率）
#         self.df = self.df[self.df['Overall_Score'] >= 20]
        
#         # 确保所有必要的列存在
#         required_columns = ['Player', 'Pos', 'Age', 'Offensive_Score', 'Defensive_Score', 
#                            'Teamwork_Score', 'Stamina_Score', 'Overall_Score', 'Salary_2023_2024']
#         for col in required_columns:
#             if col not in self.df.columns:
#                 raise ValueError(f"数据缺少必要的列: {col}")
        
#         print(f"可选球员总数: {len(self.df)}")
#         self._show_position_distribution()
        
#     def _categorize_position(self, pos):
#         """位置分类"""
#         if pd.isna(pos):
#             return 'Unknown'
#         pos_str = str(pos).upper()
#         if 'PG' in pos_str:
#             return 'PG'
#         elif 'SG' in pos_str:
#             return 'SG'
#         elif 'SF' in pos_str:
#             return 'SF'
#         elif 'PF' in pos_str:    
#             return 'PF'
#         elif 'C' in pos_str:
#             return 'C'
#         else:
#             return 'Unknown'
    
#     def _show_position_distribution(self):
#         """显示位置分布"""
#         position_counts = self.df['Primary_Position'].value_counts()
#         print("\n各位置球员数量分布:")
#         for pos, count in position_counts.items():
#             print(f"  {pos}: {count} 名球员")
    
#     def optimize_team(self, team_style, salary_cap=140000000, min_score_threshold=50):
#         """
#         优化12人轮换阵容
        
#         Parameters:
#         - team_style: 'offensive', 'defensive', 'balanced'
#         - salary_cap: 薪资帽 (默认1.4亿美元)
#         - min_score_threshold: 最低综合评分阈值
#         """
        
#         # 过滤球员
#         filtered_df = self.df[self.df['Overall_Score'] >= min_score_threshold].copy()
#         print(f"\n符合条件的球员: {len(filtered_df)}")
        
#         if len(filtered_df) < 12:
#             print("错误: 符合条件的球员数量不足12人，无法组成阵容")
#             return None
        
#         # 设置战术权重
#         if team_style == 'offensive':
#             w_off, w_def, w_team, w_stam = 0.5, 0.2, 0.2, 0.1
#             style_name = "攻击型"
#         elif team_style == 'crazy':
#             w_off, w_def, w_team, w_stam = 0.85, 0.05, 0.05, 0.05
#             style_name = "疯狂攻击型"
#         elif team_style == 'defensive':
#             w_off, w_def, w_team, w_stam = 0.2, 0.5, 0.2, 0.1
#             style_name = "防守型"
#         elif team_style == "turtle":
#             w_off, w_def, w_team, w_stam = 0.05, 0.8, 0.05, 0.1
#             style_name = "超级防守型"  
#         else:  # balanced
#             w_off, w_def, w_team, w_stam = 0.3, 0.3, 0.25, 0.15
#             style_name = "均衡型"
        
#         print(f"战术风格: {style_name}")
#         print(f"权重分配 - 进攻:{w_off:.1%}, 防守:{w_def:.1%}, 配合:{w_team:.1%}, 体能:{w_stam:.1%}")
        
#         # 计算加权评分
#         filtered_df['Weighted_Score'] = (
#             w_off * filtered_df['Offensive_Score'] +
#             w_def * filtered_df['Defensive_Score'] +
#             w_team * filtered_df['Teamwork_Score'] +
#             w_stam * filtered_df['Stamina_Score']
#         )
        
#         # 创建优化问题
#         prob = LpProblem("NBA_12Man_Rotation", LpMaximize)
        
#         # 创建决策变量
#         player_vars = {}
#         for i, row in filtered_df.iterrows():
#             safe_name = (row['Player'].replace(' ', '_').replace('.', '')
#                         .replace("'", '').replace('-', '_').replace(',', ''))
#             player_vars[row['Player']] = LpVariable(f"Select_{safe_name}_{i}", 0, 1, LpBinary)
        
#         # 目标函数：最大化加权评分
#         prob += lpSum([filtered_df.loc[i, 'Weighted_Score'] * player_vars[filtered_df.loc[i, 'Player']] 
#                       for i in filtered_df.index])
        
#         # 约束条件1：选择12名球员
#         prob += lpSum([player_vars[row['Player']] for _, row in filtered_df.iterrows()]) == 12
        
#         # 约束条件2：位置分配约束
#         positions = ['PG', 'SG', 'SF', 'PF', 'C']
#         for pos in positions:
#             pos_players = filtered_df[filtered_df['Primary_Position'] == pos]
#             if len(pos_players) > 0:
#                 prob += lpSum([player_vars[row['Player']] for _, row in pos_players.iterrows()]) >= 2
#                 prob += lpSum([player_vars[row['Player']] for _, row in pos_players.iterrows()]) <= 3
#             else:
#                 print(f"警告: 位置 {pos} 没有符合条件的球员，可能导致优化失败")
        
#         # 约束条件3：薪资限制
#         prob += lpSum([filtered_df.loc[i, 'Salary_2023_2024'] * player_vars[filtered_df.loc[i, 'Player']] 
#                       for i in filtered_df.index]) <= salary_cap
        
#         # 约束条件4：确保有足够的首发球员（5人综合评分>70）
#         high_score_players = filtered_df[filtered_df['Overall_Score'] > 70]
#         if len(high_score_players) >= 5:
#             prob += lpSum([player_vars[row['Player']] for _, row in high_score_players.iterrows()]) >= 5
#         else:
#             print(f"警告: 综合评分>70的球员不足5人，仅有 {len(high_score_players)} 人")
        
#         # 约束条件5：年龄结构平衡
#         young_players = filtered_df[filtered_df['Age'] <= 25]  # 年轻球员
#         veteran_players = filtered_df[filtered_df['Age'] >= 30]  # 老将
        
#         if len(young_players) > 0:
#             prob += lpSum([player_vars[row['Player']] for _, row in young_players.iterrows()]) >= 2
#             prob += lpSum([player_vars[row['Player']] for _, row in young_players.iterrows()]) <= 6
#         else:
#             print("警告: 没有年龄<=25岁的年轻球员")
        
#         if len(veteran_players) > 0:
#             prob += lpSum([player_vars[row['Player']] for _, row in veteran_players.iterrows()]) >= 2
#             prob += lpSum([player_vars[row['Player']] for _, row in veteran_players.iterrows()]) <= 6
#         else:
#             print("警告: 没有年龄>=30岁的老将球员")
        
#         # 约束条件6：确保综合实力下限
#         prob += lpSum([filtered_df.loc[i, 'Overall_Score'] * player_vars[filtered_df.loc[i, 'Player']] 
#                       for i in filtered_df.index]) >= 12 * 60  # 平均综合评分至少60
        
#         print("\n开始求解优化问题...")
#         # 求解问题
#         prob.solve(PULP_CBC_CMD(msg=0))
        
#         # 检查求解状态
#         if prob.status != 1:
#             print(f"优化失败，状态: {LpStatus[prob.status]}")
#             if prob.status == -1:
#                 print("建议: 放宽约束条件（如降低min_score_threshold或增加salary_cap）")
#             return None
        
#         # 收集结果
#         selected_players = []
#         for i, row in filtered_df.iterrows():
#             if value(player_vars[row['Player']]) == 1:
#                 selected_players.append(row)
        
#         result = {
#             'players': pd.DataFrame(selected_players),
#             'objective_value': value(prob.objective),
#             'team_style': style_name,
#             'weights': (w_off, w_def, w_team, w_stam),
#             'constraints': {
#                 'salary_cap': salary_cap,
#                 'min_score_threshold': min_score_threshold
#             }
#         }
        
#         return result
    
#     def display_results(self, result):
#         """显示优化结果"""
#         if result is None:
#             return
        
#         selected_df = result['players']
        
#         print("\n" + "="*100)
#         print(f"🏀 NBA 12人轮换阵容优化结果 - {result['team_style']}风格")
#         print("="*100)
        
#         # 按位置和综合评分排序显示
#         selected_df = selected_df.sort_values(['Primary_Position', 'Overall_Score'], ascending=[True, False])
        
#         # 计算字符串的显示宽度（中文字符占 2 宽度，英文字符占 1 宽度）
#         def get_display_width(s):
#             width = 0
#             for char in str(s):
#                 if ord(char) >= 0x4E00 and ord(char) <= 0x9FFF:  # 中文字符
#                     width += 2
#                 else:
#                     width += 1
#             return width
    
#         # 动态计算列宽
#         col_widths = {
#             '位置': max(8, get_display_width('位置')),  # 至少 8 宽度
#             '球员姓名': max(24, max(selected_df['Player'].apply(get_display_width)) + 2),  # 适应最长球员姓名
#             '年龄': max(6, get_display_width('年龄')),  # 至少 6 宽度
#             '进攻': max(8, get_display_width('进攻')),  # 至少 8 宽度
#             '防守': max(8, get_display_width('防守')),  # 至少 8 宽度
#             '配合': max(8, get_display_width('配合')),  # 至少 8 宽度
#             '体能': max(8, get_display_width('体能')),  # 至少 8 宽度
#             '综合': max(8, get_display_width('综合')),  # 至少 8 宽度
#             '薪资(百万)': max(14, get_display_width('薪资(百万)'))  # 至少 14 宽度
#         }
    
#         # 打印表头
#         print(f"{'位置':<{col_widths['位置']}}"
#               f"{'球员姓名':<{col_widths['球员姓名']}}"
#               f"{'年龄':<{col_widths['年龄']}}"
#               f"{'进攻':<{col_widths['进攻']}}"
#               f"{'防守':<{col_widths['防守']}}"
#               f"{'配合':<{col_widths['配合']}}"
#               f"{'体能':<{col_widths['体能']}}"
#               f"{'综合':<{col_widths['综合']}}"
#               f"{'薪资(百万)':<{col_widths['薪资(百万)']}}")
#         print("-" * 100)
        
#         total_salary = 0
#         total_scores = {'off': 0, 'def': 0, 'team': 0, 'stam': 0, 'overall': 0}
#         position_counts = {}
        
#         for _, row in selected_df.iterrows():
#             pos = row['Primary_Position']
#             position_counts[pos] = position_counts.get(pos, 0) + 1
            
#             total_salary += row['Salary_2023_2024']
#             total_scores['off'] += row['Offensive_Score']
#             total_scores['def'] += row['Defensive_Score']
#             total_scores['team'] += row['Teamwork_Score']
#             total_scores['stam'] += row['Stamina_Score']
#             total_scores['overall'] += row['Overall_Score']
            
#             print(f"{pos:<{col_widths['位置']}}"
#                   f"{row['Player']:<{col_widths['球员姓名']}}"
#                   f"{int(row['Age']):<{col_widths['年龄']}}"
#                   f"{row['Offensive_Score']:<{col_widths['进攻']}.1f}"
#                   f"{row['Defensive_Score']:<{col_widths['防守']}.1f}"
#                   f"{row['Teamwork_Score']:<{col_widths['配合']}.1f}"
#                   f"{row['Stamina_Score']:<{col_widths['体能']}.1f}"
#                   f"{row['Overall_Score']:<{col_widths['综合']}.1f}"
#                   f"${row['Salary_2023_2024']/1000000:<{col_widths['薪资(百万)']-1}.2f}")
        
#         print("-" * 100)
#         print(f"{'平均':<{col_widths['位置']}}"
#               f"{'':<{col_widths['球员姓名']}}"
#               f"{'':<{col_widths['年龄']}}"
#               f"{total_scores['off']/12:<{col_widths['进攻']}.1f}"
#               f"{total_scores['def']/12:<{col_widths['防守']}.1f}"
#               f"{total_scores['team']/12:<{col_widths['配合']}.1f}"
#               f"{total_scores['stam']/12:<{col_widths['体能']}.1f}"
#               f"{total_scores['overall']/12:<{col_widths['综合']}.1f}"
#               f"${total_salary/12000000:<{col_widths['薪资(百万)']-1}.2f}")
        
#         print("\n📊 球队统计摘要:")
#         print(f"  总薪资: ${total_salary/1000000:.2f}百万 (预算利用率: {total_salary/result['constraints']['salary_cap']:.1%})")
#         print(f"  平均年龄: {selected_df['Age'].mean():.1f}岁")
#         print(f"  综合实力: {total_scores['overall']/12:.1f}分")
#         print(f"  性价比: {total_scores['overall']/(total_salary/1000000):.2f}分/百万美元")
        
#         print("\n🏟️ 位置配置:")
#         for pos in ['PG', 'SG', 'SF', 'PF', 'C']:
#             count = position_counts.get(pos, 0)
#             print(f"  {pos}: {count} 名球员")

# # 主程序
# if __name__ == "__main__":
#     optimizer = TeamOptimizer()
#     result = optimizer.optimize_team(team_style='turtle',salary_cap=150000000)
#     optimizer.display_results(result)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NBA 12人轮换阵容优化模型
生成均衡型12人名单，并保存到CSV文件
"""

import pandas as pd
import numpy as np
from pulp import *

class TeamOptimizer:
    def __init__(self, data_file='second_dataset/nba_player_enhanced_scores_with_salary.csv', output_file='second_dataset/selected_team.csv'):
        """初始化优化器"""
        self.output_file = output_file
        try:
            self.df = pd.read_csv(data_file)
            print(f"成功加载数据: {len(self.df)} 名球员")
        except FileNotFoundError:
            print(f"错误: 找不到文件 {data_file}")
            print("请先运行数据预处理脚本")
            return
        
        # 确保Primary_Position列存在
        if 'Primary_Position' not in self.df.columns:
            self.df['Primary_Position'] = self.df['Pos'].apply(self._categorize_position)
        
        # 过滤掉综合评分过低的球员（提高求解效率）
        self.df = self.df[self.df['Overall_Score'] >= 20]
        
        # 确保所有必要的列存在
        required_columns = ['Player', 'Pos', 'Age', 'Offensive_Score', 'Defensive_Score', 
                           'Teamwork_Score', 'Stamina_Score', 'Overall_Score', 'Salary_2023_2024']
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"数据缺少必要的列: {col}")
        
        print(f"可选球员总数: {len(self.df)}")
        self._show_position_distribution()
        
    def _categorize_position(self, pos):
        """位置分类"""
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
    
    def _show_position_distribution(self):
        """显示位置分布"""
        position_counts = self.df['Primary_Position'].value_counts()
        print("\n各位置球员数量分布:")
        for pos, count in position_counts.items():
            print(f"  {pos}: {count} 名球员")
    
    def optimize_team(self, salary_cap=140000000, min_score_threshold=50):
        """
        优化12人轮换阵容（强制均衡型）
        
        Parameters:
        - salary_cap: 薪资帽 (默认1.4亿美元)
        - min_score_threshold: 最低综合评分阈值
        """
        
        # 过滤球员
        filtered_df = self.df[self.df['Overall_Score'] >= min_score_threshold].copy()
        print(f"\n符合条件的球员: {len(filtered_df)}")
        
        if len(filtered_df) < 12:
            print("错误: 符合条件的球员数量不足12人，无法组成阵容")
            return None
        
        # 设置均衡型权重
        w_off, w_def, w_team, w_stam = 0.3, 0.3, 0.25, 0.15
        style_name = "均衡型"
        
        print(f"战术风格: {style_name}")
        print(f"权重分配 - 进攻:{w_off:.1%}, 防守:{w_def:.1%}, 配合:{w_team:.1%}, 体能:{w_stam:.1%}")
        
        # 计算加权评分
        filtered_df['Weighted_Score'] = (
            w_off * filtered_df['Offensive_Score'] +
            w_def * filtered_df['Defensive_Score'] +
            w_team * filtered_df['Teamwork_Score'] +
            w_stam * filtered_df['Stamina_Score']
        )
        
        # 创建优化问题
        prob = LpProblem("NBA_12Man_Rotation", LpMaximize)
        
        # 创建决策变量
        player_vars = {}
        for i, row in filtered_df.iterrows():
            safe_name = (row['Player'].replace(' ', '_').replace('.', '')
                        .replace("'", '').replace('-', '_').replace(',', ''))
            player_vars[row['Player']] = LpVariable(f"Select_{safe_name}_{i}", 0, 1, LpBinary)
        
        # 目标函数：最大化加权评分
        prob += lpSum([filtered_df.loc[i, 'Weighted_Score'] * player_vars[filtered_df.loc[i, 'Player']] 
                      for i in filtered_df.index])
        
        # 约束条件1：选择12名球员
        prob += lpSum([player_vars[row['Player']] for _, row in filtered_df.iterrows()]) == 12
        
        # 约束条件2：位置分配约束
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        for pos in positions:
            pos_players = filtered_df[filtered_df['Primary_Position'] == pos]
            if len(pos_players) > 0:
                prob += lpSum([player_vars[row['Player']] for _, row in pos_players.iterrows()]) >= 2
                prob += lpSum([player_vars[row['Player']] for _, row in pos_players.iterrows()]) <= 3
            else:
                print(f"警告: 位置 {pos} 没有符合条件的球员，可能导致优化失败")
        
        # 约束条件3：薪资限制
        prob += lpSum([filtered_df.loc[i, 'Salary_2023_2024'] * player_vars[filtered_df.loc[i, 'Player']] 
                      for i in filtered_df.index]) <= salary_cap
        
        # 约束条件4：确保有足够的首发球员（5人综合评分>70）
        high_score_players = filtered_df[filtered_df['Overall_Score'] > 70]
        if len(high_score_players) >= 5:
            prob += lpSum([player_vars[row['Player']] for _, row in high_score_players.iterrows()]) >= 5
        else:
            print(f"警告: 综合评分>70的球员不足5人，仅有 {len(high_score_players)} 人")
        
        # 约束条件5：年龄结构平衡
        young_players = filtered_df[filtered_df['Age'] <= 25]
        veteran_players = filtered_df[filtered_df['Age'] >= 30]
        
        if len(young_players) > 0:
            prob += lpSum([player_vars[row['Player']] for _, row in young_players.iterrows()]) >= 2
            prob += lpSum([player_vars[row['Player']] for _, row in young_players.iterrows()]) <= 6
        else:
            print("警告: 没有年龄<=25岁的年轻球员")
        
        if len(veteran_players) > 0:
            prob += lpSum([player_vars[row['Player']] for _, row in veteran_players.iterrows()]) >= 2
            prob += lpSum([player_vars[row['Player']] for _, row in veteran_players.iterrows()]) <= 6
        else:
            print("警告: 没有年龄>=30岁的老将球员")
        
        # 约束条件6：确保综合实力下限
        prob += lpSum([filtered_df.loc[i, 'Overall_Score'] * player_vars[filtered_df.loc[i, 'Player']] 
                      for i in filtered_df.index]) >= 12 * 60
        
        print("\n开始求解优化问题...")
        # 求解问题
        prob.solve(PULP_CBC_CMD(msg=0))
        
        # 检查求解状态
        if prob.status != 1:
            print(f"优化失败，状态: {LpStatus[prob.status]}")
            if prob.status == -1:
                print("建议: 放宽约束条件（如降低min_score_threshold或增加salary_cap）")
            return None
        
        # 收集结果
        selected_players = []
        for i, row in filtered_df.iterrows():
            if value(player_vars[row['Player']]) == 1:
                selected_players.append(row)
        
        result = {
            'players': pd.DataFrame(selected_players),
            'objective_value': value(prob.objective),
            'team_style': style_name,
            'weights': (w_off, w_def, w_team, w_stam),
            'constraints': {
                'salary_cap': salary_cap,
                'min_score_threshold': min_score_threshold
            }
        }
        
        # 保存结果到CSV
        if not result['players'].empty:
            result['players'].to_csv(self.output_file, index=False)
            print(f"\n已将12人名单保存到: {self.output_file}")
        
        return result
    
    def display_results(self, result):
        """显示优化结果"""
        if result is None:
            return
        
        selected_df = result['players']
        
        print("\n" + "="*100)
        print(f"🏀 NBA 12人轮换阵容优化结果 - {result['team_style']}风格")
        print("="*100)
        
        selected_df = selected_df.sort_values(['Primary_Position', 'Overall_Score'], ascending=[True, False])
        
        def get_display_width(s):
            width = 0
            for char in str(s):
                if ord(char) >= 0x4E00 and ord(char) <= 0x9FFF:
                    width += 2
                else:
                    width += 1
            return width
    
        col_widths = {
            '位置': max(8, get_display_width('位置')),
            '球员姓名': max(24, max(selected_df['Player'].apply(get_display_width)) + 2),
            '年龄': max(6, get_display_width('年龄')),
            '进攻': max(8, get_display_width('进攻')),
            '防守': max(8, get_display_width('防守')),
            '配合': max(8, get_display_width('配合')),
            '体能': max(8, get_display_width('体能')),
            '综合': max(8, get_display_width('综合')),
            '薪资(百万)': max(14, get_display_width('薪资(百万)'))
        }
    
        print(f"{'位置':<{col_widths['位置']}}"
              f"{'球员姓名':<{col_widths['球员姓名']}}"
              f"{'年龄':<{col_widths['年龄']}}"
              f"{'进攻':<{col_widths['进攻']}}"
              f"{'防守':<{col_widths['防守']}}"
              f"{'配合':<{col_widths['配合']}}"
              f"{'体能':<{col_widths['体能']}}"
              f"{'综合':<{col_widths['综合']}}"
              f"{'薪资(百万)':<{col_widths['薪资(百万)']}}")
        print("-" * 100)
        
        total_salary = 0
        total_scores = {'off': 0, 'def': 0, 'team': 0, 'stam': 0, 'overall': 0}
        position_counts = {}
        
        for _, row in selected_df.iterrows():
            pos = row['Primary_Position']
            position_counts[pos] = position_counts.get(pos, 0) + 1
            
            total_salary += row['Salary_2023_2024']
            total_scores['off'] += row['Offensive_Score']
            total_scores['def'] += row['Defensive_Score']
            total_scores['team'] += row['Teamwork_Score']
            total_scores['stam'] += row['Stamina_Score']
            total_scores['overall'] += row['Overall_Score']
            
            print(f"{pos:<{col_widths['位置']}}"
                  f"{row['Player']:<{col_widths['球员姓名']}}"
                  f"{int(row['Age']):<{col_widths['年龄']}}"
                  f"{row['Offensive_Score']:<{col_widths['进攻']}.1f}"
                  f"{row['Defensive_Score']:<{col_widths['防守']}.1f}"
                  f"{row['Teamwork_Score']:<{col_widths['配合']}.1f}"
                  f"{row['Stamina_Score']:<{col_widths['体能']}.1f}"
                  f"{row['Overall_Score']:<{col_widths['综合']}.1f}"
                  f"${row['Salary_2023_2024']/1000000:<{col_widths['薪资(百万)']-1}.2f}")
        
        print("-" * 100)
        print(f"{'平均':<{col_widths['位置']}}"
              f"{'':<{col_widths['球员姓名']}}"
              f"{'':<{col_widths['年龄']}}"
              f"{total_scores['off']/12:<{col_widths['进攻']}.1f}"
              f"{total_scores['def']/12:<{col_widths['防守']}.1f}"
              f"{total_scores['team']/12:<{col_widths['配合']}.1f}"
              f"{total_scores['stam']/12:<{col_widths['体能']}.1f}"
              f"{total_scores['overall']/12:<{col_widths['综合']}.1f}"
              f"${total_salary/12000000:<{col_widths['薪资(百万)']-1}.2f}")
        
        print("\n📊 球队统计摘要:")
        print(f"  总薪资: ${total_salary/1000000:.2f}百万 (预算利用率: {total_salary/result['constraints']['salary_cap']:.1%})")
        print(f"  平均年龄: {selected_df['Age'].mean():.1f}岁")
        print(f"  综合实力: {total_scores['overall']/12:.1f}分")
        print(f"  性价比: {total_scores['overall']/(total_salary/1000000):.2f}分/百万美元")
        
        print("\n🏟️ 位置配置:")
        for pos in ['PG', 'SG', 'SF', 'PF', 'C']:
            count = position_counts.get(pos, 0)
            print(f"  {pos}: {count} 名球员")

# 主程序
if __name__ == "__main__":
    optimizer = TeamOptimizer()
    result = optimizer.optimize_team(salary_cap=250000000)
    optimizer.display_results(result)