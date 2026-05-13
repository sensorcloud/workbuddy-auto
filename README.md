# 算电协同产业互联网平台 (Phase 1 & Phase 2)

> Computing-Electricity Collaborative Industrial Internet Platform

## 项目简介

算电协同产业互联网平台是面向算力与电力协同调度场景的一体化平台，通过电力价格信号智能调度算力交易，实现算电资源的优化配置。

**项目状态**: ✅ Phase 1 & Phase 2 已完成交付，可上线试运行

## 技术栈

### 前端
- **React 18** + **TypeScript**
- **Ant Design 5** - UI 组件库
- **Vite** - 构建工具
- **Zustand** - 状态管理（含 persist 持久化）
- **ECharts** - 数据可视化
- **React Router v6** - 路由

### 后端
- **FastAPI** - Web 框架
- **SQLAlchemy 2.0** - ORM（支持异步）
- **Pydantic V2** - 数据验证
- **JWT (HS256)** - 身份认证
- **PBKDF2-SHA256** - 密码哈希（替代 bcrypt）
- **SQLite** - 数据库（开发环境）

## 项目结构

```
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── components/      # 公共组件
│   │   ├── pages/           # 页面组件
│   │   │   ├── Marketplace/ # 算力市场
│   │   │   ├── Scheduling/  # 调度中心
│   │   │   ├── AssetManagement/ # 资产管理
│   │   │   ├── Monitoring/  # 监控中心
│   │   │   ├── Orders/      # 订单管理
│   │   │   ├── Payment/     # 支付页面
│   │   │   └── UserCenter/  # 用户中心
│   │   ├── router/          # 路由配置
│   │   ├── services/        # API 服务
│   │   ├── store/           # 状态管理
│   │   └── types/           # TypeScript 类型
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/             # 9 个 API 路由模块
│   │   ├── core/            # JWT + 密码哈希配置
│   │   ├── models/          # SQLAlchemy 数据模型
│   │   ├── schemas/         # Pydantic 数据验证
│   │   └── services/        # 9 个业务服务模块
│   ├── requirements.txt
│   └── test_api.py
├── PRD-算电协同平台-Phase1.md              # 产品需求文档 (V2.0)
├── Architecture-算电协同平台-Phase1.md      # 架构设计文档 (V2.0)
├── TestReport-算电协同平台-Phase1.md        # QA 测试报告 (V2.0)
├── VerificationReport-Phase1.md             # 代码验证报告 (V2.0)
├── DeliveryReport-算电协同平台-Phase1.md    # 交付报告 (V2.0)
└── computing-electricity-synergy-trading-report.md # 行业研究报告
```

## 快速启动

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API 文档: http://localhost:8000/docs

### 测试账号

- 用户名: `verifyuser`
- 密码: `Test123456`

## 功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| 算力市场 | 算力资源浏览、筛选、下单 | ✅ Phase 1 完成 |
| 调度中心 | 任务提交、智能报价、策略选择 | ✅ Phase 1 完成 |
| 资产管理 | 资产列表、详情、注册表单、收益中心 | ✅ Phase 2 完善 |
| 订单管理 | 订单列表、详情、支付流程 | ✅ Phase 2 完善 |
| 监控中心 | 实时状态、功耗监控、日志查看 | ✅ Phase 2 完善 |
| 用户中心 | 登录注册、JWT认证、路由守卫 | ✅ Phase 1 完成 |

## API 端点（14个，全部测试通过）

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/assets/` | GET/POST | 资产查询/创建 |
| `/api/v1/marketplace/assets` | GET | 资源市场列表 |
| `/api/v1/orders/` | GET/POST | 订单查询/创建 |
| `/api/v1/orders/{id}/pay` | PUT | 订单支付 |
| `/api/v1/scheduling/quote` | POST | 智能报价 |
| `/api/v1/monitoring/tasks/{id}` | GET | 任务监控 |
| `/api/v1/earnings/summary` | GET | 收益概览 |
| `/api/v1/users/me` | GET | 用户信息 |

## 交付状态

| 检查项 | 状态 |
|--------|------|
| PRD 文档 | ✅ V2.0 已交付 |
| 架构设计 | ✅ V2.0 已交付 |
| 前端代码 | ✅ 100% 完成 |
| 后端 API | ✅ 14个端点全部通过 |
| 前后端集成 | ✅ 端到端验证通过 |
| QA 测试报告 | ✅ V2.0 已完成 |
| 代码验证报告 | ✅ V2.0 已完成 |
| 交付报告 | ✅ V2.0 已完成 |
| Bug 修复 | ✅ 9个 Bug 全部修复 |

**系统已具备上线试运行条件。**

## 团队

| 姓名 | 角色 | 职责 |
|------|------|------|
| **许清楚** | 产品经理 | PRD 文档、需求管理 |
| **高见远** | 架构师 | 架构设计、技术选型 |
| **寇豆码** | 工程师 | 前后端代码开发、Bug修复 |
| **严过关** | QA 工程师 | 测试、回归验证 |
| **齐活林** | 交付总监 | 交付报告、质量把控 |

## License

Proprietary - All rights reserved.
