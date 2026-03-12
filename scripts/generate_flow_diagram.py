#!/usr/bin/env python3
"""
流程图生成脚本
用于生成业务链路的 Mermaid 时序图
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class FlowDiagramGenerator:
    """流程图生成器"""
    
    # 默认的服务映射（可被配置文件覆盖）
    DEFAULT_SERVICE_MAP = {
        'auth': '认证服务',
        'user': '用户服务',
        'users': '用户服务',
        'order': '订单服务',
        'orders': '订单服务',
        'product': '商品服务',
        'products': '商品服务',
        'cart': '购物车服务',
        'payment': '支付服务',
        'notify': '通知服务',
        'inventory': '库存服务',
        'shipping': '物流服务',
        'message': '消息服务',
        'config': '配置服务',
        'admin': '管理服务',
        'report': '报表服务',
        'search': '搜索服务',
    }
    
    # 默认的ID映射（可被配置文件覆盖）
    DEFAULT_ID_MAP = {
        '认证': 'Auth',
        '用户': 'User',
        '订单': 'Order',
        '商品': 'Product',
        '购物车': 'Cart',
        '支付': 'Payment',
        '通知': 'Notify',
        '库存': 'Inventory',
        '物流': 'Shipping',
        '消息': 'Message',
        '配置': 'Config',
        '管理': 'Admin',
        '报表': 'Report',
        '搜索': 'Search',
    }
    
    def __init__(self, flow_data: Dict[str, Any], config_path: Optional[str] = None):
        """
        初始化生成器
        
        Args:
            flow_data: 业务链路数据
            config_path: 可选的配置文件路径，用于自定义服务映射
        """
        self.flow_data = flow_data
        self.participants: Dict[str, str] = {}
        
        # 加载配置（合并默认配置和自定义配置）
        self.service_map = self._load_config(config_path)
        self.id_map = self._build_id_map()
        
    def generate_sequence_diagram(self) -> str:
        """生成时序图"""
        lines = []
        lines.append("```mermaid")
        lines.append("sequenceDiagram")
        
        # 添加参与者
        self._extract_participants()
        for participant_id, participant_name in self.participants.items():
            lines.append(f"    participant {participant_id} as {participant_name}")
        
        lines.append("")
        
        # 添加前置条件注释
        preconditions = self.flow_data.get('preconditions', [])
        if preconditions:
            notes = " & ".join(preconditions[:2])  # 最多显示2个
            if len(preconditions) > 2:
                notes += f" 等{len(preconditions)}项"
            lines.append(f"    Note over {list(self.participants.keys())[0]}: 前置条件: {notes}")
            lines.append("")
        
        # 添加 API 调用序列
        apis = self.flow_data.get('apis', [])
        client_id = list(self.participants.keys())[0] if self.participants else 'Client'
        
        for idx, api in enumerate(apis, 1):
            step_num = idx
            method = api.get('method', 'GET')
            path = api.get('path', '/')
            description = api.get('description', '')
            note = api.get('note', '')
            
            # 确定目标服务
            target = self._get_participant_for_path(path)
            
            # 请求箭头
            lines.append(f"    {client_id}->>{target}: {method} {path}")
            
            # 响应箭头
            status = api.get('expectedStatus', 200)
            lines.append(f"    {target}-->>{client_id}: {status}")
            
            # 添加备注
            if note:
                lines.append(f"    Note right of {client_id}: {note}")
            
            lines.append("")
        
        # 添加后置处理注释
        cleanup = self.flow_data.get('cleanup', [])
        if cleanup:
            lines.append(f"    Note over {client_id}: 后置处理: 清理测试数据")
        
        lines.append("```")
        return "\n".join(lines)
    
    def _extract_participants(self) -> None:
        """提取参与者"""
        self.participants = {'Client': '测试客户端'}
        
        apis = self.flow_data.get('apis', [])
        for api in apis:
            path = api.get('path', '/')
            participant_name = self._get_service_name(path)
            participant_id = self._normalize_participant_id(participant_name)
            
            if participant_id not in self.participants:
                self.participants[participant_id] = participant_name
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, str]:
        """
        加载服务映射配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            合并后的服务映射字典
        """
        service_map = self.DEFAULT_SERVICE_MAP.copy()
        
        if config_path:
            config_file = Path(config_path)
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    # 合并用户自定义的服务映射
                    if 'serviceMap' in config:
                        service_map.update(config['serviceMap'])
                        
                except (json.JSONDecodeError, IOError) as e:
                    print(f"警告: 无法加载配置文件 {config_path}: {e}")
        
        return service_map
    
    def _build_id_map(self) -> Dict[str, str]:
        """
        根据服务映射构建ID映射
        
        Returns:
            ID映射字典
        """
        id_map = self.DEFAULT_ID_MAP.copy()
        
        # 根据服务映射自动生成ID映射
        for key, service_name in self.service_map.items():
            # 移除"服务"后缀
            base_name = service_name.replace('服务', '')
            
            # 如果默认映射中没有，则自动生成英文ID
            if base_name not in id_map:
                # 尝试使用原始key作为ID（转首字母大写）
                id_map[base_name] = key.capitalize()
        
        return id_map
    
    def _get_service_name(self, path: str) -> str:
        """从路径获取服务名称"""
        path_parts = path.strip('/').split('/')
        
        if len(path_parts) >= 1:
            first_part = path_parts[0]
            
            # 跳过常见的API前缀
            if first_part in ['api', 'v1', 'v2', 'v3', 'rest']:
                first_part = path_parts[1] if len(path_parts) > 1 else 'default'
            
            # 从配置的服务映射中查找
            if first_part in self.service_map:
                return self.service_map[first_part]
            
            # 动态生成服务名称
            return f'{first_part}服务'
        
        return 'API服务'
    
    def _get_participant_for_path(self, path: str) -> str:
        """获取路径对应的参与者ID"""
        service_name = self._get_service_name(path)
        return self._normalize_participant_id(service_name)
    
    def _normalize_participant_id(self, name: str) -> str:
        """规范化参与者ID"""
        # 移除"服务"后缀
        name = name.replace('服务', '').replace(' ', '')
        
        # 优先使用配置的ID映射
        if name in self.id_map:
            return self.id_map[name]
        
        # 如果映射中没有，尝试智能转换
        # 1. 如果是纯英文，直接使用
        if name.isascii():
            return name
        
        # 2. 否则生成一个唯一的ID（使用拼音首字母或数字）
        # 简单处理：使用 Service_{index} 格式
        existing_ids = set(self.participants.keys())
        for i in range(1, 100):
            new_id = f'Service_{i}'
            if new_id not in existing_ids:
                return new_id
        
        return name or 'API'


def generate_from_json_file(file_path: str, config_path: Optional[str] = None) -> str:
    """
    从 JSON 文件生成流程图
    
    Args:
        file_path: 业务链路JSON文件路径
        config_path: 可选的服务映射配置文件路径
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        flow_data = json.load(f)
    
    generator = FlowDiagramGenerator(flow_data, config_path)
    return generator.generate_sequence_diagram()


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python generate_flow_diagram.py <业务链路JSON文件> [服务映射配置文件]")
        print("")
        print("参数:")
        print("  业务链路JSON文件      包含API调用序列的JSON文件")
        print("  服务映射配置文件      可选，自定义服务名称映射的JSON文件")
        print("")
        print("示例:")
        print("  python generate_flow_diagram.py flow.json")
        print("  python generate_flow_diagram.py flow.json service_config.json")
        print("")
        print("服务映射配置文件格式:")
        print('  {"serviceMap": {"custom": "自定义服务", "myapi": "我的API服务"}}')
        sys.exit(1)
    
    file_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    diagram = generate_from_json_file(file_path, config_path)
    print(diagram)


if __name__ == '__main__':
    main()