---
name: arta-api
description: ARTA API 管理模块 - API 清单查看、添加、编辑、删除
license: MIT
metadata:
  author: automation-team
  version: "1.0"
  trigger: "/ARTA-api-*"
allowed-tools: Read Write
---

# ARTA API 管理模块

## 角色定义

你专注于 API 清单管理，帮助用户：
- 查看和管理 API 概况
- 添加、编辑、删除 API 条目
- 按模块筛选和搜索 API
- 维护 API 元数据

## 触发指令

| 指令 | 说明 |
|------|------|
| `/ARTA-api-list [模块]` | 查看 API 概况 |
| `/ARTA-api-add <方法> <路径> <描述> [模块]` | 添加 API |
| `/ARTA-api-edit <序号>` | 编辑 API |
| `/ARTA-api-delete <序号>` | 删除 API |

## API 列表显示

### `/ARTA-api-list`

显示所有已识别的 API：

```
┌──────────────────────────────────────────────────────────────┐
│  📊 API 概况列表                                             │
├──────────────────────────────────────────────────────────────┤
│  | 序号 | 路径                | 方法 | 描述         | 模块   | │
│  |------|---------------------|------|--------------|--------| │
│  | 1    | /api/auth/login     | POST | 用户登录     | 认证   | │
│  | 2    | /api/auth/register  | POST | 用户注册     | 认证   | │
│  | 3    | /api/users          | GET  | 用户列表     | 用户   | │
│  | 4    | /api/users/{id}     | GET  | 用户详情     | 用户   | │
│  | 5    | /api/orders         | GET  | 订单列表     | 订单   | │
│  | 6    | /api/orders         | POST | 创建订单     | 订单   | │
│  ...                                                         │
│                                                              │
│  总计: 15 个 API                                             │
└──────────────────────────────────────────────────────────────┘
```

### `/ARTA-api-list <模块>`

按模块筛选：

```
用户输入: /ARTA-api-list 认证

┌──────────────────────────────────────────────────────────────┐
│  📊 API 概况列表 - 认证模块                                   │
├──────────────────────────────────────────────────────────────┤
│  | 序号 | 路径                | 方法 | 描述         |         │
│  |------|---------------------|------|--------------|         │
│  | 1    | /api/auth/login     | POST | 用户登录     |         │
│  | 2    | /api/auth/register  | POST | 用户注册     |         │
│  | 3    | /api/auth/logout    | POST | 用户登出     |         │
│                                                              │
│  总计: 3 个 API                                              │
└──────────────────────────────────────────────────────────────┘
```

## API 添加

### `/ARTA-api-add`

```
用户输入: /ARTA-api-add POST /api/auth/logout 用户登出 认证

Agent: ✅ API 已添加
       序号: 7
       路径: POST /api/auth/logout
       描述: 用户登出
       模块: 认证
```

### 必填字段

| 字段 | 说明 | 示例 |
|------|------|------|
| 方法 | HTTP 方法 | GET, POST, PUT, PATCH, DELETE |
| 路径 | API 路径 | /api/users/{id} |
| 描述 | 功能描述 | 获取用户详情 |

### 可选字段

| 字段 | 说明 | 默认值 |
|------|------|--------|
| 模块 | 所属模块 | default |
| 标签 | 分类标签 | [] |
| 认证 | 是否需要认证 | true |

## API 编辑

### `/ARTA-api-edit <序号>`

```
用户输入: /ARTA-api-edit 3

Agent: 当前 API 信息：
       序号: 3
       路径: /api/users
       方法: GET
       描述: 获取用户列表
       模块: 用户
       标签: []
       
       请选择要修改的项目：
       1. 路径
       2. 方法
       3. 描述
       4. 模块
       5. 标签
       6. 认证要求

用户输入: 3
Agent: 请输入新的描述：
用户输入: 获取所有用户信息，支持分页和筛选
Agent: ✅ API #3 描述已更新
```

## API 删除

### `/ARTA-api-delete <序号>`

```
用户输入: /ARTA-api-delete 5

Agent: 确认删除 API #5？
       路径: GET /api/orders
       描述: 订单列表
       
       ⚠️ 此操作会影响关联的业务链路。
       是否继续？(y/n)

用户输入: y
Agent: ✅ API #5 已删除
       ⚠️ 业务链路「订单查询流程」需要更新
```

## 数据存储

API 清单保存在 `assets/templates/api_inventory.json`：

```json
{
  "projectId": "project-001",
  "lastUpdated": "2026-03-11T12:00:00Z",
  "apis": [
    {
      "id": 1,
      "method": "POST",
      "path": "/api/auth/login",
      "description": "用户登录",
      "module": "认证",
      "tags": [],
      "requiresAuth": false,
      "status": "active"
    }
  ],
  "summary": {
    "total": 15,
    "byMethod": {
      "GET": 8,
      "POST": 5,
      "PUT": 1,
      "DELETE": 1
    },
    "byModule": {
      "认证": 3,
      "用户": 4,
      "订单": 5,
      "商品": 3
    }
  }
}
```

## API 状态

| 状态 | 说明 |
|------|------|
| active | 活跃 - 当前使用的 API |
| deprecated | 已弃用 - 计划移除的 API |
| planned | 规划中 - 尚未实现的 API |

## 相关模块

- [arta-core](../arta-core/SKILL.md) - 核心模块
- [arta-project](../arta-project/SKILL.md) - 项目管理
- [arta-flow](../arta-flow/SKILL.md) - 业务链路记录

## 参考文档

详细说明见 [references/COMMAND_REFERENCE.md](../../references/COMMAND_REFERENCE.md) 的 API 管理部分
