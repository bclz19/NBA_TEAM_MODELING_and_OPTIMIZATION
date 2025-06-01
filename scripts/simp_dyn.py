# import itertools
# import random
# import pandas as pd

# # --- 模型参数 ---
# BASE_STAMINA_CONSUMPTION_RATE_PER_MINUTE = 0.035
# DECISION_INTERVAL_MINUTES = 6
# MINUTES_IN_STANDARD_QUARTER = 12
# NUM_STANDARD_QUARTERS = 4
# TOTAL_GAME_MINUTES = NUM_STANDARD_QUARTERS * MINUTES_IN_STANDARD_QUARTER
# TOTAL_SEGMENTS = TOTAL_GAME_MINUTES // DECISION_INTERVAL_MINUTES

# # 年龄修正 (消耗)
# AGE_MODIFIER_CONSUMPTION_STANDARD = 1.0
# AGE_MODIFIER_CONSUMPTION_OVER_32 = 1.1

# # 位置修正 (消耗)
# POSITION_MODIFIER_GUARD = 1.0
# POSITION_MODIFIER_FORWARD = 1.05
# POSITION_MODIFIER_CENTER = 1.1

# # 体能恢复基础百分比
# RECOVERY_PERCENT_QUARTER_BREAK = 0.50
# RECOVERY_PERCENT_HALF_TIME = 0.90

# # 体能恢复年龄修正 (>32岁)
# RECOVERY_AGE_MOD_QUARTER_BREAK_OVER_32 = 0.85
# RECOVERY_AGE_MOD_HALF_TIME_OVER_32 = 0.80

# # 战术风格权重
# TACTICAL_WEIGHTS = {
#     "极端进攻型": (0.60, 0.15, 0.15, 0.10),
#     "进攻型": (0.50, 0.20, 0.20, 0.10),
#     "均衡型": (0.30, 0.30, 0.25, 0.15),
#     "防守型": (0.20, 0.50, 0.20, 0.10),
#     "极端防守型": (0.15, 0.60, 0.15, 0.10),
# }

# # 优势系数矩阵
# ADVANTAGE_MATRIX = {
#     ("极端进攻型", "极端进攻型"): 0.000, ("极端进攻型", "进攻型"): -0.086, ("极端进攻型", "均衡型"): 0.000, ("极端进攻型", "防守型"): -0.300, ("极端进攻型", "极端防守型"): -0.100,
#     ("进攻型", "极端进攻型"): 0.086, ("进攻型", "进攻型"): 0.000, ("进攻型", "均衡型"): -0.012, ("进攻型", "防守型"): -0.120, ("进攻型", "极端防守型"): -0.093,
#     ("均衡型", "极端进攻型"): 0.000, ("均衡型", "进攻型"): 0.012, ("均衡型", "均衡型"): 0.000, ("均衡型", "防守型"): 0.135, ("均衡型", "极端防守型"): -0.052,
#     ("防守型", "极端进攻型"): 0.300, ("防守型", "进攻型"): 0.120, ("防守型", "均衡型"): -0.135, ("防守型", "防守型"): 0.000, ("防守型", "极端防守型"): -0.235,
#     ("极端防守型", "极端进攻型"): 0.100, ("极端防守型", "进攻型"): 0.093, ("极端防守型", "均衡型"): 0.052, ("极端防守型", "防守型"): 0.235, ("极端防守型", "极端防守型"): 0.000,
# }

# # 球员类
# class Player:
#     def __init__(self, name, position, age, minutes_played, offensive_score, defensive_score, teamwork_score, stamina_score):
#         self.name = name
#         self.position = position
#         self.age = age
#         self.minutes_played = minutes_played
#         self.offensive_score = float(offensive_score)
#         self.defensive_score = float(defensive_score)
#         self.teamwork_score = float(teamwork_score)
#         self.stamina_score = float(stamina_score)
#         self.current_stamina = float(stamina_score)
#         self.current_off = float(offensive_score)
#         self.current_def = float(defensive_score)
#         self.current_team = float(teamwork_score)
#         self.current_ovr = 0.0

#     def _get_age_modifier_consumption(self):
#         return AGE_MODIFIER_CONSUMPTION_OVER_32 if self.age > 32 else AGE_MODIFIER_CONSUMPTION_STANDARD

#     def _get_position_modifier_consumption(self):
#         if self.position in ['PG', 'SG']:
#             return POSITION_MODIFIER_GUARD
#         elif self.position in ['SF', 'PF']:
#             return POSITION_MODIFIER_FORWARD
#         elif self.position == 'C':
#             return POSITION_MODIFIER_CENTER
#         return 1.0

#     def consume_stamina(self, minutes):
#         if minutes <= 0:
#             return
#         base_rate = BASE_STAMINA_CONSUMPTION_RATE_PER_MINUTE
#         age_mod = self._get_age_modifier_consumption()
#         pos_mod = self._get_position_modifier_consumption()
#         consumption_rate_per_minute = base_rate * age_mod * pos_mod
#         stamina_consumed = consumption_rate_per_minute * minutes * self.stamina_score
#         self.current_stamina = max(0, self.current_stamina - stamina_consumed)

#     def recover_stamina(self, rest_type):
#         base_recovery_percentage = 0.0
#         age_modifier = 1.0
#         if rest_type == "quarter_break":
#             base_recovery_percentage = RECOVERY_PERCENT_QUARTER_BREAK
#             if self.age > 32:
#                 age_modifier = RECOVERY_AGE_MOD_QUARTER_BREAK_OVER_32
#         elif rest_type == "halftime_break":
#             base_recovery_percentage = RECOVERY_PERCENT_HALF_TIME
#             if self.age > 32:
#                 age_modifier = RECOVERY_AGE_MOD_HALF_TIME_OVER_32
#         final_recovery_percentage = base_recovery_percentage * age_modifier
#         stamina_recovered = final_recovery_percentage * self.stamina_score
#         self.current_stamina = min(self.stamina_score, self.current_stamina + stamina_recovered)

#     def update_ability_and_ovr(self, weights):
#         stamina_percentage = self.current_stamina / self.stamina_score if self.stamina_score > 0 else 0.0
#         stamina_factor = 1.0 if stamina_percentage >= 0.90 else 0.9 if stamina_percentage >= 0.70 else 0.7 if stamina_percentage >= 0.50 else 0.5
#         self.current_off = self.offensive_score * stamina_factor
#         self.current_def = self.defensive_score * stamina_factor
#         self.current_team = self.teamwork_score * stamina_factor
#         w_off, w_def, w_team, w_stam = weights
#         self.current_ovr = (w_off * self.current_off + w_def * self.current_def + w_team * self.current_team +
#                             w_stam * stamina_percentage)

#     def __repr__(self):
#         return (f"P({self.name}, {self.position}, A:{self.age}, "
#                 f"S:{self.current_stamina:.1f}/{self.stamina_score:.1f}, "
#                 f"Off:{self.current_off:.1f}, Def:{self.current_def:.1f}, Team:{self.current_team:.1f}, "
#                 f"OVR:{self.current_ovr:.2f})")

