"""
数据库性能对比 - 交互式Web界面
使用Streamlit构建的交互式数据分析平台
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# 页面配置
st.set_page_config(
    page_title="数据库性能对比分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """加载数据"""
    data_files = [
        'data/real_performance_results.csv',
        'data/performance_results.csv', 
        'data/sample_performance.csv'
    ]
    
    for file in data_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            # 计算返回时间占比
            df['return_ratio'] = (df['return_time_ms'] / df['execution_time_ms'] * 100).round(2)
            return df, file
    
    return None, None

def main():
    """主函数"""
    
    # 标题
    st.markdown('<h1 class="main-header">📊 数据库性能对比分析系统</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 加载数据
    df, data_file = load_data()
    
    if df is None:
        st.error("❌ 未找到数据文件! 请先运行: `python scripts/data_generator.py`")
        return
    
    st.success(f"✅ 数据加载成功! 数据源: `{data_file}` | 共 {len(df)} 条记录")
    
    # 侧边栏
    st.sidebar.title("📋 分析选项")
    
    # 分析类型选择
    analysis_type = st.sidebar.selectbox(
        "选择分析类型",
        ["📊 总览", "⚡ 简单查询", "🔄 复杂查询", "✏️ CRUD操作", "📈 性能对比", "🔍 详细数据"]
    )
    
    # 数据库筛选
    st.sidebar.markdown("---")
    st.sidebar.subheader("数据库筛选")
    all_databases = df['database'].unique().tolist()
    selected_databases = st.sidebar.multiselect(
        "选择要对比的数据库",
        options=all_databases,
        default=all_databases
    )
    
    # 筛选数据
    filtered_df = df[df['database'].isin(selected_databases)]
    
    # 显示选中的分析
    if analysis_type == "📊 总览":
        show_overview(filtered_df)
    elif analysis_type == "⚡ 简单查询":
        show_simple_queries(filtered_df)
    elif analysis_type == "🔄 复杂查询":
        show_complex_queries(filtered_df)
    elif analysis_type == "✏️ CRUD操作":
        show_crud_operations(filtered_df)
    elif analysis_type == "📈 性能对比":
        show_performance_comparison(filtered_df)
    else:
        show_detailed_data(filtered_df)

def show_overview(df):
    """总览页面"""
    st.markdown('<h2 class="sub-header">📊 性能测试总览</h2>', unsafe_allow_html=True)
    
    # 关键指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("总测试数", len(df))
    with col2:
        st.metric("查询类型", len(df['query_type'].unique()))
    with col3:
        st.metric("数据库数量", len(df['database'].unique()))
    with col4:
        avg_time = df['execution_time_ms'].mean()
        st.metric("平均执行时间", f"{avg_time:.2f} ms")
    
    st.markdown("---")
    
    # 数据库平均性能对比
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("各数据库平均执行时间")
        avg_by_db = df.groupby('database')['execution_time_ms'].mean().sort_values()
        
        fig = px.bar(
            x=avg_by_db.values,
            y=avg_by_db.index,
            orientation='h',
            labels={'x': '平均执行时间 (ms)', 'y': '数据库'},
            color=avg_by_db.values,
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("查询类型分布")
        query_type_counts = df['query_type'].value_counts()
        
        fig = px.pie(
            values=query_type_counts.values,
            names=query_type_counts.index,
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # 性能热力图
    st.subheader("性能热力图")
    pivot_data = df.pivot_table(
        values='execution_time_ms',
        index='query_name',
        columns='database',
        aggfunc='mean'
    )
    
    fig = px.imshow(
        pivot_data,
        labels=dict(x="数据库", y="查询", color="执行时间 (ms)"),
        color_continuous_scale='RdYlGn_r',
        aspect='auto'
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

def show_simple_queries(df):
    """简单查询分析"""
    st.markdown('<h2 class="sub-header">⚡ 简单查询性能分析</h2>', unsafe_allow_html=True)
    
    simple_df = df[df['query_type'] == 'simple']
    
    if len(simple_df) == 0:
        st.warning("没有简单查询数据")
        return
    
    # 执行时间对比（对数坐标）
    st.subheader("执行时间对比（对数坐标）")
    fig = px.bar(
        simple_df,
        x='query_name',
        y='execution_time_ms',
        color='database',
        barmode='group',
        log_y=True,
        labels={'execution_time_ms': '执行时间 (ms)', 'query_name': '查询'},
        title='简单查询执行时间对比'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # 数据返回时间占比
    st.subheader("数据返回时间占比")
    pivot_return = simple_df.pivot_table(
        values='return_ratio',
        index='query_name',
        columns='database',
        aggfunc='mean'
    )
    
    fig = px.bar(
        pivot_return,
        barmode='group',
        labels={'value': '返回时间占比 (%)', 'query_name': '查询'},
        title='数据返回时间占总执行时间的比例'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # 统计表格
    st.subheader("统计数据")
    stats = simple_df.groupby('database')['execution_time_ms'].agg(['mean', 'min', 'max', 'std']).round(2)
    stats.columns = ['平均值', '最小值', '最大值', '标准差']
    st.dataframe(stats, use_container_width=True)

def show_complex_queries(df):
    """复杂查询分析"""
    st.markdown('<h2 class="sub-header">🔄 复杂查询性能分析</h2>', unsafe_allow_html=True)
    
    complex_df = df[df['query_type'] == 'complex']
    
    if len(complex_df) == 0:
        st.warning("没有复杂查询数据")
        return
    
    # 执行时间对比
    st.subheader("执行时间对比")
    fig = px.bar(
        complex_df,
        x='query_name',
        y='execution_time_ms',
        color='database',
        barmode='group',
        labels={'execution_time_ms': '执行时间 (ms)', 'query_name': '查询'},
        title='复杂查询执行时间对比'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # 查询时间分解
    st.subheader("查询时间分解")
    
    # 创建堆叠柱状图
    fig = go.Figure()
    
    for db in complex_df['database'].unique():
        db_data = complex_df[complex_df['database'] == db]
        fig.add_trace(go.Bar(
            name=f'{db} - 查询时间',
            x=db_data['query_name'],
            y=db_data['query_time_ms'],
            text=db_data['query_time_ms'].round(2),
            textposition='inside'
        ))
        fig.add_trace(go.Bar(
            name=f'{db} - 返回时间',
            x=db_data['query_name'],
            y=db_data['return_time_ms'],
            text=db_data['return_time_ms'].round(2),
            textposition='inside'
        ))
    
    fig.update_layout(
        barmode='stack',
        title='复杂查询时间分解（查询时间 + 返回时间）',
        xaxis_title='查询',
        yaxis_title='时间 (ms)',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def show_crud_operations(df):
    """CRUD操作分析"""
    st.markdown('<h2 class="sub-header">✏️ CRUD操作性能分析</h2>', unsafe_allow_html=True)
    
    crud_df = df[df['query_type'] == 'crud']
    
    if len(crud_df) == 0:
        st.warning("没有CRUD操作数据")
        return
    
    # 执行时间对比
    st.subheader("CRUD操作执行时间对比")
    fig = px.bar(
        crud_df,
        x='query_name',
        y='execution_time_ms',
        color='database',
        barmode='group',
        labels={'execution_time_ms': '执行时间 (ms)', 'query_name': '操作'},
        title='CRUD操作性能对比'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # 操作类型说明
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**I1**: 插入操作 (INSERT)")
    with col2:
        st.info("**D1**: 删除操作 (DELETE)")
    with col3:
        st.info("**U1**: 更新操作 (UPDATE)")
    
    # 统计表格
    st.subheader("统计数据")
    stats = crud_df.pivot_table(
        values='execution_time_ms',
        index='query_name',
        columns='database',
        aggfunc='mean'
    ).round(2)
    st.dataframe(stats, use_container_width=True)

def show_performance_comparison(df):
    """性能对比分析"""
    st.markdown('<h2 class="sub-header">📈 综合性能对比</h2>', unsafe_allow_html=True)
    
    # 按查询类型分组的性能对比
    st.subheader("各数据库在不同查询类型下的表现")
    
    comparison = df.groupby(['database', 'query_type'])['execution_time_ms'].mean().unstack(fill_value=0)
    
    fig = go.Figure()
    
    for query_type in comparison.columns:
        fig.add_trace(go.Bar(
            name=query_type.capitalize(),
            x=comparison.index,
            y=comparison[query_type],
            text=comparison[query_type].round(2),
            textposition='outside'
        ))
    
    fig.update_layout(
        barmode='group',
        title='各数据库按查询类型的平均执行时间',
        xaxis_title='数据库',
        yaxis_title='平均执行时间 (ms)',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 性能排名
    st.subheader("性能排名")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**最快数据库 (平均)**")
        fastest = df.groupby('database')['execution_time_ms'].mean().sort_values().head(3)
        for i, (db, time) in enumerate(fastest.items(), 1):
            st.write(f"{i}. **{db}**: {time:.2f} ms")
    
    with col2:
        st.write("**最慢数据库 (平均)**")
        slowest = df.groupby('database')['execution_time_ms'].mean().sort_values(ascending=False).head(3)
        for i, (db, time) in enumerate(slowest.items(), 1):
            st.write(f"{i}. **{db}**: {time:.2f} ms")
    
    # 雷达图 - 各维度对比
    st.subheader("多维度性能雷达图")
    
    # 计算各维度分数（归一化）
    metrics = {}
    for db in df['database'].unique():
        db_data = df[df['database'] == db]
        metrics[db] = {
            '平均速度': 100 - (db_data['execution_time_ms'].mean() / df['execution_time_ms'].mean() * 100),
            '稳定性': 100 - (db_data['execution_time_ms'].std() / df['execution_time_ms'].std() * 100),
            '返回效率': 100 - (db_data['return_ratio'].mean() / df['return_ratio'].mean() * 100),
        }
    
    fig = go.Figure()
    
    for db, scores in metrics.items():
        fig.add_trace(go.Scatterpolar(
            r=list(scores.values()),
            theta=list(scores.keys()),
            fill='toself',
            name=db
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title='各数据库多维度性能对比',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def show_detailed_data(df):
    """详细数据查看"""
    st.markdown('<h2 class="sub-header">🔍 详细数据</h2>', unsafe_allow_html=True)
    
    # 数据筛选器
    col1, col2 = st.columns(2)
    
    with col1:
        query_type_filter = st.multiselect(
            "查询类型",
            options=df['query_type'].unique(),
            default=df['query_type'].unique()
        )
    
    with col2:
        query_name_filter = st.multiselect(
            "查询名称",
            options=df['query_name'].unique(),
            default=df['query_name'].unique()
        )
    
    # 应用筛选
    filtered = df[
        (df['query_type'].isin(query_type_filter)) &
        (df['query_name'].isin(query_name_filter))
    ]
    
    # 显示数据表
    st.subheader(f"数据表 ({len(filtered)} 条记录)")
    st.dataframe(
        filtered.style.highlight_max(axis=0, subset=['execution_time_ms'], color='#ffcccc')
                     .highlight_min(axis=0, subset=['execution_time_ms'], color='#ccffcc'),
        use_container_width=True,
        height=400
    )
    
    # 导出功能
    st.subheader("数据导出")
    csv = filtered.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 下载CSV文件",
        data=csv,
        file_name="performance_data.csv",
        mime="text/csv"
    )
    
    # 数据统计
    st.subheader("数据统计")
    st.write(filtered.describe())

if __name__ == "__main__":
    main()

