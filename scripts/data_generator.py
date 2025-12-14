"""
示例性能数据生成器
用于快速体验可视化功能，无需实际运行数据库测试
"""

import pandas as pd
import numpy as np
import os

def generate_sample_data():
    """生成示例性能测试数据"""
    
    np.random.seed(42)
    
    # 定义查询和数据库
    simple_queries = [f'Q{i}' for i in range(1, 9)]  # Q1-Q8
    complex_queries = [f'Q{i}' for i in range(1, 6)]  # Q1-Q5
    crud_operations = ['I1', 'D1', 'U1']
    
    databases = [
        'PostgreSQL',
        'PostgreSQL_indexed',
        'DuckDB',
        'DuckDB_indexed',
        'InfluxDB'
    ]
    
    data = []
    
    # 生成简单查询数据
    print("生成简单查询数据...")
    for query in simple_queries:
        for db in databases:
            # 基准时间（根据数据库类型调整）
            if db == 'PostgreSQL':
                base_time = np.random.uniform(100, 500)
            elif db == 'PostgreSQL_indexed':
                base_time = np.random.uniform(50, 200)
            elif db == 'DuckDB':
                base_time = np.random.uniform(40, 150)
            elif db == 'DuckDB_indexed':
                base_time = np.random.uniform(35, 140)
            else:  # InfluxDB
                base_time = np.random.uniform(150, 600)
            
            # 计算各部分时间
            total_time = base_time * np.random.uniform(0.9, 1.1)
            query_time = total_time * np.random.uniform(0.6, 0.8)
            return_time = total_time - query_time
            rows = int(np.random.uniform(100, 10000))
            
            data.append({
                'query_name': query,
                'database': db,
                'execution_time_ms': round(total_time, 2),
                'query_time_ms': round(query_time, 2),
                'return_time_ms': round(return_time, 2),
                'rows_returned': rows,
                'query_type': 'simple'
            })
    
    # 生成复杂查询数据
    print("生成复杂查询数据...")
    for query in complex_queries:
        for db in databases:
            if db == 'PostgreSQL':
                base_time = np.random.uniform(500, 2000)
            elif db == 'PostgreSQL_indexed':
                base_time = np.random.uniform(300, 1500)
            elif db == 'DuckDB':
                base_time = np.random.uniform(200, 1000)
            elif db == 'DuckDB_indexed':
                base_time = np.random.uniform(180, 950)
            else:  # InfluxDB
                base_time = np.random.uniform(800, 3000)
            
            total_time = base_time * np.random.uniform(0.9, 1.1)
            query_time = total_time * np.random.uniform(0.7, 0.85)
            return_time = total_time - query_time
            rows = int(np.random.uniform(1000, 50000))
            
            data.append({
                'query_name': query,
                'database': db,
                'execution_time_ms': round(total_time, 2),
                'query_time_ms': round(query_time, 2),
                'return_time_ms': round(return_time, 2),
                'rows_returned': rows,
                'query_type': 'complex'
            })
    
    # 生成CRUD操作数据
    print("生成CRUD操作数据...")
    for operation in crud_operations:
        for db in databases:
            # InfluxDB不支持传统CRUD，跳过
            if db == 'InfluxDB' and operation in ['D1', 'U1']:
                continue
            
            if db.startswith('PostgreSQL'):
                base_time = np.random.uniform(10, 50)
            else:  # DuckDB
                base_time = np.random.uniform(8, 40)
            
            if db == 'InfluxDB':
                base_time = np.random.uniform(15, 60)
            
            total_time = base_time * np.random.uniform(0.9, 1.1)
            query_time = total_time * np.random.uniform(0.85, 0.95)
            return_time = total_time - query_time
            rows = 1 if operation != 'I1' else int(np.random.uniform(1, 100))
            
            data.append({
                'query_name': operation,
                'database': db,
                'execution_time_ms': round(total_time, 2),
                'query_time_ms': round(query_time, 2),
                'return_time_ms': round(return_time, 2),
                'rows_returned': rows,
                'query_type': 'crud'
            })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存到data目录
    output_path = os.path.join('data', 'sample_performance.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ 示例数据已生成！")
    print(f"📁 保存位置: {output_path}")
    print(f"📊 数据行数: {len(df)}")
    print(f"📋 查询类型: {df['query_type'].unique()}")
    print(f"💾 数据库类型: {df['database'].unique()}")
    
    # 显示数据摘要
    print("\n数据摘要:")
    print(df.groupby(['query_type', 'database'])['execution_time_ms'].agg(['mean', 'min', 'max']).round(2))
    
    return df

if __name__ == "__main__":
    print("="*60)
    print("数据库性能测试 - 示例数据生成器")
    print("="*60)
    print()
    
    df = generate_sample_data()
    
    print("\n" + "="*60)
    print("数据预览（前10行）:")
    print("="*60)
    print(df.head(10).to_string())
    
    print("\n✨ 现在可以运行以下命令查看可视化：")
    print("   python scripts/visualize.py")
    print("   或")
    print("   streamlit run app.py")

