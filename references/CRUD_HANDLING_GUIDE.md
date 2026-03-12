# 增删改接口处理指南

本文档提供对 POST（新增）、PUT/PATCH（编辑）、DELETE（删除）类型接口的特殊处理策略。

## 概述

在业务链路中，不同类型的接口需要不同的测试策略：

| 接口类型 | 方法 | 主要关注点 |
|----------|------|------------|
| 新增 | POST | 数据创建、数据复用、清理策略 |
| 编辑 | PUT/PATCH | 数据来源、状态恢复、一致性验证 |
| 删除 | DELETE | 执行方式、数据保护、级联影响 |

---

## 一、新增接口 (POST) 处理策略

### 1.1 自动检测触发

当业务链路中包含 POST 类型接口时，自动触发以下询问：

> 📥 **新增接口数据处理策略**
> 
> 检测到新增类型接口：
> - `POST /api/auth/register`
> - `POST /api/orders`
> 
> 需要为每个新增接口配置数据处理策略。

### 1.2 关键询问项

#### 询问 1：数据复用需求

> 1️⃣ **新增的数据是否需要在后续流程中复用？**
> 
> ```
> POST /api/auth/login
> 
> 登录成功后会返回 token，后续接口需要使用此 token 进行认证。
> 
> A. 是，需要复用 → 自动提取响应数据供后续使用
> B. 否，仅用于当前测试
> ```

**选择 A 后的配置**：
```
Agent: 请选择需要提取并复用的字段：
       响应结构预览：
       {
         "status": 200,
         "data": {
           "token": "eyJhbGciOiJIUzI1NiIs...",
           "user_id": "USR_001",
           "expires_in": 3600
         }
       }
       
       可提取字段：
       1. data.token
       2. data.user_id
       3. data.expires_in
       
       请输入要提取的字段（可多选，用逗号分隔）：
用户输入: 1,2
Agent: ✅ 已设置提取字段：
       - {{response.step1.data.token}} → 用于后续接口认证
       - {{response.step1.data.user_id}} → 可用于用户相关操作
```

#### 询问 2：数据产生策略

> 2️⃣ **是否需要减少测试数据产生？**
> 
> ```
> POST /api/orders
> 
> 每次测试都会创建新订单，可能产生大量测试数据。
> 
> A. 启用数据复用池 - 同类测试共享测试数据
>    优点：减少数据冗余，提高测试效率
>    缺点：数据可能被其他测试修改
> 
> B. 每次独立创建 - 每个测试独立创建新数据
>    优点：数据隔离，测试互不影响
>    缺点：可能产生大量测试数据
> ```

**复用池配置**：
```
Agent: 数据复用池配置：
       
       数据类型：订单
       最大数量：[10] 条
       清理策略：
       1. 每日清理
       2. 测试套件后清理
       3. 手动清理
       
用户输入: 1
Agent: ✅ 已创建订单数据复用池
       最多保留 10 条测试订单，每日自动清理
```

#### 询问 3：测试完成后处理

> 3️⃣ **测试完成后如何处理创建的数据？**
> 
> ```
> POST /api/orders
> 
> A. 自动清理（推荐）
>    - 测试结束后自动删除创建的数据
>    - 保持测试环境干净
> 
> B. 标记为测试数据
>    - 通过字段标记区分测试数据
>    - 便于后续追踪和批量清理
> 
> C. 不处理
>    - 保留在环境中
>    - 依赖定期清理机制
> ```

**自动清理配置**：
```
Agent: 自动清理配置：
       
       清理时机：
       1. 每个用例执行后
       2. 整个测试套件执行后
       
       清理方式：
       - 使用 DELETE /api/orders/{id} 接口
       - 需要确认有删除权限
       
用户输入: 1
Agent: ✅ 已配置自动清理
       每个用例执行后将调用 DELETE 接口清理数据
```

### 1.3 新增接口配置示例

