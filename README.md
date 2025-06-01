# README

欢迎使用 NBA 球队优化与模拟系统！此系统旨在通过数据分析和优化算法为 NBA 球队构建最佳 12 人轮换阵容，并模拟比赛过程以评估阵容表现。以下是系统中的每个脚本的详细说明，包括其功能和生成的文件。

---

# 如何运行代码

---

## 1. `enhanced_player_scoring.py`

### 功能

此脚本用于构建增强版 NBA 球员能力评分系统。通过读取 2023-2024 NBA 常规赛球员统计数据，计算球员的进攻能力、防守能力、团队合作能力和体能属性评分，并生成综合评分。评分基于加权平均和标准化处理，新增体能属性为后续 12 人轮换建模提供支持。

### 生成的文件

- `second_dataset/nba_player_enhanced_scores.csv`: 包含增强版球员评分数据，包括 `Player`、`Pos`、`Age`、`G`、`MP`、`Offensive_Score`、`Defensive_Score`、`Teamwork_Score`、`Stamina_Score` 和 `Overall_Score` 等列。

---

## 2. `merge_salary_data.py`

### 功能

此脚本将球员薪资数据整合到增强版球员评分系统中。通过读取球员评分数据和 2024-25 赛季薪资数据，清理并合并数据集，计算球员的性价比指标（`Value_Score`），并按综合评分排序，为后续优化提供完整的数据支持。

### 生成的文件

- `second_dataset/nba_player_enhanced_scores_with_salary.csv`: 包含球员评分和薪资信息，包括 `Player`、`Primary_Position`、`Pos`、`Age`、`G`、`MP`、`Offensive_Score`、`Defensive_Score`、`Teamwork_Score`、`Stamina_Score`、`Overall_Score`、`Salary_2023_2024` 和 `Value_Score` 等列。

---

## 3. `complete_twelve_man_optimizer.py`

### 功能

此脚本实现 NBA 12 人轮换阵容优化模型。通过线性规划优化算法，根据指定的战术风格（默认均衡型）、薪资帽和最低评分阈值，生成最佳 12 人阵容。支持位置分配、年龄结构平衡和综合实力下限等约束条件。

### 生成的文件

- `second_dataset/selected_team.csv`: 包含优化后的 12 人阵容数据，包括 `Player`、`Pos`、`Age`、`Offensive_Score`、`Defensive_Score`、`Teamwork_Score`、`Stamina_Score`、`Overall_Score` 和 `Salary_2023_2024` 等列。

---

## 4. `simp_dyn.py`

### 功能

此脚本实现比赛动态模拟系统。通过读取优化后的 12 人阵容数据，模拟 48 分钟比赛过程，每 3 分钟决策一次阵容调整。模拟考虑球员体能消耗、战术风格变化和对手阵容影响，并输出每段比赛的阵容和表现数据。

### 生成的文件

- `second_dataset/simulation_results.csv`: 包含模拟结果，包括 `Segment`、`GameTime`、`Lineup`、`Total_OVR`、`Team_Style` 和 `Opponent_Style` 等列，记录每次阵容决策点的信息。

---

## 5. `ui.py`

### 功能

此脚本提供图形用户界面 (GUI)，基于 Tkinter 框架。用户可以通过输入薪资帽运行优化算法，查看优化后的 12 人阵容和模拟结果。界面分为“Team Roster”和“Simulation Results”两个标签页，支持交互式操作。

### 生成的文件

- 无直接生成文件，但通过调用 `complete_twelve_man_optimizer.py` 和 `simp_dyn.py` 间接生成 `second_dataset/selected_team.csv` 和 `second_dataset/simulation_results.csv`。

---

## 6. `team_analy.py`

### 功能

此脚本用于分析 NBA 比赛数据，计算各队之间的历史胜负差矩阵。通过读取比赛数据（`NBA_GAMES.csv`），提取“本队”和“对手”信息，统计胜场数，并生成胜负差矩阵。

### 生成的文件

- `head_to_head_diff.csv`: 包含各队对其他队的胜负差数据，行列均为球队缩写，数值表示胜负差。

---

## 使用说明

1. **依赖安装**: 确保安装所需库，例如 `pandas`、`numpy`、`pulp` 和 `matplotlib`。
2. **运行顺序建议**:
   - 首先运行 `enhanced_player_scoring.py` 生成评分数据。
   - 然后运行 `merge_salary_data.py` 整合薪资数据。
   - 接着运行 `complete_twelve_man_optimizer.py` 优化阵容。
   - 最后运行 `simp_dyn.py` 进行模拟，或通过 `ui.py` 交互式操作。
