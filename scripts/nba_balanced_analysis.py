import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 加载数据
player_stats = pd.read_csv('NBA_TEAM_MODELING_and_OPTIMIZATION/initial_dataset/2023-2024 NBA Player Stats - Regular.csv', sep=';', encoding='ISO-8859-1')
games = pd.read_csv('NBA_TEAM_MODELING_and_OPTIMIZATION/initial_dataset/NBA_GAMES.csv')

# 处理球员数据
player_main_team = player_stats.loc[player_stats.groupby('Player')['MP'].idxmax()].copy()

# 提取比赛中的球队信息
def extract_teams_from_matchup(matchup):
    if ' vs. ' in matchup:
        parts = matchup.split(' vs. ')
        return parts[0].strip(), parts[1].strip()
    elif ' @ ' in matchup:
        parts = matchup.split(' @ ')
        return parts[0].strip(), parts[1].strip()
    else:
        return None, None

team_opponent = games['MATCHUP'].apply(extract_teams_from_matchup)
games['Team'] = team_opponent.apply(lambda x: x[0] if x[0] is not None else None)
games['Opponent'] = team_opponent.apply(lambda x: x[1] if x[1] is not None else None)
games = games.dropna(subset=['Team', 'Opponent'])

# 计算球队统计数据
team_offensive_stats = player_main_team.groupby('Tm').agg({
    'PTS': 'mean', 'AST': 'mean', 'FG%': 'mean', '3PA': 'mean', 
    'FTA': 'mean', 'eFG%': 'mean', 'FT%': 'mean'
}).reset_index()

team_defensive_stats = player_main_team.groupby('Tm').agg({
    'TRB': 'mean', 'STL': 'mean', 'BLK': 'mean', 'TOV': 'mean'
}).reset_index()

# 比赛数据统计
team_offensive_game = games.groupby('Team')['PTS'].mean().reset_index()
team_offensive_game.columns = ['Team', 'Avg_Points_Scored']

team_defensive_game = games.groupby('Opponent')['PTS'].mean().reset_index()
team_defensive_game.columns = ['Team', 'Avg_Points_Allowed']

team_record = games.groupby('Team').agg({
    'WL': lambda x: (x == 'W').sum(),
    'MATCHUP': 'count'
}).reset_index()
team_record.columns = ['Team', 'Wins', 'Games']
team_record['Win_Rate'] = team_record['Wins'] / team_record['Games']

# 合并数据
team_data = pd.merge(team_offensive_stats, team_defensive_stats, on='Tm', how='outer')
team_data = pd.merge(team_data, team_offensive_game, left_on='Tm', right_on='Team', how='left')
team_data = pd.merge(team_data, team_defensive_game, left_on='Tm', right_on='Team', how='left', suffixes=('', '_def'))
team_data = pd.merge(team_data, team_record, left_on='Tm', right_on='Team', how='left', suffixes=('', '_record'))

# 清理数据
team_data = team_data.drop(['Team', 'Team_def', 'Team_record'], axis=1, errors='ignore')
team_data = team_data.rename(columns={'Tm': 'Team'})
numeric_columns = team_data.select_dtypes(include=[np.number]).columns
team_data[numeric_columns] = team_data[numeric_columns].fillna(team_data[numeric_columns].mean())

# 计算攻击倾向性指数
def calculate_offensive_tendency(row):
    offensive_score = (
        (row['PTS'] / team_data['PTS'].mean() - 1) * 0.3 +
        (row['AST'] / team_data['AST'].mean() - 1) * 0.2 +
        (row['3PA'] / team_data['3PA'].mean() - 1) * 0.1 +
        (row['FTA'] / team_data['FTA'].mean() - 1) * 0.1 +
        (row['Avg_Points_Scored'] / team_data['Avg_Points_Scored'].mean() - 1) * 0.3
    )
    
    defensive_score = (
        (row['TRB'] / team_data['TRB'].mean() - 1) * 0.15 +
        (row['STL'] / team_data['STL'].mean() - 1) * 0.1 +
        (row['BLK'] / team_data['BLK'].mean() - 1) * 0.1 +
        (1 - row['Avg_Points_Allowed'] / team_data['Avg_Points_Allowed'].mean()) * 0.35
    )
    
    return offensive_score - defensive_score

team_data['Offensive_Tendency'] = team_data.apply(calculate_offensive_tendency, axis=1)

# 战术风格分类
tendency_scores = team_data['Offensive_Tendency'].values
thresholds = np.percentile(tendency_scores, [0, 20, 40, 60, 80, 100])

def classify_team_style(tendency):
    if tendency <= thresholds[1]:
        return '极防守'
    elif tendency <= thresholds[2]:
        return '防守'
    elif tendency <= thresholds[3]:
        return '均衡'
    elif tendency <= thresholds[4]:
        return '攻击'
    else:
        return '极攻击'