# # 动态计算战术风格和权重
# def calculate_tactical_weights(lineup):
#     if not lineup:
#         return TACTICAL_WEIGHTS["均衡型"], "均衡型"
#     avg_off = sum(p.offensive_score for p in lineup) / len(lineup)
#     avg_def = sum(p.defensive_score for p in lineup) / len(lineup)
#     avg_team = sum(p.teamwork_score for p in lineup) / len(lineup)
#     max_diff = max(abs(avg_off - avg_def), abs(avg_def - avg_team), abs(avg_off - avg_team))
#     print(f"DEBUG: 平均评分 - Off: {avg_off:.2f}, Def: {avg_def:.2f}, Team: {avg_team:.2f}, 最大差值: {max_diff:.2f}")
#     scores = {'off': avg_off, 'def': avg_def, 'team': avg_team}
#     max_score = max(scores.values())
#     threshold = 5
#     significant_threshold = 20
#     if abs(avg_off - avg_def) <= threshold and abs(avg_def - avg_team) <= threshold and abs(avg_off - avg_team) <= threshold:
#         return TACTICAL_WEIGHTS["均衡型"], "均衡型"
#     elif scores['off'] == max_score:
#         if avg_off - max(avg_def, avg_team) > significant_threshold:
#             return TACTICAL_WEIGHTS["极端进攻型"], "极端进攻型"
#         return TACTICAL_WEIGHTS["进攻型"], "进攻型"
#     elif scores['def'] == max_score:
#         if avg_def - max(avg_off, avg_team) > significant_threshold:
#             return TACTICAL_WEIGHTS["极端防守型"], "极端防守型"
#         return TACTICAL_WEIGHTS["防守型"], "防守型"
#     else:
#         return TACTICAL_WEIGHTS["均衡型"], "均衡型"

# # 生成随机对手阵容
# def generate_opponent_lineup():
#     positions = ['PG', 'SG', 'SF', 'PF', 'C']
#     opponent_lineup = []
#     for pos in positions:
#         if pos in ['PG', 'SG']:
#             off_range = (85, 100)
#             def_range = (75, 90)
#             team_range = (80, 95)
#         elif pos in ['SF', 'PF']:
#             off_range = (80, 95)
#             def_range = (80, 95)
#             team_range = (80, 95)
#         else:
#             off_range = (75, 90)
#             def_range = (85, 100)
#             team_range = (80, 95)
#         player = {
#             'name': f"Opponent_{pos}_{random.randint(1, 100)}",
#             'position': pos,
#             'offensive_score': random.uniform(*off_range),
#             'defensive_score': random.uniform(*def_range),
#             'teamwork_score': random.uniform(*team_range),
#             'stamina_score': random.uniform(80, 100)
#         }
#         opponent_lineup.append(Player(
#             name=player['name'],
#             position=player['position'],
#             age=random.randint(22, 35),
#             minutes_played=random.uniform(30, 38),
#             offensive_score=player['offensive_score'],
#             defensive_score=player['defensive_score'],
#             teamwork_score=player['teamwork_score'],
#             stamina_score=player['stamina_score']
#         ))
#     weights, style = calculate_tactical_weights(opponent_lineup)
#     for p in opponent_lineup:
#         p.update_ability_and_ovr(weights)
#     return opponent_lineup, style

# # 寻找最优阵容
# def find_optimal_lineup(players, opponent_style, required_positions=('PG', 'SG', 'SF', 'PF', 'C')):
#     position_map = {pos: [] for pos in required_positions}
#     for p in players:
#         if p.position in position_map:
#             position_map[p.position].append(p)
#     for pos, player_list in position_map.items():
#         if not player_list:
#             print(f"错误: 位置 {pos} 没有可用球员。")
#             return None, 0, None
#     list_of_player_lists = [position_map[pos] for pos in required_positions]
#     best_lineup = None
#     max_adjusted_ovr_sum = -1.0
#     best_style = None
#     for lineup_tuple in itertools.product(*list_of_player_lists):
#         if len(set(p.name for p in lineup_tuple)) != len(lineup_tuple):
#             continue
#         lineup = list(lineup_tuple)
#         weights, style = calculate_tactical_weights(lineup)
#         for p in lineup:
#             p.update_ability_and_ovr(weights)
#         ovr_sum = sum(p.current_ovr for p in lineup)
#         advantage = ADVANTAGE_MATRIX.get((style, opponent_style), 0.0)
#         adjusted_ovr_sum = ovr_sum * (1 + advantage)
#         if adjusted_ovr_sum > max_adjusted_ovr_sum:
#             max_adjusted_ovr_sum = adjusted_ovr_sum
#             best_lineup = lineup
#             best_style = style
#     if best_lineup:
#         weights = calculate_tactical_weights(best_lineup)[0]
#         for p in players:
#             p.update_ability_and_ovr(weights)
#     return best_lineup, max_adjusted_ovr_sum, best_style

# # 模拟逻辑
# def run_simulation(team_data_file='selected_team.csv', team_name="选定队伍"):
#     try:
#         df = pd.read_csv(team_data_file)
#         print(f"成功从 {team_data_file} 加载12人名单: {len(df)} 名球员")
#     except FileNotFoundError:
#         print(f"错误: 找不到文件 {team_data_file}")
#         return
    
#     required_columns = ['Player', 'Primary_Position', 'Age', 'MP', 'Offensive_Score', 'Defensive_Score', 
#                        'Teamwork_Score', 'Stamina_Score']
#     for col in required_columns:
#         if col not in df.columns:
#             raise ValueError(f"数据缺少必要的列: {col}")
    
#     players = [Player(
#         name=row['Player'],
#         position=row['Primary_Position'],
#         age=row['Age'],
#         minutes_played=row.get('MP', 30.0),  # 默认30分钟如果MP缺失
#         offensive_score=row['Offensive_Score'],
#         defensive_score=row['Defensive_Score'],
#         teamwork_score=row['Teamwork_Score'],
#         stamina_score=row['Stamina_Score']
#     ) for _, row in df.iterrows()]
    
#     print(f"--- 开始模拟 {team_name} (决策间隔: {DECISION_INTERVAL_MINUTES} 分钟) ---")
    
#     current_lineup = []
#     lineup_history = []
    
#     print("--- 比赛开始前: 选择初始阵容 ---")
#     opponent_lineup, opponent_style = generate_opponent_lineup()
#     print(f"对手初始战术风格: {opponent_style}")
#     optimal_lineup, total_ovr, tactical_style = find_optimal_lineup(players, opponent_style)
#     if optimal_lineup:
#         current_lineup = optimal_lineup
#         weights = calculate_tactical_weights(current_lineup)[0]
#         print(f"本队战术风格: {tactical_style}, 权重: {weights}")
#         print(f"初始阵容 (调整后总 OVR: {total_ovr:.2f}):")
#         for p in current_lineup:
#             print(f"  {p.name} ({p.position}) - OVR: {p.current_ovr:.2f}, Stamina: {p.current_stamina:.1f}/{p.stamina_score:.1f}")
#         lineup_history.append({
#             "segment": "Start",
#             "lineup": [p.name for p in current_lineup],
#             "total_ovr": total_ovr,
#             "game_time_end": 0,
#             "tactical_style": tactical_style,
#             "weights": weights,
#             "opponent_style": opponent_style
#         })
#     else:
#         print("错误: 无法选择初始阵容。")
#         return

#     for segment_idx in range(TOTAL_SEGMENTS):
#         current_game_time_start = segment_idx * DECISION_INTERVAL_MINUTES
#         current_game_time_end = (segment_idx + 1) * DECISION_INTERVAL_MINUTES
#         current_quarter = (current_game_time_start // MINUTES_IN_STANDARD_QUARTER) + 1
#         minutes_into_quarter_start = current_game_time_start % MINUTES_IN_STANDARD_QUARTER
#         minutes_into_quarter_end = minutes_into_quarter_start + DECISION_INTERVAL_MINUTES
        