```json
{
  "apiId": 6,
  "method": "POST",
  "path": "/api/orders",
  "description": "创建订单",
  "handling": {
    "extractFields": [
      { "field": "data.order_id", "alias": "order_id", "forReuse": true },
      { "field": "data.order_no", "alias": "order_no", "forReuse": false }
    ],
    "dataReuse": {
      "enabled": true,
      "poolName": "test_orders",
      "maxCount": 10
    },
    "cleanup": {
      "enabled": true,
      "timing": "after_each",
      "method": "delete",
      "endpoint": "DELETE /api/orders/{order_id}",
      "condition": "response.status == 201"
    }
  }
}
```

---

## 二、编辑接口 (PUT/PATCH) 处理策略

### 2.1 自动检测触发

当业务链路中包含 PUT 或 PATCH 类型接口时，自动触发以下询问：

> ✏️ **编辑接口数据处理策略**
> 
> 检测到编辑类型接口：
> - `PUT /api/users/{id}`
> 
> 编辑操作会修改现有数据，需要特别注意。

### 2.2 关键询问项

#### 询问 1：编辑前数据来源

> 1️⃣ **编辑前的数据来源？**
> 
> ```
> PUT /api/users/{id}
> 
> 需要一个已存在的用户数据来进行编辑操作。
> 
> A. 使用现有测试数据
>    - 从数据池中获取已有用户
>    - 前提：数据池中存在可用用户
> 
> B. 临时创建测试数据
>    - 先调用创建用户接口
>    - 再执行编辑操作
> 
> C. 使用生产数据副本（谨慎）
>    - 复制生产环境数据到测试环境
>    - 需要特殊权限和审批
> ```

**选择 B 后的配置**：
```
Agent: 将在编辑前自动创建测试数据：
       
       步骤调整：
       1. POST /api/users - 创建临时用户
       2. PUT /api/users/{id} - 编辑用户信息
       3. [后置] DELETE /api/users/{id} - 清理临时用户
       
       临时用户数据配置：
       - 用户名：{{random_string(8)}}
       - 邮箱：{{random_email()}}
       
用户输入: 确认
Agent: ✅ 已配置临时数据创建流程
```

#### 询问 2：编辑后验证策略

> 2️⃣ **编辑后的数据验证策略？**
> 
> ```
> PUT /api/users/{id}
> 
> 请选择需要验证的内容：
> 
> [ ] 验证修改后值正确
>     - 检查请求修改的字段是否更新成功
> 
> [ ] 验证未修改字段不变
>     - 检查未在请求中的字段是否保持原值
> 
> [ ] 验证关联数据一致性
>     - 检查与该用户关联的其他数据是否一致
> 
> [ ] 验证更新时间戳
>     - 检查 updated_at 字段是否更新
> ```

**验证配置**：
```
Agent: 请选择验证项（多选，用逗号分隔）：
用户输入: 1,2,4
Agent: ✅ 已配置验证策略：
       - 验证修改后值正确
       - 验证未修改字段不变
       - 验证更新时间戳
```

#### 询问 3：测试完成后恢复

> 3️⃣ **测试完成后是否需要复原？**
> 
> ```
> PUT /api/users/{id}
> 
> 编辑操作改变了数据状态。
> 
> A. 是，自动恢复原始值（推荐）
>    - 测试前记录原始值
>    - 测试后执行恢复 PUT
> 
> B. 否，保留编辑后的状态
>    - 数据保持测试后的状态
>    - 可能影响后续测试
> 
> C. 标记为已测试，下次跳过
>    - 记录该数据已被修改
>    - 后续测试使用其他数据
> ```

**恢复配置**：
```
Agent: 数据恢复配置：
       
       恢复策略：
       1. 记录原始值，测试后恢复
       2. 重新获取数据，测试后覆盖恢复
       
       恢复时机：
       - 每个测试用例后立即恢复
       
用户输入: 1
Agent: ✅ 已配置数据恢复
       将在测试前记录原始值，测试后自动恢复
```

#### 询问 4：对其他测试的影响

