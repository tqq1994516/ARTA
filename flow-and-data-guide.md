# 业务链路和数据策略详细指南

本文档是 ARTA 业务链路记录的详细参考，仅在需要深入了解时阅读。

## 链路数据结构

```json
{
  "flows": [
    {
      "id": "flow-001",
      "name": "用户下单流程",
      "module": "订单",
      "priority": "P0",
      "status": "done",
      "description": "用户从浏览商品到完成下单的完整流程",
      "steps": [
        {
          "order": 1,
          "apiId": 1,
          "method": "POST",
          "path": "/api/auth/login",
          "description": "用户登录",
          "requestData": {
            "body": {
              "username": "testuser001",
              "password": "Test@123456"
            }
          },
          "extractVariables": {
            "token": "$.data.token",
            "userId": "$.data.user.id"
          },
          "assertions": [
            { "type": "status", "expected": 200 },
            { "type": "jsonpath", "path": "$.data.token", "condition": "exists" }
          ]
        },
        {
          "order": 2,
          "apiId": 5,
          "method": "POST",
          "path": "/api/orders",
          "description": "创建订单",
          "requestData": {
            "headers": {
              "Authorization": "Bearer ${step1.token}"
            },
            "body": {
              "productId": "${step2.response.data[0].id}",
              "quantity": 1
            }
          },
          "extractVariables": {
            "orderId": "$.data.orderId"
          },
          "assertions": [
            { "type": "status", "expected": 201 },
            { "type": "jsonpath", "path": "$.data.orderId", "condition": "exists" },
            { "type": "jsonpath", "path": "$.data.status", "condition": "equals", "expected": "pending" }
          ]
        }
      ],
      "cleanup": [
        {
          "method": "DELETE",
          "path": "/api/orders/${orderId}",
          "description": "清理测试订单"
        }
      ],
      "createdAt": "2026-03-11T12:00:00Z"
    }
  ]
}
```

## 测试数据策略详解

### 固定值

直接指定的常量，适用于已知的测试账号或配置：

```json
{
  "username": "testuser001",
  "page": 1,
  "size": 10,
  "status": "active"
}
```

### 生成数据 (`{{函数()}}`)

使用内置函数动态生成测试数据：

| 函数 | 说明 | 示例输出 |
|------|------|---------|
| `{{uuid()}}` | UUID v4 | `"a1b2c3d4-..."` |
| `{{timestamp()}}` | 当前时间戳 | `1710180000` |
| `{{random_email()}}` | 随机邮箱 | `"test_abc123@test.com"` |
| `{{random_phone()}}` | 随机手机号 | `"13800138001"` |
| `{{increment(prefix)}}` | 自增序列 | `"user_001"`, `"user_002"` |
| `{{faker(name)}}` | 随机姓名 | `"张三"` |
| `{{faker(address)}}` | 随机地址 | `"北京市朝阳区..."` |
| `{{random_string(N)}}` | N位随机字符串 | `"aB3kF9"` |
| `{{random_int(min,max)}}` | 范围随机整数 | `42` |

### 引用上游 (`${步骤.字段}`)

引用前面步骤的响应数据，实现跨步骤数据传递：

```
${step1.token}                  -> 步骤1提取的token变量
${step2.response.data[0].id}    -> 步骤2响应体中的字段
${step1.userId}                 -> 步骤1提取的userId变量
```

引用规则：
- `${stepN.变量名}` - 引用步骤N中 extractVariables 定义的变量
- `${stepN.response.路径}` - 直接引用步骤N响应体的 JSON 路径
- 被引用的步骤必须在当前步骤之前执行

### 环境变量 (`$ENV{变量}`)

引用运行时环境变量：

```
$ENV{BASE_URL}     -> API 基础地址
$ENV{API_KEY}      -> API 密钥
$ENV{TEST_ENV}     -> 测试环境标识
```

## 断言类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `status` | HTTP 状态码 | `{ "type": "status", "expected": 200 }` |
| `jsonpath` + `exists` | 字段存在 | `{ "path": "$.data.token", "condition": "exists" }` |
| `jsonpath` + `equals` | 值相等 | `{ "path": "$.data.status", "condition": "equals", "expected": "active" }` |
| `jsonpath` + `contains` | 包含字符串 | `{ "path": "$.message", "condition": "contains", "expected": "success" }` |
| `jsonpath` + `type` | 类型检查 | `{ "path": "$.data.list", "condition": "type", "expected": "array" }` |
| `jsonpath` + `length_gte` | 数组长度 | `{ "path": "$.data.list", "condition": "length_gte", "expected": 1 }` |
| `response_time` | 响应时间 | `{ "type": "response_time", "max_ms": 1000 }` |
| `header` | 响应头 | `{ "type": "header", "name": "Content-Type", "contains": "application/json" }` |

## CRUD 接口处理策略

### 创建(Create) 接口

```
建议测试场景:
1. 创建成功 - 必填字段完整
2. 创建失败 - 缺少必填字段
3. 创建失败 - 字段格式错误
4. 创建失败 - 重复创建（唯一约束）

数据策略: 使用生成数据避免冲突，如 {{uuid()}} 作为唯一标识
清理: 记录创建的资源 ID，测试结束后删除
```

### 更新(Update) 接口

```
建议测试场景:
1. 更新成功 - 有效字段
2. 更新失败 - 资源不存在
3. 更新失败 - 无权限
4. 部分更新 - 只修改部分字段

前置: 需要先创建资源
数据策略: 引用创建步骤返回的 ID
```

### 删除(Delete) 接口

```
建议测试场景:
1. 删除成功 - 存在的资源
2. 删除失败 - 不存在的资源
3. 删除失败 - 无权限
4. 级联删除验证

前置: 需要先创建资源
注意: 删除接口通常放在测试最后执行，兼做清理
```

### 查询(Read) 接口

```
建议测试场景:
1. 查询成功 - 有数据
2. 查询成功 - 无数据（空结果）
3. 分页查询 - 默认分页
4. 条件筛选 - 各筛选参数
5. 查询失败 - 无权限

数据策略: 先确保有测试数据，再进行查询验证
```

## 优先级排序建议

按以下顺序记录链路：

| 优先级 | 说明 | 示例 |
|--------|------|------|
| P0 | 核心业务，宕机影响收入 | 登录、下单、支付 |
| P1 | 重要功能，影响用户体验 | 搜索、评论、收藏 |
| P2 | 一般功能，可降级 | 个人设置、通知偏好 |
| P3 | 边缘功能 | 帮助页、反馈表单 |

## 链路状态

| 状态 | 说明 |
|------|------|
| `draft` | 草稿 - 正在编辑，API序列或数据未完整 |
| `done` | 完成 - 可用于生成测试用例 |
| `deprecated` | 已弃用 - 业务下线或重构 |