#         print(f"\n--- 比赛段 {segment_idx + 1}/{TOTAL_SEGMENTS} 开始 ---")
#         print(f"(第 {current_quarter} 节, {minutes_into_quarter_start}-{minutes_into_quarter_end} 分钟, 总比赛时间: {current_game_time_start} 分钟)")
        
#         if not current_lineup:
#             print("错误: 当前阵容为空。")
#             break
            
#         print(f"场上球员 (比赛段 {segment_idx + 1}):")
#         weights, style = calculate_tactical_weights(current_lineup)
#         print(f"本队当前战术风格: {style}, 权重: {weights}, 对手战术风格: {opponent_style}")
#         for p in current_lineup:
#             print(f"  {p.name} ({p.position}) 上场前 - Stamina: {p.current_stamina:.1f}, OVR: {p.current_ovr:.2f}")
#             p.consume_stamina(DECISION_INTERVAL_MINUTES)
#             p.update_ability_and_ovr(weights)
#             print(f"  {p.name} ({p.position}) 上场后 - Stamina: {p.current_stamina:.1f}, OVR: {p.current_ovr:.2f}")

#         print(f"\n--- 比赛段 {segment_idx + 1} 结束 (总比赛时间: {current_game_time_end} 分钟) ---")
        
#         official_break_occurred = False
#         if current_game_time_end == MINUTES_IN_STANDARD_QUARTER * 2:
#             print("进行半场休息 (15分钟)...")
#             for p in players:
#                 p.recover_stamina("halftime_break")
#             official_break_occurred = True
#         elif current_game_time_end % MINUTES_IN_STANDARD_QUARTER == 0 and current_game_time_end < TOTAL_GAME_MINUTES:
#             print("进行节间休息 (2分钟)...")
#             for p in players:
#                 p.recover_stamina("quarter_break")
#             official_break_occurred = True

#         if official_break_occurred:
#             print("休息后更新球员状态...")
#             weights = calculate_tactical_weights(current_lineup)[0]
#             for p in players:
#                 p.update_ability_and_ovr(weights)

#         if current_game_time_end < TOTAL_GAME_MINUTES:
#             print(f"\n为下一个比赛段 (比赛段 {segment_idx + 2}) 选择阵容:")
#             opponent_lineup, opponent_style = generate_opponent_lineup()
#             print(f"对手战术风格: {opponent_style}")
#             optimal_lineup, total_ovr, tactical_style = find_optimal_lineup(players, opponent_style)
#             if optimal_lineup:
#                 current_lineup = optimal_lineup
#                 weights = calculate_tactical_weights(current_lineup)[0]
#                 print(f"本队战术风格: {tactical_style}, 权重: {weights}")
#                 print(f"下一个比赛段阵容 (调整后总 OVR: {total_ovr:.2f}):")
#                 for p in current_lineup:
#                     print(f"  {p.name} ({p.position}) - OVR: {p.current_ovr:.2f}, Stamina: {p.current_stamina:.1f}/{p.stamina_score:.1f}")
#                 lineup_history.append({
#                     "segment": f"Seg{segment_idx + 2}_Start",
#                     "lineup": [p.name for p in current_lineup],
#                     "total_ovr": total_ovr,
#                     "game_time_end": current_game_time_end,
#                     "tactical_style": tactical_style,
#                     "weights": weights,
#                     "opponent_style": opponent_style
#                 })
#             else:
#                 print(f"错误: 无法为下一个比赛段选择阵容。")
#                 break
#         else:
#             print("\n--- 比赛结束 (所有比赛段完成) ---")

#     print("\n\n--- 阵容历史 (每6分钟决策点) ---")
#     for entry in lineup_history:
#         print(f"时刻: {entry['segment']} (在 {entry['game_time_end']} 分钟后), 阵容: {', '.join(entry['lineup'])}, "
#               f"总OVR: {entry['total_ovr']:.2f}, 战术风格: {entry['tactical_style']}, 权重: {entry['weights']}, "
#               f"对手风格: {entry['opponent_style']}")

#     print(f"\n--- {team_name} 最终球员状态 ---")
#     for p in sorted(players, key=lambda x: x.name):
#         print(p)

# # 主程序
# if __name__ == "__main__":
#     run_simulation(team_data_file='second_dataset/selected_team.csv', team_name="Dynamic Team")

# import itertools
# import random
# import pandas as pd
# import matplotlib.pyplot as plt

# # --- 模型参数 ---
# BASE_STAMINA_CONSUMPTION_RATE_PER_MINUTE = 0.035
# DECISION_INTERVAL_MINUTES = 3  # 决策间隔改为3分钟
# MINUTES_IN_STANDARD_QUARTER = 12
# NUM_STANDARD_QUARTERS = 4
# TOTAL_GAME_MINUTES = NUM_STANDARD_QUARTERS * MINUTES_IN_STANDARD_QUARTER
# TOTAL_SEGMENTS = TOTAL_GAME_MINUTES // DECISION_INTERVAL_MINUTES

# # 年龄修正 (消耗)
# AGE_MODIFIER_CONSUMPTION_STANDARD = 1.0
# AGE_MODIFIER_CONSUMPTION_OVER_32 = 1.1

# # 位置修正 (消耗)
# POSITION_MODIFIER_GUARD = 1.0
# POSITION_MODIFIER_FORWARD = 1.05
# POSITION_MODIFIER_CENTER = 1.1

# # 体能恢复基础百分比
# RECOVERY_PERCENT_QUARTER_BREAK = 0.50
# RECOVERY_PERCENT_HALF_TIME = 0.90

# # 体能恢复年龄修正 (>32岁)
# RECOVERY_AGE_MOD_QUARTER_BREAK_OVER_32 = 0.85
# RECOVERY_AGE_MOD_HALF_TIME_OVER_32 = 0.80

# # 战术风格权重
# TACTICAL_WEIGHTS = {
#     "极端进攻型": (0.60, 0.15, 0.15, 0.10),
#     "进攻型": (0.50, 0.20, 0.20, 0.10),
#     "均衡型": (0.30, 0.30, 0.25, 0.15),
#     "防守型": (0.20, 0.50, 0.20, 0.10),
#     "极端防守型": (0.15, 0.60, 0.15, 0.10),
# }

# # 优势系数矩阵
# ADVANTAGE_MATRIX = {
#     ("极端进攻型", "极端进攻型"): 0.000, ("极端进攻型", "进攻型"): -0.086, ("极端进攻型", "均衡型"): 0.000, ("极端进攻型", "防守型"): -0.300, ("极端进攻型", "极端防守型"): -0.100,
#     ("进攻型", "极端进攻型"): 0.086, ("进攻型", "进攻型"): 0.000, ("进攻型", "均衡型"): -0.012, ("进攻型", "防守型"): -0.120, ("进攻型", "极端防守型"): -0.093,
#     ("均衡型", "极端进攻型"): 0.000, ("均衡型", "进攻型"): 0.012, ("均衡型", "均衡型"): 0.000, ("均衡型", "防守型"): 0.135, ("均衡型", "极端防守型"): -0.052,
#     ("防守型", "极端进攻型"): 0.300, ("防守型", "进攻型"): 0.120, ("防守型", "均衡型"): -0.135, ("防守型", "防守型"): 0.000, ("防守型", "极端防守型"): -0.235,
#     ("极端防守型", "极端进攻型"): 0.100, ("极端防守型", "进攻型"): 0.093, ("极端防守型", "均衡型"): 0.052, ("极端防守型", "防守型"): 0.235, ("极端防守型", "极端防守型"): 0.000,
# }

