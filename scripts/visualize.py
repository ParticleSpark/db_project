"""
静态图表生成脚本
生成论文所需的所有性能对比图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from pathlib import Path

# 设置中文字体（支持中文显示）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

# 设置绘图样式
sns.set_style("whitegrid")
sns.set_palette("husl")

class PerformanceVisualizer:
    """性能可视化类"""
    
    def __init__(self, data_path=None):
        """初始化"""
        # 自动查找数据文件
        if data_path is None:
            possible_files = [
                'data/real_performance_results.csv',
                'data/performance_results.csv',
                'data/sample_performance.csv'
            ]
            for file in possible_files:
                if Path(file).exists():
                    data_path = file
                    break
            
            if data_path is None:
                raise FileNotFoundError("未找到数据文件! 请先运行: python scripts/data_loader.py")
        
        self.data_path = data_path
        self.output_dir = Path('visualizations')
        self.output_dir.mkdir(exist_ok=True)
        
        # 读取数据
        print(f"📖 正在读取数据: {data_path}")
        self.df = pd.read_csv(data_path)
        print(f"✅ 数据加载成功! 共 {len(self.df)} 条记录\n")
        
        # 数据库颜色映射
        self.db_colors = {
            'PostgreSQL': '#E74C3C',
            'PostgreSQL_indexed': '#C0392B',
            'DuckDB': '#3498DB',
            'DuckDB_indexed': '#2874A6',
            'InfluxDB': '#F39C12'
        }
    
    def plot_simple_queries(self):
        """图1: 简单查询性能对比（对数坐标）"""
        print("📊 生成图表 1: 简单查询性能对比...")
        
        # 筛选简单查询数据
        simple_data = self.df[self.df['query_type'] == 'simple'].copy()
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # 获取查询名称和数据库类型
        queries = sorted(simple_data['query_name'].unique())
        databases = simple_data['database'].unique()
        
        # 设置柱状图位置
        x = np.arange(len(queries))
        width = 0.15
        
        # 为每个数据库绘制柱状图
        for i, db in enumerate(databases):
            db_data = simple_data[simple_data['database'] == db]
            times = [db_data[db_data['query_name'] == q]['execution_time_ms'].values[0] 
                     if len(db_data[db_data['query_name'] == q]) > 0 else 0 
                     for q in queries]
            
            ax.bar(x + i*width, times, width, 
                   label=db.replace('_', ' '), 
                   color=self.db_colors.get(db, None))
        
        # 设置坐标轴
        ax.set_xlabel('Query', fontsize=12, fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Simple Query Performance Comparison (Log Scale)', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(queries)
        ax.set_yscale('log')
        ax.legend(loc='upper left', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, which='both')
        
        plt.tight_layout()
        output_path = self.output_dir / 'simple_query_performance.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 已保存: {output_path}")
        plt.close()
    
    def plot_complex_queries(self):
        """图2: 复杂查询性能对比"""
        print("📊 生成图表 2: 复杂查询性能对比...")
        
        # 筛选复杂查询数据
        complex_data = self.df[self.df['query_type'] == 'complex'].copy()
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # 透视表
        pivot_data = complex_data.pivot_table(
            values='execution_time_ms',
            index='query_name',
            columns='database',
            aggfunc='mean'
        )
        
        # 绘制分组柱状图
        pivot_data.plot(kind='bar', ax=ax, width=0.8, 
                        color=[self.db_colors.get(col, None) for col in pivot_data.columns])
        
        ax.set_xlabel('Query', fontsize=12, fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Complex Query Performance Comparison', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(title='Database', loc='upper left', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=0)
        
        plt.tight_layout()
        output_path = self.output_dir / 'complex_query_performance.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 已保存: {output_path}")
        plt.close()
    
    def plot_crud_operations(self):
        """图3: CRUD操作性能对比"""
        print("📊 生成图表 3: CRUD操作性能对比...")
        
        # 筛选CRUD数据
        crud_data = self.df[self.df['query_type'] == 'crud'].copy()
        
        if len(crud_data) == 0:
            print("   ⚠️  警告: 没有CRUD操作数据")
            return
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # 透视表
        pivot_data = crud_data.pivot_table(
            values='execution_time_ms',
            index='query_name',
            columns='database',
            aggfunc='mean'
        )
        
        # 绘制分组柱状图
        pivot_data.plot(kind='bar', ax=ax, width=0.8,
                        color=[self.db_colors.get(col, None) for col in pivot_data.columns])
        
        ax.set_xlabel('Operation', fontsize=12, fontweight='bold')
        ax.set_ylabel('Execution Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('CRUD Operations Performance Comparison', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(title='Database', loc='upper left', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=0)
        
        plt.tight_layout()
        output_path = self.output_dir / 'crud_performance.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 已保存: {output_path}")
        plt.close()
    
    def plot_return_time_ratio(self):
        """图4: 数据返回时间占比分析"""
        print("📊 生成图表 4: 数据返回时间占比...")
        
        # 计算返回时间占比
        self.df['return_ratio'] = (self.df['return_time_ms'] / 
                                    self.df['execution_time_ms'] * 100)
        
        # 筛选简单查询（更能体现差异）
        simple_data = self.df[self.df['query_type'] == 'simple'].copy()
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # 透视表
        pivot_data = simple_data.pivot_table(
            values='return_ratio',
            index='query_name',
            columns='database',
            aggfunc='mean'
        )
        
        # 绘制堆叠柱状图
        pivot_data.plot(kind='bar', ax=ax, width=0.8,
                        color=[self.db_colors.get(col, None) for col in pivot_data.columns])
        
        ax.set_xlabel('Query', fontsize=12, fontweight='bold')
        ax.set_ylabel('Return Time Ratio (%)', fontsize=12, fontweight='bold')
        ax.set_title('Data Return Time Ratio in Total Execution Time', 
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(title='Database', loc='upper right', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        output_path = self.output_dir / 'return_time_ratio.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 已保存: {output_path}")
        plt.close()
    
    def plot_performance_heatmap(self):
        """图5: 性能热力图"""
        print("📊 生成图表 5: 性能热力图...")
        
        # 创建透视表
        pivot_data = self.df.pivot_table(
            values='execution_time_ms',
            index='query_name',
            columns='database',
            aggfunc='mean'
        )
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 绘制热力图
        sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='YlOrRd',
                    cbar_kws={'label': 'Execution Time (ms)'},
                    linewidths=0.5, ax=ax)
        
        ax.set_title('Performance Heatmap: Execution Time Across Queries and Databases',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Database', fontsize=12, fontweight='bold')
        ax.set_ylabel('Query', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        output_path = self.output_dir / 'performance_heatmap.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 已保存: {output_path}")
        plt.close()
    
    def plot_database_comparison(self):
        """图6: 数据库综合性能对比"""
        print("📊 生成图表 6: 数据库综合性能对比...")
        
        # 按数据库和查询类型分组统计
        comparison = self.df.groupby(['database', 'query_type'])['execution_time_ms'].mean().unstack()
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 7))
        
        comparison.plot(kind='bar', ax=ax, width=0.8)
        
        ax.set_xlabel('Database', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Execution Time (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Database Performance Comparison by Query Type',
                     fontsize=14, fontweight='bold', pad=20)
        ax.legend(title='Query Type', loc='upper right', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        output_path = self.output_dir / 'database_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   ✅ 已保存: {output_path}")
        plt.close()
    
    def plot_all(self):
        """生成所有图表"""
        print("\n" + "="*60)
        print("开始生成所有图表...")
        print("="*60 + "\n")
        
        self.plot_simple_queries()
        self.plot_complex_queries()
        self.plot_crud_operations()
        self.plot_return_time_ratio()
        self.plot_performance_heatmap()
        self.plot_database_comparison()
        
        print("\n" + "="*60)
        print("✨ 所有图表生成完成!")
        print(f"📁 保存位置: {self.output_dir}")
        print("="*60)
    
    def generate_summary_report(self):
        """生成摘要报告"""
        print("\n" + "="*60)
        print("📋 性能测试摘要报告")
        print("="*60 + "\n")
        
        # 总体统计
        print("1. 总体统计")
        print(f"   - 总测试数: {len(self.df)}")
        print(f"   - 查询类型: {', '.join(self.df['query_type'].unique())}")
        print(f"   - 数据库类型: {len(self.df['database'].unique())} 种")
        print()
        
        # 各数据库平均性能
        print("2. 各数据库平均执行时间 (ms)")
        avg_performance = self.df.groupby('database')['execution_time_ms'].mean().sort_values()
        for db, time in avg_performance.items():
            print(f"   - {db:25s}: {time:8.2f} ms")
        print()
        
        # 最快和最慢的查询
        print("3. 性能极值")
        fastest = self.df.loc[self.df['execution_time_ms'].idxmin()]
        slowest = self.df.loc[self.df['execution_time_ms'].idxmax()]
        print(f"   最快: {fastest['query_name']} on {fastest['database']} - {fastest['execution_time_ms']:.2f} ms")
        print(f"   最慢: {slowest['query_name']} on {slowest['database']} - {slowest['execution_time_ms']:.2f} ms")
        print()
        
        # 返回时间占比
        print("4. 数据返回时间占比 (%)")
        self.df['return_ratio'] = self.df['return_time_ms'] / self.df['execution_time_ms'] * 100
        return_ratios = self.df.groupby('database')['return_ratio'].mean().sort_values(ascending=False)
        for db, ratio in return_ratios.items():
            print(f"   - {db:25s}: {ratio:6.2f}%")
        
        print("\n" + "="*60)

def main():
    """主函数"""
    print("\n" + "="*70)
    print(" "*15 + "数据库性能可视化系统")
    print("="*70)
    
    # 检查数据文件
    data_files = ['data/performance_results.csv', 'data/sample_performance.csv']
    data_path = None
    
    for file in data_files:
        if os.path.exists(file):
            data_path = file
            break
    
    if data_path is None:
        print("\n❌ 错误: 未找到数据文件!")
        print("请先运行以下命令生成数据:")
        print("   python scripts/data_generator.py")
        return
    
    # 创建可视化器
    visualizer = PerformanceVisualizer(data_path)
    
    # 生成所有图表
    visualizer.plot_all()
    
    # 生成摘要报告
    visualizer.generate_summary_report()
    
    print("\n💡 提示: 可以运行 'streamlit run app.py' 查看交互式界面")

if __name__ == "__main__":
    main()

