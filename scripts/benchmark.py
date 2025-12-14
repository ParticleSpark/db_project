"""
数据库性能测试脚本
用于实际测试PostgreSQL、DuckDB和InfluxDB的性能
"""

import time
import pandas as pd
import os
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'database': 'your_database',
        'user': 'your_user',
        'password': 'your_password'
    },
    'duckdb': {
        'database': 'your_database.duckdb'
    },
    'influxdb': {
        'url': 'http://localhost:8086',
        'token': 'your_token',
        'org': 'your_org',
        'bucket': 'your_bucket'
    }
}

# 查询定义
QUERIES = {
    # 简单查询
    'Q1': {
        'sql': "SELECT * FROM sale WHERE sale_date BETWEEN '2020-01-01' AND '2022-01-01' AND sale_price > 10",
        'flux': 'from(bucket: "your_bucket") |> range(start: 2020-01-01T00:00:00Z, stop: 2022-01-01T00:00:00Z) |> filter(fn: (r) => r["_measurement"] == "sale") |> filter(fn: (r) => r["sale_price"] > 10)',
        'type': 'simple'
    },
    'Q2': {
        'sql': "SELECT category_name, AVG(sale_price) as avg_price FROM sale JOIN product USING(product_id) JOIN category USING(category_id) GROUP BY category_name",
        'flux': None,  # 复杂JOIN在InfluxDB中不适用
        'type': 'simple'
    },
    # 更多查询...
    
    # 复杂查询
    'Q1_complex': {
        'sql': """
            SELECT sale_type, 
                   SUM(sale_quantity) as total_quantity,
                   AVG(sale_price) as avg_price,
                   AVG(CASE WHEN discounted THEN 1 ELSE 0 END) as discount_rate
            FROM sale
            GROUP BY sale_type
            ORDER BY total_quantity DESC
        """,
        'flux': None,
        'type': 'complex'
    },
    
    # CRUD操作
    'I1': {
        'sql': "INSERT INTO wholesale (wholesale_date, product_id, wholesale_price) VALUES ('2023-01-01', '102900005115168', 5.5)",
        'flux': None,
        'type': 'crud'
    },
    'D1': {
        'sql': "DELETE FROM sale WHERE sale_id = 1",
        'flux': None,
        'type': 'crud'
    },
    'U1': {
        'sql': "UPDATE product SET loss_rate = 10.5 WHERE product_id = '102900005115168'",
        'flux': None,
        'type': 'crud'
    }
}

