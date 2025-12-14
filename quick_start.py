"""
快速启动脚本
一键运行完整的可视化流程
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """打印标题"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def run_command(command, description):
    """运行命令"""
    print(f"▶️  {description}...")
    print(f"   命令: {command}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description}完成!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}\n")
        return False

def check_dependencies():
    """检查依赖"""
    print_header("检查依赖包")
    
    required_packages = [
        'pandas',
        'matplotlib',
        'seaborn',
        'numpy',
        'streamlit',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package:15s} 已安装")
        except ImportError:
            print(f"❌ {package:15s} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少以下包: {', '.join(missing_packages)}")
        print("\n正在安装缺失的包...")
        return run_command("pip install -r requirements.txt", "安装依赖包")
    else:
        print("\n✅ 所有依赖包已安装!")
        return True

def check_data_files():
    """检查数据文件"""
    print_header("检查数据文件")
    
    # 检查真实数据
    real_data_files = [
        'data/订单表.csv',
        'data/客户表.csv',
        'data/卖家表.csv',
        'data/支付表.csv',
        'data/订单项表.csv'
    ]
    
    has_real_data = all(Path(f).exists() for f in real_data_files)
    
    if has_real_data:
        print("✅ 发现真实数据文件:")
        for f in real_data_files:
            print(f"   - {f}")
        return 'real'
    
    # 检查结果文件
    result_files = [
        'data/real_performance_results.csv',
        'data/performance_results.csv',
        'data/sample_performance.csv'
    ]
    
    for f in result_files:
        if Path(f).exists():
            print(f"✅ 发现性能结果文件: {f}")
            return 'results'
    
    print("⚠️  未找到数据文件")
    return 'none'

def main():
    """主函数"""
    print("\n" + "="*70)
    print(" "*15 + "🚀 数据库性能可视化 - 快速启动")
    print("="*70)
    
    # 步骤1: 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖安装失败，请手动运行: pip install -r requirements.txt")
        return
    
    # 步骤2: 检查数据
    data_status = check_data_files()
    
    # 步骤3: 根据数据状态选择操作
    print_header("数据准备")
    
    if data_status == 'none':
        print("📊 未找到数据，将生成示例数据...")
        choice = input("\n选择操作:\n  [1] 生成示例数据（快速体验）\n  [2] 退出\n请输入选择 (1/2): ")
        
        if choice == '1':
            if not run_command("python scripts/data_generator.py", "生成示例数据"):
                return
        else:
            print("已取消")
            return
    
    elif data_status == 'real':
        print("📊 发现真实数据文件")
        
        # 检查是否已有结果文件
        has_results = Path('data/real_performance_results.csv').exists()
        
        if has_results:
            print("✅ 已存在性能结果文件: data/real_performance_results.csv")
            choice = input("\n是否重新生成? (y/n): ")
            if choice.lower() == 'y':
                if not run_command("python scripts/data_loader.py", "加载真实数据"):
                    return
        else:
            print("正在加载真实数据并生成性能结果...")
            if not run_command("python scripts/data_loader.py", "加载真实数据"):
                return
    
    else:  # data_status == 'results'
        print("✅ 已有性能结果文件，跳过数据生成")
    
    # 步骤4: 生成图表
    print_header("生成可视化图表")
    
    choice = input("是否生成静态图表? (y/n): ")
    if choice.lower() == 'y':
        if not run_command("python scripts/visualize.py", "生成图表"):
            print("⚠️  图表生成失败，但仍可继续")
    
    # 步骤5: 启动Web界面
    print_header("启动交互式界面")
    
    print("即将启动Streamlit Web界面...")
    print("浏览器将自动打开 http://localhost:8501")
    print("\n💡 提示: 按 Ctrl+C 可以停止服务器\n")
    
    choice = input("是否启动? (y/n): ")
    if choice.lower() == 'y':
        print("\n" + "="*70)
        print("🌐 启动中...")
        print("="*70 + "\n")
        
        try:
            subprocess.run("streamlit run app.py", shell=True, check=True)
        except KeyboardInterrupt:
            print("\n\n✅ 已停止服务器")
        except Exception as e:
            print(f"\n❌ 启动失败: {e}")
    else:
        print("\n✅ 完成! 你可以稍后手动运行:")
        print("   streamlit run app.py")
    
    # 完成总结
    print("\n" + "="*70)
    print("📊 可视化资源位置:")
    print("="*70)
    print(f"  📁 静态图表: visualizations/")
    print(f"  📄 性能数据: data/")
    print("\n✨ 所有操作完成!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
        sys.exit(0)

