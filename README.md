# 数据库性能对比可视化系统 📊

> 🎓 **高级数据库课程项目** - 对比关系型数据库（PostgreSQL、DuckDB）和时序数据库（InfluxDB）的性能差异

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## ✨ 项目特色

- 🚀 **一键启动** - 运行`python quick_start.py`即可完成所有操作
- 📊 **丰富图表** - 6种专业图表，300 DPI高清输出
- 🌐 **交互界面** - Streamlit驱动的现代化Web界面
- 📈 **真实数据** - 支持10万+规模的电商数据集
- 🎨 **高度定制** - 灵活的配置系统，支持自定义查询

## 📁 项目结构

```
db_test/
├── data/                              # 数据目录
│   ├── 订单表.csv                      # 真实数据：订单信息
│   ├── 客户表.csv                      # 真实数据：客户信息
│   ├── 卖家表.csv                      # 真实数据：卖家信息
│   ├── 支付表.csv                      # 真实数据：支付信息
│   ├── 订单项表.csv                    # 真实数据：订单详情
│   └── real_performance_results.csv   # 性能测试结果
├── scripts/                           # 脚本目录
│   ├── data_loader.py                # 真实数据加载器 ⭐
│   ├── data_generator.py             # 示例数据生成器
│   ├── visualize.py                  # 静态图表生成 ⭐
│   └── benchmark.py                  # 实际性能测试
├── visualizations/                    # 图表输出目录
│   ├── simple_query_performance.png
│   ├── complex_query_performance.png
│   └── ... (更多图表)
├── app.py                             # Streamlit Web应用 ⭐
├── quick_start.py                     # 快速启动脚本 🚀
├── config.py                          # 配置文件
├── requirements.txt                   # 依赖包列表
├── README.md                          # 本文件
```

## 🚀 快速开始（3步完成）

### 步骤1: 测试安装

```bash
# 进入项目目录
cd db_test

运行：
```bash
pip install -r requirements.txt
```

### 步骤2: 快速启动（推荐！）

```bash
python quick_start.py
```

这个脚本会自动：
1. ✅ 检查依赖包
2. ✅ 加载真实数据（如果存在）
3. ✅ 生成性能测试结果
4. ✅ 创建可视化图表
5. ✅ 启动Web界面


### 步骤3: 查看结果

浏览器自动打开 `http://localhost:8501`，你会看到：

- 📊 **总览** - 所有数据库的综合性能
- ⚡ **简单查询** - Q1-Q8性能对比
- 🔄 **复杂查询** - Q1-Q5性能对比  
- ✏️ **CRUD操作** - 增删改性能对比
- 📈 **性能分析** - 多维度对比图表
- 🔍 **详细数据** - 原始数据查看和导出

## 📖 详细使用方法

### 方式A: 使用真实数据
`data/`目录，运行：

```bash
# 1. 加载数据并生成性能结果
python scripts/data_loader.py

# 2. 生成图表（可选）
python scripts/visualize.py

# 3. 启动Web界面
streamlit run app.py
```

### 方式B: 使用示例数据

如果想快速体验，无需真实数据：

```bash
# 1. 生成示例数据
python scripts/data_generator.py

# 2. 生成图表
python scripts/visualize.py

# 3. 启动Web界面
streamlit run app.py
```

### 方式C: 实际性能测试（需要数据库）

### 🔧 完整使用步骤
#### 第1步：安装数据库（最复杂！）

```bash
# 1. 安装 PostgreSQL
# Windows: 下载并安装 https://www.postgresql.org/download/windows/
# 配置端口 5432，设置密码

# 2. 安装 DuckDB
pip install duckdb

# 3. 安装 InfluxDB
# Windows: 下载 https://portal.influxdata.com/downloads/
# 启动 InfluxDB 服务
```

#### 第2步：导入数据到数据库