3. **数据文件**: 确保 `initial_dataset` 和 `second_dataset` 目录中存在所需 CSV 文件（路径可在脚本中调整）。
4. **输出检查**: 生成的文件保存在 `second_dataset` 目录下，可用于进一步分析或可视化。

---

# 对核心代码的说明

---

以下是对 `enhanced_player_scoring.py`、`complete_twelve_man_optimizer.py` 和 `simp_dyn.py` 脚本的算法补充，融入了一些高级但不过于复杂的术语（如加权线性组合、动态规划、蒙特卡洛模拟等），以提升技术深度，同时保持可读性和实用性。算法描述将聚焦于核心逻辑，结合原有代码结构进行优化和解释。

---

### 1. `enhanced_player_scoring.py` - 增强版球员能力评分系统算法

#### 算法概述

该脚本采用**多维能力评估框架**，通过加权线性组合和标准化变换，构建球员的综合能力评分模型。核心目标是通过统计数据提取特征，计算进攻、防守、团队合作和体能四个维度评分，并利用四分位标准化法处理异常值，确保评分分布在 0-100 范围内。

#### 算法细节

1. **数据预处理与特征提取**:

   - 输入：2023-2024 NBA 球员统计数据（`2023-2024 NBA Player Stats - Regular.csv`）。
   - 步骤：使用加权平均法（weighted averaging）合并多条球员记录，权重基于出场场次（`G`），以减少数据噪声。
   - 输出：合并后的数据集，保留关键统计特征（如 `FG%`、`PTS`、`DRB` 等）。

2. **多维度评分计算**:

   - **进攻能力评分 (`calculate_offensive_score`)**:
     - 采用**线性加权模型**，结合得分效率（`PTS * eFG%`）、投篮稳定性（加权平均 `3P%`、`2P%`、`FT%`）和失误控制（`1 - TOV/FGA`）。
     - 权重分配为 0.5（效率）、0.3（稳定性）、0.2（控制），通过经验校准。
   - **防守能力评分 (`calculate_defensive_score`)**:
     - 基于**加权线性组合**，集成篮板（`DRB`）、抢断（`STL`）和盖帽（`BLK`）的贡献（权重 0.8），并加入犯规控制因子（`1 - PF/6`，权重 0.2）。
   - **团队合作评分 (`calculate_teamwork_score`)**:
     - 综合助攻（`AST`）和进攻篮板（`ORB`）贡献，结合球权保护（`1 - TOV/(AST+FGA+TOV)`）和上场时间稳定性（`MP/48`），权重分别为 0.4、0.3、0.3。
   - **体能属性评分 (`calculate_stamina_score`)**:
     - 引入**分层评估模型**，基于出场持久性（`G/82 * MP/48`）、年龄因子（分段线性插值）、效率维持（`PTS/MP`）和首发稳定性（`GS/G`），权重为 0.25、0.2、0.25、0.15、0.15。

3. **标准化与异常值处理**:

   - 使用**四分位范围法 (IQR)** 检测并裁剪异常值，公式为 `[Q1 - 1.5*IQR, Q3 + 1.5*IQR]`。
   - 应用**线性归一化**将评分映射到 [0, 100]，避免除零错误时赋默认值 50。

4. **综合评分生成**:
   - 采用**加权线性组合**，权重分别为 0.3（进攻）、0.25（防守）、0.25（团队）、0.2（体能），生成 `Overall_Score`。

#### 输出

- 生成 `nba_player_enhanced_scores.csv`，包含标准化后的多维度评分数据。

---

### 2. `complete_twelve_man_optimizer.py` - 12 人轮换阵容优化模型算法

#### 算法概述

该脚本基于**线性规划 (Linear Programming)** 和**约束优化**技术，构建 NBA 12 人轮换阵容优化模型。目标是最大化加权综合实力，同时满足薪资帽、位置分配和年龄结构等约束条件，采用 PuLP 库实现求解。

#### 算法细节

1. **问题建模**:

   - **目标函数**: 最大化加权评分总和，公式为：
     \[
     \text{Maximize} \sum*{i} w*{\text{off}} \cdot S*{\text{off},i} + w*{\text{def}} \cdot S*{\text{def},i} + w*{\text{team}} \cdot S*{\text{team},i} + w*{\text{stam}} \cdot S\_{\text{stam},i}
     \]
     其中 \( w \) 为战术风格权重，\( S \) 为球员评分，\( i \) 为球员索引。
   - **决策变量**: 二元变量 \( x_i \)（0 或 1），表示是否选择球员 \( i \)。