# # 球员类
# class Player:
#     def __init__(self, name, position, age, minutes_played, offensive_score, defensive_score, teamwork_score, stamina_score):
#         self.name = name
#         self.position = position
#         self.age = age
#         self.minutes_played = minutes_played
#         self.offensive_score = float(offensive_score)
#         self.defensive_score = float(defensive_score)
#         self.teamwork_score = float(teamwork_score)
#         self.stamina_score = float(stamina_score)
#         self.current_stamina = float(stamina_score)
#         self.current_off = float(offensive_score)
#         self.current_def = float(defensive_score)
#         self.current_team = float(teamwork_score)
#         self.current_ovr = 0.0

#     def _get_age_modifier_consumption(self):
#         return AGE_MODIFIER_CONSUMPTION_OVER_32 if self.age > 32 else AGE_MODIFIER_CONSUMPTION_STANDARD

#     def _get_position_modifier_consumption(self):
#         if self.position in ['PG', 'SG']:
#             return POSITION_MODIFIER_GUARD
#         elif self.position in ['SF', 'PF']:
#             return POSITION_MODIFIER_FORWARD
#         elif self.position == 'C':
#             return POSITION_MODIFIER_CENTER
#         return 1.0

#     def consume_stamina(self, minutes):
#         if minutes <= 0:
#             return
#         base_rate = BASE_STAMINA_CONSUMPTION_RATE_PER_MINUTE
#         age_mod = self._get_age_modifier_consumption()
#         pos_mod = self._get_position_modifier_consumption()
#         consumption_rate_per_minute = base_rate * age_mod * pos_mod
#         stamina_consumed = consumption_rate_per_minute * minutes * self.stamina_score
#         self.current_stamina = max(0, self.current_stamina - stamina_consumed)

#     def recover_stamina(self, rest_type):
#         base_recovery_percentage = 0.0
#         age_modifier = 1.0
#         if rest_type == "quarter_break":
#             base_recovery_percentage = RECOVERY_PERCENT_QUARTER_BREAK
#             if self.age > 32:
#                 age_modifier = RECOVERY_AGE_MOD_QUARTER_BREAK_OVER_32
#         elif rest_type == "halftime_break":
#             base_recovery_percentage = RECOVERY_PERCENT_HALF_TIME
#             if self.age > 32:
#                 age_modifier = RECOVERY_AGE_MOD_HALF_TIME_OVER_32
#         final_recovery_percentage = base_recovery_percentage * age_modifier
#         stamina_recovered = final_recovery_percentage * self.stamina_score
#         self.current_stamina = min(self.stamina_score, self.current_stamina + stamina_recovered)

#     def update_ability_and_ovr(self, weights):
#         stamina_percentage = self.current_stamina / self.stamina_score if self.stamina_score > 0 else 0.0
#         stamina_factor = 1.0 if stamina_percentage >= 0.90 else 0.9 if stamina_percentage >= 0.70 else 0.7 if stamina_percentage >= 0.50 else 0.5
#         self.current_off = self.offensive_score * stamina_factor
#         self.current_def = self.defensive_score * stamina_factor
#         self.current_team = self.teamwork_score * stamina_factor
#         w_off, w_def, w_team, w_stam = weights
#         self.current_ovr = (w_off * self.current_off + w_def * self.current_def + w_team * self.current_team +
#                             w_stam * stamina_percentage)

#     def __repr__(self):
#         return (f"P({self.name}, {self.position}, A:{self.age}, "
#                 f"S:{self.current_stamina:.1f}/{self.stamina_score:.1f}, "
#                 f"Off:{self.current_off:.1f}, Def:{self.current_def:.1f}, Team:{self.current_team:.1f}, "
#                 f"OVR:{self.current_ovr:.2f})")

# # 动态计算战术风格和权重
# def calculate_tactical_weights(lineup):
#     if not lineup:
#         return TACTICAL_WEIGHTS["均衡型"], "均衡型"
#     avg_off = sum(p.offensive_score for p in lineup) / len(lineup)
#     avg_def = sum(p.defensive_score for p in lineup) / len(lineup)
#     avg_team = sum(p.teamwork_score for p in lineup) / len(lineup)
#     max_diff = max(abs(avg_off - avg_def), abs(avg_def - avg_team), abs(avg_off - avg_team))
#     print(f"DEBUG: 平均评分 - Off: {avg_off:.2f}, Def: {avg_def:.2f}, Team: {avg_team:.2f}, 最大差值: {max_diff:.2f}")
#     scores = {'off': avg_off, 'def': avg_def, 'team': avg_team}
#     max_score = max(scores.values())
#     threshold = 5
#     significant_threshold = 20
#     if abs(avg_off - avg_def) <= threshold and abs(avg_def - avg_team) <= threshold and abs(avg_off - avg_team) <= threshold:
#         return TACTICAL_WEIGHTS["均衡型"], "均衡型"
#     elif scores['off'] == max_score:
#         if avg_off - max(avg_def, avg_team) > significant_threshold:
#             return TACTICAL_WEIGHTS["极端进攻型"], "极端进攻型"
#         return TACTICAL_WEIGHTS["进攻型"], "进攻型"
#     elif scores['def'] == max_score:
#         if avg_def - max(avg_off, avg_team) > significant_threshold:
#             return TACTICAL_WEIGHTS["极端防守型"], "极端防守型"
#         return TACTICAL_WEIGHTS["防守型"], "防守型"
#     else:
#         return TACTICAL_WEIGHTS["均衡型"], "均衡型"

# # 生成随机对手阵容
# def generate_opponent_lineup():
#     positions = ['PG', 'SG', 'SF', 'PF', 'C']
#     opponent_lineup = []
#     for pos in positions:
#         if pos in ['PG', 'SG']:
#             off_range = (85, 100)
#             def_range = (75, 90)
#             team_range = (80, 95)
#         elif pos in ['SF', 'PF']:
#             off_range = (80, 95)
#             def_range = (80, 95)
#             team_range = (80, 95)
#         else:
#             off_range = (75, 90)
#             def_range = (85, 100)
#             team_range = (80, 95)
#         player = {
#             'name': f"Opponent_{pos}_{random.randint(1, 100)}",
#             'position': pos,
#             'offensive_score': random.uniform(*off_range),
#             'defensive_score': random.uniform(*def_range),
#             'teamwork_score': random.uniform(*team_range),
#             'stamina_score': random.uniform(80, 100)
#         }
#         opponent_lineup.append(Player(
#             name=player['name'],
#             position=player['position'],
#             age=random.randint(22, 35),
#             minutes_played=random.uniform(30, 38),
#             offensive_score=player['offensive_score'],
#             defensive_score=player['defensive_score'],
#             teamwork_score=player['teamwork_score'],
#             stamina_score=player['stamina_score']
#         ))
#     weights, style = calculate_tactical_weights(opponent_lineup)
#     for p in opponent_lineup:
#         p.update_ability_and_ovr(weights)
#     return opponent_lineup, style

