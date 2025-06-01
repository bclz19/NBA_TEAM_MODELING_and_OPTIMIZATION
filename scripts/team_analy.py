import pandas as pd

# 1. 读取 CSV 文件（请根据实际路径修改文件名）
df = pd.read_csv(r'C:\Users\Administrator\Desktop\NBA_TEAM_MODELING\initial_dataset\NBA_GAMES.csv')

# 2. 从 MATCHUP 中提取“本队”与“对手”简称
#    假设 MATCHUP 格式为 "XXX vs. YYY" 或 "XXX @ YYY"，其中 XXX、YYY 为三字母球队缩写
df['Team']     = df['MATCHUP'].str.split().str[0]       # “本队”是字符串的第一个元素
df['Opponent'] = df['MATCHUP'].str.split().str[-1]      # “对手”是字符串的最后一个元素

# 3. 标记胜利：如果 WL == 'W'，则本队获胜（标记 1），否则标记 0
df['WinFlag'] = df['WL'].map(lambda x: 1 if x == 'W' else 0)

# 4. 构造球队列表：合并“Team”和“Opponent”列后去重、排序
all_teams = pd.concat([df['Team'], df['Opponent']]).unique()
teams = sorted(all_teams)

# 5. 初始化一个全 0 的 DataFrame，用来存储各队对每个对手的胜场数
win_counts = pd.DataFrame(0, index=teams, columns=teams, dtype=int)

# 6. 遍历每一行，如果本队赢，则 win_counts[Team][Opponent] 加 1
for _, row in df.iterrows():
    t = row['Team']
    o = row['Opponent']
    if row['WinFlag'] == 1:
        win_counts.at[t, o] += 1

# 7. 计算胜负差矩阵：diff_matrix[A][B] = A 对 B 的胜场数 - B 对 A 的胜场数
diff_matrix = pd.DataFrame(index=teams, columns=teams, dtype=int)

for a in teams:
    for b in teams:
        if a == b:
            diff_matrix.at[a, b] = 0
        else:
            diff_matrix.at[a, b] = win_counts.at[a, b] - win_counts.at[b, a]

# 8. 保存结果（可选）并打印
output_path = r'C:\Users\Administrator\Desktop\NBA_TEAM_MODELING\head_to_head_diff.csv'
diff_matrix.to_csv(output_path)
print(f"胜负差矩阵已保存到：{output_path}\n")
print(diff_matrix)