team_data['Tactical_Style'] = team_data['Offensive_Tendency'].apply(classify_team_style)

# 计算球队实力
def calculate_team_strength(row):
    strength_components = {
        'eFG%': 0.20, 'FT%': 0.10, 'Win_Rate': 0.35,
        'Avg_Points_Scored': 0.20, 'Avg_Points_Allowed': -0.15
    }
    
    strength_score = 0
    for stat, weight in strength_components.items():
        if stat in team_data.columns and not pd.isna(row[stat]):
            if stat == 'Avg_Points_Allowed':
                normalized = 1 - (row[stat] - team_data[stat].min()) / (team_data[stat].max() - team_data[stat].min())
            else:
                normalized = (row[stat] - team_data[stat].min()) / (team_data[stat].max() - team_data[stat].min())
            strength_score += normalized * weight
    
    return strength_score

team_data['Team_Strength'] = team_data.apply(calculate_team_strength, axis=1)

# 准备比赛分析数据
games_analysis = games.copy()
games_analysis['WinFlag'] = (games_analysis['WL'] == 'W').astype(int)

games_analysis = games_analysis.merge(
    team_data[['Team', 'Tactical_Style', 'Team_Strength']], 
    left_on='Team', right_on='Team', how='left'
)
games_analysis = games_analysis.merge(
    team_data[['Team', 'Tactical_Style', 'Team_Strength']], 
    left_on='Opponent', right_on='Team', how='left', 
    suffixes=('_Team', '_Opponent')
)

games_analysis = games_analysis.dropna(subset=['Tactical_Style_Team', 'Tactical_Style_Opponent'])
games_analysis['Strength_Diff'] = games_analysis['Team_Strength_Team'] - games_analysis['Team_Strength_Opponent']

# ================== 专注于实力均衡分析 ==================

print("=== NBA实力均衡下的战术风格克制关系分析 ===\n")

# 分析不同实力差距阈值
strength_thresholds = [0.08, 0.10, 0.12, 0.15]
all_styles = ['极攻击', '攻击', '均衡', '防守', '极防守']