# # 寻找最优阵容
# def find_optimal_lineup(players, opponent_style, required_positions=('PG', 'SG', 'SF', 'PF', 'C')):
#     position_map = {pos: [] for pos in required_positions}
#     for p in players:
#         if p.position in position_map:
#             position_map[p.position].append(p)
#     for pos, player_list in position_map.items():
#         if not player_list:
#             print(f"错误: 位置 {pos} 没有可用球员。")
#             return None, 0, None
#     list_of_player_lists = [position_map[pos] for pos in required_positions]
#     best_lineup = None
#     max_adjusted_ovr_sum = -1.0
#     best_style = None
#     for lineup_tuple in itertools.product(*list_of_player_lists):
#         if len(set(p.name for p in lineup_tuple)) != len(lineup_tuple):
#             continue
#         lineup = list(lineup_tuple)
#         weights, style = calculate_tactical_weights(lineup)
#         for p in lineup:
#             p.update_ability_and_ovr(weights)
#         ovr_sum = sum(p.current_ovr for p in lineup)
#         advantage = ADVANTAGE_MATRIX.get((style, opponent_style), 0.0)
#         adjusted_ovr_sum = ovr_sum * (1 + advantage)
#         if adjusted_ovr_sum > max_adjusted_ovr_sum:
#             max_adjusted_ovr_sum = adjusted_ovr_sum
#             best_lineup = lineup
#             best_style = style
#     if best_lineup:
#         weights = calculate_tactical_weights(best_lineup)[0]
#         for p in players:
#             p.update_ability_and_ovr(weights)
#     return best_lineup, max_adjusted_ovr_sum, best_style

# # 局势评估函数
# def evaluate_situation(current_lineup, opponent_lineup):
#     our_avg_off = sum(p.current_off for p in current_lineup) / len(current_lineup)
#     opp_avg_def = sum(p.current_def for p in opponent_lineup) / len(opponent_lineup)
#     if our_avg_off > opp_avg_def + 10:
#         return random.choice(["防守型", "极端防守型"]) if random.random() < 0.5 else None
#     elif opp_avg_def > our_avg_off + 10:
#         return random.choice(["进攻型", "极端进攻型"]) if random.random() < 0.3 else None
#     return None

# # 可视化风格变化
# def plot_opponent_style_history(lineup_history):
#     segments = [entry["segment"] for entry in lineup_history]
#     styles = [entry["opponent_style"] for entry in lineup_history]
#     style_map = {s: i for i, s in enumerate(TACTICAL_WEIGHTS.keys())}
#     style_nums = [style_map[s] for s in styles]
    
#     plt.figure(figsize=(10, 6))
#     plt.plot(segments, style_nums, marker='o', color='b')
#     plt.yticks(range(len(style_map)), list(style_map.keys()))
#     plt.xlabel("比赛段")
#     plt.ylabel("对手战术风格")
#     plt.title("对手战术风格变化")
#     plt.grid(True)
#     plt.show()

# # 模拟逻辑
# def run_simulation(team_data_file='selected_team.csv', team_name="选定队伍"):
#     try:
#         df = pd.read_csv(team_data_file)
#         print(f"成功从 {team_data_file} 加载12人名单: {len(df)} 名球员")
#     except FileNotFoundError:
#         print(f"错误: 找不到文件 {team_data_file}")
#         return
    
#     required_columns = ['Player', 'Primary_Position', 'Age', 'MP', 'Offensive_Score', 'Defensive_Score', 
#                        'Teamwork_Score', 'Stamina_Score']
#     for col in required_columns:
#         if col not in df.columns:
#             raise ValueError(f"数据缺少必要的列: {col}")
    
#     players = [Player(
#         name=row['Player'],
#         position=row['Primary_Position'],
#         age=row['Age'],
#         minutes_played=row.get('MP', 30.0),
#         offensive_score=row['Offensive_Score'],
#         defensive_score=row['Defensive_Score'],
#         teamwork_score=row['Teamwork_Score'],
#         stamina_score=row['Stamina_Score']
#     ) for _, row in df.iterrows()]
    
#     print(f"--- 开始模拟 {team_name} (决策间隔: {DECISION_INTERVAL_MINUTES} 分钟) ---")
    
#     current_lineup = []
#     lineup_history = []
    
#     print("--- 比赛开始前: 选择初始阵容 ---")
#     opponent_lineup, opponent_style = generate_opponent_lineup()
#     print(f"对手初始战术风格: {opponent_style}")
#     optimal_lineup, total_ovr, tactical_style = find_optimal_lineup(players, opponent_style)
#     if optimal_lineup:
#         current_lineup = optimal_lineup
#         weights = calculate_tactical_weights(current_lineup)[0]
#         print(f"本队战术风格: {tactical_style}, 权重: {weights}")
#         print(f"初始阵容 (调整后总 OVR: {total_ovr:.2f}):")
#         for p in current_lineup:
#             print(f"  {p.name} ({p.position}) - OVR: {p.current_ovr:.2f}, Stamina: {p.current_stamina:.1f}/{p.stamina_score:.1f}")
#         lineup_history.append({
#             "segment": "Start",
#             "lineup": [p.name for p in current_lineup],
#             "total_ovr": total_ovr,
#             "game_time_end": 0,
#             "tactical_style": tactical_style,
#             "weights": weights,
#             "opponent_style": opponent_style
#         })
#     else:
#         print("错误: 无法选择初始阵容。")
#         return

#     for segment_idx in range(TOTAL_SEGMENTS):
#         current_game_time_start = segment_idx * DECISION_INTERVAL_MINUTES
#         current_game_time_end = (segment_idx + 1) * DECISION_INTERVAL_MINUTES
#         current_quarter = (current_game_time_start // MINUTES_IN_STANDARD_QUARTER) + 1
#         minutes_into_quarter_start = current_game_time_start % MINUTES_IN_STANDARD_QUARTER
#         minutes_into_quarter_end = minutes_into_quarter_start + DECISION_INTERVAL_MINUTES
        
#         print(f"\n--- 比赛段 {segment_idx + 1}/{TOTAL_SEGMENTS} 开始 ---")
#         print(f"(第 {current_quarter} 节, {minutes_into_quarter_start}-{minutes_into_quarter_end} 分钟, 总比赛时间: {current_game_time_start} 分钟)")
        
#         if not current_lineup:
#             print("错误: 当前阵容为空。")
#             break
            
#         print(f"场上球员 (比赛段 {segment_idx + 1}):")
#         weights, style = calculate_tactical_weights(current_lineup)
#         print(f"本队当前战术风格: {style}, 权重: {weights}, 对手战术风格: {opponent_style}")
#         for p in current_lineup:
#             print(f"  {p.name} ({p.position}) 上场前 - Stamina: {p.current_stamina:.1f}, OVR: {p.current_ovr:.2f}")
#             p.consume_stamina(DECISION_INTERVAL_MINUTES)
#             p.update_ability_and_ovr(weights)
#             print(f"  {p.name} ({p.position}) 上场后 - Stamina: {p.current_stamina:.1f}, OVR: {p.current_ovr:.2f}")

#         print(f"\n--- 比赛段 {segment_idx + 1} 结束 (总比赛时间: {current_game_time_end} 分钟) ---")
        
#         official_break_occurred = False
#         if current_game_time_end == MINUTES_IN_STANDARD_QUARTER * 2:
#             print("进行半场休息 (15分钟)...")
#             for p in players:
#                 p.recover_stamina("halftime_break")
#             official_break_occurred = True
#         elif current_game_time_end % MINUTES_IN_STANDARD_QUARTER == 0 and current_game_time_end < TOTAL_GAME_MINUTES:
#             print("进行节间休息 (2分钟)...")
#             for p in players:
#                 p.recover_stamina("quarter_break")
#             official_break_occurred = True

#         if official_break_occurred:
#             print("休息后更新球员状态...")
#             weights = calculate_tactical_weights(current_lineup)[0]
#             for p in players:
#                 p.update_ability_and_ovr(weights)

