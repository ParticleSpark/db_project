"""
项目配置文件
集中管理所有可配置参数
"""

# ============================================================================
# 数据库连接配置（用于实际性能测试）
# ============================================================================

DATABASE_CONFIG = {
    # PostgreSQL配置
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'database': 'ecommerce_db',
        'user': 'postgres',
        'password': 'your_password'
    },
    
    # DuckDB配置
    'duckdb': {
        'database': 'data/ecommerce.duckdb'
    },
    
    # InfluxDB配置
    'influxdb': {
        'url': 'http://localhost:8086',
        'token': 'your_influxdb_token',
        'org': 'your_org',
        'bucket': 'ecommerce'
    }
}

# ============================================================================
# 文件路径配置
# ============================================================================

DATA_PATHS = {
    # 输入数据文件
    'orders': 'data/订单表.csv',
    'customers': 'data/客户表.csv',
    'sellers': 'data/卖家表.csv',
    'payments': 'data/支付表.csv',
    'order_items': 'data/订单项表.csv',
    
    # 输出文件
    'real_results': 'data/real_performance_results.csv',
    'sample_results': 'data/sample_performance.csv',
    'benchmark_results': 'data/performance_results.csv',
    
    # 可视化输出
    'output_dir': 'visualizations'
}

# ============================================================================
# 可视化配置
# ============================================================================

VISUALIZATION_CONFIG = {
    # 图表尺寸（英寸）
    'figure_sizes': {
        'default': (14, 7),
        'heatmap': (12, 10),
        'small': (10, 6)
    },
    
    # 分辨率
    'dpi': 300,
    
    # 颜色方案
    'colors': {
        'PostgreSQL': '#E74C3C',
        'PostgreSQL_indexed': '#C0392B',
        'DuckDB': '#3498DB',
        'DuckDB_indexed': '#2874A6',
        'InfluxDB': '#F39C12'
    },
    
    # 字体设置
    'fonts': {
        'family': ['SimHei', 'Microsoft YaHei', 'DejaVu Sans'],
        'size': {
            'title': 14,
            'label': 12,
            'tick': 10
        }
    },
    
    # 图表样式
    'style': 'whitegrid',
    'palette': 'husl'
}

# ============================================================================
# 性能测试配置
# ============================================================================

BENCHMARK_CONFIG = {
    # 测试重复次数（取平均值）
    'repeat_times': 3,
    
    # 是否预热（首次运行不计入统计）
    'warmup': True,
    
    # 超时时间（秒）
    'timeout': 300,
    
    # 是否测试索引优化
    'test_index': True,
    
    # 查询类型
    'query_types': ['simple', 'complex', 'crud']
}

# ============================================================================
# 查询定义（示例）
# ============================================================================

QUERY_DEFINITIONS = {
    # 简单查询
    'simple_queries': [
        {
            'name': 'Q1',
            'description': '按日期范围查询订单',
            'sql': "SELECT * FROM orders WHERE order_date BETWEEN '2017-01-01' AND '2017-12-31'",
            'flux': None  # InfluxDB查询
        },
        {
            'name': 'Q2',
            'description': '统计每个州的订单数量',
            'sql': "SELECT state, COUNT(*) as order_count FROM customers JOIN orders USING(customer_id) GROUP BY state",
            'flux': None
        }
        # 更多查询...
    ],
    
    # 复杂查询
    'complex_queries': [
        {
            'name': 'Q1',
            'description': '多表关联查询客户订单详情',
            'sql': """
                SELECT 
                    c.customer_id,
                    o.order_id,
                    p.payment_value,
                    oi.price,
                    s.seller_id
                FROM customers c
                JOIN orders o ON c.customer_id = o.customer_id
                JOIN payments p ON o.order_id = p.order_id
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN sellers s ON oi.seller_id = s.seller_id
                WHERE o.order_status = 'delivered'
            """,
            'flux': None
        }
        # 更多查询...
    ],
    
    # CRUD操作
    'crud_operations': [
        {
            'name': 'I1',
            'description': '插入新订单',
            'sql': "INSERT INTO orders (order_id, customer_id, order_status) VALUES ('test_001', 'cust_001', 'pending')"
        },
        {
            'name': 'D1',
            'description': '删除订单',
            'sql': "DELETE FROM orders WHERE order_id = 'test_001'"
        },
        {
            'name': 'U1',
            'description': '更新订单状态',
            'sql': "UPDATE orders SET order_status = 'delivered' WHERE order_id = 'test_001'"
        }
    ]
}

# ============================================================================
# 日志配置
# ============================================================================

LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/performance_test.log'
}

# ============================================================================
# Web界面配置（Streamlit）
# ============================================================================

WEB_CONFIG = {
    'title': '数据库性能对比分析系统',
    'icon': '📊',
    'layout': 'wide',
    'port': 8501
}

# ============================================================================
# 辅助函数
# ============================================================================

def get_database_config(db_type):
    """获取指定数据库的配置"""
    return DATABASE_CONFIG.get(db_type.lower(), {})

def get_data_path(file_key):
    """获取数据文件路径"""
    return DATA_PATHS.get(file_key, None)

def get_visualization_color(database):
    """获取数据库对应的颜色"""
    return VISUALIZATION_CONFIG['colors'].get(database, '#7F8C8D')

# ============================================================================
# 配置验证
# ============================================================================

def validate_config():
    """验证配置的有效性"""
    errors = []
    
    # 检查必要的路径
    import os
    if not os.path.exists('data'):
        errors.append("data目录不存在")
    
    if not os.path.exists('visualizations'):
        try:
            os.makedirs('visualizations')
        except:
            errors.append("无法创建visualizations目录")
    
    if errors:
        print("⚠️  配置验证失败:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ 配置验证通过")
    return True

if __name__ == "__main__":
    # 测试配置
    print("="*60)
    print("配置文件测试")
    print("="*60 + "\n")
    
    validate_config()
    
    print("\n数据库配置:")
    for db, config in DATABASE_CONFIG.items():
        print(f"  {db}: {config}")
    
    print("\n颜色方案:")
    for db, color in VISUALIZATION_CONFIG['colors'].items():
        print(f"  {db}: {color}")

