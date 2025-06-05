from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Device, DeviceUsageRecord, Room, House
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
from pathlib import Path

class VisualizationService:
    def __init__(self, db: Session):
        self.db = db
        self.output_dir = Path("app/static/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _save_figure(self, fig, filename: str) -> str:
        """保存图表为图片文件"""
        filepath = self.output_dir / filename
        fig.write_image(str(filepath))
        return f"/static/visualizations/{filename}"

    def generate_device_usage_trend(self, device_id: int, days: int = 7) -> str:
        """生成设备使用趋势图"""
        # 获取设备使用记录
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        records = self.db.query(DeviceUsageRecord).filter(
            DeviceUsageRecord.device_id == device_id,
            DeviceUsageRecord.start_time >= start_date,
            DeviceUsageRecord.start_time <= end_date
        ).all()
        
        # 转换为DataFrame
        data = []
        for record in records:
            data.append({
                'start_time': record.start_time,
                'duration': record.duration,
                'energy_consumption': record.energy_consumption
            })
        df = pd.DataFrame(data)
        
        # 创建图表
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['start_time'],
            y=df['duration'],
            mode='lines+markers',
            name='使用时长'
        ))
        fig.add_trace(go.Scatter(
            x=df['start_time'],
            y=df['energy_consumption'],
            mode='lines+markers',
            name='能耗',
            yaxis='y2'
        ))
        
        # 设置图表布局
        fig.update_layout(
            title=f'设备使用趋势（过去{days}天）',
            xaxis_title='时间',
            yaxis_title='使用时长（分钟）',
            yaxis2=dict(
                title='能耗（kWh）',
                overlaying='y',
                side='right'
            )
        )
        
        return self._save_figure(fig, f'device_{device_id}_usage_trend.png')

    def generate_device_correlation(self) -> str:
        """生成设备关联使用热力图"""
        # 获取所有设备的使用记录
        records = self.db.query(DeviceUsageRecord).all()
        
        # 创建设备使用时间矩阵
        devices = self.db.query(Device).all()
        device_ids = [d.id for d in devices]
        device_names = [d.name for d in devices]
        
        # 创建关联矩阵
        correlation_matrix = pd.DataFrame(0, index=device_names, columns=device_names)
        
        # 分析设备同时使用情况
        for record in records:
            start_time = record.start_time
            end_time = record.end_time or (start_time + timedelta(minutes=record.duration))
            
            # 查找同时使用的设备
            concurrent_records = self.db.query(DeviceUsageRecord).filter(
                DeviceUsageRecord.start_time <= end_time,
                DeviceUsageRecord.end_time >= start_time
            ).all()
            
            # 更新关联矩阵
            for r1 in concurrent_records:
                for r2 in concurrent_records:
                    if r1.device_id != r2.device_id:
                        device1 = self.db.query(Device).get(r1.device_id)
                        device2 = self.db.query(Device).get(r2.device_id)
                        if device1 and device2:
                            correlation_matrix.loc[device1.name, device2.name] += 1
        
        # 创建热力图
        fig = px.imshow(
            correlation_matrix,
            labels=dict(x="设备", y="设备", color="同时使用次数"),
            title="设备关联使用热力图"
        )
        
        return self._save_figure(fig, 'device_correlation.png')

    def generate_area_impact_analysis(self) -> str:
        """生成房屋面积对设备使用的影响分析图"""
        # 获取房屋和设备使用数据
        houses = self.db.query(House).all()
        
        data = []
        for house in houses:
            # 获取该房屋的所有设备使用记录
            usage_records = self.db.query(DeviceUsageRecord).join(
                Device, DeviceUsageRecord.device_id == Device.id
            ).join(
                Room, Device.room_id == Room.id
            ).filter(
                Room.house_id == house.id
            ).all()
            
            if usage_records:
                total_usage = sum(record.duration or 0 for record in usage_records)
                total_energy = sum(record.energy_consumption or 0 for record in usage_records)
                data.append({
                    'house_id': house.id,
                    'area': house.area,
                    'total_usage': total_usage,
                    'total_energy': total_energy
                })
        
        df = pd.DataFrame(data)
        
        # 创建散点图
        fig = px.scatter(
            df,
            x='area',
            y='total_usage',
            size='total_energy',
            title='房屋面积对设备使用的影响',
            labels={
                'area': '房屋面积（平方米）',
                'total_usage': '总使用时长（分钟）',
                'total_energy': '总能耗（kWh）'
            }
        )
        
        return self._save_figure(fig, 'area_impact.png')

    def generate_device_usage_by_time(self, device_id: int) -> str:
        """生成设备使用时间分布图"""
        # 获取设备使用记录
        records = self.db.query(DeviceUsageRecord).filter(
            DeviceUsageRecord.device_id == device_id
        ).all()
        
        # 统计每小时使用次数
        hourly_usage = [0] * 24
        for record in records:
            hour = record.start_time.hour
            hourly_usage[hour] += 1
        
        # 创建柱状图
        fig = px.bar(
            x=list(range(24)),
            y=hourly_usage,
            title='设备使用时间分布',
            labels={
                'x': '小时',
                'y': '使用次数'
            }
        )
        
        return self._save_figure(fig, f'device_{device_id}_time_distribution.png')

    def generate_device_usage_by_scenario(self, device_id: int) -> str:
        """生成设备使用场景分析图"""
        # 获取设备使用记录
        records = self.db.query(DeviceUsageRecord).filter(
            DeviceUsageRecord.device_id == device_id
        ).all()
        
        # 统计不同场景的使用情况
        scenario_stats = {}
        for record in records:
            scenario = record.usage_scenario
            if scenario not in scenario_stats:
                scenario_stats[scenario] = {
                    'count': 0,
                    'total_duration': 0,
                    'total_energy': 0
                }
            scenario_stats[scenario]['count'] += 1
            scenario_stats[scenario]['total_duration'] += record.duration or 0
            scenario_stats[scenario]['total_energy'] += record.energy_consumption or 0
        
        # 创建柱状图
        fig = go.Figure()
        scenarios = list(scenario_stats.keys())
        counts = [stats['count'] for stats in scenario_stats.values()]
        durations = [stats['total_duration'] for stats in scenario_stats.values()]
        energies = [stats['total_energy'] for stats in scenario_stats.values()]
        
        fig.add_trace(go.Bar(
            name='使用次数',
            x=scenarios,
            y=counts,
            yaxis='y'
        ))
        fig.add_trace(go.Bar(
            name='总时长(分钟)',
            x=scenarios,
            y=durations,
            yaxis='y2'
        ))
        fig.add_trace(go.Bar(
            name='总能耗(kWh)',
            x=scenarios,
            y=energies,
            yaxis='y3'
        ))
        
        fig.update_layout(
            title='设备使用场景分析',
            barmode='group',
            yaxis=dict(title='使用次数'),
            yaxis2=dict(title='总时长(分钟)', overlaying='y', side='right'),
            yaxis3=dict(title='总能耗(kWh)', overlaying='y', side='right', anchor='free', position=1)
        )
        
        return self._save_figure(fig, f'device_{device_id}_scenario_analysis.png')

    def generate_environmental_impact(self, device_id: int) -> str:
        """生成环境因素影响分析图"""
        # 获取设备使用记录
        records = self.db.query(DeviceUsageRecord).filter(
            DeviceUsageRecord.device_id == device_id
        ).all()
        
        # 准备数据
        data = []
        for record in records:
            if record.temperature and record.humidity:
                data.append({
                    'temperature': record.temperature,
                    'humidity': record.humidity,
                    'duration': record.duration or 0,
                    'energy': record.energy_consumption or 0
                })
        
        df = pd.DataFrame(data)
        
        # 创建散点图
        fig = px.scatter(
            df,
            x='temperature',
            y='humidity',
            size='duration',
            color='energy',
            title='环境因素对设备使用的影响',
            labels={
                'temperature': '温度 (°C)',
                'humidity': '湿度 (%)',
                'duration': '使用时长',
                'energy': '能耗'
            }
        )
        
        return self._save_figure(fig, f'device_{device_id}_environmental_impact.png')

    def generate_automation_analysis(self) -> str:
        """生成自动化使用分析图"""
        # 获取所有设备的使用记录
        records = self.db.query(DeviceUsageRecord).all()
        
        # 统计自动化和手动控制的使用情况
        automation_stats = {
            'automated': {'count': 0, 'total_energy': 0},
            'manual': {'count': 0, 'total_energy': 0}
        }
        
        for record in records:
            key = 'automated' if record.is_automated else 'manual'
            automation_stats[key]['count'] += 1
            automation_stats[key]['total_energy'] += record.energy_consumption or 0
        
        # 创建饼图
        fig = go.Figure(data=[go.Pie(
            labels=['自动控制', '手动控制'],
            values=[automation_stats['automated']['count'], automation_stats['manual']['count']],
            hole=.3
        )])
        
        fig.update_layout(
            title='设备控制方式分布',
            annotations=[dict(text='控制方式', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return self._save_figure(fig, 'automation_analysis.png')

    def get_area_impact_data(self) -> Dict:
        """获取房屋面积影响分析数据"""
        # 获取房屋和设备使用数据
        houses = self.db.query(House).all()
        
        areas = []
        usage_counts = []
        for house in houses:
            # 获取该房屋的所有设备使用记录
            usage_count = self.db.query(func.count(DeviceUsageRecord.id)).join(
                Device, DeviceUsageRecord.device_id == Device.id
            ).join(
                Room, Device.room_id == Room.id
            ).filter(
                Room.house_id == house.id
            ).scalar()
            
            areas.append(house.area)
            usage_counts.append(usage_count)
        
        return {
            "areas": areas,
            "usage_counts": usage_counts
        }

    def get_device_usage_trend_data(self, device_id: int) -> Dict:
        """获取设备使用趋势数据"""
        # 获取最近30天的使用记录
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        records = self.db.query(
            func.date(DeviceUsageRecord.start_time).label('date'),
            func.count(DeviceUsageRecord.id).label('count')
        ).filter(
            DeviceUsageRecord.device_id == device_id,
            DeviceUsageRecord.start_time >= start_date
        ).group_by(
            func.date(DeviceUsageRecord.start_time)
        ).all()
        
        dates = [str(record.date) for record in records]
        counts = [record.count for record in records]
        
        return {
            "dates": dates,
            "usage_counts": counts
        }

    def get_device_time_distribution_data(self, device_id: int) -> Dict:
        """获取设备使用时间分布数据"""
        # 获取所有使用记录的小时分布
        records = self.db.query(
            func.extract('hour', DeviceUsageRecord.start_time).label('hour'),
            func.count(DeviceUsageRecord.id).label('count')
        ).filter(
            DeviceUsageRecord.device_id == device_id
        ).group_by(
            func.extract('hour', DeviceUsageRecord.start_time)
        ).all()
        
        hours = [int(record.hour) for record in records]
        counts = [record.count for record in records]
        
        # 确保24小时都有数据
        all_hours = list(range(24))
        all_counts = [0] * 24
        for hour, count in zip(hours, counts):
            all_counts[hour] = count
        
        return {
            "hours": all_hours,
            "usage_counts": all_counts
        }

    def get_device_usage_by_scenario_data(self, device_id: int) -> Dict:
        """获取设备使用场景分析数据"""
        # 获取所有使用记录的场景分布
        records = self.db.query(
            DeviceUsageRecord.usage_scenario,
            func.count(DeviceUsageRecord.id).label('count')
        ).filter(
            DeviceUsageRecord.device_id == device_id,
            DeviceUsageRecord.usage_scenario.isnot(None)
        ).group_by(
            DeviceUsageRecord.usage_scenario
        ).all()
        
        scenarios = [record.usage_scenario for record in records]
        counts = [record.count for record in records]
        
        return {
            "scenarios": scenarios,
            "usage_counts": counts
        }

    def get_environmental_impact_data(self, device_id: int) -> Dict:
        """获取环境因素影响分析数据"""
        # 获取所有使用记录的环境数据
        records = self.db.query(
            DeviceUsageRecord.temperature,
            DeviceUsageRecord.humidity,
            func.count(DeviceUsageRecord.id).label('count')
        ).filter(
            DeviceUsageRecord.device_id == device_id,
            DeviceUsageRecord.temperature.isnot(None),
            DeviceUsageRecord.humidity.isnot(None)
        ).group_by(
            DeviceUsageRecord.temperature,
            DeviceUsageRecord.humidity
        ).all()
        
        temperatures = [record.temperature for record in records]
        humidities = [record.humidity for record in records]
        counts = [record.count for record in records]
        
        return {
            "temperatures": temperatures,
            "humidities": humidities,
            "usage_counts": counts
        }

    def get_device_correlation_data(self, device_id: int = None) -> Dict:
        """获取设备关联使用分析数据"""
        # 获取所有设备
        devices = self.db.query(Device).all()
        device_ids = [d.id for d in devices]
        device_names = {d.id: d.name for d in devices}
        
        # 如果指定了设备ID，只获取与该设备相关的关联数据
        if device_id is not None:
            records = self.db.query(
                DeviceUsageRecord.device_id,
                func.count(DeviceUsageRecord.id).label('count')
            ).filter(
                DeviceUsageRecord.start_time.in_(
                    self.db.query(DeviceUsageRecord.start_time)
                    .filter(DeviceUsageRecord.device_id == device_id)
                ),
                DeviceUsageRecord.device_id != device_id
            ).group_by(
                DeviceUsageRecord.device_id
            ).all()
            
            device_ids = [record.device_id for record in records]
            counts = [record.count for record in records]
        else:
            # 获取所有设备之间的关联数据
            correlation_matrix = {}
            for d1 in device_ids:
                for d2 in device_ids:
                    if d1 != d2:
                        key = f"{d1}-{d2}"
                        if key not in correlation_matrix:
                            # 查询两个设备同时使用的次数
                            count = self.db.query(func.count(DeviceUsageRecord.id)).filter(
                                DeviceUsageRecord.device_id == d2,
                                DeviceUsageRecord.start_time.in_(
                                    self.db.query(DeviceUsageRecord.start_time)
                                    .filter(DeviceUsageRecord.device_id == d1)
                                )
                            ).scalar()
                            correlation_matrix[key] = count
            
            # 转换为列表格式
            device_ids = []
            counts = []
            for key, count in correlation_matrix.items():
                if count > 0:  # 只返回有关联的数据
                    d1, d2 = map(int, key.split('-'))
                    device_ids.append(d2)
                    counts.append(count)
        
        return {
            "device_ids": device_ids,
            "device_names": [device_names.get(did, f"设备{did}") for did in device_ids],
            "correlation_counts": counts
        }

    def get_automation_analysis_data(self) -> Dict:
        """获取自动化使用分析数据"""
        # 获取所有设备的使用记录
        records = self.db.query(DeviceUsageRecord).all()
        
        # 统计自动化和手动控制的使用情况
        automation_stats = {
            'automated': {'count': 0, 'total_energy': 0},
            'manual': {'count': 0, 'total_energy': 0}
        }
        
        for record in records:
            key = 'automated' if record.is_automated else 'manual'
            automation_stats[key]['count'] += 1
            automation_stats[key]['total_energy'] += record.energy_consumption or 0
        
        return {
            "control_types": ["自动控制", "手动控制"],
            "usage_counts": [
                automation_stats['automated']['count'],
                automation_stats['manual']['count']
            ],
            "energy_consumption": [
                automation_stats['automated']['total_energy'],
                automation_stats['manual']['total_energy']
            ]
        } 