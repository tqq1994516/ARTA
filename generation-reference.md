# 测试生成详细参考

本文档是 ARTA 测试用例生成的详细参考，仅在需要深入了解时阅读。

## 各框架代码模板

### Jest / Vitest (TypeScript)

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import axios from 'axios';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const http = axios.create({ baseURL: BASE_URL });

describe('{链路名称}', () => {
  const ctx: Record<string, any> = {};

  afterAll(async () => {
    // 清理: DELETE 创建的测试数据
    if (ctx.orderId) {
      await http.delete(`/api/orders/${ctx.orderId}`, {
        headers: { Authorization: `Bearer ${ctx.token}` }
      });
    }
  });

  it('Step 1: 用户登录', async () => {
    const res = await http.post('/api/auth/login', {
      username: 'testuser001',
      password: 'Test@123456'
    });
    expect(res.status).toBe(200);
    expect(res.data.data.token).toBeDefined();
    ctx.token = res.data.data.token;
  });

  it('Step 2: 查询商品列表', async () => {
    const res = await http.get('/api/products', {
      headers: { Authorization: `Bearer ${ctx.token}` },
      params: { page: 1, size: 10 }
    });
    expect(res.status).toBe(200);
    expect(res.data.data.list).toBeInstanceOf(Array);
    expect(res.data.data.list.length).toBeGreaterThan(0);
    ctx.productId = res.data.data.list[0].id;
  });

  it('Step 3: 创建订单', async () => {
    const res = await http.post('/api/orders', {
      productId: ctx.productId,
      quantity: 1
    }, {
      headers: { Authorization: `Bearer ${ctx.token}` }
    });
    expect(res.status).toBe(201);
    expect(res.data.data.orderId).toBeDefined();
    expect(res.data.data.status).toBe('pending');
    ctx.orderId = res.data.data.orderId;
  });
});
```

### Pytest (Python)

```python
import pytest
import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

