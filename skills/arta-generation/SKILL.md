---
name: arta-generation
description: ARTA 测试用例生成模块 - 测试用例生成、测试报告、文档导出
license: MIT
metadata:
  author: automation-team
  version: "1.0"
  trigger: "/ARTA-generate-*, /ARTA-export"
allowed-tools: Read Write Bash(python:*)
---

# ARTA 测试用例生成模块

## 角色定义

你专注于测试用例生成和输出，帮助用户：
- 基于业务链路生成测试用例
- 生成测试报告和覆盖率分析
- 导出所有配置和文档
- 生成测试代码框架

## 触发指令

| 指令 | 说明 |
|------|------|
| `/ARTA-generate-cases [链路序号]` | 生成测试用例 |
| `/ARTA-generate-report` | 生成测试报告 |
| `/ARTA-export [输出目录]` | 导出所有文档 |

## 测试用例生成

### 学习模式应用

生成测试用例时，自动应用学习到的模式：

```
生成测试用例流程:
    ↓
读取模式库 (assets/data/patterns.json)
    ↓
应用模式:
├── 测试数据推荐 - 基于历史成功数据
├── 断言模板应用 - 基于同类型 API
└── API 序列优化 - 基于相似链路
    ↓
生成测试代码
    ↓
更新模式统计 (命中率)
```

### `/ARTA-generate-cases`

生成所有业务链路的测试用例：

```
用户输入: /ARTA-generate-cases

Agent: 开始生成测试用例...

🧠 正在加载学习模式...
   - 已加载 5 个 API 序列模式
   - 已加载 8 个断言模板
   - 已加载 3 个数据策略模式

┌──────────────────────────────────────────────────────────────┐
│  📝 测试用例生成                                             │
├──────────────────────────────────────────────────────────────┤
│  正在处理: 用户下单流程 (1/3)                                │
│  ✓ 登录接口测试用例生成完成                                  │
│  ✓ 商品查询测试用例生成完成                                  │
│  ✓ 订单创建测试用例生成完成                                  │
│  ✓ 支付流程测试用例生成完成                                  │
│                                                              │
│  正在处理: 用户注册流程 (2/3)                                │
│  ✓ 注册成功测试用例生成完成                                  │
│  ✓ 注册失败测试用例生成完成                                  │
│                                                              │
│  正在处理: 商品管理流程 (3/3)                                │
│  ✓ 商品CRUD测试用例生成完成                                  │
└──────────────────────────────────────────────────────────────┘

✅ 测试用例生成完成！

生成统计:
- 测试用例文件: 3 个
- 测试用例总数: 24 个
- 覆盖 API: 15 个
- 覆盖率估算: 85%

输出文件:
- tests/flows/user_order_flow.test.ts
- tests/flows/user_register_flow.test.ts
- tests/flows/product_management_flow.test.ts
```

### 指定链路生成

```
用户输入: /ARTA-generate-cases 1

Agent: 为「用户下单流程」生成测试用例...

┌──────────────────────────────────────────────────────────────┐
│  📝 测试用例生成 - 用户下单流程                              │
├──────────────────────────────────────────────────────────────┤
│  API 数量: 6                                                 │
│  生成用例: 12 个                                             │
│  输出文件: tests/flows/user_order_flow.test.ts               │
│                                                              │
│  用例列表:                                                   │
│  1. 登录成功_正确凭证                                        │
│  2. 登录失败_密码错误                                        │
│  3. 商品列表查询_默认分页                                    │
│  4. 商品详情查询_有效ID                                      │
│  5. 添加购物车_正常流程                                      │
│  6. 创建订单_完整流程                                        │
│  7. 创建订单_库存不足                                        │
│  8. 支付成功_微信支付                                        │
│  9. 支付成功_支付宝支付                                      │
│  10. 支付失败_余额不足                                       │
│  11. 订单状态流转验证                                        │
│  12. 完整流程_端到端测试                                     │
└──────────────────────────────────────────────────────────────┘
```

## 测试用例格式

### 生成的测试用例示例

```typescript
// tests/flows/user_order_flow.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { httpClient } from '../helpers/httpClient';

describe('用户下单流程', () => {
  let authToken: string;
  let productId: string;
  let orderId: string;

  beforeAll(async () => {
    // 测试数据准备
  });

  afterAll(async () => {
    // 清理测试数据
  });

  describe('POST /api/auth/login', () => {
    it('登录成功_正确凭证', async () => {
      const response = await httpClient.post('/api/auth/login', {
        username: 'testuser001',
        password: 'Test@123456'
      });

      expect(response.status).toBe(200);
      expect(response.data.token).toBeDefined();
      expect(response.data.user.username).toBe('testuser001');
      
      authToken = response.data.token;
    });

    it('登录失败_密码错误', async () => {
      const response = await httpClient.post('/api/auth/login', {
        username: 'testuser001',
        password: 'wrongpassword'
      });

      expect(response.status).toBe(401);
      expect(response.data.error).toBe('INVALID_CREDENTIALS');
    });
  });

  describe('POST /api/orders', () => {
    it('创建订单_完整流程', async () => {
      const response = await httpClient.post('/api/orders', {
        productId: productId,
        quantity: 1
      }, {
        headers: { Authorization: `Bearer ${authToken}` }
      });

      expect(response.status).toBe(201);
      expect(response.data.orderId).toBeDefined();
      expect(response.data.status).toBe('pending');
      
      orderId = response.data.orderId;
    });
  });
});
```

