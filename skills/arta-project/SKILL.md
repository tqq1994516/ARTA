---
name: arta-project
description: ARTA 项目管理模块 - 项目接入、分析、配置管理
license: MIT
metadata:
  author: automation-team
  version: "1.0"
  trigger: "/ARTA-init, /ARTA-project-*, /ARTA-openapi-*"
allowed-tools: Bash(git:*) Bash(python:*) Read Write
---

# ARTA 项目管理模块

## 角色定义

你专注于项目接入和初始化工作，帮助用户：
- 快速接入新项目或已有项目
- 分析项目代码结构，识别 API 路由
- 解析 OpenAPI/Swagger 规范
- 生成 API 概况清单

## 触发指令

| 指令 | 说明 |
|------|------|
| `/ARTA-init` | 初始化新项目 |
| `/ARTA-project-set <路径>` | 设置项目地址 |
| `/ARTA-openapi-set <URL>` | 设置 OpenAPI 来源 |
| `/ARTA-project-info` | 查看项目信息 |
| `/ARTA-project-analyze` | 重新分析项目 |

## 工作流程

### 项目初始化流程

```
用户输入: /ARTA-init

步骤 1: 询问项目类型
┌──────────────────────────────────────────────────────────────┐
│  🚀 项目初始化                                               │
├──────────────────────────────────────────────────────────────┤
│  请问您的项目是：                                            │
│  A. 🆕 全新项目（从零开始）                                  │
│  B. 📁 已有项目（已有自动化测试）                            │
│  C. 🔄 已有项目（无自动化测试）                              │
└──────────────────────────────────────────────────────────────┘

步骤 2: 根据类型引导
- A (全新项目): 询问项目名称、框架类型、API前缀等
- B (已有测试): 询问项目路径、测试框架、现有测试目录
- C (无测试): 询问项目路径、期望的测试框架

步骤 3: API 来源选择
┌──────────────────────────────────────────────────────────────┐
│  📊 API 信息来源                                             │
├──────────────────────────────────────────────────────────────┤
│  请选择 API 信息来源：                                       │
│  A. 📁 本地项目代码（自动分析路由）                          │
│  B. 📄 OpenAPI/Swagger 规范文件                             │
│  C. 🔗 OpenAPI URL（在线文档）                              │
│  D. ✏️ 手动输入                                             │
└──────────────────────────────────────────────────────────────┘

步骤 4: 分析并生成 API 概况
- 使用 scripts/analyze_project.py 分析本地代码
- 使用 scripts/parse_openapi.py 解析 OpenAPI

步骤 5: 确认并保存
- 显示 API 概况列表
- 用户确认后保存到 assets/templates/api_inventory.json
```

## 项目分析

### 本地代码分析

当用户提供本地项目路径时：

```python
# 调用分析脚本
python scripts/analyze_project.py --path <项目路径>

# 支持的框架
- Express (Node.js)
- NestJS (Node.js)
- Flask (Python)
- Django (Python)
- FastAPI (Python)
- Spring Boot (Java)
- Gin (Go)
- Echo (Go)
```

分析配置详见 `assets/configs/analyzer_config.json`

### OpenAPI 解析

当用户提供 OpenAPI 来源时：

```python
# 解析本地文件
python scripts/parse_openapi.py --file ./docs/swagger.yaml

# 解析远程 URL
python scripts/parse_openapi.py --url https://api.example.com/openapi.json
```

支持格式：
- OpenAPI 3.0 / 3.1 (JSON/YAML)
- Swagger 2.0 (JSON/YAML)

## 配置管理

### `/ARTA-config-list`

查看所有配置文件：
```
┌──────────────────────────────────────────────────────────────┐
│  ⚙️ 配置文件列表                                             │
├──────────────────────────────────────────────────────────────┤
│  | 配置名        | 用途             | 状态     | 路径       | │
│  |---------------|------------------|----------|------------| │
│  | analyzer      | 项目分析配置     | 默认     | configs/   | │
│  | flow_diagram  | 流程图服务映射   | 自定义   | configs/   | │
│  | testpoint     | 测试点关键词映射 | 默认     | configs/   | │
└──────────────────────────────────────────────────────────────┘
```

### `/ARTA-config-show <配置名>`

显示指定配置内容。

### `/ARTA-config-edit <配置名>`

编辑指定配置。

### `/ARTA-config-reset <配置名>`

重置配置为默认值。

## 数据存储

项目配置保存在 `assets/templates/project_config.json`：

```json
{
  "projectName": "my-api-project",
  "projectType": "existing-without-tests",
  "localPath": "/path/to/project",
  "framework": "Express",
  "openapiSource": "https://api.example.com/openapi.json",
  "testFramework": "jest",
  "createdAt": "2026-03-11T12:00:00Z",
  "updatedAt": "2026-03-11T12:30:00Z"
}
```

## 相关模块

- [arta-core](../arta-core/SKILL.md) - 核心模块
- [arta-api](../arta-api/SKILL.md) - API 管理
- [arta-flow](../arta-flow/SKILL.md) - 业务链路记录

## 参考文档

详细说明见 [references/PROJECT_ONBOARDING.md](../../references/PROJECT_ONBOARDING.md)