class TestUserOrderFlow:
    """用户下单流程"""

    ctx = {}

    @classmethod
    def setup_class(cls):
        """测试环境准备"""
        pass

    @classmethod
    def teardown_class(cls):
        """清理测试数据"""
        if cls.ctx.get("order_id"):
            requests.delete(
                f"{BASE_URL}/api/orders/{cls.ctx['order_id']}",
                headers={"Authorization": f"Bearer {cls.ctx['token']}"}
            )

    def test_step1_login(self):
        """Step 1: 用户登录"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "testuser001",
            "password": "Test@123456"
        })
        assert res.status_code == 200
        data = res.json()
        assert "token" in data["data"]
        self.__class__.ctx["token"] = data["data"]["token"]

    def test_step2_list_products(self):
        """Step 2: 查询商品列表"""
        res = requests.get(f"{BASE_URL}/api/products", 
            headers={"Authorization": f"Bearer {self.ctx['token']}"},
            params={"page": 1, "size": 10}
        )
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data["data"]["list"], list)
        assert len(data["data"]["list"]) > 0
        self.__class__.ctx["product_id"] = data["data"]["list"][0]["id"]

    def test_step3_create_order(self):
        """Step 3: 创建订单"""
        res = requests.post(f"{BASE_URL}/api/orders", 
            headers={"Authorization": f"Bearer {self.ctx['token']}"},
            json={
                "productId": self.ctx["product_id"],
                "quantity": 1
            }
        )
        assert res.status_code == 201
        data = res.json()
        assert "orderId" in data["data"]
        assert data["data"]["status"] == "pending"
        self.__class__.ctx["order_id"] = data["data"]["orderId"]
```

### JUnit 5 (Java)

```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.net.http.*;
import com.google.gson.JsonObject;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class UserOrderFlowTest {
    
    static String BASE_URL = System.getenv().getOrDefault("BASE_URL", "http://localhost:3000");
    static HttpClient client = HttpClient.newHttpClient();
    static String token;
    static String orderId;

    @Test @Order(1) @DisplayName("Step 1: 用户登录")
    void testLogin() throws Exception {
        var body = """
            {"username":"testuser001","password":"Test@123456"}
            """;
        var req = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/api/auth/login"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(body))
            .build();
        var res = client.send(req, HttpResponse.BodyHandlers.ofString());
        
        assertEquals(200, res.statusCode());
        // 解析 token 并保存
    }

    @AfterAll
    static void cleanup() throws Exception {
        // 删除测试订单
    }
}
```

### Go testing

```go
package flows_test

import (
    "encoding/json"
    "net/http"
    "os"
    "testing"
    "strings"
)

var baseURL = getEnv("BASE_URL", "http://localhost:3000")
var ctx = map[string]string{}

func getEnv(key, fallback string) string {
    if v := os.Getenv(key); v != "" {
        return v
    }
    return fallback
}

func TestUserOrderFlow(t *testing.T) {
    t.Cleanup(func() {
        // 清理测试数据
    })

    t.Run("Step1_Login", func(t *testing.T) {
        body := `{"username":"testuser001","password":"Test@123456"}`
        resp, err := http.Post(baseURL+"/api/auth/login", "application/json", strings.NewReader(body))
        if err != nil {
            t.Fatal(err)
        }
        defer resp.Body.Close()
        
        if resp.StatusCode != 200 {
            t.Fatalf("expected 200, got %d", resp.StatusCode)
        }
        // 解析 token 并保存到 ctx
    })

    t.Run("Step2_CreateOrder", func(t *testing.T) {
        // ...
    })
}
```

## 生成策略

### 场景覆盖

每个链路默认生成以下场景：

| 场景类型 | 说明 | 数量 |
|----------|------|------|
| 正向流程 | 完整业务链路端到端 | 1 |
| 单步正向 | 每个 API 单独的成功场景 | N (API数量) |
| 关键异常 | 认证失败、资源不存在、参数错误 | 2-4 |

### 异常场景规则

根据 API 特征自动建议异常场景：

| API 特征 | 建议异常场景 |
|----------|-------------|
| 需要认证 | 401 未认证 / token过期 |
| POST 创建 | 400 缺少必填字段 / 409 重复创建 |
| GET 带路径参数 | 404 资源不存在 |
| PUT/PATCH 更新 | 403 无权限 / 404 不存在 |
| DELETE 删除 | 403 无权限 / 404 不存在 |

### 测试文件结构

```
tests/
├── flows/                    # 业务流程测试（链路生成）
│   ├── user_order.test.ts
│   ├── user_register.test.ts
│   └── product_crud.test.ts
├── helpers/                  # 辅助工具（按需生成）
│   └── httpClient.ts
└── fixtures/                 # 测试数据（按需生成）
    └── testData.json
```

## 测试报告格式

`/ARTA-generate` 完成后自动输出统计摘要：

```
ARTA 测试生成报告
=================

项目: my-api-project
框架: Vitest (TypeScript)
生成时间: 2026-03-11 21:00:00

API 覆盖:
  总计: 15 个
  已覆盖: 12 个 (80%)
  未覆盖: GET /api/settings, POST /api/feedback, DELETE /api/cache

测试用例:
  正向用例: 15 个
  异常用例: 7 个
  合计: 22 个

文件清单:
  tests/flows/user_order.test.ts        (12 cases)
  tests/flows/user_register.test.ts     (6 cases)
  tests/flows/product_crud.test.ts      (4 cases)

建议:
  - 为未覆盖的 3 个 API 添加业务链路
  - 商品管理流程链路为 draft 状态，完成后可再次生成
```

## 导出结构

`/ARTA-export` 输出的目录结构：

```
export-{项目名}-{日期}/
├── config/
│   ├── project.json          # 项目配置
│   ├── apis.json             # API 清单
│   └── flows.json            # 业务链路
├── tests/
│   └── flows/                # 测试用例文件
├── reports/
│   └── summary.md            # 生成报告
└── README.md                 # 导出说明
```