## 测试报告生成

### `/ARTA-generate-report`

```
用户输入: /ARTA-generate-report

Agent: 生成测试报告...

┌──────────────────────────────────────────────────────────────┐
│  📊 ARTA 测试报告                                            │
│  生成时间: 2026-03-11 21:00:00                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  📋 项目概况                                                 │
│  ├── 项目名称: my-api-project                                │
│  ├── 框架类型: Express                                       │
│  └── 分析时间: 2026-03-11                                    │
│                                                              │
│  📊 API 统计                                                 │
│  ├── 总计: 15 个                                             │
│  ├── GET: 8 个                                               │
│  ├── POST: 5 个                                              │
│  ├── PUT: 1 个                                               │
│  └── DELETE: 1 个                                            │
│                                                              │
│  🔗 业务链路统计                                             │
│  ├── 总计: 3 条                                              │
│  ├── 已完成: 2 条                                            │
│  └── 草稿: 1 条                                              │
│                                                              │
│  ✅ 测试覆盖                                                 │
│  ├── 已覆盖 API: 12 个 (80%)                                 │
│  ├── 未覆盖 API: 3 个                                        │
│  │   ├── GET /api/settings                                  │
│  │   ├── POST /api/feedback                                 │
│  │   └── DELETE /api/cache                                  │
│  └── 建议优先覆盖: /api/settings (核心配置接口)              │
│                                                              │
│  📝 测试用例                                                 │
│  ├── 总计: 24 个                                             │
│  ├── 正向用例: 15 个                                         │
│  ├── 异常用例: 7 个                                          │
│  └── 边界用例: 2 个                                          │
│                                                              │
│  🎯 质量评估                                                 │
│  ├── API 覆盖率: ████████░░ 80%                              │
│  ├── 链路覆盖率: ██████████ 100%                             │
│  ├── 测试完整性: ███████░░░ 70%                              │
│  └── 总体评分: B+ (良好)                                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘

报告已保存到: reports/test_report_20260311.md
```

## 文档导出

### `/ARTA-export`

```
用户输入: /ARTA-export

Agent: 导出所有配置和文档...

┌──────────────────────────────────────────────────────────────┐
│  📦 导出完成                                                 │
├──────────────────────────────────────────────────────────────┤
│  导出目录: ./arta-export-20260311/                           │
│                                                              │
│  📁 配置文件:                                                │
│  ├── project_config.json                                     │
│  ├── api_inventory.json                                      │
│  ├── business_flow.json                                      │
│  ├── data_strategy.json                                      │
│  └── testpoint_template.json                                 │
│                                                              │
│  📁 测试用例:                                                │
│  ├── tests/flows/user_order_flow.test.ts                     │
│  ├── tests/flows/user_register_flow.test.ts                  │
│  └── tests/flows/product_management_flow.test.ts             │
│                                                              │
│  📁 报告文档:                                                │
│  ├── reports/test_report.md                                  │
│  └── reports/api_analysis.md                                 │
│                                                              │
│  📁 流程图:                                                  │
│  └── flow_diagrams/order_flow.md                             │
│                                                              │
│  总计: 12 个文件                                             │
└──────────────────────────────────────────────────────────────┘
```

### 指定输出目录

```
/ARTA-export ./my-output
```

## 测试框架支持

| 框架 | 语言 | 文件格式 |
|------|------|----------|
| Jest | JavaScript/TypeScript | .test.ts |
| Vitest | JavaScript/TypeScript | .test.ts |
| Mocha | JavaScript/TypeScript | .spec.ts |
| Pytest | Python | test_*.py |
| JUnit | Java | *Test.java |
| Go testing | Go | *_test.go |

## 数据存储

生成的测试用例保存在 `tests/` 目录下：

```
tests/
├── flows/                    # 业务流程测试
│   ├── user_order_flow.test.ts
│   └── user_register_flow.test.ts
├── api/                      # 单接口测试
│   ├── auth.test.ts
│   └── users.test.ts
├── helpers/                  # 测试辅助工具
│   └── httpClient.ts
└── fixtures/                 # 测试数据
    └── testData.json
```

## 报告目录结构

```
reports/
├── test_report.md            # 主测试报告
├── api_analysis.md           # API 分析报告
├── coverage/                 # 覆盖率报告
│   └── coverage.html
└── history/                  # 历史报告
    └── report_20260310.md
```

## 相关模块

- [arta-core](../arta-core/SKILL.md) - 核心模块
- [arta-flow](../arta-flow/SKILL.md) - 业务链路记录
- [arta-testpoint](../arta-testpoint/SKILL.md) - 测试点处理

## 参考文档

详细说明见：
- [references/COMMAND_REFERENCE.md](../../references/COMMAND_REFERENCE.md) 的输出指令部分
- [references/CRUD_HANDLING_GUIDE.md](../../references/CRUD_HANDLING_GUIDE.md)
