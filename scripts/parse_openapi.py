#!/usr/bin/env python3
"""
OpenAPI 规范解析脚本
用于解析 OpenAPI/Swagger 规范文件，提取 API 端点信息
"""

import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.request import urlopen
from urllib.error import URLError


class OpenAPIParser:
    """OpenAPI 规范解析器"""
    
    def __init__(self, source: str):
        """
        初始化解析器
        
        Args:
            source: OpenAPI 文件路径或 URL
        """
        self.source = source
        self.spec: Dict[str, Any] = {}
        self.apis: List[Dict[str, Any]] = []
        
    def parse(self) -> Dict[str, Any]:
        """执行解析"""
        # 加载规范文件
        self.spec = self._load_spec()
        
        if not self.spec:
            return {'error': f'无法加载 OpenAPI 规范: {self.source}'}
        
        # 提取 API 端点
        self.apis = self._extract_apis()
        
        # 提取信息
        info = self._extract_info()
        
        return {
            'info': info,
            'apis': self.apis,
            'apiCount': len(self.apis),
            'source': self.source,
        }
    
    def _load_spec(self) -> Dict[str, Any]:
        """加载 OpenAPI 规范文件"""
        content = None
        
        # 判断是 URL 还是本地文件
        if self.source.startswith(('http://', 'https://')):
            try:
                with urlopen(self.source, timeout=30) as response:
                    content = response.read().decode('utf-8')
            except URLError as e:
                print(f"Error fetching URL: {e}")
                return {}
        else:
            file_path = Path(self.source)
            if not file_path.exists():
                print(f"File not found: {file_path}")
                return {}
            content = file_path.read_text(encoding='utf-8')
        
        # 解析 JSON 或 YAML
        try:
            if self.source.endswith(('.yaml', '.yml')) or 'openapi' in content[:100]:
                # 尝试 YAML 解析
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    pass
            
            # 尝试 JSON 解析
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}
    
    def _extract_info(self) -> Dict[str, Any]:
        """提取 OpenAPI 基本信息"""
        info = self.spec.get('info', {})
        
        return {
            'title': info.get('title', 'Unknown API'),
            'version': info.get('version', '1.0.0'),
            'description': info.get('description', ''),
            'openapiVersion': self.spec.get('openapi') or self.spec.get('swagger', 'unknown'),
        }
    
    def _extract_apis(self) -> List[Dict[str, Any]]:
        """提取所有 API 端点"""
        apis = []
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method in ['get', 'post', 'put', 'patch', 'delete']:
                if method in path_item:
                    operation = path_item[method]
                    api_info = self._parse_operation(path, method, operation)
                    apis.append(api_info)
        
        return apis
    
    def _parse_operation(self, path: str, method: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """解析单个操作"""
        # 提取基本信息
        summary = operation.get('summary', '')
        description = operation.get('description', summary)
        operation_id = operation.get('operationId', '')
        tags = operation.get('tags', [])
        
        # 提取参数
        params = self._extract_parameters(operation)
        
        # 提取请求体
        request_body = self._extract_request_body(operation)
        
        # 提取响应
        responses = self._extract_responses(operation)
        
        return {
            'path': path,
            'method': method.upper(),
            'description': description or summary or f'{method.upper()} {path}',
            'summary': summary,
            'operationId': operation_id,
            'module': tags[0] if tags else self._infer_module(path),
            'tags': tags,
            'params': params,
            'requestBody': request_body,
            'responses': responses,
        }
    
    def _extract_parameters(self, operation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取参数列表"""
        params = []
        
        for param in operation.get('parameters', []):
            param_info = {
                'name': param.get('name', ''),
                'in': param.get('in', 'query'),  # query, path, header, cookie
                'required': param.get('required', False),
                'description': param.get('description', ''),
                'schema': param.get('schema', {}),
            }
            params.append(param_info)
        
        return params
    
    def _extract_request_body(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """提取请求体定义"""
        request_body = operation.get('requestBody', {})
        
        if not request_body:
            return {}
        
        content = request_body.get('content', {})
        description = request_body.get('description', '')
        required = request_body.get('required', False)
        
        # 提取内容类型
        body_schema = {}
        for content_type, media_type in content.items():
            if 'schema' in media_type:
                body_schema = {
                    'contentType': content_type,
                    'schema': media_type['schema'],
                }
                break
        
        return {
            'description': description,
            'required': required,
            'content': body_schema,
        }
    
    def _extract_responses(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """提取响应定义"""
        responses = operation.get('responses', {})
        
        result = {}
        for status_code, response in responses.items():
            description = response.get('description', '')
            content = response.get('content', {})
            
            # 提取响应 schema
            schema = {}
            for content_type, media_type in content.items():
                if 'schema' in media_type:
                    schema = media_type['schema']
                    break
            
            result[status_code] = {
                'description': description,
                'schema': schema,
            }
        
        return result
    
    def _infer_module(self, path: str) -> str:
        """从路径推断模块名"""
        path_parts = path.strip('/').split('/')
        
        # 跳过常见的 API 前缀
        skip_prefixes = {'api', 'v1', 'v2', 'v3', 'rest'}
        
        for part in path_parts:
            if part not in skip_prefixes and not part.startswith('{'):
                return part
        
        return 'default'
    
    def generate_api_inventory(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """生成 API 清单格式"""
        apis = []
        
        for idx, api in enumerate(self.apis, 1):
            apis.append({
                'id': idx,
                'path': api['path'],
                'method': api['method'],
                'description': api['description'],
                'module': api['module'],
                'auth': self._check_auth_required(api),
                'params': api['params'],
                'requestBody': api['requestBody'].get('content', {}).get('schema', {}),
                'responses': {k: v['description'] for k, v in api['responses'].items()},
            })
        
        inventory = {
            'version': '1.0',
            'source': self.source,
            'apis': apis,
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, indent=2, ensure_ascii=False)
            print(f"API 清单已保存到: {output_path}")
        
        return inventory
    
    def _check_auth_required(self, api: Dict[str, Any]) -> bool:
        """检查 API 是否需要认证"""
        security = self.spec.get('security', [])
        path_item_security = None
        
        paths = self.spec.get('paths', {})
        if api['path'] in paths:
            path_item = paths[api['path']]
            method_lower = api['method'].lower()
            if method_lower in path_item:
                path_item_security = path_item[method_lower].get('security')
        
        # 如果路径级别有 security 定义，使用它
        if path_item_security is not None:
            return len(path_item_security) > 0
        
        # 否则使用全局 security
        return len(security) > 0


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python parse_openapi.py <OpenAPI文件路径或URL> [输出文件路径]")
        print("示例:")
        print("  python parse_openapi.py https://api.example.com/openapi.json")
        print("  python parse_openapi.py ./docs/openapi.yaml ./api_inventory.json")
        sys.exit(1)
    
    source = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    parser = OpenAPIParser(source)
    result = parser.parse()
    
    if output_path:
        parser.generate_api_inventory(output_path)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()