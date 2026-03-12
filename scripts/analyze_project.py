#!/usr/bin/env python3
"""
项目分析脚本
用于分析本地项目代码，识别框架类型，提取 API 路由定义
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


class ProjectAnalyzer:
    """项目分析器"""
    
    # 默认配置（可通过配置文件覆盖）
    DEFAULT_CONFIG = {
        # 框架特征识别规则
        'framework_patterns': {
            'express': {
                'files': ['package.json'],
                'dependencies': ['express'],
                'route_patterns': [
                    r'app\.(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]',
                    r'router\.(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]',
                ]
            },
            'nestjs': {
                'files': ['package.json'],
                'dependencies': ['@nestjs/core'],
                'route_patterns': [
                    r'@(\w+)Mapping\s*\([\'"]([^\'"]+)[\'"]',
                    r'@Get\s*\([\'"]([^\'"]+)[\'"]',
                    r'@Post\s*\([\'"]([^\'"]+)[\'"]',
                ]
            },
            'flask': {
                'files': ['requirements.txt', 'app.py'],
                'dependencies': ['flask'],
                'route_patterns': [
                    r'@app\.route\s*\([\'"]([^\'"]+)[\'"](?:,\s*methods\s*=\s*\[([^\]]+)\])?',
                ]
            },
            'django': {
                'files': ['manage.py', 'settings.py'],
                'dependencies': ['django'],
                'route_patterns': [
                    r'path\s*\([\'"]([^\'"]+)[\'"]',
                    r'url\s*\([\'"]([^\'"]+)[\'"]',
                ]
            },
            'fastapi': {
                'files': ['requirements.txt', 'main.py'],
                'dependencies': ['fastapi'],
                'route_patterns': [
                    r'@app\.(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]',
                    r'@router\.(get|post|put|delete|patch)\s*\([\'"]([^\'"]+)[\'"]',
                ]
            },
            'spring': {
                'files': ['pom.xml', 'build.gradle'],
                'dependencies': ['spring-boot'],
                'route_patterns': [
                    r'@RequestMapping\s*\([\'"]([^\'"]+)[\'"]',
                    r'@(\w+)Mapping\s*\([\'"]([^\'"]+)[\'"]',
                    r'@GetMapping\s*\([\'"]([^\'"]+)[\'"]',
                    r'@PostMapping\s*\([\'"]([^\'"]+)[\'"]',
                ]
            },
            'gin': {
                'files': ['go.mod'],
                'dependencies': ['gin-gonic'],
                'route_patterns': [
                    r'\.(GET|POST|PUT|DELETE|PATCH)\s*\([\'"]([^\'"]+)[\'"]',
                ]
            },
            'echo': {
                'files': ['go.mod'],
                'dependencies': ['labstack/echo'],
                'route_patterns': [
                    r'\.(GET|POST|PUT|DELETE|PATCH)\s*\([\'"]([^\'"]+)[\'"]',
                ]
            },
        },
        # 排除的目录
        'exclude_dirs': {'node_modules', 'venv', '__pycache__', '.git', 'dist', 'build', 
                         'vendor', 'target', 'bin', 'obj', '.idea', '.vscode'},
        # API 路径前缀
        'api_prefixes': ['api', 'v1', 'v2', 'v3', 'v4', 'rest', 'service'],
        # HTTP 方法描述映射
        'method_descriptions': {
            'GET': '获取',
            'POST': '创建',
            'PUT': '更新',
            'PATCH': '部分更新',
            'DELETE': '删除',
        },
        # 文件扩展名映射
        'framework_extensions': {
            'express': ['.js', '.ts'],
            'nestjs': ['.ts'],
            'flask': ['.py'],
            'django': ['.py'],
            'fastapi': ['.py'],
            'spring': ['.java'],
            'gin': ['.go'],
            'echo': ['.go'],
        },
    }
    
    def __init__(self, project_path: str, config_path: Optional[str] = None):
        """
        初始化分析器
        
        Args:
            project_path: 项目路径
            config_path: 可选的配置文件路径
        """
        self.project_path = Path(project_path)
        self.framework: Optional[str] = None
        self.apis: List[Dict[str, Any]] = []
        self.modules: List[str] = []
        
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
                    if 'framework_patterns' in user_config:
                        config['framework_patterns'].update(user_config['framework_patterns'])
                    if 'exclude_dirs' in user_config:
                        config['exclude_dirs'].update(user_config['exclude_dirs'])
                    if 'api_prefixes' in user_config:
                        config['api_prefixes'].extend(user_config['api_prefixes'])
                    if 'method_descriptions' in user_config:
                        config['method_descriptions'].update(user_config['method_descriptions'])
                    if 'framework_extensions' in user_config:
                        config['framework_extensions'].update(user_config['framework_extensions'])
                        
                except (json.JSONDecodeError, IOError) as e:
                    print(f"警告: 无法加载配置文件 {config_path}: {e}")
        
        return config
        
    def analyze(self) -> Dict[str, Any]:
        """执行项目分析"""
        if not self.project_path.exists():
            return {'error': f'项目路径不存在: {self.project_path}'}
        
        # 识别框架
        self.framework = self._detect_framework()
        
        # 提取 API 路由
        self.apis = self._extract_routes()
        
        # 提取模块
        self.modules = self._extract_modules()
        
        return {
            'framework': self.framework,
            'apis': self.apis,
            'modules': self.modules,
            'apiCount': len(self.apis),
            'projectPath': str(self.project_path),
        }
    
    def _detect_framework(self) -> Optional[str]:
        """检测项目使用的框架"""
        framework_patterns = self.config['framework_patterns']
        
        for framework, config in framework_patterns.items():
            for file_name in config['files']:
                file_path = self.project_path / file_name
                if file_path.exists():
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for dep in config['dependencies']:
                        if dep.lower() in content.lower():
                            return framework
        return 'unknown'
    
    def _extract_routes(self) -> List[Dict[str, Any]]:
        """提取 API 路由"""
        apis = []
        
        if self.framework is None:
            return apis
        
        framework_patterns = self.config['framework_patterns']
        config = framework_patterns.get(self.framework, {})
        patterns = config.get('route_patterns', [])
        
        # 遍历项目文件
        for file_path in self._get_source_files():
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        api_info = self._parse_route_match(match, str(file_path))
                        if api_info and api_info not in apis:
                            apis.append(api_info)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return apis
    
    def _parse_route_match(self, match, file_path: str) -> Optional[Dict[str, Any]]:
        """解析路由匹配结果"""
        groups = match.groups()
        
        if len(groups) >= 2:
            method = groups[0].upper() if groups[0] else 'GET'
            path = groups[1] if len(groups) > 1 else groups[0]
        else:
            method = 'GET'
            path = groups[0] if groups else None
        
        if not path:
            return None
        
        # 清理路径
        path = path.strip('/')
        path = f'/{path}' if not path.startswith('/') else path
        
        return {
            'method': method.upper(),
            'path': path,
            'description': self._infer_description(path, method),
            'module': self._infer_module(path),
            'sourceFile': file_path,
        }
    
    def _infer_description(self, path: str, method: str) -> str:
        """推断 API 描述"""
        path_parts = path.strip('/').split('/')
        
        # 使用配置的方法描述
        method_descriptions = self.config['method_descriptions']
        
        resource = path_parts[-1] if path_parts else '资源'
        action = method_descriptions.get(method.upper(), '操作')
        
        return f'{action}{resource}'
    
    def _infer_module(self, path: str) -> str:
        """推断所属模块"""
        path_parts = path.strip('/').split('/')
        api_prefixes = self.config['api_prefixes']
        
        if len(path_parts) > 1:
            return path_parts[1] if path_parts[0] in api_prefixes else path_parts[0]
        return path_parts[0] if path_parts else 'default'
    
    def _extract_modules(self) -> List[str]:
        """提取模块列表"""
        modules = set()
        for api in self.apis:
            if api.get('module'):
                modules.add(api['module'])
        return sorted(list(modules))
    
    def _get_source_files(self) -> List[Path]:
        """获取需要分析的源文件"""
        source_files = []
        
        framework_extensions = self.config['framework_extensions']
        exts = framework_extensions.get(self.framework, ['.js', '.ts', '.py', '.java', '.go'])
        
        exclude_dirs = self.config['exclude_dirs']
        
        for ext in exts:
            for file_path in self.project_path.rglob(f'*{ext}'):
                # 排除特定目录
                if not any(part in file_path.parts for part in exclude_dirs):
                    source_files.append(file_path)
        
        return source_files


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python analyze_project.py <项目路径> [配置文件路径]")
        print("")
        print("参数:")
        print("  项目路径            要分析的项目根目录")
        print("  配置文件路径        可选，自定义框架识别规则")
        print("")
        print("示例:")
        print("  python analyze_project.py /path/to/project")
        print("  python analyze_project.py /path/to/project config.json")
        sys.exit(1)
    
    project_path = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyzer = ProjectAnalyzer(project_path, config_path)
    result = analyzer.analyze()
    
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()