> 4️⃣ **是否会影响其他测试用例？**
> 
> ```
> PUT /api/users/{id}
> 
> 编辑用户信息可能影响：
> - 依赖该用户数据的其他测试
> - 用户相关的业务流程测试
> 
> A. 可能影响 → 建议调整执行顺序或添加依赖声明
> B. 无影响
> ```

**依赖声明配置**：
```
Agent: 请选择依赖处理方式：
       
       1. 声明前置依赖（其他测试需在此测试前执行）
       2. 声明后置依赖（其他测试需在此测试后执行）
       3. 独立执行（不影响其他测试）
       
用户输入: 1
Agent: 请输入依赖的测试用例或链路名称：
用户输入: 用户查询流程, 用户权限验证流程
Agent: ✅ 已声明前置依赖
       「用户查询流程」「用户权限验证流程」需在此编辑测试前执行
```

### 2.3 编辑接口配置示例

```json
{
  "apiId": 4,
  "method": "PUT",
  "path": "/api/users/{id}",
  "description": "更新用户信息",
  "handling": {
    "dataSource": {
      "type": "create_temp",
      "createApi": "POST /api/users",
      "cleanupAfter": true
    },
    "validation": {
      "modifiedFields": true,
      "unmodifiedFields": true,
      "timestamp": true,
      "relatedData": false
    },
    "restore": {
      "enabled": true,
      "method": "record_and_restore",
      "timing": "after_each"
    },
    "dependencies": {
      "before": ["用户查询流程", "用户权限验证流程"],
      "after": []
    }
  }
}
```

---

## 三、删除接口 (DELETE) 处理策略

### 3.1 自动检测触发

当业务链路中包含 DELETE 类型接口时，自动触发以下询问：

> 🗑️ **删除接口执行策略**
> 
> 检测到删除类型接口：
> - `DELETE /api/orders/{id}`
> 
> ⚠️ 警告：删除操作不可逆，请选择执行策略。

### 3.2 关键询问项

#### 询问：执行方式选择

> **请选择执行方式：**
> 
> ```
> DELETE /api/orders/{id}
> 
> A. 🎭 Mock 模拟（推荐）
>    - 不真实执行删除请求
>    - Mock 返回成功响应
>    - 验证请求参数正确性
>    适用场景：接口开发阶段、危险操作测试
> 
> B. 🔄 软删除验证
>    - 验证数据标记为"已删除"状态
>    - 数据仍存在但不可见
>    - 可通过管理员接口恢复
>    适用场景：支持软删除的系统
> 
> C. 📝 创建后删除（安全真实执行）
>    - 先创建临时测试数据
>    - 执行删除该临时数据
>    - 确保不删除有价值数据
>    适用场景：需要验证真实删除流程
> 
> D. ⚡ 真实执行（谨慎使用）
>    - 直接执行删除操作
>    - 需要明确确认
>    适用场景：特殊情况，需审批
> ```

### 3.3 各执行方式的详细配置

#### 方式 A：Mock 模拟

```
Agent: Mock 模拟配置：
       
       Mock 响应：
       {
         "status": 200,
         "message": "删除成功"
       }
       
       验证项：
       - [ ] 请求路径正确
       - [ ] 请求方法为 DELETE
       - [ ] 认证信息正确
       - [ ] 请求参数格式正确
       
用户输入: 确认
Agent: ✅ 已配置 Mock 模式
       删除请求将被拦截，返回 Mock 响应
```

#### 方式 B：软删除验证

```
Agent: 软删除验证配置：
       
       验证步骤：
       1. 记录删除前的数据状态
       2. 执行删除操作
       3. 验证数据状态变更
       
       验证项：
       - [ ] status 字段变为 "deleted"
       - [ ] deleted_at 字段有值
       - [ ] 数据在正常查询中不可见
       - [ ] 数据在管理员查询中可见
       
       恢复接口（可选）：
       POST /api/admin/orders/{id}/restore
       
用户输入: 确认
Agent: ✅ 已配置软删除验证
       将验证数据标记删除而非物理删除
```

#### 方式 C：创建后删除

