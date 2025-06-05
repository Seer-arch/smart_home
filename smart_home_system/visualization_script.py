import requests
import json
import os
import logging
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib as mpl

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API配置
API_BASE_URL = "http://localhost:8000/api/v1"
ADMIN_USERNAME = "test@example.com"
ADMIN_PASSWORD = "test123"

def get_access_token():
    """获取访问令牌"""
    try:
        logger.info("正在获取访问令牌...")
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        logger.info("成功获取访问令牌")
        return token
    except Exception as e:
        logger.error(f"获取访问令牌失败: {str(e)}")
        raise

def get_visualization_data(endpoint, token):
    """获取可视化数据"""
    try:
        logger.info(f"正在获取数据: {endpoint}")
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"成功获取数据: {endpoint}")
        logger.info(f"数据格式: {json.dumps(data, indent=2, ensure_ascii=False)}")
        return data
    except Exception as e:
        logger.error(f"获取数据失败 {endpoint}: {str(e)}")
        raise

def create_visualization_folder():
    """创建可视化结果保存目录"""
    if not os.path.exists("visualization_results"):
        os.makedirs("visualization_results")

def save_figure(fig, filename):
    """保存图表为PNG图片"""
    try:
        logger.info(f"正在保存图表: {filename}")
        # 确保目录存在
        if not os.path.exists("visualization_results"):
            os.makedirs("visualization_results")
            
        # 保存图表
        output_path = f"visualization_results/{filename}.png"
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)  # 关闭图表以释放内存
        logger.info(f"图表保存成功: {filename}")
    except Exception as e:
        logger.error(f"保存图表失败 {filename}: {str(e)}")
        raise

def visualize_device_usage_trend(data):
    """可视化设备使用趋势"""
    try:
        logger.info("正在生成设备使用趋势图表...")
        logger.info(f"接收到的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        if isinstance(data, dict) and "dates" in data and "usage_counts" in data:
            dates = [datetime.strptime(date, "%Y-%m-%d") for date in data["dates"]]
            counts = data["usage_counts"]
        else:
            raise ValueError(f"不支持的数据格式: {data}")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dates, counts, marker='o', linestyle='-', linewidth=2)
        ax.set_xlabel("日期")
        ax.set_ylabel("使用次数")
        ax.set_title("设备使用趋势（最近30天）")
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        
        save_figure(fig, "device_usage_trend")
    except Exception as e:
        logger.error(f"生成设备使用趋势图表失败: {str(e)}")
        raise