2. **约束条件**:

   - **人数约束**: \(\sum x_i = 12\)，确保选择 12 名球员。
   - **位置分配约束**: 对每个位置（`PG`、`SG`、`SF`、`PF`、`C`），设置下限 2 人、上限 3 人：
     \[
     2 \leq \sum\_{i \in \text{pos}} x_i \leq 3
     \]
   - **薪资约束**: \(\sum\_{i} \text{Salary}\_i \cdot x_i \leq \text{salary_cap}\)，限制总薪资。
   - **首发约束**: \(\sum\_{i \in \text{Overall_Score} > 70} x_i \geq 5\)，确保至少 5 名高评分球员。
   - **年龄结构约束**: 年轻球员（\(\text{Age} \leq 25\)）和老将（\(\text{Age} \geq 30\)）数量分别在 [2, 6] 范围内。
   - **实力下限**: \(\sum\_{i} \text{Overall_Score}\_i \cdot x_i \geq 12 \cdot 60\)，平均评分不低于 60。

3. **战术风格权重**:

   - 根据 `team_style`（进攻型、防守型、均衡型等）动态调整权重，例如均衡型为 (0.3, 0.3, 0.25, 0.15)。
   - 引入**动态加权调整**，基于球员评分分布优化权重分配。

4. **求解与后处理**:
   - 使用**CBC 求解器**（PuLP_CBC_CMD）求解优化问题。
   - 若无解，提示调整参数（如降低 `min_score_threshold` 或增加 `salary_cap`）。
   - 输出选定球员数据，排序并保存。

#### 输出

- 生成 `selected_team.csv`，包含优化后的 12 人阵容数据。

---

### 3. `simp_dyn.py` - 比赛动态模拟算法

#### 算法概述

该脚本基于**动态规划 (Dynamic Programming)** 和**蒙特卡洛模拟 (Monte Carlo Simulation)**，实现 48 分钟比赛的动态阵容调整和体能管理。核心目标是根据实时体能和对手战术，优化每 3 分钟的五人阵容，模拟比赛过程。

#### 算法细节

1. **球员状态建模**:

   - **体能消耗模型**: 每分钟消耗率基于基线率（0.035）、年龄修正和位置修正，公式为：
     \[
     \text{Stamina_Consumed} = 0.035 \cdot \text{Age_Mod} \cdot \text{Pos_Mod} \cdot \text{Stamina_Score} \cdot \text{Minutes}
     \]
   - **体能恢复模型**: 节间（50%）和半场（90%）恢复率，结合年龄修正（如 >32 岁降至 85%/80%）。

2. **战术风格动态调整**:

   - 采用**加权聚类分析**，根据阵容平均评分（进攻、防守、团队）动态推断战术风格（均衡型、进攻型等）。
   - 引入**优势矩阵 (Advantage Matrix)**，根据对手风格调整 OVR 得分，公式为：
     \[
     \text{Adjusted*OVR} = \text{OVR_Sum} \cdot (1 + \text{Advantage}*{style*{our}, style*{opp}})
     \]

3. **阵容优化**:

   - **贪婪搜索 (Greedy Search)**: 每段比赛从所有球员中选择五人，满足位置要求（`PG`、`SG`、`SF`、`PF`、`C`）。
   - **能力衰减修正**: 体能百分比影响能力得分，采用分层函数（>90% 1.0，70-90% 0.9，50-70% 0.7，<50% 0.5）。
   - **局势评估**: 基于攻防差（>10 分触发战术切换），引入随机扰动模拟对手策略变化。

4. **模拟流程**:

   - **时间分段**: 将 48 分钟分为 16 段（每 3 分钟决策一次）。
   - **状态更新**: 每段更新球员体能和能力，节间/半场触发恢复。
   - **结果记录**: 保存每段阵容、总 OVR 和战术风格至历史记录。

5. **输出与可视化**:
   - 生成 `simulation_results.csv`，包含 `Segment`、`GameTime`、`Lineup` 等字段。
   - 可选**时间序列可视化**，绘制对手战术风格变化（当前注释掉）。

#### 输出

- 生成 `second_dataset/simulation_results.csv`，记录模拟过程数据。

---

### 总结

这些算法结合了**统计建模**、**优化理论**和**动态模拟**，从数据处理到策略优化再到实时调整，形成了完整的 NBA 球队分析与模拟体系。用户可根据需求调整参数（如权重、阈值）以适应不同场景。
