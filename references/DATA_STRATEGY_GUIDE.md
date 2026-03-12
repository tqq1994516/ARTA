# 测试数据策略指南

本文档提供测试数据来源定义的详细策略说明。

## 数据来源类型

### 类型 A：固定数据 (Fixed Data)

**说明**：用户主动提供的固定测试数据

**适用场景**：
- 测试账号信息
- 已知的配置参数
- 稳定的测试数据

**格式**：
```json
{
  "source": "fixed",
  "value": "test_user_001"
}
```

**示例**：
```
Agent: 参数 `username` 的数据来源？
用户输入: A
Agent: 请输入固定值：
用户输入: test_user_001
Agent: ✅ 已记录固定值: test_user_001
```

---

### 类型 B：生成数据 (Generated Data)

**说明**：通过规则自动生成的测试数据

**适用场景**：
- 需要唯一性的数据（如用户名、订单号）
- 需要随机性的数据
- 需要特定格式的数据

**支持的生成函数**：

| 函数 | 说明 | 示例输出 |
|------|------|----------|
| `{{uuid()}}` | 生成 UUID | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| `{{timestamp()}}` | 时间戳 | `1710176400000` |
| `{{datetime(format)}}` | 格式化日期 | `2026-03-11 19:00:00` |
| `{{random_int(min, max)}}` | 随机整数 | `42` |
| `{{random_string(length)}}` | 随机字符串 | `AbC123` |
| `{{random_email()}}` | 随机邮箱 | `test_abc123@example.com` |
| `{{random_phone()}}` | 随机手机号 | `13812345678` |
| `{{random_float(min, max, decimals)}}` | 随机浮点数 | `99.99` |
| `{{increment(prefix)}}` | 自增序列 | `USER_001`, `USER_002` |
| `{{faker(type)}}` | Faker 数据 | 根据 type 生成 |

**格式**：
```json
{
  "source": "generated",
  "function": "random_email",
  "params": {}
}
```

**示例**：
```
Agent: 参数 `email` 的数据来源？
用户输入: B
Agent: 请选择生成函数：
       1. {{uuid()}}
       2. {{timestamp()}}
       3. {{random_email()}}
       4. {{random_string(10)}}
       5. 自定义函数
用户输入: 3
Agent: ✅ 已设置生成函数: {{random_email()}}
       预览: test_x7k9m2@example.com
```

---

### 类型 C：链路生成 (Chain Generated)

**说明**从前序 API 响应中提取的数据

**适用场景**：
- 关联接口间的数据传递
- 动态获取的资源 ID
- 依赖于前序步骤的数据

**格式**：
```json
{
  "source": "chain",
  "path": "response.step1.data.token",
  "default": null
}
```

**路径表达式**：

| 表达式 | 说明 |
|--------|------|
| `response.step{n}` | 第 n 步的完整响应 |
| `response.step{n}.data` | 第 n 步的 data 字段 |
| `response.step{n}.data.items[0]` | 数组第一个元素 |
| `response.step{n}.data.user.id` | 嵌套字段访问 |
| `response.step{n}.headers.Authorization` | 响应头 |

**示例**：
```
Agent: 参数 `product_id` 的数据来源？
用户输入: C
Agent: 可用的前序响应：
       Step 1: POST /api/auth/login → response.step1.data.token
       Step 2: GET /api/products → response.step2.data.items[]
       
       请输入提取路径：
用户输入: response.step2.data.items[0].id
Agent: ✅ 已设置链路引用: {{response.step2.data.items[0].id}}
```

---

### 类型 D：数据池 (Data Pool)

**说明**：从预设数据池中获取数据

**适用场景**：
- 共享测试数据集
- 需要数据轮换
- 预置的测试数据

**格式**：
```json
{
  "source": "pool",
  "poolName": "user_accounts",
  "strategy": "random",
  "reuse": true
}
```

**数据池策略**：

| 策略 | 说明 |
|------|------|
| `random` | 随机选择一条 |
| `sequential` | 按顺序取用 |
| `round_robin` | 循环取用 |

**数据池配置示例**：
```json
{
  "pools": {
    "user_accounts": [
      { "username": "test_user_001", "password": "Test@123" },
      { "username": "test_user_002", "password": "Test@456" },
      { "username": "test_user_003", "password": "Test@789" }
    ],
    "products": [
      { "id": "PROD_001", "name": "商品A", "price": 99.99 },
      { "id": "PROD_002", "name": "商品B", "price": 199.99 }
    ]
  }
}
```

**示例**：
```
Agent: 参数 `username` 的数据来源？
用户输入: D
Agent: 可用数据池：
       1. user_accounts (3条)
       2. products (2条)
       
       请选择数据池：
用户输入: 1
Agent: 请选择取用策略：
       1. random (随机)
       2. sequential (顺序)
       3. round_robin (循环)
用户输入: 1
Agent: ✅ 已设置数据池引用: {{pool.user_accounts.random()}}
       预览: { username: "test_user_002", password: "Test@456" }
```

---

## 数据复用策略

### 数据复用池

**问题**：多个测试用例需要相同类型的数据，每次创建会产生大量冗余数据

**解决方案**：启用数据复用池，同类测试共享测试数据