#         if current_game_time_end < TOTAL_GAME_MINUTES:
#             print(f"\n为下一个比赛段 (比赛段 {segment_idx + 2}) 选择阵容:")
#             situation_style = evaluate_situation(current_lineup, opponent_lineup)
#             if situation_style:
#                 opponent_style = situation_style
#                 print(f"局势触发: 对手切换到 {opponent_style}")
#             else:
#                 opponent_lineup, opponent_style = generate_opponent_lineup()
#                 print(f"对手战术风格: {opponent_style}")
#             optimal_lineup, total_ovr, tactical_style = find_optimal_lineup(players, opponent_style)
#             if optimal_lineup:
#                 current_lineup = optimal_lineup
#                 weights = calculate_tactical_weights(current_lineup)[0]
#                 print(f"本队战术风格: {tactical_style}, 权重: {weights}")
#                 print(f"下一个比赛段阵容 (调整后总 OVR: {total_ovr:.2f}):")
#                 for p in current_lineup:
#                     print(f"  {p.name} ({p.position}) - OVR: {p.current_ovr:.2f}, Stamina: {p.current_stamina:.1f}/{p.stamina_score:.1f}")
#                 lineup_history.append({
#                     "segment": f"Seg{segment_idx + 2}_Start",
#                     "lineup": [p.name for p in current_lineup],
#                     "total_ovr": total_ovr,
#                     "game_time_end": current_game_time_end,
#                     "tactical_style": tactical_style,
#                     "weights": weights,
#                     "opponent_style": opponent_style
#                 })
#             else:
#                 print(f"错误: 无法为下一个比赛段选择阵容。")
#                 break
#         else:
#             print("\n--- 比赛结束 (所有比赛段完成) ---")

#     print("\n\n--- 阵容历史 (每3分钟决策点) ---")
#     for entry in lineup_history:
#         print(f"时刻: {entry['segment']} (在 {entry['game_time_end']} 分钟后), 阵容: {', '.join(entry['lineup'])}, "
#               f"总OVR: {entry['total_ovr']:.2f}, 战术风格: {entry['tactical_style']}, 权重: {entry['weights']}, "
#               f"对手风格: {entry['opponent_style']}")

#     print(f"\n--- {team_name} 最终球员状态 ---")
#     for p in sorted(players, key=lambda x: x.name):
#         print(p)
    
#     # # 可视化对手风格
#     # plot_opponent_style_history(lineup_history)

# # 主程序
# if __name__ == "__main__":
#     run_simulation(team_data_file='second_dataset/selected_team.csv', team_name="Dynamic Team")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools
import random
import pandas as pd
import matplotlib.pyplot as plt

# --- 模型参数 ---
BASE_STAMINA_CONSUMPTION_RATE_PER_MINUTE = 0.035
DECISION_INTERVAL_MINUTES = 3
MINUTES_IN_STANDARD_QUARTER = 12
NUM_STANDARD_QUARTERS = 4
TOTAL_GAME_MINUTES = NUM_STANDARD_QUARTERS * MINUTES_IN_STANDARD_QUARTER
TOTAL_SEGMENTS = TOTAL_GAME_MINUTES // DECISION_INTERVAL_MINUTES

# 年龄修正 (消耗)
AGE_MODIFIER_CONSUMPTION_STANDARD = 1.0
AGE_MODIFIER_CONSUMPTION_OVER_32 = 1.1

# 位置修正 (消耗)
POSITION_MODIFIER_GUARD = 1.0
POSITION_MODIFIER_FORWARD = 1.05
POSITION_MODIFIER_CENTER = 1.1

# 体能恢复基础百分比
RECOVERY_PERCENT_QUARTER_BREAK = 0.50
RECOVERY_PERCENT_HALF_TIME = 0.90

# 体能恢复年龄修正 (>32岁)
RECOVERY_AGE_MOD_QUARTER_BREAK_OVER_32 = 0.85
RECOVERY_AGE_MOD_HALF_TIME_OVER_32 = 0.80

# 战术风格权重
TACTICAL_WEIGHTS = {
    "极端进攻型": (0.60, 0.15, 0.15, 0.10),
    "进攻型": (0.50, 0.20, 0.20, 0.10),
    "均衡型": (0.30, 0.30, 0.25, 0.15),
    "防守型": (0.20, 0.50, 0.20, 0.10),
    "极端防守型": (0.15, 0.60, 0.15, 0.10),
}

# 优势系数矩阵
ADVANTAGE_MATRIX = {
    ("极端进攻型", "极端进攻型"): 0.000, ("极端进攻型", "进攻型"): -0.086, ("极端进攻型", "均衡型"): 0.000, ("极端进攻型", "防守型"): -0.300, ("极端进攻型", "极端防守型"): -0.100,
    ("进攻型", "极端进攻型"): 0.086, ("进攻型", "进攻型"): 0.000, ("进攻型", "均衡型"): -0.012, ("进攻型", "防守型"): -0.120, ("进攻型", "极端防守型"): -0.093,
    ("均衡型", "极端进攻型"): 0.000, ("均衡型", "进攻型"): 0.012, ("均衡型", "均衡型"): 0.000, ("均衡型", "防守型"): 0.135, ("均衡型", "极端防守型"): -0.052,
    ("防守型", "极端进攻型"): 0.300, ("防守型", "进攻型"): 0.120, ("防守型", "均衡型"): -0.135, ("防守型", "防守型"): 0.000, ("防守型", "极端防守型"): -0.235,
    ("极端防守型", "极端进攻型"): 0.100, ("极端防守型", "进攻型"): 0.093, ("极端防守型", "均衡型"): 0.052, ("极端防守型", "防守型"): 0.235, ("极端防守型", "极端防守型"): 0.000,
}

# 球员类
class Player:
    def __init__(self, name, position, age, minutes_played, offensive_score, defensive_score, teamwork_score, stamina_score):
        self.name = name
        self.position = position
        self.age = age
        self.minutes_played = minutes_played
        self.offensive_score = float(offensive_score)
        self.defensive_score = float(defensive_score)
        self.teamwork_score = float(teamwork_score)
        self.stamina_score = float(stamina_score)
        self.current_stamina = float(stamina_score)
        self.current_off = float(offensive_score)
        self.current_def = float(defensive_score)
        self.current_team = float(teamwork_score)
        self.current_ovr = 0.0

    def _get_age_modifier_consumption(self):
        return AGE_MODIFIER_CONSUMPTION_OVER_32 if self.age > 32 else AGE_MODIFIER_CONSUMPTION_STANDARD

    def _get_position_modifier_consumption(self):
        if self.position in ['PG', 'SG']:
            return POSITION_MODIFIER_GUARD
        elif self.position in ['SF', 'PF']:
            return POSITION_MODIFIER_FORWARD
        elif self.position == 'C':
            return POSITION_MODIFIER_CENTER
        return 1.0

    def consume_stamina(self, minutes):
        if minutes <= 0:
            return
        base_rate = BASE_STAMINA_CONSUMPTION_RATE_PER_MINUTE
        age_mod = self._get_age_modifier_consumption()
        pos_mod = self._get_position_modifier_consumption()
        consumption_rate_per_minute = base_rate * age_mod * pos_mod
        stamina_consumed = consumption_rate_per_minute * minutes * self.stamina_score
        self.current_stamina = max(0, self.current_stamina - stamina_consumed)

    def recover_stamina(self, rest_type):
        base_recovery_percentage = 0.0
        age_modifier = 1.0
        if rest_type == "quarter_break":
            base_recovery_percentage = RECOVERY_PERCENT_QUARTER_BREAK
            if self.age > 32:
                age_modifier = RECOVERY_AGE_MOD_QUARTER_BREAK_OVER_32
        elif rest_type == "halftime_break":
            base_recovery_percentage = RECOVERY_PERCENT_HALF_TIME
            if self.age > 32:
                age_modifier = RECOVERY_AGE_MOD_HALF_TIME_OVER_32
        final_recovery_percentage = base_recovery_percentage * age_modifier
        stamina_recovered = final_recovery_percentage * self.stamina_score
        self.current_stamina = min(self.stamina_score, self.current_stamina + stamina_recovered)

    def update_ability_and_ovr(self, weights):
        stamina_percentage = self.current_stamina / self.stamina_score if self.stamina_score > 0 else 0.0
        stamina_factor = 1.0 if stamina_percentage >= 0.90 else 0.9 if stamina_percentage >= 0.70 else 0.7 if stamina_percentage >= 0.50 else 0.5
        self.current_off = self.offensive_score * stamina_factor
        self.current_def = self.defensive_score * stamina_factor
        self.current_team = self.teamwork_score * stamina_factor
        w_off, w_def, w_team, w_stam = weights
        self.current_ovr = (w_off * self.current_off + w_def * self.current_def + w_team * self.current_team +
                            w_stam * stamina_percentage)

    def __repr__(self):
        return (f"P({self.name}, {self.position}, A:{self.age}, "
                f"S:{self.current_stamina:.1f}/{self.stamina_score:.1f}, "
                f"Off:{self.current_off:.1f}, Def:{self.current_def:.1f}, Team:{self.current_team:.1f}, "
                f"OVR:{self.current_ovr:.2f})")

