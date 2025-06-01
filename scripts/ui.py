#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from complete_twelve_man_optimizer import TeamOptimizer
from simp_dyn import run_simulation

class NBATeamOptimizerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NBA Team Optimizer")
        self.root.geometry("1200x800")

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # Team Roster Tab
        self.team_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.team_frame, text="Team Roster")

        # Simulation Results Tab
        self.simulation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.simulation_frame, text="Simulation Results")

        # Initialize UI components
        self.setup_team_tab()
        self.setup_simulation_tab()

    def setup_team_tab(self):
        # Salary Cap Input
        ttk.Label(self.team_frame, text="Enter Salary Cap (in millions):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.salary_cap_entry = ttk.Entry(self.team_frame)
        self.salary_cap_entry.insert(0, "250")
        self.salary_cap_entry.grid(row=0, column=1, padx=5, pady=5)

        # Run Optimization Button
        ttk.Button(self.team_frame, text="Run Optimization", command=self.run_optimization).grid(row=0, column=2, padx=5, pady=5)

        # Treeview for Team Roster
        self.team_tree = ttk.Treeview(self.team_frame, columns=(
            "Position", "Player", "Age", "Games", "Minutes", "Offensive", "Defensive", "Teamwork", "Stamina", "Overall", "Salary", "Value", "Weighted"
        ), show="headings")
        self.team_tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Configure column headings
        headings = {
            "Position": "位置", "Player": "球员姓名", "Age": "年龄", "Games": "场次", "Minutes": "分钟",
            "Offensive": "进攻", "Defensive": "防守", "Teamwork": "配合", "Stamina": "体能",
            "Overall": "综合", "Salary": "薪资(百万)", "Value": "性价比", "Weighted": "加权评分"
        }
        for col, text in headings.items():
            self.team_tree.heading(col, text=text)
            self.team_tree.column(col, width=100, anchor="center")

        # Configure grid weights
        self.team_frame.columnconfigure(0, weight=1)
        self.team_frame.rowconfigure(1, weight=1)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.team_frame, orient="vertical", command=self.team_tree.yview)
        scrollbar.grid(row=1, column=3, sticky="ns")
        self.team_tree.configure(yscrollcommand=scrollbar.set)

    def setup_simulation_tab(self):
        # Treeview for Simulation Results
        self.simulation_tree = ttk.Treeview(self.simulation_frame, columns=(
            "Segment", "GameTime", "Lineup", "Total_OVR", "Team_Style", "Opponent_Style"
        ), show="headings")
        self.simulation_tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Configure column headings
        sim_headings = {
            "Segment": "比赛段", "GameTime": "比赛时间", "Lineup": "阵容",
            "Total_OVR": "总OVR", "Team_Style": "本队风格", "Opponent_Style": "对手风格"
        }
        # for col, text in sim_headings.items():
        #     self.simulation_tree.heading(col, text=text)
        #     self.simulation_tree.column(col, width=150, anchor="center")

        for col, text in sim_headings.items():
            self.simulation_tree.heading(col, text=text)
            if col == "Lineup":  # 增加 Lineup 列宽度以适应较长字符串
                self.simulation_tree.column(col, width=470, anchor="w")  # 宽度从 150 增加到 300
            else:
                self.simulation_tree.column(col, width=120, anchor="center")

        # Configure grid weights
        self.simulation_frame.columnconfigure(0, weight=1)
        self.simulation_frame.rowconfigure(0, weight=1)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.simulation_frame, orient="vertical", command=self.simulation_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.simulation_tree.configure(yscrollcommand=scrollbar.set)



    def run_optimization(self):
        try:
            # Get salary cap
            salary_cap = float(self.salary_cap_entry.get()) * 1_000_000
            if salary_cap <= 0:
                raise ValueError("薪资帽必须为正数")

            # Clear previous simulation results file to ensure fresh simulation
            sim_file = "second_dataset/simulation_results.csv"
            if os.path.exists(sim_file):
                os.remove(sim_file)
                print(f"已删除旧的模拟结果文件: {sim_file}")

            # Run optimizer
            optimizer = TeamOptimizer()
            result = optimizer.optimize_team(salary_cap=salary_cap)
            if result is None:
                messagebox.showerror("错误", "优化失败，请检查薪资帽或数据文件")
                return

            # Clear previous team data
            for item in self.team_tree.get_children():
                self.team_tree.delete(item)

            # Load and display team roster
            team_file = "second_dataset/selected_team.csv"
            if not os.path.exists(team_file):
                messagebox.showerror("错误", f"未找到队伍数据文件: {team_file}")
                return
            team_df = pd.read_csv(team_file)
            for _, row in team_df.iterrows():
                self.team_tree.insert("", "end", values=(
                    row["Primary_Position"],
                    row["Player"],
                    int(row["Age"]),
                    row.get("G", 0),
                    f"{row.get('MP', 0):.1f}",
                    f"{row['Offensive_Score']:.1f}",
                    f"{row['Defensive_Score']:.1f}",
                    f"{row['Teamwork_Score']:.1f}",
                    f"{row['Stamina_Score']:.1f}",
                    f"{row['Overall_Score']:.1f}",
                    f"{row['Salary_2023_2024']/1_000_000:.2f}",
                    f"{row.get('Value_Score', 0):.2f}",
                    f"{row.get('Weighted_Score', 0):.2f}"
                ))

            # Run simulation
            run_simulation(team_data_file="second_dataset/selected_team.csv", team_name="Dynamic Team")

            # Load and display simulation results
            if not os.path.exists(sim_file):
                messagebox.showerror("错误", f"模拟结果文件未生成: {sim_file}")
                return
            sim_df = pd.read_csv(sim_file)
            for item in self.simulation_tree.get_children():
                self.simulation_tree.delete(item)
            for _, row in sim_df.iterrows():
                self.simulation_tree.insert("", "end", values=(
                    row["Segment"],
                    row["GameTime"],
                    row["Lineup"],
                    f"{row['Total_OVR']:.2f}",
                    row["Team_Style"],
                    row["Opponent_Style"]
                ))

            messagebox.showinfo("成功", "优化和模拟已完成，结果已显示")

        except ValueError as e:
            messagebox.showerror("错误", f"无效输入: {str(e)}")
        except FileNotFoundError as e:
            messagebox.showerror("错误", f"数据文件缺失或路径错误: {str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NBATeamOptimizerUI(root)
    root.mainloop()