```
Agent: 创建后删除配置：
       
       执行流程：
       1. POST /api/orders - 创建临时订单
       2. DELETE /api/orders/{id} - 删除该订单
       3. GET /api/orders/{id} - 验证已删除
       
       临时订单数据：
       - 自动生成测试数据
       - 确保不使用生产数据
       
       验证项：
       - [ ] 删除返回成功
       - [ ] 删除后查询返回 404
       - [ ] 关联数据正确处理
       
用户输入: 确认
Agent: ✅ 已配置创建后删除模式
       将创建临时数据进行删除测试
```

#### 方式 D：真实执行

```
Agent: ⚠️ 真实执行警告
       
       您选择了真实执行删除操作。
       这将永久删除数据，无法恢复。
       
       请确认以下事项：
       - [ ] 确认删除的是测试数据
       - [ ] 确认有数据备份或恢复机制
       - [ ] 确认不影响其他业务流程
       - [ ] 已获得相关审批
       
       请输入 "确认真实删除" 继续：
用户输入: 确认真实删除
Agent: ✅ 已配置真实执行模式
       请谨慎操作，建议在独立测试环境中执行
```

### 3.4 删除接口配置示例

```json
{
  "apiId": 8,
  "method": "DELETE",
  "path": "/api/orders/{id}",
  "description": "删除订单",
  "handling": {
    "executionMode": "create_and_delete",
    "mock": null,
    "softDelete": null,
    "createAndDelete": {
      "createApi": "POST /api/orders",
      "verifyApi": "GET /api/orders/{id}",
      "expectedStatus": 404
    },
    "realDelete": null,
    "validation": {
      "deleteSuccess": true,
      "notFoundAfterDelete": true,
      "relatedDataHandling": true
    },
    "warnings": [
      "确保删除的是测试数据",
      "检查是否有级联删除影响"
    ]
  }
}
```

---

## 四、综合配置示例

一个包含增删改操作的完整业务链路配置：

```json
{
  "flowId": "BF-003",
  "flowName": "用户订单管理流程",
  "apis": [
    {
      "order": 1,
      "method": "POST",
      "path": "/api/auth/login",
      "handling": {
        "extractFields": [
          { "field": "data.token", "alias": "auth_token", "forReuse": true }
        ]
      }
    },
    {
      "order": 2,
      "method": "POST",
      "path": "/api/orders",
      "handling": {
        "extractFields": [
          { "field": "data.order_id", "alias": "order_id", "forReuse": true }
        ],
        "dataReuse": {
          "enabled": true,
          "poolName": "test_orders"
        },
        "cleanup": {
          "enabled": true,
          "timing": "after_suite"
        }
      }
    },
    {
      "order": 3,
      "method": "PUT",
      "path": "/api/orders/{order_id}",
      "handling": {
        "dataSource": {
          "type": "chain",
          "from": "step2"
        },
        "validation": {
          "modifiedFields": true,
          "unmodifiedFields": true
        },
        "restore": {
          "enabled": true,
          "method": "record_and_restore"
        }
      }
    },
    {
      "order": 4,
      "method": "DELETE",
      "path": "/api/orders/{order_id}",
      "handling": {
        "executionMode": "create_and_delete",
        "createAndDelete": {
          "useExisting": "step2"
        }
      }
    }
  ]
}
```

---

## 五、最佳实践建议

### 新增接口 (POST)
1. ✅ 始终考虑数据清理策略
2. ✅ 对于认证相关接口，提取 token 供后续使用
3. ✅ 对于高频创建的数据，考虑复用池
4. ❌ 避免无限制地创建测试数据

### 编辑接口 (PUT/PATCH)
1. ✅ 测试前明确数据来源
2. ✅ 测试后恢复原始状态
3. ✅ 声明测试依赖关系
4. ❌ 避免修改共享测试数据

### 删除接口 (DELETE)
1. ✅ 优先使用 Mock 或软删除验证
2. ✅ 如需真实删除，使用"创建后删除"模式
3. ✅ 确保删除测试数据而非生产数据
4. ❌ 避免直接删除生产或共享数据