# 动态计算战术风格和权重
def calculate_tactical_weights(lineup):
    if not lineup:
        return TACTICAL_WEIGHTS["均衡型"], "均衡型"
    avg_off = sum(p.offensive_score for p in lineup) / len(lineup)
    avg_def = sum(p.defensive_score for p in lineup) / len(lineup)
    avg_team = sum(p.teamwork_score for p in lineup) / len(lineup)
    max_diff = max(abs(avg_off - avg_def), abs(avg_def - avg_team), abs(avg_off - avg_team))
    print(f"DEBUG: 平均评分 - Off: {avg_off:.2f}, Def: {avg_def:.2f}, Team: {avg_team:.2f}, 最大差值: {max_diff:.2f}")
    scores = {'off': avg_off, 'def': avg_def, 'team': avg_team}
    max_score = max(scores.values())
    threshold = 5
    significant_threshold = 20
    if abs(avg_off - avg_def) <= threshold and abs(avg_def - avg_team) <= threshold and abs(avg_off - avg_team) <= threshold:
        return TACTICAL_WEIGHTS["均衡型"], "均衡型"
    elif scores['off'] == max_score:
        if avg_off - max(avg_def, avg_team) > significant_threshold:
            return TACTICAL_WEIGHTS["极端进攻型"], "极端进攻型"
        return TACTICAL_WEIGHTS["进攻型"], "进攻型"
    elif scores['def'] == max_score:
        if avg_def - max(avg_off, avg_team) > significant_threshold:
            return TACTICAL_WEIGHTS["极端防守型"], "极端防守型"
        return TACTICAL_WEIGHTS["防守型"], "防守型"
    else:
        return TACTICAL_WEIGHTS["均衡型"], "均衡型"

# 生成随机对手阵容
def generate_opponent_lineup():
    positions = ['PG', 'SG', 'SF', 'PF', 'C']
    opponent_lineup = []
    for pos in positions:
        if pos in ['PG', 'SG']:
            off_range = (85, 100)
            def_range = (75, 90)
            team_range = (80, 95)
        elif pos in ['SF', 'PF']:
            off_range = (80, 95)
            def_range = (80, 95)
            team_range = (80, 95)
        else:
            off_range = (75, 90)
            def_range = (85, 100)
            team_range = (80, 95)
        player = {
            'name': f"Opponent_{pos}_{random.randint(1, 100)}",
            'position': pos,
            'offensive_score': random.uniform(*off_range),
            'defensive_score': random.uniform(*def_range),
            'teamwork_score': random.uniform(*team_range),
            'stamina_score': random.uniform(80, 100)
        }
        opponent_lineup.append(Player(
            name=player['name'],
            position=player['position'],
            age=random.randint(22, 35),
            minutes_played=random.uniform(30, 38),
            offensive_score=player['offensive_score'],
            defensive_score=player['defensive_score'],
            teamwork_score=player['teamwork_score'],
            stamina_score=player['stamina_score']
        ))
    weights, style = calculate_tactical_weights(opponent_lineup)
    for p in opponent_lineup:
        p.update_ability_and_ovr(weights)
    return opponent_lineup, style

# 寻找最优阵容
def find_optimal_lineup(players, opponent_style, required_positions=('PG', 'SG', 'SF', 'PF', 'C')):
    position_map = {pos: [] for pos in required_positions}
    for p in players:
        if p.position in position_map:
            position_map[p.position].append(p)
    for pos, player_list in position_map.items():
        if not player_list:
            print(f"错误: 位置 {pos} 没有可用球员。")
            return None, 0, None
    list_of_player_lists = [position_map[pos] for pos in required_positions]
    best_lineup = None
    max_adjusted_ovr_sum = -1.0
    best_style = None
    for lineup_tuple in itertools.product(*list_of_player_lists):
        if len(set(p.name for p in lineup_tuple)) != len(lineup_tuple):
            continue
        lineup = list(lineup_tuple)
        weights, style = calculate_tactical_weights(lineup)
        for p in lineup:
            p.update_ability_and_ovr(weights)
        ovr_sum = sum(p.current_ovr for p in lineup)
        advantage = ADVANTAGE_MATRIX.get((style, opponent_style), 0.0)
        adjusted_ovr_sum = ovr_sum * (1 + advantage)
        if adjusted_ovr_sum > max_adjusted_ovr_sum:
            max_adjusted_ovr_sum = adjusted_ovr_sum
            best_lineup = lineup
            best_style = style
    if best_lineup:
        weights = calculate_tactical_weights(best_lineup)[0]
        for p in players:
            p.update_ability_and_ovr(weights)
    return best_lineup, max_adjusted_ovr_sum, best_style

# 局势评估函数
def evaluate_situation(current_lineup, opponent_lineup):
    our_avg_off = sum(p.current_off for p in current_lineup) / len(current_lineup)
    opp_avg_def = sum(p.current_def for p in opponent_lineup) / len(opponent_lineup)
    if our_avg_off > opp_avg_def + 10:
        return random.choice(["防守型", "极端防守型"]) if random.random() < 0.5 else None
    elif opp_avg_def > our_avg_off + 10:
        return random.choice(["进攻型", "极端进攻型"]) if random.random() < 0.3 else None
    return None

# 可视化风格变化
def plot_opponent_style_history(lineup_history):
    segments = [entry["segment"] for entry in lineup_history]
    styles = [entry["opponent_style"] for entry in lineup_history]
    style_map = {s: i for i, s in enumerate(TACTICAL_WEIGHTS.keys())}
    style_nums = [style_map[s] for s in styles]
    
    plt.figure(figsize=(10, 6))
    plt.plot(segments, style_nums, marker='o', color='b')
    plt.yticks(range(len(style_map)), list(style_map.keys()))
    plt.xlabel("比赛段")
    plt.ylabel("对手战术风格")
    plt.title("对手战术风格变化")
    plt.grid(True)
    plt.show()

