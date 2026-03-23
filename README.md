# ARTA - 自动化回归测试助手

ARTA（Automation Regression Test Assistant）是一个端到端 API 自动化测试流程引导工具，帮助开发团队从项目接入到测试用例生成的完整流程。

## 功能描述

ARTA 提供四阶段测试工作流程：

```
Phase 1         Phase 2         Phase 3          Phase 4
接入项目    -->  扫描 API    -->  记录业务链路  -->  生成测试用例
```

### 核心功能

- **项目接入** - 配置项目基本信息、选择后端框架和测试框架
- **API 扫描** - 自动分析代码路由或解析 OpenAPI/Swagger 规范
- **业务链路记录** - 定义 API 调用序列、测试数据和断言规则
- **测试用例生成** - 基于链路自动生成多框架测试代码
- **测试点导入** - 支持从 Mermaid 思维导图导入测试点

### 支持的技术栈

| 后端框架 | 测试框架 | 语言 |
|---------|---------|------|
| Express, NestJS | Jest, Vitest, Mocha | TypeScript |
| Flask, Django, FastAPI | Pytest | Python |
| Spring Boot | JUnit 5 | Java |
| Gin, Echo | Go testing | Go |

## 安装方法

### 环境要求

- Claude Code / OpenCode / VSCode Cline 等支持 Skill 的 AI 编程助手
- 项目代码需放在可访问的工作目录中

### 安装步骤

1. 将本 Skill 文件复制到你的 AI 助手的 skills 目录：
   - **Claude Code**: `.claude/skills/`
   - **OpenCode**: `.opencode/skills/`
   - **VSCode Cline**: `.vscode/cline/skills/`

2. 目录结构示例：
   ```
   .claude/skills/arta-test-workflow/
   ├── SKILL.md                  # 本 Skill 主文件
   ├── README.md                 # 说明文档
   ├── flow-and-data-guide.md    # 业务链路详细指南
   └── generation-reference.md   # 测试生成参考
   ```

3. 重启 AI 助手，Skill 将自动加载

## 使用方法

### 快速开始

在 AI 助手的对话中输入以下任一方式启动：

```
ARTA
```

或

```
/ARTA-start
```

### 指令速查

| 指令 | 说明 |
|------|------|
| `/ARTA-start` | 启动新项目，配置基本信息 |
| `/ARTA-scan` | 扫描项目代码或解析 OpenAPI，生成 API 清单 |
| `/ARTA-flow` | 添加/查看/编辑业务链路 |
| `/ARTA-testpoint` | 导入 mermaid 思维导图测试点 |
| `/ARTA-generate` | 基于链路生成测试用例代码 |
| `/ARTA-status` | 查看项目当前状态和进度 |
| `/ARTA-export` | 导出所有配置和测试文件 |

### 使用示例

#### 1. 初始化项目

```
用户: /ARTA-start

Agent: 回答以下几个问题来初始化项目：
1. 项目名称是什么？
2. API 信息来源：
   A. 本地项目代码（自动分析路由）
   B. OpenAPI/Swagger 规范文件
   C. OpenAPI URL
   D. 手动输入 API 列表
3. 项目使用什么后端框架？
4. 期望用什么测试框架生成用例？
```

#### 2. 扫描 API

```
用户: /ARTA-scan

Agent: 扫描完成，发现 15 个 API:
| # | 方法   | 路径                 | 描述     | 模块 |
|---|--------|----------------------|----------|------|
| 1 | POST   | /api/auth/login      | 用户登录 | 认证 |
| 2 | POST   | /api/auth/register   | 用户注册 | 认证 |
...
```

#### 3. 记录业务链路

```
用户: /ARTA-flow 添加用户下单流程

Agent: 引导完成 5 个步骤：
- Step 1: 基本信息（名称、模块、优先级）
- Step 2: 选择 API 调用序列
- Step 3: 配置测试数据（固定值/生成数据/引用上游/环境变量）
- Step 4: 配置断言规则
- Step 5: 确认保存
```

#### 4. 生成测试用例

```
用户: /ARTA-generate

Agent: 生成完成:
- 测试文件: 3 个
- 测试用例: 24 个
- 覆盖 API: 12/15 (80%)
- 输出目录: tests/flows/
```

### 测试数据语法

支持 4 种数据类型：

| 类型 | 语法 | 示例 |
|------|------|------|
| 固定值 | 直接写值 | `"testuser001"` |
| 生成数据 | `{{函数()}}` | `{{uuid()}}`, `{{random_email()}}` |
| 引用上游 | `${步骤.字段}` | `${login.response.token}` |
| 环境变量 | `$ENV{变量}` | `$ENV{BASE_URL}` |

### 数据存储

所有数据存储在当前工作目录的 `arta-data/` 下：

| 文件 | 内容 |
|------|------|
| `arta-data/project.json` | 项目配置 |
| `arta-data/apis.json` | API 清单 |
| `arta-data/flows.json` | 业务链路 |
| `arta-data/testpoints.json` | 测试点（如有导入） |

生成的测试代码默认输出到 `tests/flows/` 目录。

## 文档参考

- [业务链路和数据策略详细指南](./flow-and-data-guide.md) - 深入了解链路数据结构、测试数据策略、断言类型
- [测试生成详细参考](./generation-reference.md) - 各框架代码模板、生成策略、测试报告格式

## 特性

- **自然语言优先** - 无需记忆指令，用自然语言描述需求即可
- **断点续作** - 随时暂停，通过 `/ARTA-status` 了解进度并继续
- **增量操作** - 支持随时添加新 API、新链路，不需要从头开始
- **智能提醒** - 包含写入操作的链路自动建议添加清理步骤
- **多框架支持** - 一次配置，生成多种测试框架代码