class DatabaseBenchmark:
    """数据库性能测试类"""
    
    def __init__(self):
        self.results = []
        self.connections = {}
    
    def connect_postgresql(self, with_index=False):
        """连接PostgreSQL"""
        try:
            import psycopg2
            conn = psycopg2.connect(**DB_CONFIG['postgresql'])
            db_name = 'PostgreSQL_indexed' if with_index else 'PostgreSQL'
            self.connections[db_name] = conn
            print(f"✅ {db_name} 连接成功")
            return conn
        except ImportError:
            print("❌ 请安装 psycopg2: pip install psycopg2-binary")
            return None
        except Exception as e:
            print(f"❌ PostgreSQL 连接失败: {e}")
            return None
    
    def connect_duckdb(self, with_index=False):
        """连接DuckDB"""
        try:
            import duckdb
            conn = duckdb.connect(DB_CONFIG['duckdb']['database'])
            db_name = 'DuckDB_indexed' if with_index else 'DuckDB'
            self.connections[db_name] = conn
            print(f"✅ {db_name} 连接成功")
            return conn
        except ImportError:
            print("❌ 请安装 duckdb: pip install duckdb")
            return None
        except Exception as e:
            print(f"❌ DuckDB 连接失败: {e}")
            return None
    
    def connect_influxdb(self):
        """连接InfluxDB"""
        try:
            from influxdb_client import InfluxDBClient
            client = InfluxDBClient(**DB_CONFIG['influxdb'])
            self.connections['InfluxDB'] = client
            print("✅ InfluxDB 连接成功")
            return client
        except ImportError:
            print("❌ 请安装 influxdb-client: pip install influxdb-client")
            return None
        except Exception as e:
            print(f"❌ InfluxDB 连接失败: {e}")
            return None
    
    def benchmark_sql_query(self, conn, query, db_name, query_name, query_type):
        """测试SQL查询"""
        cursor = conn.cursor()
        
        # 预热
        try:
            cursor.execute(query)
            cursor.fetchall()
        except:
            pass
        
        # 多次测试取平均值
        times = []
        return_times = []
        rows_count = 0
        
        for i in range(3):  # 运行3次
            start_time = time.time()
            
            try:
                cursor.execute(query)
                query_end_time = time.time()
                
                results = cursor.fetchall()
                rows_count = len(results)
                end_time = time.time()
                
                total_time = (end_time - start_time) * 1000
                query_time = (query_end_time - start_time) * 1000
                return_time = (end_time - query_end_time) * 1000
                
                times.append(total_time)
                return_times.append(return_time)
                
            except Exception as e:
                print(f"   ⚠️  {query_name} 执行失败: {e}")
                cursor.close()
                return
        
        # 记录平均结果
        avg_time = sum(times) / len(times)
        avg_return_time = sum(return_times) / len(return_times)
        avg_query_time = avg_time - avg_return_time
        
        self.results.append({
            'query_name': query_name,
            'database': db_name,
            'execution_time_ms': round(avg_time, 2),
            'query_time_ms': round(avg_query_time, 2),
            'return_time_ms': round(avg_return_time, 2),
            'rows_returned': rows_count,
            'query_type': query_type
        })
        
        print(f"   ✅ {query_name} on {db_name}: {avg_time:.2f} ms ({rows_count} rows)")
        cursor.close()
    
    def benchmark_influx_query(self, client, query, query_name, query_type):
        """测试InfluxDB查询"""
        if query is None:
            print(f"   ⚠️  {query_name} 不支持 InfluxDB")
            return
        
        query_api = client.query_api()
        
        # 预热
        try:
            query_api.query(query)
        except:
            pass
        
        # 多次测试取平均值
        times = []
        return_times = []
        rows_count = 0
        
        for i in range(3):
            start_time = time.time()
            
            try:
                result = query_api.query(query)
                query_end_time = time.time()
                
                # 计算返回的行数
                rows_count = sum([len(table.records) for table in result])
                end_time = time.time()
                
                total_time = (end_time - start_time) * 1000
                return_time = (end_time - query_end_time) * 1000
                
                times.append(total_time)
                return_times.append(return_time)
                
            except Exception as e:
                print(f"   ⚠️  {query_name} 执行失败: {e}")
                return
        
        # 记录平均结果
        avg_time = sum(times) / len(times)
        avg_return_time = sum(return_times) / len(return_times)
        avg_query_time = avg_time - avg_return_time
        
        self.results.append({
            'query_name': query_name,
            'database': 'InfluxDB',
            'execution_time_ms': round(avg_time, 2),
            'query_time_ms': round(avg_query_time, 2),
            'return_time_ms': round(avg_return_time, 2),
            'rows_returned': rows_count,
            'query_type': query_type
        })
        
        print(f"   ✅ {query_name} on InfluxDB: {avg_time:.2f} ms ({rows_count} rows)")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*60)
        print("开始性能测试...")
        print("="*60 + "\n")
        
        # 连接所有数据库
        print("1. 连接数据库...")
        self.connect_postgresql(with_index=False)
        self.connect_postgresql(with_index=True)
        self.connect_duckdb(with_index=False)
        self.connect_duckdb(with_index=True)
        self.connect_influxdb()
        print()
        
        # 测试每个查询
        print("2. 执行性能测试...")
        for query_name, query_info in QUERIES.items():
            print(f"\n测试 {query_name} ({query_info['type']}):")
            
            # SQL数据库
            for db_name, conn in self.connections.items():
                if db_name != 'InfluxDB' and query_info['sql']:
                    self.benchmark_sql_query(
                        conn, 
                        query_info['sql'], 
                        db_name, 
                        query_name, 
                        query_info['type']
                    )
            
            # InfluxDB
            if 'InfluxDB' in self.connections and query_info['flux']:
                self.benchmark_influx_query(
                    self.connections['InfluxDB'],
                    query_info['flux'],
                    query_name,
                    query_info['type']
                )
        
        # 保存结果
        self.save_results()
    
    def save_results(self):
        """保存测试结果"""
        if not self.results:
            print("\n❌ 没有测试结果可保存")
            return
        
        df = pd.DataFrame(self.results)
        output_path = 'data/performance_results.csv'
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print("\n" + "="*60)
        print(f"✅ 测试完成! 结果已保存到: {output_path}")
        print(f"📊 共测试 {len(self.results)} 条记录")
        print("="*60)
        
        # 显示摘要
        print("\n性能摘要:")
        print(df.groupby('database')['execution_time_ms'].agg(['mean', 'min', 'max']).round(2))
    
    def close_connections(self):
        """关闭所有连接"""
        for db_name, conn in self.connections.items():
            try:
                if db_name == 'InfluxDB':
                    conn.close()
                else:
                    conn.close()
                print(f"✅ {db_name} 连接已关闭")
            except:
                pass

def main():
    """主函数"""
    print("\n" + "="*70)
    print(" "*15 + "数据库性能测试系统")
    print("="*70)
    
    print("\n⚠️  注意: 请先配置数据库连接信息 (DB_CONFIG)")
    print("⚠️  注意: 请根据实际项目修改查询语句 (QUERIES)")
    
    response = input("\n是否继续? (y/n): ")
    if response.lower() != 'y':
        print("已取消测试")
        return
    
    benchmark = DatabaseBenchmark()
    
    try:
        benchmark.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
    finally:
        benchmark.close_connections()
    
    print("\n💡 提示: 运行 'python scripts/visualize.py' 生成图表")

if __name__ == "__main__":
    main()

