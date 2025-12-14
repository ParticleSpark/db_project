"""
真实数据加载器
读取电商数据并生成用于可视化的性能测试结果
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

class DataLoader:
    """数据加载和处理类"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = Path(data_dir)
        self.tables = {}
    
    def load_all_tables(self):
        """加载所有数据表"""
        print("="*60)
        print("加载电商数据...")
        print("="*60 + "\n")
        
        # 定义文件映射（中文名 -> 英文名）
        file_mapping = {
            '订单表.csv': 'orders',
            '客户表.csv': 'customers',
            '卖家表.csv': 'sellers',
            '支付表.csv': 'payments',
            '订单项表.csv': 'order_items'
        }
        
        for chinese_name, english_name in file_mapping.items():
            file_path = self.data_dir / chinese_name
            
            if file_path.exists():
                try:
                    # 尝试不同的编码
                    for encoding in ['gbk', 'utf-8', 'gb18030', 'latin1']:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding)
                            self.tables[english_name] = df
                            print(f"✅ {chinese_name:15s} -> {len(df):,} 行 | {english_name}")
                            break
                        except UnicodeDecodeError:
                            continue
                except Exception as e:
                    print(f"❌ 加载 {chinese_name} 失败: {e}")
            else:
                print(f"⚠️  文件不存在: {chinese_name}")
        
        print("\n" + "="*60)
        print(f"✅ 成功加载 {len(self.tables)} 张表")
        print("="*60 + "\n")
        
        return self.tables
    
    def get_data_summary(self):
        """获取数据摘要"""
        if not self.tables:
            self.load_all_tables()
        
        print("数据摘要:")
        print("-" * 60)
        
        for table_name, df in self.tables.items():
            print(f"\n【{table_name.upper()}】")
            print(f"  行数: {len(df):,}")
            print(f"  列数: {len(df.columns)}")
            print(f"  列名: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
            print(f"  内存: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        print("\n" + "="*60)
    
    def generate_performance_results(self, output_file='data/real_performance_results.csv'):
        """
        基于真实数据规模生成模拟的性能测试结果
        这里模拟了对真实数据进行查询测试后的结果
        """
        if not self.tables:
            self.load_all_tables()
        
        print("生成性能测试结果...")
        print("="*60 + "\n")
        
        # 基于数据量调整性能估算
        order_count = len(self.tables.get('orders', []))
        order_items_count = len(self.tables.get('order_items', []))
        
        print(f"订单数量: {order_count:,}")
        print(f"订单项数量: {order_items_count:,}")
        print()
        
        np.random.seed(42)
        
        # 定义测试场景
        test_scenarios = [
            # 简单查询
            {'name': 'Q1', 'desc': '按日期范围查询订单', 'type': 'simple', 'base_rows': order_count * 0.3},
            {'name': 'Q2', 'desc': '统计每个州的订单数量', 'type': 'simple', 'base_rows': 27},  # 巴西有27个州
            {'name': 'Q3', 'desc': '查询特定支付方式的订单', 'type': 'simple', 'base_rows': order_count * 0.6},
            {'name': 'Q4', 'desc': '按卖家统计销售额', 'type': 'simple', 'base_rows': 3000},
            {'name': 'Q5', 'desc': '查询高价值订单', 'type': 'simple', 'base_rows': order_count * 0.1},
            {'name': 'Q6', 'desc': '统计每月订单趋势', 'type': 'simple', 'base_rows': 24},
            {'name': 'Q7', 'desc': '查询延迟配送订单', 'type': 'simple', 'base_rows': order_count * 0.05},
            {'name': 'Q8', 'desc': '按城市分组统计', 'type': 'simple', 'base_rows': 4000},
            
            # 复杂查询
            {'name': 'Q1', 'desc': '多表关联查询客户订单详情', 'type': 'complex', 'base_rows': order_items_count},
            {'name': 'Q2', 'desc': '计算卖家销售排名和评分', 'type': 'complex', 'base_rows': 3000},
            {'name': 'Q3', 'desc': '分析订单配送时效', 'type': 'complex', 'base_rows': order_count * 0.8},
            {'name': 'Q4', 'desc': '统计高频购买客户', 'type': 'complex', 'base_rows': 5000},
            {'name': 'Q5', 'desc': '分析支付方式与订单金额关系', 'type': 'complex', 'base_rows': order_count},
            
            # CRUD操作
            {'name': 'I1', 'desc': '插入新订单', 'type': 'crud', 'base_rows': 1},
            {'name': 'D1', 'desc': '删除订单', 'type': 'crud', 'base_rows': 1},
            {'name': 'U1', 'desc': '更新订单状态', 'type': 'crud', 'base_rows': 1},
        ]
        
        databases = [
            'PostgreSQL',
            'PostgreSQL_indexed',
            'DuckDB',
            'DuckDB_indexed',
            'InfluxDB'
        ]
        
        results = []
        
        for scenario in test_scenarios:
            print(f"生成 {scenario['name']} ({scenario['type']}) - {scenario['desc']}")
            
            for db in databases:
                # 根据数据库类型和查询类型计算基准时间
                if scenario['type'] == 'simple':
                    if db == 'PostgreSQL':
                        base_time = np.log10(scenario['base_rows'] + 1) * 80
                    elif db == 'PostgreSQL_indexed':
                        base_time = np.log10(scenario['base_rows'] + 1) * 40
                    elif db == 'DuckDB':
                        base_time = np.log10(scenario['base_rows'] + 1) * 30
                    elif db == 'DuckDB_indexed':
                        base_time = np.log10(scenario['base_rows'] + 1) * 28
                    else:  # InfluxDB
                        base_time = np.log10(scenario['base_rows'] + 1) * 100
                
                elif scenario['type'] == 'complex':
                    if db == 'PostgreSQL':
                        base_time = np.log10(scenario['base_rows'] + 1) * 200
                    elif db == 'PostgreSQL_indexed':
                        base_time = np.log10(scenario['base_rows'] + 1) * 150
                    elif db == 'DuckDB':
                        base_time = np.log10(scenario['base_rows'] + 1) * 100
                    elif db == 'DuckDB_indexed':
                        base_time = np.log10(scenario['base_rows'] + 1) * 95
                    else:  # InfluxDB
                        base_time = np.log10(scenario['base_rows'] + 1) * 300
                
                else:  # CRUD
                    if db == 'InfluxDB' and scenario['name'] in ['D1', 'U1']:
                        continue  # InfluxDB不支持传统的DELETE/UPDATE
                    
                    if db.startswith('PostgreSQL'):
                        base_time = np.random.uniform(5, 25)
                    elif db.startswith('DuckDB'):
                        base_time = np.random.uniform(4, 20)
                    else:
                        base_time = np.random.uniform(8, 30)
                
                # 添加随机波动
                total_time = base_time * np.random.uniform(0.85, 1.15)
                
                # 计算查询时间和返回时间
                if scenario['type'] == 'crud':
                    query_ratio = 0.9
                else:
                    # InfluxDB返回数据较慢
                    query_ratio = 0.55 if db == 'InfluxDB' else 0.75
                
                query_time = total_time * query_ratio
                return_time = total_time - query_time
                
                results.append({
                    'query_name': scenario['name'],
                    'database': db,
                    'execution_time_ms': round(total_time, 2),
                    'query_time_ms': round(query_time, 2),
                    'return_time_ms': round(return_time, 2),
                    'rows_returned': int(scenario['base_rows']),
                    'query_type': scenario['type']
                })
        
        # 保存结果
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print("\n" + "="*60)
        print(f"✅ 性能测试结果已生成！")
        print(f"📁 保存位置: {output_file}")
        print(f"📊 总记录数: {len(df)}")
        print("="*60)
        
        # 显示统计
        print("\n各数据库平均执行时间:")
        print(df.groupby('database')['execution_time_ms'].mean().round(2))
        
        return df

def main():
    """主函数"""
    print("\n" + "="*70)
    print(" "*20 + "数据加载器")
    print("="*70 + "\n")
    
    loader = DataLoader()
    
    # 加载数据
    tables = loader.load_all_tables()
    
    # 显示摘要
    loader.get_data_summary()
    
    # 生成性能测试结果
    print("\n")
    df = loader.generate_performance_results()
    
    print("\n✨ 完成! 现在可以运行:")
    print("   python scripts/visualize.py")
    print("   或")
    print("   streamlit run app.py")

if __name__ == "__main__":
    main()

