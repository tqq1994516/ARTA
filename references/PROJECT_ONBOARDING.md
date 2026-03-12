# 项目接入引导

本文档提供项目接入的详细引导流程。

## 流程概览

```
┌─────────────────────────────────────────────────────────────┐
│                   项目接入流程                               │
├─────────────────────────────────────────────────────────────┤
│  步骤1: 询问项目类型                                        │
│  步骤2: 询问项目代码来源                                    │
│  步骤3: 分析项目并生成 API 概况                             │
│  步骤4: 用户确认 API 概况                                   │
│  步骤5: 进入业务链路记录                                    │
└─────────────────────────────────────────────────────────────┘
```

## 步骤1：询问项目类型

> 请问您的项目是：
> 
> A. 🆕 全新项目（还没有自动化测试）
> B. 📁 已有项目（已有部分自动化测试用例）
> C. 🔄 已有项目（还没有自动化测试）

根据用户选择：

### 选择 A：全新项目
- 进入步骤2，询问代码来源
- 初始化新的测试项目结构

### 选择 B：已有项目+已有测试
- 询问现有测试代码路径
- 分析现有测试用例结构
- 展示测试覆盖统计

### 选择 C：已有项目+无测试
- 进入步骤2，询问代码来源
- 从零开始建立测试体系

## 步骤2：询问项目代码来源

> 请问您能提供项目代码吗？
> 
> **方式一：本地项目路径**
> - Windows 示例：`C:\Users\YourName\projects\my-api`
> - Linux/Mac 示例：`/home/user/projects/my-api`
> 
> **方式二：OpenAPI/Swagger 规范文件**
> - URL 示例：`https://api.example.com/openapi.json`
> - 本地文件示例：`./docs/openapi.yaml`
> 
> 请提供路径或链接，或输入"跳过"手动输入 API 信息。

### 如果提供本地代码路径

1. 验证路径有效性
2. 扫描项目结构
3. 识别项目框架类型：
   - Node.js: Express, NestJS, Koa, Fastify
   - Python: Flask, Django, FastAPI
   - Java: Spring Boot, JAX-RS
   - Go: Gin, Echo, Fiber
   - 其他框架
4. 提取 API 路由定义
5. 生成 API 清单

### 如果提供 OpenAPI 规范

1. 验证 URL/路径有效性
2. 解析 OpenAPI/Swagger 格式
3. 提取所有 endpoints
4. 提取请求/响应模式
5. 生成 API 清单

### 如果选择"跳过"

进入手动添加 API 模式，引导用户逐个添加 API。

## 步骤3：生成 API 概况

分析完成后，展示 API 概况表：

> 📊 已分析出以下 API 概况：
> 
> | 序号 | 路径 | 方法 | 功能描述 | 模块 |
> |------|------|------|----------|------|
> | 1 | /api/auth/login | POST | 用户登录 | 认证 |
> | 2 | /api/auth/register | POST | 用户注册 | 认证 |
> | 3 | /api/users | GET | 获取用户列表 | 用户 |
> | 4 | /api/users/{id} | GET | 获取用户详情 | 用户 |
> | 5 | /api/orders | GET | 获取订单列表 | 订单 |
> | 6 | /api/orders | POST | 创建订单 | 订单 |
> | ... | ... | ... | ... | ... |
> 
> **统计信息**：
> - 总 API 数量：15
> - 涉及模块：认证、用户、订单、商品

## 步骤4：用户确认 API 概况

> 请确认以上 API 概况是否正确？
> 
> - 输入序号修改描述（如：`修改 3`）
> - 输入 `添加` 补充遗漏的 API
> - 输入 `删除 序号` 移除无效 API（如：`删除 5`）
> - 输入 `确认` 继续下一步

### 修改 API 描述
```
用户输入: 修改 3
Agent: 请输入新的描述信息：
用户输入: 获取所有用户信息，支持分页
Agent: 已更新 API #3 的描述
```

### 添加新 API
```
用户输入: 添加
Agent: 请输入 API 信息（格式：方法 路径 描述）：
用户输入: POST /api/logout 用户登出
Agent: 已添加新 API #16
```

### 删除 API
```
用户输入: 删除 5
Agent: 确认删除 API #5 GET /api/orders？(y/n)
用户输入: y
Agent: 已删除 API #5
```

## 步骤5：进入业务链路记录

API 概况确认后：

> ✅ API 概况已确认！
> 
> 接下来可以：
> 
> A. ➕ 开始添加业务链路
> B. 📥 导入测试点思维导图
> C. 📋 查看当前项目状态
> D. 💾 保存并稍后继续

选择 A：加载 [BUSINESS_FLOW_RECORDER.md](BUSINESS_FLOW_RECORDER.md)
选择 B：加载 [TESTPOINT_GUIDE.md](TESTPOINT_GUIDE.md)