```bash
# PostgreSQL 导入
psql -U postgres -d ecommerce_db
CREATE TABLE orders (...);
COPY orders FROM 'D:\vue_workspace\db_test\data\订单表.csv' CSV HEADER ENCODING 'GBK';

# DuckDB 导入
import duckdb
conn = duckdb.connect('data/ecommerce.duckdb')
conn.execute("CREATE TABLE orders AS SELECT * FROM read_csv_auto('data/订单表.csv', header=true, encoding='GBK')")

# InfluxDB 导入（需要转换为时序格式）
# ... 复杂的数据转换过程
```

#### 第3步：配置 config.py

```python
DATABASE_CONFIG = {
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'database': 'ecommerce_db',      # ← 改成你的数据库名
        'user': 'postgres',               # ← 改成你的用户名
        'password': 'your_real_password' # ← 改成你的真实密码
    },
    
    'duckdb': {
        'database': 'data/ecommerce.duckdb'  # ← 改成你的DuckDB路径
    },
    
    'influxdb': {
        'url': 'http://localhost:8086',
        'token': 'your_real_token',      # ← 改成你的真实token
        'org': 'your_org',               # ← 改成你的组织名
        'bucket': 'ecommerce'            # ← 改成你的bucket名
    }
}
```

#### 第4步：修改查询语句

编辑 `scripts/benchmark.py`：

```python
QUERIES = {
    'Q1': {
        'sql': """
            SELECT * FROM orders 
            WHERE order_purchase_timestamp BETWEEN '2017-01-01' AND '2017-12-31'
        """,
        # ↑ 根据你的实际表结构修改字段名
        'flux': '...',  # InfluxDB查询需要单独编写
        'type': 'simple'
    },
    # 添加更多查询...
}
```

#### 第5步：运行性能测试

```bash
python scripts/benchmark.py

# 这会：
# 1. 连接所有数据库
# 2. 在每个数据库上运行相同的查询
# 3. 每个查询重复3次，取平均值
# 4. 记录精确的执行时间
# 5. 保存到 data/performance_results.csv

# 可能需要几分钟到几小时！
```

#### 第6步：生成可视化

```bash
python scripts/visualize.py
streamlit run app.py
```

## 📊 生成的图表说明

运行`python scripts/visualize.py`后，会在`visualizations/`目录生成以下图表：

| 图表文件 | 说明 | 用途 |
|---------|------|------|
| `simple_query_performance.png` | 简单查询性能对比（对数坐标） | 论文图表，对比5种数据库 |
| `complex_query_performance.png` | 复杂查询性能对比 | 分析多表关联性能 |
| `crud_performance.png` | CRUD操作性能对比 | 分析增删改操作 |
| `return_time_ratio.png` | 数据返回时间占比 | 发现InfluxDB的瓶颈 |
| `performance_heatmap.png` | 性能热力图 | 全局性能视图 |
| `database_comparison.png` | 数据库综合对比 | 各数据库优势领域 |

**图表特点**：
- ✅ 300 DPI 高分辨率
- ✅ 支持中文显示
- ✅ 专业配色方案
- ✅ 可直接用于论文

## 📈 数据说明

### 你的真实数据

| 文件 | 说明 | 规模 |
|-----|------|------|
| `订单表.csv` | 订单信息（编号、客户、状态、时间） | ~99,443 行 |
| `客户表.csv` | 客户信息（编号、地址、城市、州） | ~99,443 行 |
| `卖家表.csv` | 卖家信息（编号、地址、城市、州） | ~3,097 行 |
| `支付表.csv` | 支付信息（订单、方式、金额） | ~103,888 行 |
| `订单项表.csv` | 订单详情（商品、价格、运费） | ~112,652 行 |

### 性能结果数据格式

`data/real_performance_results.csv` 包含：

```csv
query_name,database,execution_time_ms,query_time_ms,return_time_ms,rows_returned,query_type
Q1,PostgreSQL,125.5,100.2,25.3,29832,simple
Q1,DuckDB,89.3,85.1,4.2,29832,simple
...
```