def visualize_time_distribution(data):
    """可视化时间分布"""
    try:
        logger.info("正在生成时间分布图表...")
        logger.info(f"接收到的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        if isinstance(data, dict) and "hours" in data and "usage_counts" in data:
            hours = data["hours"]
            counts = data["usage_counts"]
        else:
            raise ValueError(f"不支持的数据格式: {data}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(hours, counts, alpha=0.7)
        ax.set_xlabel("小时")
        ax.set_ylabel("使用次数")
        ax.set_title("设备使用时间分布")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_xticks(range(0, 24, 2))
        
        save_figure(fig, "time_distribution")
    except Exception as e:
        logger.error(f"生成时间分布图表失败: {str(e)}")
        raise

def visualize_scenario_analysis(data):
    """可视化场景分析"""
    try:
        logger.info("正在生成场景分析图表...")
        logger.info(f"接收到的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        if isinstance(data, dict) and "scenarios" in data and "usage_counts" in data:
            scenarios = data["scenarios"]
            counts = data["usage_counts"]
        else:
            raise ValueError(f"不支持的数据格式: {data}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.pie(counts, labels=scenarios, autopct='%1.1f%%', startangle=90)
        ax.set_title("设备使用场景分布")
        
        save_figure(fig, "scenario_analysis")
    except Exception as e:
        logger.error(f"生成场景分析图表失败: {str(e)}")
        raise

def visualize_environmental_impact(data):
    """可视化环境影响分析"""
    try:
        logger.info("正在生成环境影响分析图表...")
        logger.info(f"接收到的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        if isinstance(data, dict) and "temperatures" in data and "humidities" in data and "usage_counts" in data:
            temperatures = data["temperatures"]
            humidities = data["humidities"]
            counts = data["usage_counts"]
        else:
            raise ValueError(f"不支持的数据格式: {data}")
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(temperatures, humidities, counts, c=counts, cmap='viridis')
        ax.set_xlabel("温度 (°C)")
        ax.set_ylabel("湿度 (%)")
        ax.set_zlabel("使用次数")
        ax.set_title("环境因素对设备使用的影响")
        plt.colorbar(scatter)
        
        save_figure(fig, "environmental_impact")
    except Exception as e:
        logger.error(f"生成环境影响分析图表失败: {str(e)}")
        raise

def visualize_device_correlation(data):
    """可视化设备关联分析"""
    try:
        logger.info("正在生成设备关联分析图表...")
        logger.info(f"接收到的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        if isinstance(data, dict) and "device_names" in data and "correlation_counts" in data:
            devices = data["device_names"]
            correlations = data["correlation_counts"]
        else:
            raise ValueError(f"不支持的数据格式: {data}")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(devices, correlations, alpha=0.7)
        ax.set_xlabel("设备")
        ax.set_ylabel("关联次数")
        ax.set_title("设备使用关联度分析")
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45, ha='right')
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height}',
                   ha='center', va='bottom')
        
        save_figure(fig, "device_correlation")
    except Exception as e:
        logger.error(f"生成设备关联分析图表失败: {str(e)}")
        raise

def visualize_automation_analysis(data):
    """可视化自动化分析"""
    try:
        logger.info("正在生成自动化分析图表...")
        logger.info(f"接收到的数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 处理数据
        if isinstance(data, dict) and "control_types" in data and "usage_counts" in data and "energy_consumption" in data:
            categories = data["control_types"]
            usage_counts = data["usage_counts"]
            energy_consumption = data["energy_consumption"]
        else:
            raise ValueError(f"不支持的数据格式: {data}")
        
        # 创建两个子图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 使用次数对比
        bars1 = ax1.bar(categories, usage_counts, alpha=0.7)
        ax1.set_ylabel("使用次数")
        ax1.set_title("自动化控制与手动控制使用次数对比")
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height}',
                    ha='center', va='bottom')
        
        # 能源消耗对比
        bars2 = ax2.bar(categories, energy_consumption, alpha=0.7)
        ax2.set_ylabel("能源消耗 (kWh)")
        ax2.set_title("自动化控制与手动控制能源消耗对比")
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # 添加数值标签
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        save_figure(fig, "automation_analysis")
    except Exception as e:
        logger.error(f"生成自动化分析图表失败: {str(e)}")
        raise

def main():
    """主函数"""
    start_time = time.time()
    try:
        logger.info("开始生成可视化图表...")
        
        # 创建保存目录
        create_visualization_folder()
        
        # 获取访问令牌
        token = get_access_token()
        
        # 获取并可视化各类数据
        # 1. 设备使用趋势（以设备ID=1为例）
        trend_data = get_visualization_data("/visualization/device/1/usage-trend", token)
        visualize_device_usage_trend(trend_data)
        
        # 2. 设备时间分布
        time_data = get_visualization_data("/visualization/device/1/time-distribution", token)
        visualize_time_distribution(time_data)
        
        # 3. 设备场景分析
        scenario_data = get_visualization_data("/visualization/device/1/scenario-analysis", token)
        visualize_scenario_analysis(scenario_data)
        
        # 4. 环境影响分析
        env_data = get_visualization_data("/visualization/device/1/environmental-impact", token)
        visualize_environmental_impact(env_data)
        
        # 5. 自动化分析
        automation_data = get_visualization_data("/visualization/automation-analysis", token)
        visualize_automation_analysis(automation_data)
        
        end_time = time.time()
        logger.info(f"所有可视化图表生成完成，耗时: {end_time - start_time:.2f} 秒")
        logger.info(f"图表保存在 visualization_results 目录下")
        
    except Exception as e:
        logger.error(f"生成可视化图表时发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main() 