# 模拟逻辑
def run_simulation(team_data_file='second_dataset/selected_team.csv', team_name="选定队伍"):
    try:
        df = pd.read_csv(team_data_file)
        print(f"成功从 {team_data_file} 加载12人名单: {len(df)} 名球员")
    except FileNotFoundError:
        print(f"错误: 找不到文件 {team_data_file}")
        return
    
    required_columns = ['Player', 'Primary_Position', 'Age', 'MP', 'Offensive_Score', 'Defensive_Score', 
                       'Teamwork_Score', 'Stamina_Score']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"数据缺少必要的列: {col}")
    
    players = [Player(
        name=row['Player'],
        position=row['Primary_Position'],
        age=row['Age'],
        minutes_played=row.get('MP', 30.0),
        offensive_score=row['Offensive_Score'],
        defensive_score=row['Defensive_Score'],
        teamwork_score=row['Teamwork_Score'],
        stamina_score=row['Stamina_Score']
    ) for _, row in df.iterrows()]
    
    print(f"--- 开始模拟 {team_name} (决策间隔: {DECISION_INTERVAL_MINUTES} 分钟) ---")
    
    current_lineup = []
    lineup_history = []
    
    print("--- 比赛开始前: 选择初始阵容 ---")
    opponent_lineup, opponent_style = generate_opponent_lineup()
    print(f"对手初始战术风格: {opponent_style}")
    optimal_lineup, total_ovr, tactical_style = find_optimal_lineup(players, opponent_style)
    if optimal_lineup:
        current_lineup = optimal_lineup
        weights = calculate_tactical_weights(current_lineup)[0]
        print(f"本队战术风格: {tactical_style}, 权重: {weights}")
        print(f"初始阵容 (调整后总 OVR: {total_ovr:.2f}):")
        for p in current_lineup:
            print(f"  {p.name} ({p.position}) - OVR: {p.current_ovr:.2f}, Stamina: {p.current_stamina:.1f}/{p.stamina_score:.1f}")
        lineup_history.append({
            "segment": "Start",
            "lineup": [p.name for p in current_lineup],
            "total_ovr": total_ovr,
            "game_time_end": 0,
            "tactical_style": tactical_style,
            "weights": weights,
            "opponent_style": opponent_style
        })
    else:
        print("错误: 无法选择初始阵容。")
        return

    for segment_idx in range(TOTAL_SEGMENTS):
        current_game_time_start = segment_idx * DECISION_INTERVAL_MINUTES
        current_game_time_end = (segment_idx + 1) * DECISION_INTERVAL_MINUTES
        current_quarter = (current_game_time_start // MINUTES_IN_STANDARD_QUARTER) + 1
        minutes_into_quarter_start = current_game_time_start % MINUTES_IN_STANDARD_QUARTER
        minutes_into_quarter_end = minutes_into_quarter_start + DECISION_INTERVAL_MINUTES
        
        print(f"\n--- 比赛段 {segment_idx + 1}/{TOTAL_SEGMENTS} 开始 ---")
        print(f"(第 {current_quarter} 节, {minutes_into_quarter_start}-{minutes_into_quarter_end} 分钟, 总比赛时间: {current_game_time_start} 分钟)")
        
        if not current_lineup:
            print("错误: 当前阵容为空。")
            break
            
        print(f"场上球员 (比赛段 {segment_idx + 1}):")
        weights, style = calculate_tactical_weights(current_lineup)
        print(f"本队当前战术风格: {style}, 权重: {weights}, 对手战术风格: {opponent_style}")
        for p in current_lineup:
            print(f"  {p.name} ({p.position}) 上场前 - Stamina: {p.current_stamina:.1f}, OVR: {p.current_ovr:.2f}")
            p.consume_stamina(DECISION_INTERVAL_MINUTES)
            p.update_ability_and_ovr(weights)
            print(f"  {p.name} ({p.position}) 上场后 - Stamina: {p.current_stamina:.1f}, OVR: {p.current_ovr:.2f}")

        print(f"\n--- 比赛段 {segment_idx + 1} 结束 (总比赛时间: {current_game_time_end} 分钟) ---")
        
        official_break_occurred = False
        if current_game_time_end == MINUTES_IN_STANDARD_QUARTER * 2:
            print("进行半场休息 (15分钟)...")
            for p in players:
                p.recover_stamina("halftime_break")
            official_break_occurred = True
        elif current_game_time_end % MINUTES_IN_STANDARD_QUARTER == 0 and current_game_time_end < TOTAL_GAME_MINUTES:
            print("进行节间休息 (2分钟)...")
            for p in players:
                p.recover_stamina("quarter_break")
            official_break_occurred = True

        if official_break_occurred:
            print("休息后更新球员状态...")
            weights = calculate_tactical_weights(current_lineup)[0]
            for p in players:
                p.update_ability_and_ovr(weights)

        if current_game_time_end < TOTAL_GAME_MINUTES:
            print(f"\n为下一个比赛段 (比赛段 {segment_idx + 2}) 选择阵容:")
            situation_style = evaluate_situation(current_lineup, opponent_lineup)
            if situation_style:
                opponent_style = situation_style
                print(f"局势触发: 对手切换到 {opponent_style}")
            else:
                opponent_lineup, opponent_style = generate_opponent_lineup()
                print(f"对手战术风格: {opponent_style}")
            optimal_lineup, total_ovr, tactical_style = find_optimal_lineup(players, opponent_style)
            if optimal_lineup:
                current_lineup = optimal_lineup
                weights = calculate_tactical_weights(current_lineup)[0]
                print(f"本队战术风格: {tactical_style}, 权重: {weights}")
                print(f"下一个比赛段阵容 (调整后总 OVR: {total_ovr:.2f}):")
                for p in current_lineup:
                    print(f"  {p.name} ({p.position}) - OVR: {p.current_ovr:.2f}, Stamina: {p.current_stamina:.1f}/{p.stamina_score:.1f}")
                lineup_history.append({
                    "segment": f"Seg{segment_idx + 2}",
                    "lineup": [p.name for p in current_lineup],
                    "total_ovr": total_ovr,
                    "game_time_end": current_game_time_end,
                    "tactical_style": tactical_style,
                    "weights": weights,
                    "opponent_style": opponent_style
                })
            else:
                print(f"错误: 无法为下一个比赛段选择阵容。")
                break
        else:
            print("\n--- 比赛结束 (所有比赛段完成) ---")

    print("\n\n--- 阵容历史 (每3分钟决策点) ---")
    for entry in lineup_history:
        print(f"时刻: {entry['segment']} (在 {entry['game_time_end']} 分钟后), 阵容: {', '.join(entry['lineup'])}, "
              f"总OVR: {entry['total_ovr']:.2f}, 战术风格: {entry['tactical_style']}, 权重: {entry['weights']}, "
              f"对手风格: {entry['opponent_style']}")

    # 保存模拟结果到 CSV
    sim_data = [{
        "Segment": entry["segment"],
        "GameTime": entry["game_time_end"],
        "Lineup": ", ".join(entry["lineup"]),
        "Total_OVR": entry["total_ovr"],
        "Team_Style": entry["tactical_style"],
        "Opponent_Style": entry["opponent_style"]
    } for entry in lineup_history]
    sim_df = pd.DataFrame(sim_data)
    sim_df.to_csv("second_dataset/simulation_results.csv", index=False)
    print(f"模拟结果已保存到: second_dataset/simulation_results.csv")

    print(f"\n--- {team_name} 最终球员状态 ---")
    for p in sorted(players, key=lambda x: x.name):
        print(p)

    # # 可视化对手风格
    # plot_opponent_style_history(lineup_history)

# 主程序
if __name__ == "__main__":
    run_simulation(team_data_file='second_dataset/selected_team.csv', team_name="Dynamic Team")