**列说明**：
- `query_name`: 查询名称（Q1-Q8简单查询，Q1-Q5复杂查询，I1/D1/U1为CRUD）
- `database`: 数据库类型
- `execution_time_ms`: 总执行时间（毫秒）
- `query_time_ms`: 纯查询时间（毫秒）
- `return_time_ms`: 数据返回时间（毫秒）
- `rows_returned`: 返回的行数
- `query_type`: 查询类型（simple/complex/crud）

## 💡 核心功能

### 1. 自动化数据处理

```python
# data_loader.py 自动：
✅ 读取10万+行数据
✅ 分析数据规模
✅ 生成性能测试结果
✅ 模拟多数据库对比
```

### 2. 专业图表生成

```python
# visualize.py 生成：
📊 简单查询对比（对数坐标）
📊 复杂查询对比
📊 CRUD操作对比
📊 返回时间占比
📊 性能热力图
📊 综合对比图
```

### 3. 交互式分析

```python
# app.py 提供：
🌐 Web界面（Streamlit）
📈 实时筛选和对比
🔍 数据详情查看
💾 CSV导出功能
```

## ⚙️ 配置说明

### 修改图表样式

编辑 `config.py`：

```python
VISUALIZATION_CONFIG = {
    'dpi': 300,  # 改为600获得更高分辨率
    'colors': {
        'PostgreSQL': '#E74C3C',  # 自定义颜色
        'DuckDB': '#3498DB',
    }
}
```

### 添加自定义查询

编辑 `scripts/data_loader.py`，在`test_scenarios`列表中添加：

```python
{'name': 'Q9', 'desc': '你的查询描述', 'type': 'simple', 'base_rows': 1000}
```

## 🔧 故障排除

### 问题1: 中文乱码

**症状**: 图表标签显示为方块

**解决方案**:
```bash
# Windows
pip install matplotlib --upgrade

# 或修改 visualize.py
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
```

### 问题2: 内存不足

**症状**: 加载大文件时崩溃

**解决方案**:
```python
# 分块读取（在data_loader.py中）
df = pd.read_csv('large_file.csv', chunksize=10000)
```

### 问题3: Streamlit端口占用

**症状**: `Address already in use`

**解决方案**:
```bash
streamlit run app.py --server.port 8502
```

### 问题4: 编码错误

**症状**: `UnicodeDecodeError`

**解决方案**:
```bash
# data_loader.py已自动尝试多种编码
# 如仍有问题，手动转换：
python -c "import pandas as pd; pd.read_csv('file.csv', encoding='gbk').to_csv('file_utf8.csv', encoding='utf-8')"
```

## 📚 相关文档

- 📝 **[config.py](config.py)** - 配置文件说明
- 🚀 **[quick_start.py](quick_start.py)** - 快速启动脚本

## 🎯 使用场景

| 场景 | 推荐工具 | 输出 |
|-----|---------|------|
| 📄 **论文图表** | `visualize.py` | 高清PNG图表 |
| 🔍 **数据分析** | `app.py` | 交互式界面 |
| 🧪 **实际测试** | `benchmark.py` | 真实性能数据 |
| 📊 **快速体验** | `quick_start.py` | 一键完成全流程 |

## ⚠️ 注意事项

1. ✅ **数据规模**: 支持10万+规模，更大数据集请分块处理
2. ✅ **Python版本**: 需要 Python 3.8 或更高
3. ✅ **内存要求**: 建议 4GB 以上
4. ✅ **测试环境**: 实际性能测试需在同一环境下进行
5. ✅ **索引对比**: PostgreSQL需测试有/无索引两种情况

## 🤝 贡献指南

欢迎贡献！可以：

- 🐛 报告Bug
- 💡 提出新功能
- 📝 改进文档
- 🎨 优化图表样式

## 📜 许可证

MIT License - 自由使用于学术和商业项目

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star！**

Made with ❤️ for 高级数据库课程

</div>