for threshold in strength_thresholds:
    balanced_games = games_analysis[abs(games_analysis['Strength_Diff']) <= threshold].copy()
    
    if len(balanced_games) < 50:  # 样本量太少则跳过
        continue
        
    print(f"【实力差距 ≤ {threshold:.2f} 的比赛分析】")
    print(f"符合条件的比赛数量: {len(balanced_games)}场 (占总数 {len(balanced_games)/len(games_analysis):.1%})")
    print()
    
    # 检查数据问题
    print("数据检查:")
    print(f"实力差距范围: {balanced_games['Strength_Diff'].min():.3f} 到 {balanced_games['Strength_Diff'].max():.3f}")
    print(f"平均实力差距: {balanced_games['Strength_Diff'].mean():.3f}")
    print()
    
    # 正确的方法：综合计算每对战术风格的所有对战
    style_matchup_results = {}
    
    # 收集所有战术风格对战的结果
    for _, game in balanced_games.iterrows():
        style_a = game['Tactical_Style_Team']
        style_b = game['Tactical_Style_Opponent']
        
        # 创建有序的战术对（字典序排序确保一致性）
        if style_a <= style_b:
            matchup = (style_a, style_b)
            a_win = game['WinFlag']
        else:
            matchup = (style_b, style_a)
            a_win = 1 - game['WinFlag']
        
        if matchup not in style_matchup_results:
            style_matchup_results[matchup] = {'wins_a': 0, 'wins_b': 0, 'total': 0}
        
        if a_win == 1:
            style_matchup_results[matchup]['wins_a'] += 1
        else:
            style_matchup_results[matchup]['wins_b'] += 1
        style_matchup_results[matchup]['total'] += 1
    
    # 构建反对称的胜率矩阵
    balanced_win_matrix = pd.DataFrame(
        0.5, index=all_styles, columns=all_styles
    )
    count_matrix = pd.DataFrame(
        0, index=all_styles, columns=all_styles
    )
    
    # 填充矩阵
    for (style_a, style_b), results in style_matchup_results.items():
        total_games = results['total']
        wins_a = results['wins_a']
        wins_b = results['wins_b']
        
        if style_a == style_b:
            # 相同战术风格内部对战
            balanced_win_matrix.loc[style_a, style_b] = 0.5
            count_matrix.loc[style_a, style_b] = total_games
        else:
            # 不同战术风格对战
            winrate_a = wins_a / total_games
            winrate_b = wins_b / total_games
            
            balanced_win_matrix.loc[style_a, style_b] = winrate_a
            balanced_win_matrix.loc[style_b, style_a] = winrate_b
            count_matrix.loc[style_a, style_b] = total_games
            count_matrix.loc[style_b, style_a] = total_games
    
    # 检查对角线数据（相同风格对战）
    print("相同战术风格对战检查:")
    for style in all_styles:
        if style in balanced_win_matrix.index and style in balanced_win_matrix.columns:
            winrate = balanced_win_matrix.loc[style, style]
            count = count_matrix.loc[style, style]
            print(f"• {style} vs {style}: 胜率={winrate:.3f}, 比赛数={count}")
    print()
    
    # 优势系数矩阵 - 修正算法
    advantage_matrix = balanced_win_matrix - 0.5
    
    # 强制对角线为0（相同风格对战应该没有优势）
    for style in all_styles:
        if style in advantage_matrix.index and style in advantage_matrix.columns:
            advantage_matrix.loc[style, style] = 0.0
    
    print("胜率矩阵 (行打列):")
    print(balanced_win_matrix.round(3))
    print()
    
    print("比赛数量矩阵:")
    print(count_matrix)
    print()
    
    # 验证反对称性（应该严格成立）
    print("反对称性验证:")
    for i, style_i in enumerate(all_styles):
        for j, style_j in enumerate(all_styles):
            if i < j:  # 只检查上三角
                winrate_ij = balanced_win_matrix.loc[style_i, style_j]
                winrate_ji = balanced_win_matrix.loc[style_j, style_i]
                sum_rates = winrate_ij + winrate_ji
                print(f"{style_i} vs {style_j}: {winrate_ij:.3f} + {winrate_ji:.3f} = {sum_rates:.3f}")
    print()
    
    print("优势系数矩阵 (>0优势, <0劣势, 对角线强制为0):")
    print(advantage_matrix.round(3))
    print()
    
    # 显著克制关系识别 - 只考虑上三角矩阵避免重复
    significant_relations = []
    for i, style_i in enumerate(all_styles):
        for j, style_j in enumerate(all_styles):
            if i < j:  # 只看上三角矩阵
                winrate_ij = balanced_win_matrix.loc[style_i, style_j]
                games_count = count_matrix.loc[style_i, style_j]
                adv = winrate_ij - 0.5
                
                # 显著性标准：样本量>=3且优势>=8%
                if games_count >= 3 and abs(adv) >= 0.08:
                    if adv > 0:
                        significant_relations.append({
                            'winner': style_i, 'loser': style_j, 
                            'advantage': adv, 'count': games_count,
                            'winrate': winrate_ij
                        })
                    else:
                        significant_relations.append({
                            'winner': style_j, 'loser': style_i, 
                            'advantage': -adv, 'count': games_count,
                            'winrate': 1 - winrate_ij
                        })
    
    if significant_relations:
        print("显著克制关系:")
        # 按优势程度排序
        sorted_relations = sorted(significant_relations, key=lambda x: x['advantage'], reverse=True)
        for rel in sorted_relations:
            print(f"• {rel['winner']} 克制 {rel['loser']}: {rel['winrate']:.1%} 胜率 (优势+{rel['advantage']:.1%}, {rel['count']}场)")
    else:
        print("• 未发现显著的克制关系")
    
    print("-" * 60)
    print()

# 总体战术风格分布
print("=== 球队战术风格分布 ===")
style_counts = team_data['Tactical_Style'].value_counts()
for style in all_styles:
    count = style_counts.get(style, 0)
    teams_in_style = team_data[team_data['Tactical_Style'] == style]['Team'].tolist()
    print(f"• {style}: {count}支球队")
    if count > 0 and count <= 8:  # 只显示数量不太多的球队名单
        print(f"  {', '.join(teams_in_style)}")

print()

# 实力分布分析
print("=== 球队实力分布分析 ===")
print(f"实力指数范围: {team_data['Team_Strength'].min():.3f} - {team_data['Team_Strength'].max():.3f}")
print(f"实力标准差: {team_data['Team_Strength'].std():.3f}")

# 最强和最弱的几支球队
strongest_teams = team_data.nlargest(5, 'Team_Strength')[['Team', 'Team_Strength', 'Tactical_Style']]
weakest_teams = team_data.nsmallest(5, 'Team_Strength')[['Team', 'Team_Strength', 'Tactical_Style']]

print("\n最强5支球队:")
for _, row in strongest_teams.iterrows():
    print(f"• {row['Team']}: {row['Team_Strength']:.3f} ({row['Tactical_Style']})")

print("\n最弱5支球队:")
for _, row in weakest_teams.iterrows():
    print(f"• {row['Team']}: {row['Team_Strength']:.3f} ({row['Tactical_Style']})")

print("\n=== 分析完成 ===")
print("建议重点关注实力差距≤0.10的比赛结果，这些比赛更能反映纯战术层面的克制关系。")