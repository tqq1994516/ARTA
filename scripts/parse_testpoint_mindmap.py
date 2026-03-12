#!/usr/bin/env python3
"""
测试点思维导图解析脚本
用于解析 Mermaid Mindmap 格式的测试点，并匹配 API 和业务链路
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TestPoint:
    """测试点数据结构"""
    id: int
    path: str
    name: str
    level: int
    children: List['TestPoint'] = field(default_factory=list)
    parent: Optional[str] = None
    status: str = 'pending'  # pending, matched, no_api, skipped
    matched_api: Optional[Dict] = None
    matched_flow: Optional[Dict] = None


class TestpointParser:
    """测试点解析器"""
    
    # 默认配置（可通过配置文件覆盖）
    DEFAULT_CONFIG = {
        # 关键词映射：中文关键词 -> 英文API路径关键词
        'keyword_map': {
            '登录': ['login', 'auth', 'signin'],
            '注册': ['register', 'signup', 'create'],
            '查询': ['get', 'list', 'query', 'search'],
            '创建': ['create', 'add', 'post', 'new'],
            '修改': ['update', 'edit', 'modify', 'put', 'patch'],
            '删除': ['delete', 'remove'],
            '详情': ['detail', 'info', 'get'],
            '列表': ['list', 'all', 'query'],
            '导出': ['export', 'download'],
            '导入': ['import', 'upload'],
            '搜索': ['search', 'find', 'query'],
            '保存': ['save', 'store', 'create'],
            '更新': ['update', 'modify', 'put', 'patch'],
            '获取': ['get', 'fetch', 'retrieve'],
            '提交': ['submit', 'post', 'create'],
            '审核': ['audit', 'review', 'approve'],
            '发布': ['publish', 'release'],
            '取消': ['cancel', 'revoke'],
        },
        # 方法映射：中文关键词 -> HTTP方法
        'method_map': {
            '获取': 'GET',
            '查询': 'GET',
            '列表': 'GET',
            '详情': 'GET',
            '搜索': 'GET',
            '创建': 'POST',
            '新增': 'POST',
            '添加': 'POST',
            '提交': 'POST',
            '保存': 'POST',
            '修改': ['PUT', 'PATCH'],
            '编辑': ['PUT', 'PATCH'],
            '更新': ['PUT', 'PATCH'],
            '删除': 'DELETE',
            '移除': 'DELETE',
        },
        # 缩进配置
        'indent_size': 2,  # 每级缩进的空格数
    }
    
    def __init__(self, api_inventory: Optional[Dict] = None, flows: Optional[List[Dict]] = None,
                 config_path: Optional[str] = None):
        """
        初始化解析器
        
        Args:
            api_inventory: API 清单数据
            flows: 业务链路列表
            config_path: 可选的配置文件路径
        """
        self.api_inventory = api_inventory or {}
        self.flows = flows or []
        self.testpoints: List[TestPoint] = []
        self.flat_testpoints: List[TestPoint] = []
        
        # 加载配置
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """加载配置文件"""
        config = self.DEFAULT_CONFIG.copy()
        
        if config_path:
            config_file = Path(config_path)
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        user_config = json.load(f)
                    
                    # 合并配置
                    if 'keyword_map' in user_config:
                        config['keyword_map'].update(user_config['keyword_map'])
                    if 'method_map' in user_config:
                        config['method_map'].update(user_config['method_map'])
                    if 'indent_size' in user_config:
                        config['indent_size'] = user_config['indent_size']
                        
                except (json.JSONDecodeError, IOError) as e:
                    print(f"警告: 无法加载配置文件 {config_path}: {e}")
        
        return config
        
    def parse_mermaid_mindmap(self, content: str) -> List[TestPoint]:
        """解析 Mermaid Mindmap 格式"""
        lines = content.strip().split('\n')
        
        # 验证格式
        if not any('mindmap' in line.lower() for line in lines):
            raise ValueError("不是有效的 Mermaid Mindmap 格式")
        
        # 解析节点
        self.testpoints = []
        self.flat_testpoints = []
        point_id = 0
        
        # 获取缩进配置
        indent_size = self.config.get('indent_size', 2)
        
        # 解析每一行
        stack: List[tuple] = []  # (level, testpoint)
        root_points = []
        
        for line in lines:
            # 跳过 mindmap 声明行
            if 'mindmap' in line.lower():
                continue
            
            # 计算缩进级别
            stripped = line.lstrip()
            if not stripped:
                continue
            
            indent = len(line) - len(stripped)
            level = indent // indent_size
            
            # 提取节点名称
            name = self._extract_node_name(stripped)
            if not name:
                continue
            
            # 创建测试点
            point_id += 1
            testpoint = TestPoint(
                id=point_id,
                path=name,
                name=name,
                level=level,
            )
            
            self.flat_testpoints.append(testpoint)
            
            # 构建树结构
            while stack and stack[-1][0] >= level:
                stack.pop()
            
            if stack:
                parent_level, parent = stack[-1]
                testpoint.parent = parent.name
                testpoint.path = f"{parent.path} > {name}"
                parent.children.append(testpoint)
            else:
                root_points.append(testpoint)
            
            stack.append((level, testpoint))
        
        self.testpoints = root_points
        return root_points
    
    def _extract_node_name(self, line: str) -> str:
        """从行中提取节点名称"""
        # 移除常见的前缀符号
        line = re.sub(r'^[\s\-\*\+]+', '', line)
        
        # 处理括号格式 ((name)) 或 (name)
        match = re.search(r'\(\(([^)]+)\)\)', line)
        if match:
            return match.group(1)
        
        match = re.search(r'\(([^)]+)\)', line)
        if match:
            return match.group(1)
        
        # 处理方括号格式 [name]
        match = re.search(r'\[([^\]]+)\]', line)
        if match:
            return match.group(1)
        
        # 直接返回清理后的文本
        return line.strip()
    
    def match_apis(self) -> Dict[str, Any]:
        """匹配 API"""
        apis = self.api_inventory.get('apis', [])
        results = {
            'matched': [],
            'no_match': [],
        }
        
        for testpoint in self.flat_testpoints:
            # 跳过非叶子节点
            if testpoint.children:
                continue
            
            # 尝试匹配 API
            matched = self._find_matching_api(testpoint, apis)
            
            if matched:
                testpoint.status = 'matched'
                testpoint.matched_api = matched
                results['matched'].append({
                    'testpoint': testpoint.path,
                    'api': f"{matched['method']} {matched['path']}",
                })
            else:
                testpoint.status = 'no_api'
                results['no_match'].append({
                    'testpoint': testpoint.path,
                })
        
        return results
    
    def match_flows(self) -> Dict[str, Any]:
        """匹配业务链路"""
        results = {
            'matched': [],
            'no_match': [],
        }
        
        for testpoint in self.flat_testpoints:
            # 跳过非叶子节点
            if testpoint.children:
                continue
            
            # 尝试匹配业务链路
            matched = self._find_matching_flow(testpoint)
            
            if matched:
                testpoint.matched_flow = matched
                results['matched'].append({
                    'testpoint': testpoint.path,
                    'flow': matched.get('name', ''),
                })
            else:
                results['no_match'].append({
                    'testpoint': testpoint.path,
                })
        
        return results
    
    def _find_matching_api(self, testpoint: TestPoint, apis: List[Dict]) -> Optional[Dict]:
        """查找匹配的 API"""
        name = testpoint.name.lower()
        path_parts = testpoint.path.lower().split(' > ')
        
        # 从配置获取映射
        keyword_map = self.config['keyword_map']
        method_map = self.config['method_map']
        
        for api in apis:
            path = api.get('path', '').lower()
            description = api.get('description', '').lower()
            api_method = api.get('method', '').upper()
            
            # 路径匹配
            if any(part in path for part in path_parts):
                return api
            
            # 描述匹配
            if name in description:
                return api
            
            # 关键词匹配
            for key, keywords in keyword_map.items():
                if key in name:
                    if any(kw in path or kw in description for kw in keywords):
                        return api
            
            # 方法+资源匹配
            for key, methods in method_map.items():
                if key in name:
                    method_list = [methods] if isinstance(methods, str) else methods
                    if api_method in method_list:
                        # 检查资源名是否匹配
                        for part in path_parts:
                            if part in path:
                                return api
        
        return None
    
    def _find_matching_flow(self, testpoint: TestPoint) -> Optional[Dict]:
        """查找匹配的业务链路"""
        name = testpoint.name.lower()
        
        for flow in self.flows:
            flow_name = flow.get('name', '').lower()
            
            # 名称相似度匹配
            if name in flow_name or flow_name in name:
                return flow
            
            # 路径关键词匹配
            if testpoint.matched_api:
                api_path = testpoint.matched_api.get('path', '')
                flow_apis = flow.get('apis', [])
                
                for flow_api in flow_apis:
                    if flow_api.get('path') == api_path:
                        return flow
        
        return None
    
    def generate_analysis_report(self) -> Dict[str, Any]:
        """生成分析报告"""
        total = len([t for t in self.flat_testpoints if not t.children])
        matched_apis = len([t for t in self.flat_testpoints if t.status == 'matched'])
        no_apis = len([t for t in self.flat_testpoints if t.status == 'no_api'])
        
        return {
            'summary': {
                'totalTestpoints': total,
                'matchedApis': matched_apis,
                'noApis': no_apis,
                'matchRate': f"{matched_apis / total * 100:.1f}%" if total > 0 else "0%",
            },
            'testpoints': [
                {
                    'id': t.id,
                    'path': t.path,
                    'name': t.name,
                    'level': t.level,
                    'status': t.status,
                    'matchedApi': f"{t.matched_api['method']} {t.matched_api['path']}" if t.matched_api else None,
                    'matchedFlow': t.matched_flow.get('name') if t.matched_flow else None,
                }
                for t in self.flat_testpoints
                if not t.children
            ],
        }


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python parse_testpoint_mindmap.py <mermaid文件路径> [api_inventory.json] [config.json]")
        print("")
        print("参数:")
        print("  mermaid文件路径      包含思维导图的文件")
        print("  api_inventory.json   可选，API清单文件")
        print("  config.json          可选，自定义关键词映射配置")
        print("")
        print("示例:")
        print("  python parse_testpoint_mindmap.py mindmap.mmd")
        print("  python parse_testpoint_mindmap.py mindmap.mmd api_inventory.json")
        print("  python parse_testpoint_mindmap.py mindmap.mmd api_inventory.json config.json")
        sys.exit(1)
    
    mindmap_path = sys.argv[1]
    api_path = sys.argv[2] if len(sys.argv) > 2 else None
    config_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 读取思维导图
    with open(mindmap_path, 'r', encoding='utf-8') as f:
        mindmap_content = f.read()
    
    # 读取 API 清单（如果提供）
    api_inventory = {}
    if api_path:
        with open(api_path, 'r', encoding='utf-8') as f:
            api_inventory = json.load(f)
    
    # 解析
    parser = TestpointParser(api_inventory, config_path=config_path)
    parser.parse_mermaid_mindmap(mindmap_content)
    parser.match_apis()
    report = parser.generate_analysis_report()
    
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()