## 项目配置存储

项目信息存储到 `assets/templates/project_config.json`：

```json
{
  "projectName": "my-api-project",
  "projectType": "existing",
  "hasExistingTests": true,
  "localPath": "C:\\Users\\xxx\\projects\\my-api",
  "openapiUrl": null,
  "testPath": "C:\\Users\\xxx\\projects\\my-api\\tests",
  "framework": "Express",
  "apiCount": 15,
  "modules": ["auth", "users", "orders", "products"],
  "createdAt": "2026-03-11T18:00:00Z",
  "updatedAt": "2026-03-11T18:30:00Z"
}
```

## API 清单存储

API 信息存储到 `assets/templates/api_inventory.json`：

```json
{
  "version": "1.0",
  "lastUpdated": "2026-03-11T18:30:00Z",
  "apis": [
    {
      "id": 1,
      "path": "/api/auth/login",
      "method": "POST",
      "description": "用户登录",
      "module": "认证",
      "auth": true,
      "params": [],
      "requestBody": {
        "username": "string",
        "password": "string"
      },
      "responses": {
        "200": "登录成功",
        "401": "认证失败"
      }
    }
  ]
}
```

## 脚本配置

### 分析脚本配置文件

当默认框架识别规则无法满足需求时，可以通过配置文件自定义：

**配置文件路径**：`assets/configs/analyzer_config.json`

**配置文件格式**：
```json
{
  "framework_patterns": {
    "自定义框架名": {
      "files": ["特征文件名"],
      "dependencies": ["依赖包名"],
      "route_patterns": ["路由正则表达式"]
    }
  },
  "exclude_dirs": ["自定义排除目录"],
  "api_prefixes": ["自定义API前缀"],
  "method_descriptions": {
    "GET": "自定义描述"
  },
  "framework_extensions": {
    "自定义框架名": [".扩展名"]
  }
}
```

**示例：添加 Koa 框架支持**
```json
{
  "framework_patterns": {
    "koa": {
      "files": ["package.json"],
      "dependencies": ["koa", "@koa/router"],
      "route_patterns": [
        "router\\.(get|post|put|delete|patch)\\s*\\([\\'"]([^\\'"]+)[\\'"]"
      ]
    }
  },
  "framework_extensions": {
    "koa": [".js", ".ts"]
  }
}
```

### 使用配置文件

```
方式一：Agent 自动加载
Agent 会在项目分析时自动查找 assets/configs/analyzer_config.json

方式二：手动指定
/ARTA-project-analyze-with-config <配置文件路径>
```

### 配置生成流程

```
┌──────────────────────────────────────────────────────────────┐
│  Agent: 检测到项目使用未知框架                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  项目框架: unknown                                           │
│  已识别的框架模式无法匹配此项目                               │
│                                                              │
│  请选择操作：                                                 │
│  A. 手动选择框架类型                                         │
│     - 从已有框架列表中选择                                   │
│  B. 添加自定义框架配置                                       │
│     - 提供框架识别特征                                       │
│  C. 跳过框架识别，手动添加API                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**选择 B 后的配置引导**：
```
Agent: 请提供自定义框架配置信息：

1. 框架名称：[输入框架名]
2. 特征文件（如 package.json, go.mod）：[输入文件名]
3. 依赖包名（用于确认框架）：[输入包名]
4. 文件扩展名（如 .js, .ts）：[输入扩展名]
5. 路由正则表达式：[输入正则]

示例路由正则：
  Express: app\\.(get|post)\\s*\\([\\'"]([^\\'"]+)[\\'"]
  Flask: @app\\.route\\s*\\([\\'"]([^\\'"]+)[\\'"]

用户输入: ...

Agent: ✅ 配置已保存到 assets/configs/analyzer_config.json
       正在重新分析项目...
```

## 常见问题

### Q: 项目路径识别失败怎么办？
A: 请确认路径格式正确，Windows 使用反斜杠或正斜杠均可。如果仍失败，可以手动添加 API。

### Q: OpenAPI 解析失败怎么办？
A: 请确认 OpenAPI 版本（支持 2.0/3.0/3.1），检查 JSON/YAML 格式是否正确。

### Q: 如何重新分析项目？
A: 使用指令 `/ARTA-project-analyze` 重新扫描项目。

### Q: 如何添加自定义框架支持？
A: 创建 `assets/configs/analyzer_config.json` 配置文件，添加框架识别规则。

### Q: 默认支持哪些框架？
A: 默认支持：Express、NestJS、Flask、Django、FastAPI、Spring、Gin、Echo。

### Q: 如何修改方法描述的语言？
A: 在配置文件中设置 `method_descriptions`，可以将描述改为其他语言。