**配置示例**：
```yaml
dataReuse:
  enabled: true
  pools:
    - name: "test_users"
      type: "user"
      maxCount: 10
      cleanup: "daily"
      
    - name: "test_orders"
      type: "order"
      maxCount: 100
      cleanup: "after_suite"
```

**询问时机**：当检测到 POST 类型接口时

> 💡 **数据复用建议**
> 
> 检测到此接口会创建用户数据。
> 
> 是否启用数据复用？
> - A. 启用复用池 - 同类测试共享数据，减少创建次数
> - B. 每次独立创建 - 每个测试独立创建新数据
> 
> 如果选择 A：
> - 最大数据数量：10
> - 清理策略：每日清理 / 测试套件后清理

---

## 数据格式验证

### 支持的格式规则

| 格式 | 正则表达式 | 示例 |
|------|-----------|------|
| 手机号 | `^1[3-9]\d{9}$` | 13812345678 |
| 邮箱 | `^[\w-]+@[\w-]+\.\w+$` | test@example.com |
| 身份证 | `^\d{17}[\dXx]$` | 110101199001011234 |
| URL | `^https?://[\w\-\.]+` | https://example.com |
| 日期 | `^\d{4}-\d{2}-\d{2}$` | 2026-03-11 |
| 时间 | `^\d{2}:\d{2}:\d{2}$` | 19:30:00 |
| 金额 | `^\d+(\.\d{1,2})?$` | 99.99 |

**格式验证询问**：
```
Agent: 参数 `phone` 是否需要格式验证？
       1. 手机号格式 (11位，1开头)
       2. 自定义正则
       3. 不需要验证
用户输入: 1
Agent: ✅ 已设置格式验证: 手机号格式
       正则: ^1[3-9]\d{9}$
```

---

## 数据依赖处理

### 依赖声明

当一个参数依赖于另一个参数时：

```json
{
  "params": {
    "start_date": {
      "source": "generated",
      "function": "datetime",
      "params": { "format": "YYYY-MM-DD" }
    },
    "end_date": {
      "source": "generated",
      "function": "datetime",
      "params": { "format": "YYYY-MM-DD", "offset": "+7d" },
      "dependsOn": "start_date"
    }
  }
}
```

### 动态计算

支持基于其他参数的计算：

```json
{
  "params": {
    "price": { "source": "fixed", "value": 100 },
    "quantity": { "source": "fixed", "value": 2 },
    "total_amount": {
      "source": "computed",
      "expression": "{{price}} * {{quantity}}"
    }
  }
}
```

---

## 完整配置示例

```json
{
  "flowId": "BF-001",
  "flowName": "用户下单流程",
  "testData": {
    "params": {
      "username": {
        "source": "pool",
        "poolName": "user_accounts",
        "strategy": "random",
        "field": "username"
      },
      "password": {
        "source": "pool",
        "poolName": "user_accounts",
        "strategy": "same_as_username",
        "field": "password"
      },
      "product_id": {
        "source": "chain",
        "path": "response.step2.data.items[0].id"
      },
      "quantity": {
        "source": "generated",
        "function": "random_int",
        "params": { "min": 1, "max": 5 }
      },
      "order_time": {
        "source": "generated",
        "function": "datetime",
        "params": { "format": "YYYY-MM-DD HH:mm:ss" }
      }
    },
    "dataReuse": {
      "enabled": true,
      "pools": ["user_accounts"]
    },
    "validation": {
      "phone": {
        "format": "mobile_cn",
        "required": true
      }
    }
  }
}
```

---

## 交互流程示例

完整的测试数据配置交互：

```
Agent: 📊 测试数据配置
       
       API #1: POST /api/auth/login
       ┌─────────────────────────────────────────────────────┐
       │ 参数         │ 类型     │ 来源     │ 值/规则       │
       │──────────────│──────────│──────────│───────────────│
       │ username     │ string   │ ?        │ ?             │
       │ password     │ string   │ ?        │ ?             │
       └─────────────────────────────────────────────────────┘
       
       数据来源选项：
       A. 📝 固定数据
       B. 🔧 生成数据
       C. 🔗 链路生成
       D. 📊 数据池

用户输入: D

Agent: 可用数据池：
       1. user_accounts (3条)
       2. products (5条)
       
       请选择或输入"新建"创建数据池：
用户输入: 1

Agent: 已选择数据池 "user_accounts"
       取用策略：
       A. 随机取用
       B. 顺序取用
       C. 循环取用
用户输入: A

Agent: ✅ username 已配置：{{pool.user_accounts.random().username}}
       
       password 参数：
       检测到与 username 来自同一数据池，是否关联？
       A. 是，使用同一数据条目的 password 字段
       B. 否，单独配置
用户输入: A

Agent: ✅ password 已配置：{{pool.user_accounts.random().password}}
       
       API #1 数据配置完成！
       ┌─────────────────────────────────────────────────────┐
       │ 参数         │ 类型     │ 来源     │ 值/规则       │
       │──────────────│──────────│──────────│───────────────│
       │ username     │ string   │ 数据池   │ user_accounts │
       │ password     │ string   │ 数据池   │ 同上条目      │
       └─────────────────────────────────────────────────────┘
       
       继续配置 API #2...