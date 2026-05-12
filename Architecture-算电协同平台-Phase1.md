# 算电协同产业互联网平台 Phase 1 系统架构设计

**文档版本**：V1.0  
**创建日期**：2026-05-11  
**架构师**：高见远（Gao）  
**文档状态**：待评审  

---

## 目录

1. [实现方案 + 框架选型](#一实现方案--框架选型)
2. [文件列表及相对路径](#二文件列表及相对路径)
3. [数据结构和接口](#三数据结构和接口)
4. [程序调用流程](#四程序调用流程)
5. [任务列表](#五任务列表)
6. [依赖包列表](#六依赖包列表)
7. [共享知识](#七共享知识)
8. [待明确事项](#八待明确事项)

---

## 一、实现方案 + 框架选型

### 1.1 技术栈选择

#### 前端技术栈

| 技术项 | 选型 | 版本 | 选型理由 |
|--------|------|------|----------|
| **框架** | React + TypeScript | React 18.2+ / TypeScript 5.3+ | 生态成熟、组件化开发、类型安全 |
| **UI组件库** | Ant Design | 5.12+ | 企业级UI组件、主题定制能力强 |
| **状态管理** | Zustand | 4.4+ | 轻量级、API简洁、TypeScript友好 |
| **图表库** | ECharts | 5.4+ | 图表类型丰富、性能优秀、支持实时更新 |
| **实时通信** | Socket.io-client | 4.7+ | 可靠的WebSocket封装、自动重连 |
| **路由** | React Router | 6.20+ | 标准路由方案 |
| **HTTP客户端** | Axios | 1.6+ | 拦截器机制完善 |
| **构建工具** | Vite | 5.0+ | 快速冷启动、HMR性能优异 |
| **代码规范** | ESLint + Prettier | - | 统一代码风格 |

**备选方案**：Vue 3 + TypeScript + Element Plus（如团队更熟悉Vue生态）

#### 后端技术栈

| 技术项 | 选型 | 版本 | 选型理由 |
|--------|------|------|----------|
| **语言** | Python | 3.11+ | AI生态丰富、快速开发、异步支持好 |
| **Web框架** | FastAPI | 0.109+ | 高性能、自动生成OpenAPI文档、原生异步 |
| **ORM** | SQLAlchemy | 2.0+ | 成熟稳定、支持异步、迁移工具完善 |
| **数据库驱动** | asyncpg | 0.29+ | PostgreSQL高性能异步驱动 |
| **数据验证** | Pydantic v2 | 2.5+ | 高性能数据验证、与FastAPI深度集成 |
| **认证** | python-jose + passlib | - | JWT Token生成与验证、密码哈希 |
| **任务队列** | Celery + Redis | 5.3+ | 成熟的分布式任务队列 |
| **缓存** | Redis (aioredis) | 7.0+ | 高性能缓存、Pub/Sub支持 |
| **时序数据库** | InfluxDB | 2.7+ | 专为时序数据优化、压缩率高 |
| **消息队列** | RabbitMQ | 3.12+ | 可靠的消息传递、支持多种交换模式 |
| **容器编排** | Kubernetes | 1.28+ | 自定义调度器支持、GPU资源调度 |
| **API文档** | Swagger UI (内置) | - | FastAPI自动生成 |

**备选方案**：Node.js + Express.js / Go + Gin（如需要更高并发性能）

#### 数据库技术栈

| 数据库类型 | 选型 | 版本 | 用途 |
|------------|------|------|------|
| **主数据库** | PostgreSQL | 16+ | 存储用户、订单、资产等关系型数据 |
| **缓存数据库** | Redis | 7+ | 会话缓存、热点数据、分布式锁 |
| **时序数据库** | InfluxDB | 2.7+ | 存储监控指标、功耗数据、碳排放数据 |
| **对象存储** | MinIO | RELEASE.2024+ | 存储镜像、数据集、日志文件 |

#### 中间件与基础设施

| 组件 | 选型 | 版本 | 用途 |
|------|------|------|------|
| **API网关** | Kong | 3.5+ | API路由、认证、限流、日志 |
| **服务通信** | RESTful API + gRPC | - | 外部通信用REST、内部服务用gRPC |
| **消息队列** | RabbitMQ | 3.12+ | 异步任务、事件驱动 |
| **监控** | Prometheus + Grafana | 2.48+ / 10.2+ | 指标采集、可视化、告警 |
| **日志** | ELK Stack | 8.11+ | 日志收集、搜索、分析 |
| **链路追踪** | Jaeger | 1.52+ | 分布式追踪、性能分析 |
| **容器运行时** | Docker | 24.0+ | 容器化部署 |
| **CI/CD** | GitLab CI / GitHub Actions | - | 自动化构建、测试、部署 |

### 1.2 架构风格

#### 微服务架构（推荐）

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Web    │  │ Mobile   │  │   API    │  │  Admin   │     │
│  │ Frontend │  │  Web    │  │  Client  │  │  Panel   │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼──────────────┼──────────────┼──────────────┼──────────┘
        │              │              │              │
┌───────┴──────────────┴──────────────┴──────────────┴──────────┐
│                      API 网关层 (Kong)                          │
└───────┬──────────────┬──────────────┬──────────────┬──────────┘
        │              │              │              │
┌───────┴──────────────┴──────────────┴──────────────┴──────────┐
│                      微服务层                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  用户    │  │  资产    │  │  市场    │  │  订单    │     │
│  │ 服务     │  │ 服务     │  │ 服务     │  │ 服务     │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  调度    │  │  支付    │  │  监控    │  │  收益    │     │
│  │ 引擎     │  │ 服务     │  │ 服务     │  │ 服务     │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└───────┬──────────────┬──────────────┬──────────────┬──────────┘
        │              │              │              │
┌───────┴──────────────┴──────────────┴──────────────┴──────────┐
│                      数据层                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ PostgreSQL│  │  Redis   │  │ InfluxDB │  │  MinIO   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

**微服务划分**：

| 服务名 | 职责 | 数据库 |
|--------|------|--------|
| **用户服务** | 用户注册、登录、认证、权限管理 | PostgreSQL |
| **资产服务** | 资产注册、审核、状态管理 | PostgreSQL + Redis |
| **市场服务** | 资源展示、搜索、筛选 | PostgreSQL + Elasticsearch |
| **调度服务** | 智能报价、资源匹配、任务调度 | PostgreSQL + Redis |
| **订单服务** | 订单管理、状态流转 | PostgreSQL |
| **支付服务** | 支付、结算、退款 | PostgreSQL + Redis |
| **监控服务** | 数据采集、实时指标、告警 | InfluxDB + Redis |
| **收益服务** | 收益计算、提现管理 | PostgreSQL |
| **碳足迹服务** | 碳排放计算、报告生成 | PostgreSQL + InfluxDB |

**优势**：
- 独立部署和扩展
- 技术栈灵活选择
- 故障隔离

**挑战**：
- 分布式事务复杂性
- 服务间通信开销
- 运维复杂度增加

#### 备选方案：模块化单体

如团队规模较小（<5人），可先采用模块化单体架构，降低运维复杂度。

```
┌──────────────────────────────────────────────────────┐
│              算电协同平台 (Monolith)                  │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │
│  │ 用户模块│  │ 资产模块│  │ 市场模块│  │ 订单模块│   │
│  └────────┘  └────────┘  └────────┘  └────────┘   │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │
│  │ 调度模块│  │ 支付模块│  │ 监控模块│  │ 收益模块│   │
│  └────────┘  └────────┘  └────────┘  └────────┘   │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │         共享内核 (Shared Kernel)                 │ │
│  │  - 数据库连接池                                 │ │
│  │  - Redis连接池                                  │ │
│  │  - 消息队列客户端                               │ │
│  │  - 日志、监控、配置                             │ │
│  └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

**决策建议**：
- Phase 1：采用**模块化单体**，快速交付
- Phase 2：逐步迁移到**微服务架构**

### 1.3 Kubernetes自定义调度器

由于需要实现"算电协同"调度（考虑电力价格、绿电比例等因素），需要开发Kubernetes自定义调度器。

**调度器架构**：

```
┌─────────────────────────────────────────────────┐
│         自定义调度器 (Custom Scheduler)           │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │        调度队列 (Priority Queue)          │   │
│  └─────────────┬───────────────────────────┘   │
│                ↓                               │
│  ┌─────────────────────────────────────────┐   │
│  │     预选阶段 (Filtering)                 │   │
│  │  - GPU型号匹配                           │   │
│  │  - 可用区匹配                           │   │
│  │  - 电力来源匹配                         │   │
│  └─────────────┬───────────────────────────┘   │
│                ↓                               │
│  ┌─────────────────────────────────────────┐   │
│  │     优选阶段 (Scoring)                   │   │
│  │  - 电价评分 (权重40%)                    │   │
│  │  - 绿电比例评分 (权重30%)                │   │
│  │  - 资源利用率评分 (权重20%)              │   │
│  │  - 网络延迟评分 (权重10%)                │   │
│  └─────────────┬───────────────────────────┘   │
│                ↓                               │
│  ┌─────────────────────────────────────────┐   │
│  │     绑定阶段 (Binding)                  │   │
│  │  - 绑定GPU节点                          │   │
│  │  - 绑定储能单元                         │   │
│  │  - 写入调度决策日志                     │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

**技术实现**：
- 基于Kubernetes Scheduling Framework
- 使用Go语言开发（与K8s保持一致）
- 实现Filter和Score插件接口

---

## 二、文件列表及相对路径

### 2.1 项目整体结构

```
calc-electric-platform/
├── README.md                           # 项目说明文档
├── docker-compose.yml                  # 本地开发环境编排
├── .gitignore                          # Git忽略文件配置
├── .env.example                        # 环境变量示例
├── package.json                        # 前端依赖配置（Monorepo根）
├── pyproject.toml                      # Python项目配置（Poetry）
│
├── frontend/                          # 前端项目
│   ├── package.json                    # 前端依赖配置
│   ├── tsconfig.json                  # TypeScript配置
│   ├── vite.config.ts                 # Vite构建配置
│   ├── .eslintrc.cjs                  # ESLint配置
│   ├── .prettierrc                    # Prettier配置
│   ├── index.html                     # 入口HTML
│   ├── public/                        # 静态资源
│   │   ├── favicon.ico
│   │   ├── logo.png
│   │   └── robots.txt
│   ├── src/
│   │   ├── main.tsx                   # 应用入口
│   │   ├── App.tsx                    # 根组件
│   │   ├── vite-env.d.ts              # Vite类型声明
│   │   │
│   │   ├── assets/                    # 资源文件
│   │   │   ├── styles/
│   │   │   │   ├── global.less        # 全局样式
│   │   │   │   ├── variables.less     # 主题变量
│   │   │   │   └── reset.less         # 样式重置
│   │   │   ├── images/
│   │   │   └── fonts/
│   │   │
│   │   ├── components/                # 通用组件
│   │   │   ├── Layout/                # 布局组件
│   │   │   │   ├── index.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── Charts/                # 图表组件
│   │   │   │   ├── LineChart.tsx
│   │   │   │   ├── BarChart.tsx
│   │   │   │   └── GaugeChart.tsx
│   │   │   ├── Tables/                # 表格组件
│   │   │   │   └── DataTable.tsx
│   │   │   ├── Forms/                 # 表单组件
│   │   │   │   ├── AssetForm.tsx
│   │   │   │   └── OrderForm.tsx
│   │   │   ├── Common/                # 通用UI组件
│   │   │   │   ├── Loading.tsx
│   │   │   │   ├── ErrorBoundary.tsx
│   │   │   │   ├── EmptyState.tsx
│   │   │   │   └── ConfirmModal.tsx
│   │   │   └── index.ts               # 组件导出
│   │   │
│   │   ├── pages/                     # 页面组件
│   │   │   ├── Home/                  # 首页
│   │   │   │   ├── index.tsx
│   │   │   │   └── styles.module.less
│   │   │   ├── Marketplace/           # 资源市场
│   │   │   │   ├── index.tsx
│   │   │   │   ├── AssetCard.tsx
│   │   │   │   ├── AssetDetail.tsx
│   │   │   │   ├── FilterPanel.tsx
│   │   │   │   └── styles.module.less
│   │   │   ├── Scheduling/            # 智能调度
│   │   │   │   ├── index.tsx
│   │   │   │   ├── TaskSubmit.tsx
│   │   │   │   ├── StrategySelect.tsx
│   │   │   │   ├── QuoteDisplay.tsx
│   │   │   │   └── styles.module.less
│   │   │   ├── Monitoring/            # 任务监控
│   │   │   │   ├── index.tsx
│   │   │   │   ├── PowerChart.tsx
│   │   │   │   ├── CarbonChart.tsx
│   │   │   │   ├── TaskLog.tsx
│   │   │   │   └── styles.module.less
│   │   │   ├── AssetManagement/       # 资产管理
│   │   │   │   ├── index.tsx
│   │   │   │   ├── AssetList.tsx
│   │   │   │   ├── AssetRegister.tsx
│   │   │   │   ├── EarningsPanel.tsx
│   │   │   │   └── styles.module.less
│   │   │   ├── Orders/                # 订单管理
│   │   │   │   ├── index.tsx
│   │   │   │   ├── OrderList.tsx
│   │   │   │   ├── OrderDetail.tsx
│   │   │   │   └── styles.module.less
│   │   │   ├── Payment/               # 支付页面
│   │   │   │   ├── index.tsx
│   │   │   │   ├── Checkout.tsx
│   │   │   │   └── styles.module.less
│   │   │   ├── UserCenter/            # 用户中心
│   │   │   │   ├── index.tsx
│   │   │   │   ├── Profile.tsx
│   │   │   │   ├── Auth.tsx
│   │   │   │   └── styles.module.less
│   │   │   └── NotFound/              # 404页面
│   │   │       └── index.tsx
│   │   │
│   │   ├── hooks/                     # 自定义Hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useWebSocket.ts
│   │   │   ├── usePagination.ts
│   │   │   └── useECharts.ts
│   │   │
│   │   ├── services/                  # API服务层
│   │   │   ├── api.ts                 # Axios实例配置
│   │   │   ├── auth.service.ts
│   │   │   ├── asset.service.ts
│   │   │   ├── marketplace.service.ts
│   │   │   ├── scheduling.service.ts
│   │   │   ├── order.service.ts
│   │   │   ├── payment.service.ts
│   │   │   └── monitoring.service.ts
│   │   │
│   │   ├── store/                     # 状态管理(Zustand)
│   │   │   ├── index.ts               # Store入口
│   │   │   ├── authStore.ts           # 认证状态
│   │   │   ├── assetStore.ts          # 资产状态
│   │   │   ├── orderStore.ts          # 订单状态
│   │   │   └── uiStore.ts             # UI状态
│   │   │
│   │   ├── types/                     # TypeScript类型定义
│   │   │   ├── index.ts
│   │   │   ├── auth.types.ts
│   │   │   ├── asset.types.ts
│   │   │   ├── order.types.ts
│   │   │   └── api.types.ts
│   │   │
│   │   ├── utils/                     # 工具函数
│   │   │   ├── request.ts             # 请求封装
│   │   │   ├── format.ts              # 格式化函数
│   │   │   ├── storage.ts             # 本地存储封装
│   │   │   ├── constants.ts           # 常量定义
│   │   │   └── validators.ts          # 表单验证
│   │   │
│   │   └── router/                    # 路由配置
│   │       ├── index.tsx              # 路由入口
│   │       ├── routes.tsx             # 路由定义
│   │       └── guards.tsx             # 路由守卫
│   │
│   └── tests/                         # 前端测试
│       ├── unit/
│       ├── integration/
│       └── e2e/
│
├── backend/                           # 后端项目（模块化单体）
│   ├── pyproject.toml                 # Poetry配置
│   ├── poetry.lock                    # 依赖锁定文件
│   ├── .env                           # 环境变量（不提交）
│   ├── alembic.ini                    # Alembic配置
│   ├── Dockerfile                     # 后端Docker镜像
│   │
│   ├── app/                           # 应用主目录
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI应用入口
│   │   ├── config.py                  # 配置管理
│   │   ├── dependencies.py             # 依赖注入
│   │   │
│   │   ├── api/                       # API路由层
│   │   │   ├── __init__.py
│   │   │   ├── v1/                     # API版本v1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py           # 认证路由
│   │   │   │   ├── users.py          # 用户路由
│   │   │   │   ├── assets.py         # 资产路由
│   │   │   │   ├── marketplace.py    # 市场路由
│   │   │   │   ├── scheduling.py     # 调度路由
│   │   │   │   ├── orders.py         # 订单路由
│   │   │   │   ├── payments.py       # 支付路由
│   │   │   │   ├── monitoring.py     # 监控路由
│   │   │   │   └── earnings.py       # 收益路由
│   │   │   └── deps.py               # API依赖
│   │   │
│   │   ├── models/                    # 数据模型层（ORM）
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # 基础模型类
│   │   │   ├── user.py               # 用户模型
│   │   │   ├── asset.py              # 资产模型
│   │   │   ├── order.py              # 订单模型
│   │   │   ├── task.py               # 任务模型
│   │   │   ├── payment.py            # 支付模型
│   │   │   ├── carbon_report.py      # 碳报告模型
│   │   │   └── monitoring.py         # 监控数据模型
│   │   │
│   │   ├── schemas/                   # Pydantic验证模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── asset.py
│   │   │   ├── order.py
│   │   │   ├── task.py
│   │   │   ├── payment.py
│   │   │   └── response.py           # 统一响应格式
│   │   │
│   │   ├── services/                  # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py        # 认证服务
│   │   │   ├── user_service.py        # 用户服务
│   │   │   ├── asset_service.py       # 资产服务
│   │   │   ├── marketplace_service.py # 市场服务
│   │   │   ├── scheduling_service.py  # 调度服务
│   │   │   ├── order_service.py       # 订单服务
│   │   │   ├── payment_service.py     # 支付服务
│   │   │   ├── monitoring_service.py  # 监控服务
│   │   │   ├── earnings_service.py    # 收益服务
│   │   │   └── carbon_service.py      # 碳足迹服务
│   │   │
│   │   ├── core/                      # 核心功能模块
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # 安全工具（JWT、密码哈希）
│   │   │   ├── config.py              # 配置加载
│   │   │   ├── logging.py             # 日志配置
│   │   │   └── exceptions.py          # 自定义异常
│   │   │
│   │   ├── db/                        # 数据库相关
│   │   │   ├── __init__.py
│   │   │   ├── session.py             # 数据库会话管理
│   │   │   ├── base.py                # SQLAlchemy Base
│   │   │   ├── init_db.py             # 数据库初始化
│   │   │   └── migrations/            # Alembic迁移脚本
│   │   │       ├── env.py
│   │   │       ├── script.py.mako
│   │   │       └── versions/
│   │   │
│   │   ├── redis/                     # Redis相关
│   │   │   ├── __init__.py
│   │   │   └── client.py              # Redis客户端
│   │   │
│   │   ├── queue/                     # 消息队列
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py          # Celery应用配置
│   │   │   ├── tasks.py               # 异步任务定义
│   │   │   └── workers.py             # Worker进程
│   │   │
│   │   ├── scheduler/                 # K8s调度器
│   │   │   ├── __init__.py
│   │   │   ├── custom_scheduler.py    # 自定义调度器主程序
│   │   │   ├── filters.py             # 预选插件
│   │   │   ├── scorers.py             # 优选插件
│   │   │   └── binder.py              # 绑定插件
│   │   │
│   │   ├── monitoring/                # 监控相关
│   │   │   ├── __init__.py
│   │   │   ├── collector.py           # 数据采集
│   │   │   ├── influxdb_client.py     # InfluxDB客户端
│   │   │   └── websocket.py           # WebSocket推送
│   │   │
│   │   ├── integrations/              # 第三方集成
│   │   │   ├── __init__.py
│   │   │   ├── alipay.py              # 支付宝集成
│   │   │   ├── wechat_pay.py          # 微信支付集成
│   │   │   └── carbon_factor.py       # 碳排放因子API
│   │   │
│   │   └── utils/                     # 工具函数
│   │       ├── __init__.py
│   │       ├── datetime_utils.py
│   │       ├── validators.py
│   │       └── id_generator.py
│   │
│   ├── tests/                         # 后端测试
│   │   ├── __init__.py
│   │   ├── conftest.py                # Pytest配置
│   │   ├── unit/                      # 单元测试
│   │   │   ├── test_auth.py
│   │   │   ├── test_asset.py
│   │   │   └── test_scheduling.py
│   │   ├── integration/                # 集成测试
│   │   │   ├── test_api.py
│   │   │   └── test_db.py
│   │   └── fixtures/                  # 测试数据
│   │       └── users.json
│   │
│   └── scripts/                       # 脚本工具
│       ├── seed_data.py               # 种子数据
│       ├── backup_db.py               # 数据库备份
│       └── migrate_legacy.py          # 数据迁移
│
├── infra/                             # 基础设施配置
│   ├── docker/                        # Docker配置
│   │   ├── docker-compose.dev.yml     # 开发环境
│   │   ├── docker-compose.prod.yml    # 生产环境
│   │   ├── postgres/
│   │   │   └── init.sql              # PostgreSQL初始化
│   │   ├── redis/
│   │   │   └── redis.conf            # Redis配置
│   │   ├── influxdb/
│   │   │   └── init.iql              # InfluxDB初始化
│   │   └── rabbitmq/
│   │       └── rabbitmq.conf         # RabbitMQ配置
│   │
│   ├── kubernetes/                    # K8s配置
│   │   ├── namespaces/
│   │   │   └── calc-electric.yaml
│   │   ├── deployments/
│   │   │   ├── backend.yaml
│   │   │   ├── frontend.yaml
│   │   │   └── scheduler.yaml
│   │   ├── services/
│   │   │   ├── backend-svc.yaml
│   │   │   └── frontend-svc.yaml
│   │   ├── configmaps/
│   │   │   └── app-config.yaml
│   │   ├── secrets/
│   │   │   └── app-secrets.yaml
│   │   └── ingress/
│   │       └── ingress.yaml
│   │
│   ├── monitoring/                    # 监控配置
│   │   ├── prometheus/
│   │   │   ├── prometheus.yml
│   │   │   └── alerts.yml
│   │   ├── grafana/
│   │   │   ├── dashboards/
│   │   │   │   ├── system-metrics.json
│   │   │   │   ├── business-metrics.json
│   │   │   │   └── gpu-monitoring.json
│   │   │   └── datasources/
│   │   │       └── prometheus.yml
│   │   └── elk/
│   │       ├── elasticsearch/
│   │       ├── logstash/
│   │       │   └── logstash.conf
│   │       └── kibana/
│   │
│   └── ci-cd/                         # CI/CD配置
│       ├── .gitlab-ci.yml             # GitLab CI配置
│       ├── github-actions.yml         # GitHub Actions配置
│       └── helm/                      # Helm Charts
│           └── calc-electric/
│
├── docs/                              # 文档
│   ├── README.md                      # 文档入口
│   ├── architecture/                  # 架构文档
│   │   └── (本文件)
│   ├── api/                           # API文档
│   │   ├── openapi.yaml               # OpenAPI规范
│   │   └── examples/                 # API示例
│   ├── database/                      # 数据库文档
│   │   ├── schema.md                  # Schema设计
│   │   └── migrations.md              # 迁移指南
│   ├── deployment/                    # 部署文档
│   │   ├── deploy-guide.md
│   │   └── troubleshooting.md
│   └── development/                   # 开发文档
│       ├── setup.md                   # 环境搭建
│       ├── coding-style.md            # 编码规范
│       └── contrib.md                 # 贡献指南
│
└── scripts/                           # 根目录脚本
    ├── setup.sh                       # 环境初始化
    ├── start-dev.sh                   # 启动开发环境
    ├── start-prod.sh                  # 启动生产环境
    └── backup.sh                      # 备份脚本
```

### 2.2 关键文件说明

| 文件路径 | 职责说明 |
|----------|----------|
| `backend/app/main.py` | FastAPI应用工厂，注册路由、中间件、异常处理 |
| `backend/app/core/security.py` | JWT Token生成/验证、密码哈希/验证 |
| `backend/app/db/session.py` | 异步数据库会话管理、连接池配置 |
| `backend/app/scheduler/custom_scheduler.go` | K8s自定义调度器（Go实现） |
| `frontend/src/services/api.ts` | Axios实例、请求/响应拦截器 |
| `frontend/src/store/authStore.ts` | 认证状态管理（登录、Token刷新） |
| `infra/docker/docker-compose.dev.yml` | 本地开发环境一站式启动 |
| `infra/kubernetes/deployments/backend.yaml` | 后端服务K8s部署配置 |

---

## 三、数据结构和接口

### 3.1 核心数据模型（Mermaid类图）

```mermaid
classDiagram
    class User {
        +UUID id
        +String email
        +String phone
        +String password_hash
        +String real_name
        +String id_card_hash
        +Enum role
        +Boolean is_verified
        +Datetime created_at
        +Datetime updated_at
        +register()
        +login()
        +verify_identity()
    }
    
    class Asset {
        +UUID id
        +UUID owner_id
        +Enum type
        +JSONB spec
        +JSONB energy_profile
        +JSONB pricing
        +Enum status
        +JSONB location
        +Datetime created_at
        +Datetime updated_at
        +register()
        +update_status()
        +calculate_price()
    }
    
    class Order {
        +UUID id
        +UUID user_id
        +Enum task_type
        +Enum strategy
        +Float estimated_duration
        +JSONB quotes
        +JSONB selected_quote
        +Enum status
        +JSONB payment
        +JSONB execution
        +JSONB carbon_report
        +Datetime created_at
        +Datetime updated_at
        +create()
        +pay()
        +cancel()
        +complete()
    }
    
    class Task {
        +UUID id
        +UUID order_id
        +UUID asset_id
        +String container_image
        +String dataset_location
        +Enum status
        +Datetime started_at
        +Datetime finished_at
        +JSONB real_time_metrics
        +submit()
        +start()
        +monitor()
        +complete()
    }
    
    class Payment {
        +UUID id
        +UUID order_id
        +UUID user_id
        +Float amount
        +Enum method
        +Enum status
        +String transaction_id
        +Datetime paid_at
        +Datetime created_at
        +pay()
        +refund()
        +check_status()
    }
    
    class CarbonReport {
        +UUID id
        +UUID order_id
        +UUID task_id
        +Float total_power_kwh
        +Float total_carbon_kg
        +Float carbon_saved_kg
        +String report_url
        +Datetime generated_at
        +calculate()
        +generate_pdf()
        +upload_to_minio()
    }
    
    class Earnings {
        +UUID id
        +UUID provider_id
        +UUID order_id
        +Float amount
        +Float platform_fee
        +Float provider_income
        +Enum status
        +Datetime created_at
        +calculate()
        +withdraw()
    }
    
    User "1" --> "many" Asset : owns
    User "1" --> "many" Order : places
    User "1" --> "many" Payment : makes
    User "1" --> "many" Earnings : earns
    Asset "1" --> "many" Task : runs
    Order "1" --> "1" Payment : has
    Order "1" --> "many" Task : contains
    Order "1" --> "1" CarbonReport : generates
    Task "1" --> "1" CarbonReport : produces
    Order "1" --> "1" Earnings : creates
```

### 3.2 数据库表结构（PostgreSQL）

#### users 表

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100),
    id_card_hash VARCHAR(255),  -- AES-256加密
    role VARCHAR(20) NOT NULL DEFAULT 'consumer',  -- consumer/provider/admin
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    balance DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
```

#### assets 表

```sql
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR(20) NOT NULL,  -- compute/storage/solar/grid
    spec JSONB NOT NULL,  -- GPU型号、显存、CPU、内存等
    energy_profile JSONB NOT NULL,  -- 电价、碳因子、PUE、电力来源
    pricing JSONB NOT NULL,  -- 算力单价、储能价格、是否竞价等
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/online/offline/maintenance
    location JSONB,  -- 区域、可用区、数据中心ID
    audit_status VARCHAR(20) DEFAULT 'pending',  -- pending/approved/rejected
    audit_comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_assets_owner ON assets(owner_id);
CREATE INDEX idx_assets_type ON assets(type);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_assets_audit ON assets(audit_status);
```

#### orders 表

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    task_type VARCHAR(20) NOT NULL,  -- inference/training/render
    strategy VARCHAR(20) NOT NULL,  -- cheapest/fastest/greenest/custom
    estimated_duration_hours FLOAT,
    quotes JSONB,  -- 报价列表
    selected_quote JSONB,  -- 用户选择的报价
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/paid/running/completed/failed/cancelled
    payment_id UUID REFERENCES payments(id),
    carbon_report_id UUID REFERENCES carbon_reports(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created ON orders(created_at);
```

#### tasks 表

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id),
    asset_id UUID NOT NULL REFERENCES assets(id),
    container_image VARCHAR(255) NOT NULL,
    dataset_location TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/running/completed/failed/cancelled
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    real_time_metrics JSONB,  -- 实时指标（功耗、碳排放等）
    checkpoint_path TEXT,  -- 检查点路径（用于中断恢复）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tasks_order ON tasks(order_id);
CREATE INDEX idx_tasks_asset ON tasks(asset_id);
CREATE INDEX idx_tasks_status ON tasks(status);
```

#### payments 表

```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id),
    user_id UUID NOT NULL REFERENCES users(id),
    amount DECIMAL(12, 2) NOT NULL,
    method VARCHAR(20) NOT NULL,  -- balance/alipay/wechat/bank_transfer
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/success/failed/refunded
    transaction_id VARCHAR(255),  -- 第三方交易ID
    paid_at TIMESTAMP WITH TIME ZONE,
    refund_amount DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_payments_order ON payments(order_id);
CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
```

#### carbon_reports 表

```sql
CREATE TABLE carbon_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id),
    task_id UUID REFERENCES tasks(id),
    total_power_kwh DECIMAL(12, 4),
    total_carbon_kg DECIMAL(12, 4),
    carbon_saved_kg DECIMAL(12, 4),
    report_url TEXT,  -- MinIO存储路径
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_carbon_reports_order ON carbon_reports(order_id);
```

#### earnings 表

```sql
CREATE TABLE earnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES users(id),
    order_id UUID NOT NULL REFERENCES orders(id),
    asset_id UUID NOT NULL REFERENCES assets(id),
    amount DECIMAL(12, 2) NOT NULL,  -- 订单总金额
    platform_fee DECIMAL(12, 2) NOT NULL,  -- 平台服务费（10%）
    provider_income DECIMAL(12, 2) NOT NULL,  -- 提供者收益
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/settled/withdrawn
    settled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_earnings_provider ON earnings(provider_id);
CREATE INDEX idx_earnings_order ON earnings(order_id);
```

### 3.3 RESTful API接口设计（OpenAPI 3.0规范）

#### 认证模块 `/api/v1/auth`

```yaml
openapi: 3.0.3
info:
  title: 算电协同平台 API
  version: 1.0.0
paths:
  /api/v1/auth/register:
    post:
      summary: 用户注册
      tags: [Auth]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                  format: email
                phone:
                  type: string
                password:
                  type: string
                  format: password
      responses:
        '201':
          description: 注册成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthResponse'
        '400':
          description: 参数错误
        '409':
          description: 用户已存在
  
  /api/v1/auth/login:
    post:
      summary: 用户登录
      tags: [Auth]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        '200':
          description: 登录成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AuthResponse'
        '401':
          description: 认证失败
  
  /api/v1/auth/refresh:
    post:
      summary: 刷新Token
      tags: [Auth]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [refresh_token]
              properties:
                refresh_token:
                  type: string
      responses:
        '200':
          description: Token刷新成功
        '401':
          description: Refresh Token无效

  /api/v1/auth/verify:
    post:
      summary: 身份认证（实名/企业认证）
      tags: [Auth]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                real_name:
                  type: string
                id_card_number:
                  type: string
                business_license:
                  type: string
      responses:
        '200':
          description: 认证成功
```

#### 市场模块 `/api/v1/marketplace`

```yaml
  /api/v1/marketplace/assets:
    get:
      summary: 查询可用资源列表
      tags: [Marketplace]
      parameters:
        - name: gpu_model
          in: query
          schema:
            type: string
        - name: min_vram
          in: query
          schema:
            type: integer
        - name: max_price
          in: query
          schema:
            type: number
        - name: power_source
          in: query
          schema:
            type: string
        - name: region
          in: query
          schema:
            type: string
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: 查询成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      items:
                        type: array
                        items:
                          $ref: '#/components/schemas/Asset'
                      total:
                        type: integer
                  message:
                    type: string
    
    post:
      summary: 批量查询资源
      tags: [Marketplace]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                asset_ids:
                  type: array
                  items:
                    type: string
      responses:
        '200':
          description: 查询成功

  /api/v1/marketplace/assets/{asset_id}:
    get:
      summary: 查询资源详情
      tags: [Marketplace]
      parameters:
        - name: asset_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: 查询成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AssetDetail'
        '404':
          description: 资源不存在
```

#### 调度模块 `/api/v1/scheduling`

```yaml
  /api/v1/scheduling/quote:
    post:
      summary: 获取智能报价
      tags: [Scheduling]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [task_type, strategy, estimated_duration_hours]
              properties:
                task_type:
                  type: string
                  enum: [inference, training, render]
                strategy:
                  type: string
                  enum: [cheapest, fastest, greenest, custom]
                estimated_duration_hours:
                  type: number
                custom_weights:
                  type: object
                  properties:
                    price:
                      type: number
                    speed:
                      type: number
                    green:
                      type: number
      responses:
        '200':
          description: 报价生成成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      quotes:
                        type: array
                        items:
                          $ref: '#/components/schemas/Quote'
                      recommended_quote:
                        $ref: '#/components/schemas/Quote'
                  message:
                    type: string
        '400':
          description: 参数错误
        '500':
          description: 调度引擎错误
  
  /api/v1/scheduling/tasks:
    post:
      summary: 提交任务
      tags: [Scheduling]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskSubmit'
      responses:
        '201':
          description: 任务提交成功
        '400':
          description: 参数错误
        '402':
          description: 余额不足
  
  /api/v1/scheduling/tasks/{task_id}:
    get:
      summary: 查询任务状态
      tags: [Scheduling]
      security:
        - BearerAuth: []
      parameters:
        - name: task_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: 查询成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TaskStatus'
```

#### 订单模块 `/api/v1/orders`

```yaml
  /api/v1/orders:
    get:
      summary: 查询订单列表
      tags: [Orders]
      security:
        - BearerAuth: []
      parameters:
        - name: status
          in: query
          schema:
            type: string
        - name: page
          in: query
          schema:
            type: integer
        - name: page_size
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: 查询成功
    
    post:
      summary: 创建订单
      tags: [Orders]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OrderCreate'
      responses:
        '201':
          description: 订单创建成功
  
  /api/v1/orders/{order_id}:
    get:
      summary: 查询订单详情
      tags: [Orders]
      security:
        - BearerAuth: []
      parameters:
        - name: order_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: 查询成功
  
  /api/v1/orders/{order_id}/pay:
    post:
      summary: 支付订单
      tags: [Orders]
      security:
        - BearerAuth: []
      parameters:
        - name: order_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [method]
              properties:
                method:
                  type: string
                  enum: [balance, alipay, wechat]
                amount:
                  type: number
      responses:
        '200':
          description: 支付成功
        '400':
          description: 订单状态错误
        '402':
          description: 余额不足
```

#### 资产模块 `/api/v1/assets`

```yaml
  /api/v1/assets:
    get:
      summary: 查询我的资产列表（提供者）
      tags: [Assets]
      security:
        - BearerAuth: []
      responses:
        '200':
          description: 查询成功
    
    post:
      summary: 注册资产
      tags: [Assets]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AssetRegister'
      responses:
        '201':
          description: 资产注册成功
        '400':
          description: 参数错误
  
  /api/v1/assets/{asset_id}/status:
    put:
      summary: 更新资产状态
      tags: [Assets]
      security:
        - BearerAuth: []
      parameters:
        - name: asset_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [status]
              properties:
                status:
                  type: string
                  enum: [online, offline, maintenance]
      responses:
        '200':
          description: 状态更新成功
  
  /api/v1/assets/{asset_id}/metrics:
    get:
      summary: 查询资产监控指标
      tags: [Assets]
      security:
        - BearerAuth: []
      parameters:
        - name: asset_id
          in: path
          required: true
          schema:
            type: string
        - name: start_time
          in: query
          schema:
            type: string
            format: date-time
        - name: end_time
          in: query
          schema:
            type: string
            format: date-time
      responses:
        '200':
          description: 查询成功
```

#### 收益模块 `/api/v1/earnings`

```yaml
  /api/v1/earnings/summary:
    get:
      summary: 查询收益概览
      tags: [Earnings]
      security:
        - BearerAuth: []
      parameters:
        - name: period
          in: query
          schema:
            type: string
            enum: [today, this_week, this_month, custom]
        - name: start_date
          in: query
          schema:
            type: string
            format: date
        - name: end_date
          in: query
          schema:
            type: string
            format: date
      responses:
        '200':
          description: 查询成功
          content:
            application/json:
              schema:
                type: object
                properties:
                  code:
                    type: integer
                  data:
                    type: object
                    properties:
                      today_earnings:
                        type: number
                      month_earnings:
                        type: number
                      total_earnings:
                        type: number
                      real_time_rate:
                        type: number
  
  /api/v1/earnings/details:
    get:
      summary: 查询收益明细
      tags: [Earnings]
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
        - name: page_size
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: 查询成功
  
  /api/v1/earnings/withdraw:
    post:
      summary: 提现申请
      tags: [Earnings]
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [amount, bank_account]
              properties:
                amount:
                  type: number
                bank_account:
                  type: string
      responses:
        '200':
          description: 提现申请成功
        '400':
          description: 余额不足或未满100元
```

#### 组件定义

```yaml
components:
  schemas:
    Asset:
      type: object
      properties:
        id:
          type: string
        type:
          type: string
        spec:
          type: object
        pricing:
          type: object
        status:
          type: string
    
    Quote:
      type: object
      properties:
        asset_id:
          type: string
        compute_cost:
          type: number
        energy_cost:
          type: number
        total_cost:
          type: number
        carbon_saved_kg:
          type: number
        match_reason:
          type: string
    
    TaskSubmit:
      type: object
      required: [container_image, task_type]
      properties:
        container_image:
          type: string
        dataset_location:
          type: string
        task_type:
          type: string
        estimated_duration_hours:
          type: number
    
    OrderCreate:
      type: object
      required: [selected_quote]
      properties:
        selected_quote:
          $ref: '#/components/schemas/Quote'
    
    AuthResponse:
      type: object
      properties:
        code:
          type: integer
        data:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            token_type:
              type: string
            expires_in:
              type: integer
        message:
          type: string
  
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### 3.4 统一响应格式

```json
{
  "code": 200,
  "message": "成功",
  "data": {
    // 业务数据
  },
  "timestamp": "2026-05-11T02:00:00Z"
}
```

**错误响应**：

```json
{
  "code": 400,
  "message": "参数错误：email格式不正确",
  "data": null,
  "timestamp": "2026-05-11T02:00:00Z"
}
```

---

## 四、程序调用流程

### 4.1 流程1：任务提交与智能报价

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant API as 后端API
    participant Scheduler as 调度引擎
    participant Resource as 资源检索服务
    participant Quote as 报价生成服务
    participant DB as 数据库
    participant Cache as Redis缓存
    
    U->>F: 提交任务表单
    F->>F: 表单验证
    F->>API: POST /api/v1/scheduling/quote
    API->>API: 参数验证
    API->>Scheduler: 请求智能报价
    
    Scheduler->>Resource: 检索可用算力资源
    Resource->>DB: 查询资产表
    DB-->>Resource: 返回可用资产列表
    Resource->>Cache: 查询实时库存
    Cache-->>Resource: 返回库存状态
    Resource-->>Scheduler: 返回候选资源列表
    
    Scheduler->>Resource: 检索配套能源资源
    Resource->>DB: 查询电价、绿电比例
    DB-->>Resource: 返回能源信息
    Resource-->>Scheduler: 返回能源列表
    
    Scheduler->>Scheduler: 计算最优组合
    Note over Scheduler: 根据策略权重计算：<br/>价格(40%) + 速度(30%) + 绿色(30%)
    
    Scheduler->>Quote: 生成报价方案
    Quote->>Quote: 计算费用明细
    Quote->>Quote: 计算碳减排量
    Quote-->>Scheduler: 返回报价方案
    
    Scheduler-->>API: 返回报价列表
    API-->>F: 返回报价JSON
    F->>F: 展示报价卡片
    F-->>U: 显示报价方案
    
    U->>F: 确认下单
    F->>API: POST /api/v1/orders
    API->>DB: 创建订单记录
    DB-->>API: 返回订单ID
    API-->>F: 返回订单信息
    F-->>U: 跳转到支付页面
```

### 4.2 流程2：订单支付与资源绑定

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant API as 后端API
    participant Payment as 支付服务
    participant Order as 订单服务
    participant Binding as 资源绑定服务
    participant K8s as K8s调度器
    participant TaskEngine as 任务执行引擎
    participant DB as 数据库
    participant WS as WebSocket
    
    U->>F: 点击支付
    F->>API: POST /api/v1/orders/{id}/pay
    API->>API: 验证订单状态
    API->>Payment: 发起支付
    
    alt 余额支付
        Payment->>DB: 扣减用户余额
        DB-->>Payment: 扣减成功
    else 第三方支付
        Payment->>Payment: 调用支付宝/微信API
        Payment-->>API: 支付成功回调
    end
    
    Payment-->>API: 支付成功
    API->>DB: 更新订单状态为paid
    API-->>F: 返回支付成功
    F-->>U: 显示支付成功页面
    
    API->>Binding: 触发资源绑定
    Binding->>K8s: 提交Pod调度请求
    K8s->>K8s: 自定义调度器决策
    Note over K8s: 考虑：<br/>1. GPU型号匹配<br/>2. 电力价格<br/>3. 绿电比例<br/>4. 资源利用率
    K8s-->>Binding: 调度成功，返回Pod ID
    
    Binding->>DB: 更新任务状态为running
    Binding->>DB: 记录资源绑定信息
    Binding-->>API: 绑定成功
    
    API->>TaskEngine: 下发任务到GPU节点
    TaskEngine->>TaskEngine: 拉取容器镜像
    TaskEngine->>TaskEngine: 挂载数据集
    TaskEngine->>TaskEngine: 启动任务
    TaskEngine-->>DB: 更新任务开始时间
    
    TaskEngine->>WS: 推送任务状态变更
    WS-->>F: 实时更新任务状态
    F-->>U: 显示任务运行中
    
    loop 任务执行期间
        TaskEngine->>DB: 写入监控指标
        TaskEngine->>WS: 推送实时指标
        WS-->>F: 更新实时监控面板
    end
    
    TaskEngine-->>DB: 任务完成
    DB-->>Order: 触发订单完成
    Order->>Order: 计算收益分配
    Order->>DB: 写入收益记录
    Order-->>API: 订单完成
    API->>WS: 推送订单完成通知
    WS-->>F: 显示任务完成
    F-->>U: 显示完成页面 + 碳足迹报告
```

### 4.3 流程3：实时监控数据流转

```mermaid
sequenceDiagram
    participant GPU as GPU节点
    participant Agent as 数据采集Agent
    participant Kafka as Kafka消息队列
    participant InfluxDB as InfluxDB
    participant Monitoring as 监控服务
    participant WS as WebSocket服务
    participant F as 前端
    participant U as 用户
    
    loop 每5秒采集一次
        GPU->>Agent: 暴露metrics端点
        Note over GPU: 指标：<br/>- 功耗(W)<br/>- GPU利用率(%)<br/>- 温度(°C)<br/>- 显存使用率(%)
        Agent->>Agent: 采集指标数据
        Agent->>Kafka: 发送指标数据
        Note over Agent: 数据格式：<br/>{asset_id, timestamp, metrics{...}}
    end
    
    Kafka->>InfluxDB: 消费指标数据
    InfluxDB->>InfluxDB: 写入时序数据库
    
    Monitoring->>InfluxDB: 查询最新指标
    InfluxDB-->>Monitoring: 返回指标数据
    
    Monitoring->>Monitoring: 计算碳排放量
    Note over Monitoring: 碳排放 = 功耗 × 时间间隔 × 碳因子
    
    Monitoring->>WS: 推送实时数据
    Note over WS: WebSocket通道：<br/>/ws/monitoring/{task_id}
    
    WS-->>F: 推送实时更新
    F->>F: 更新图表和指标显示
    F-->>U: 实时显示功耗曲线、碳排放
```

### 4.4 流程4：资产注册与审核

```mermaid
sequenceDiagram
    participant P as 提供者
    participant F as 前端
    participant API as 后端API
    participant Asset as 资产服务
    participant Audit as 审核服务
    participant DB as 数据库
    participant Index as 市场索引服务
    participant Notification as 通知服务
    
    P->>F: 填写资产注册表单
    F->>F: 表单验证
    F->>API: POST /api/v1/assets
    API->>API: 参数验证
    API->>Asset: 创建资产记录
    
    Asset->>DB: 插入资产记录（status=pending）
    DB-->>Asset: 返回资产ID
    Asset-->>API: 注册成功
    API-->>F: 返回资产信息
    F-->>P: 显示"待审核"状态
    
    API->>Audit: 触发审核流程
    
    Audit->>Audit: 自动审核检查
    Note over Audit: 检查项：<br/>1. GPU型号是否支持<br/>2. 电价是否合理<br/>3. 位置信息是否完整
    
    alt 自动审核通过
        Audit->>DB: 更新audit_status=approved
        Audit->>Notification: 发送审核通过通知
        Notification-->>P: 短信/邮件通知
        Audit->>Index: 通知资源上架
        Index->>Index: 更新市场索引
        Index->>DB: 更新资产status=online
        Index-->>F: 资源可搜索
    else 需要人工审核
        Audit->>DB: 更新audit_status=pending_manual
        Audit->>Notification: 通知运营团队
        Notification-->>Admin: 站内信通知
        Note over Admin: 运营人员在后台审核
        Admin->>Audit: 审核通过/拒绝
        Audit->>DB: 更新审核状态
        alt 审核通过
            Audit->>Index: 通知资源上架
            Index->>DB: 更新资产status=online
        else 审核拒绝
            Audit->>Notification: 发送拒绝原因
            Notification-->>P: 邮件通知
        end
    end
    
    P->>F: 查看资产状态
    F->>API: GET /api/v1/assets/{id}
    API->>DB: 查询资产状态
    DB-->>API: 返回资产信息
    API-->>F: 返回状态
    F-->>P: 显示"在线"状态、可接单
```

---

## 五、任务列表

### 5.1 任务分解原则

- **优先级**：P0（必须）- P1（重要）- P2（可选）
- **工时单位**：人天（8小时/天）
- **依赖关系**：标注前置任务ID
- **角色**：Frontend（前端）/ Backend（后端）/ Fullstack（全栈）/ DevOps（运维）

### 5.2 完整任务列表

#### 阶段1：基础设施与项目初始化（Week 1）

| ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 角色 | 详细描述 |
|----|----------|--------|----------|------|------|----------|
| T001 | 项目初始化 + 代码仓库搭建 | P0 | 1 | 无 | DevOps | 创建Monorepo仓库结构、配置Git、添加README、配置.gitignore |
| T002 | 开发环境Docker编排配置 | P0 | 1 | T001 | DevOps | 编写docker-compose.dev.yml，包含PostgreSQL、Redis、InfluxDB、RabbitMQ |
| T003 | CI/CD流水线搭建 | P0 | 1 | T001 | DevOps | 配置GitLab CI或GitHub Actions，实现自动构建、测试、镜像推送 |
| T004 | 数据库Schema设计与迁移脚本 | P0 | 2 | T002 | Backend | 设计所有表的DDL、配置Alembic、编写初始迁移脚本 |
| T005 | 前端项目初始化 | P0 | 1 | T001 | Frontend | 使用Vite创建React+TS项目、配置Ant Design、ESLint、Prettier |
| T006 | 后端项目初始化 | P0 | 1 | T001 | Backend | 搭建FastAPI项目结构、配置中间件、异常处理、日志、CORS |
| T007 | 认证基础设施搭建 | P0 | 1 | T004, T006 | Backend | 实现JWT工具类、密码哈希工具、认证中间件 |

#### 阶段2：核心业务模块开发（Week 2-3）

| ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 角色 | 详细描述 |
|----|----------|--------|----------|------|------|----------|
| T008 | 用户注册/登录功能 | P0 | 3 | T007 | Fullstack | 前端：注册/登录页面；后端：API实现、Token签发
| T009 | 用户认证中心（前端） | P0 | 2 | T005, T008 | Frontend | 实现AuthStore、路由守卫、Token刷新机制、登录状态管理 |
| T010 | 资产管理模块 - 后端API | P0 | 3 | T004, T007 | Backend | 实现资产注册、查询、更新状态等API、数据验证 |
| T011 | 资产管理模块 - 前端页面 | P0 | 3 | T009, T010 | Frontend | 资产注册表单、资产列表、资产详情页、表单验证 |
| T012 | 资源市场模块 - 后端API | P0 | 3 | T010 | Backend | 实现资源列表查询（支持筛选、分页）、资源详情API |
| T013 | 资源市场模块 - 前端页面 | P0 | 4 | T009, T012 | Frontend | 市场首页、资源卡片组件、筛选面板、分页、详情页 |
| T014 | 订单管理模块 - 后端API | P0 | 3 | T010, T012 | Backend | 实现订单创建、查询、取消、状态流转等API |
| T015 | 订单管理模块 - 前端页面 | P0 | 3 | T009, T014 | Frontend | 订单列表、订单详情、订单状态展示、取消订单功能 |

#### 阶段3：智能调度与支付（Week 4）

| ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 角色 | 详细描述 |
|----|----------|--------|----------|------|------|----------|
| T016 | 调度引擎 - 资源检索服务 | P0 | 3 | T012 | Backend | 实现基于多维度（GPU、价格、能源）的资源检索算法 |
| T017 | 调度引擎 - 报价生成服务 | P0 | 3 | T016 | Backend | 实现报价计算逻辑、费用明细生成、碳减排计算 |
| T018 | 调度引擎 - API接口 | P0 | 2 | T017 | Backend | 实现获取报价、提交任务等API、参数验证 |
| T019 | 智能调度 - 前端页面 | P0 | 4 | T013, T018 | Frontend | 任务提交表单、策略选择、报价展示、确认下单流程 |
| T020 | 支付系统 - 余额支付 | P0 | 2 | T014 | Backend | 实现余额扣减逻辑、支付API、事务管理 |
| T021 | 支付系统 - 第三方支付集成 | P1 | 3 | T020 | Backend | 集成支付宝、微信支付SDK、实现回调处理 |
| T022 | 支付系统 - 前端页面 | P0 | 2 | T020 | Frontend | 支付页面、支付结果展示、支付密码输入 |

#### 阶段4：实时监控与任务执行（Week 5）

| ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 角色 | 详细描述 |
|----|----------|--------|----------|------|------|----------|
| T023 | 数据采集Agent开发 | P0 | 3 | T002 | Backend | 开发部署在GPU节点的Agent、采集功耗/利用率等指标 |
| T024 | Kafka + InfluxDB集成 | P0 | 2 | T023 | Backend | 配置Kafka Topic、实现数据消费、写入InfluxDB |
| T025 | 监控服务 - 后端API | P0 | 2 | T024 | Backend | 实现监控数据查询API、实时指标计算 |
| T026 | WebSocket服务开发 | P0 | 2 | T025 | Backend | 实现WebSocket端点、实时推送任务状态和指标 |
| T027 | 任务监控 - 前端页面 | P0 | 4 | T019, T026 | Frontend | 实时监控面板、功耗曲线图、碳排放显示、任务日志 |
| T028 | K8s自定义调度器开发 | P1 | 5 | T016 | Backend | 使用Go开发K8s自定义调度器、实现算电协同调度逻辑 |

#### 阶段5：收益与碳足迹（Week 6）

| ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 角色 | 详细描述 |
|----|----------|--------|----------|------|------|----------|
| T029 | 收益计算服务 | P0 | 2 | T014 | Backend | 实现收益计算逻辑（订单金额 - 平台服务费）、分账 |
| T030 | 收益中心 - 后端API | P0 | 2 | T029 | Backend | 实现收益概览、明细查询、提现申请等API |
| T031 | 收益中心 - 前端页面 | P0 | 3 | T009, T030 | Frontend | 收益概览仪表盘、收益曲线图、提现申请页面 |
| T032 | 碳足迹计算服务 | P0 | 2 | T025 | Backend | 实现碳排放计算（基于功耗和碳因子）、报告生成 |
| T033 | 碳足迹报告 - 后端API | P1 | 2 | T032 | Backend | 实现报告查询API、PDF生成和上传 |
| T034 | 碳足迹报告 - 前端页面 | P1 | 2 | T027, T033 | Frontend | 报告展示页面、PDF下载、碳减排 badge展示 |

#### 阶段6：系统集成与测试（Week 7）

| ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 角色 | 详细描述 |
|----|----------|--------|----------|------|------|----------|
| T035 | 端到端集成测试 | P0 | 3 | T019, T022, T031 | Fullstack | 编写和执行关键流程的E2E测试（注册→下单→支付→执行→完成） |
| T036 | 性能压力测试 | P1 | 2 | T035 | DevOps | 使用JMeter或Locust进行API压力测试、识别性能瓶颈 |
| T037 | 前端E2E测试 | P1 | 2 | T013, T019, T027 | Frontend | 使用Cypress或Playwright编写前端E2E测试 |
| T038 | 后端单元测试补充 | P0 | 2 | All backend tasks | Backend | 提高测试覆盖率到80%以上 |
| T039 | 安全测试 | P1 | 2 | T035 | Fullstack | SQL注入、XSS、CSRF、JWT安全、敏感数据加密验证 |

#### 阶段7：部署与上线准备（Week 8）

| ID | 任务名称 | 优先级 | 预估工时 | 依赖 | 角色 | 详细描述 |
|----|----------|--------|----------|------|------|----------|
| T040 | Kubernetes部署配置 | P0 | 2 | T002, T028 | DevOps | 编写Deployment、Service、Ingress、ConfigMap、Secret等YAML |
| T041 | 数据库备份与恢复脚本 | P0 | 1 | T004 | DevOps | 编写自动备份脚本、恢复测试、定时任务配置 |
| T042 | 监控与告警配置 | P0 | 2 | T024 | DevOps | 配置Prometheus + Grafana、设置关键指标告警规则 |
| T043 | 日志系统搭建 | P1 | 2 | T002 | DevOps | 部署ELK Stack、配置日志收集、创建常用查询 |
| T044 | 上线部署与验证 | P0 | 2 | T040, T041, T042 | DevOps | 生产环境部署、冒烟测试、回滚方案准备 |
| T045 | 文档编写 | P0 | 2 | All tasks | Fullstack | API文档、部署文档、用户手册、运维手册 |

### 5.3 任务依赖关系图（Mermaid）

```mermaid
gantt
    title 算电协同平台 Phase 1 开发计划
    dateFormat  YYYY-MM-DD
    section 基础设施
    项目初始化           :t001, 2026-05-11, 1d
    Docker环境配置       :t002, after t001, 1d
    CI/CD搭建           :t003, after t001, 1d
    数据库设计           :t004, after t002, 2d
    前端项目初始化       :t005, after t001, 1d
    后端项目初始化       :t006, after t001, 1d
    认证基础设施         :t007, after t004 t006, 1d
    
    section 核心业务
    用户认证功能         :t008, after t007, 3d
    前端认证中心         :t009, after t005 t008, 2d
    资产管理后端         :t010, after t004 t007, 3d
    资产管理前端         :t011, after t009 t010, 3d
    资源市场后端         :t012, after t010, 3d
    资源市场前端         :t013, after t009 t012, 4d
    订单管理后端         :t014, after t010 t012, 3d
    订单管理前端         :t015, after t009 t014, 3d
    
    section 智能调度
    资源检索服务         :t016, after t012, 3d
    报价生成服务         :t017, after t016, 3d
    调度API接口          :t018, after t017, 2d
    智能调度前端         :t019, after t013 t018, 4d
    
    section 支付系统
    余额支付             :t020, after t014, 2d
    第三方支付集成       :t021, after t020, 3d
    支付前端页面         :t022, after t020, 2d
    
    section 实时监控
    数据采集Agent        :t023, after t002, 3d
    Kafka+InfluxDB      :t024, after t023, 2d
    监控API             :t025, after t024, 2d
    WebSocket服务        :t026, after t025, 2d
    任务监控前端         :t027, after t019 t026, 4d
    K8s调度器           :t028, after t016, 5d
    
    section 收益与碳足迹
    收益计算服务         :t029, after t014, 2d
    收益API             :t030, after t029, 2d
    收益前端             :t031, after t009 t030, 3d
    碳足迹计算           :t032, after t025, 2d
    碳足迹API           :t033, after t032, 2d
    碳足迹前端           :t034, after t027 t033, 2d
    
    section 测试
    集成测试             :t035, after t019 t022 t031, 3d
    性能测试             :t036, after t035, 2d
    前端E2E测试          :t037, after t013 t019 t027, 2d
    后端单元测试         :t038, after t035, 2d
    安全测试             :t039, after t035, 2d
    
    section 部署上线
    K8s部署配置         :t040, after t002 t028, 2d
    备份恢复脚本         :t041, after t004, 1d
    监控告警配置         :t042, after t024, 2d
    日志系统             :t043, after t002, 2d
    上线部署             :t044, after t040 t041 t042, 2d
    文档编写             :t045, after t035, 2d
```

### 5.4 任务工时汇总

| 阶段 | 任务数 | 总工时（人天） | 依赖的关键路径 |
|------|--------|----------------|----------------|
| 基础设施 | 7 | 9 | 无 |
| 核心业务 | 8 | 21 | T007 |
| 智能调度 | 4 | 12 | T012 |
| 支付系统 | 3 | 7 | T014 |
| 实时监控 | 6 | 18 | T012, T019 |
| 收益与碳足迹 | 6 | 11 | T014, T025 |
| 测试 | 5 | 11 | 多个前置任务 |
| 部署上线 | 6 | 11 | 多个前置任务 |
| **总计** | **45** | **100** | - |

**关键路径分析**：
- 最长路径：T001 → T004 → T007 → T010 → T012 → T016 → T017 → T018 → T019 → T035 → T044
- 预计最短完成时间：**7-8周**（按5人团队并行开发）

---

## 六、依赖包列表

### 6.1 前端依赖（package.json）

```json
{
  "name": "calc-electric-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "typescript": "^5.3.0",
    "antd": "^5.12.0",
    "@ant-design/icons": "^5.2.0",
    "zustand": "^4.4.0",
    "echarts": "^5.4.3",
    "echarts-for-react": "^3.0.2",
    "socket.io-client": "^4.7.2",
    "axios": "^1.6.0",
    "dayjs": "^1.11.10",
    "lodash": "^4.17.21",
    "classnames": "^2.3.2",
    "less": "^4.2.0",
    "react-scripts": "5.0.1"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "eslint": "^8.55.0",
    "eslint-config-prettier": "^9.1.0",
    "eslint-plugin-react": "^7.33.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "prettier": "^3.1.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "cypress": "^13.6.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,css,less}\"",
    "test:e2e": "cypress open"
  }
}
```

### 6.2 后端依赖（pyproject.toml - Poetry）

```toml
[tool.poetry]
name = "calc-electric-backend"
version = "1.0.0"
description = "算电协同平台后端服务"
authors = ["高见远 <gao@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.109.0"
uvicorn = {extras = ["standard"], version = "^0.27.0"}
sqlalchemy = "^2.0.25"
asyncpg = "^0.29.0"
aioredis = "^2.0.1"
alembic = "^1.13.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-multipart = "^0.0.6"
itsdangerous = "^2.1.2"
celery = "^5.3.4"
kombu = "^5.3.4"
influxdb-client = "^1.39.0"
minio = "^7.1.0"
httpx = "^0.26.0"
python-dotenv = "^1.0.0"
loguru = "^0.7.2"
prometheus-client = "^0.19.0"
opentelemetry-api = "^1.22.0"
opentelemetry-sdk = "^1.22.0"
opentelemetry-instrumentation-fastapi = "^0.43b0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
httpx = "^0.26.0"
alembic = "^1.13.0"
autoflake = "^2.2.0"
black = "^23.12.0"
isort = "^5.13.0"
mypy = "^1.8.0"
flake8 = "^7.0.0"
```

### 6.3 K8s自定义调度器依赖（Go - go.mod）

```go
module calc-electric-scheduler

go 1.21

require (
    k8s.io/api v0.29.0
    k8s.io/apimachinery v0.29.0
    k8s.io/client-go v0.29.0
    k8s.io/kubernetes v1.29.0
    k8s.io/klog/v2 v2.110.0
)
```

### 6.4 系统级依赖（Docker容器）

| 组件 | 镜像 | 版本 | 用途 |
|------|------|------|------|
| PostgreSQL | postgres | 16-alpine | 主数据库 |
| Redis | redis | 7-alpine | 缓存、Session、Pub/Sub |
| InfluxDB | influxdb | 2.7-alpine | 时序数据存储 |
| RabbitMQ | rabbitmq | 3.12-management-alpine | 消息队列 |
| MinIO | minio/minio | RELEASE.2024-01-16T16-07-38Z | 对象存储 |
| Kong | kong | 3.5-alpine | API网关 |
| Prometheus | prom/prometheus | v2.48.0 | 监控指标采集 |
| Grafana | grafana/grafana | 10.2.0 | 监控可视化 |
| Jaeger | jaegertracing/all-in-one | 1.52.0 | 分布式追踪 |
| Elasticsearch | elasticsearch | 8.11.0 | 日志存储 |
| Logstash | logstash | 8.11.0 | 日志收集 |
| Kibana | kibana | 8.11.0 | 日志可视化 |

---

## 七、共享知识

### 7.1 代码规范

#### 命名约定

| 层级 | 约定 | 示例 |
|------|------|------|
| **前端 - 变量/函数** | 驼峰命名（camelCase） | `getUserInfo`, `isLoading` |
| **前端 - 组件** | 大驼峰命名（PascalCase） | `UserProfile`, `OrderList` |
| **前端 - 常量** | 大写下划线（UPPER_SNAKE_CASE） | `API_BASE_URL`, `MAX_RETRY_COUNT` |
| **前端 - CSS类** | kebab-case或BEM | `user-profile`, `user-profile--active` |
| **后端 - 变量/函数** | 下划线命名（snake_case） | `get_user_info`, `is_loading` |
| **后端 - 类** | 大驼峰命名（PascalCase） | `UserService`, `OrderModel` |
| **后端 - 常量** | 大写下划线（UPPER_SNAKE_CASE） | `MAX_RETRY_COUNT`, `DEFAULT_PAGE_SIZE` |
| **后端 - 数据库字段** | 下划线命名（snake_case） | `user_id`, `created_at`, `total_amount` |
| **后端 - API路径** | 下划线小写（lowercase） | `/api/v1/user_profile` （推荐用中划线：`/api/v1/user-profile`） |
| **数据库 - 表名** | 复数、下划线（snake_case） | `users`, `asset_types`, `order_items` |
| **数据库 - 索引** | `idx_<table>_<column>` | `idx_users_email`, `idx_orders_status` |

#### 代码格式化

| 语言/框架 | 工具 | 配置文件 | 关键规则 |
|-----------|------|----------|----------|
| **前端（TypeScript/JavaScript）** | Prettier | `.prettierrc` | 单引号、分号、2空格缩进 |
| **前端（TypeScript）** | ESLint | `.eslintrc.cjs` | 强制类型注解、禁止any |
| **后端（Python）** | Black | `pyproject.toml` | 行长度88、双引号 |
| **后端（Python）** | isort | `pyproject.toml` | 导入排序：标准库→第三方→本地 |
| **后端（Python）** | Flake8 | `.flake8` | 复杂度检查、未使用导入检查 |
| **Go（调度器）** | gofmt | - | 官方格式化工具 |
| **SQL** | pg_format | - | 关键字大写、缩进规范 |

#### Git提交规范（Conventional Commits）

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type列表**：

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): 添加手机号登录功能` |
| `fix` | Bug修复 | `fix(order): 修复订单状态流转错误` |
| `docs` | 文档更新 | `docs(README): 更新API文档` |
| `style` | 代码格式（不影响功能） | `style(user): 格式化用户模块代码` |
| `refactor` | 重构（既不是feat也不是fix） | `refactor(api): 重构认证中间件` |
| `perf` | 性能优化 | `perf(query): 优化订单查询索引` |
| `test` | 测试相关 | `test(payment): 添加支付模块单元测试` |
| `chore` | 构建/工具链修改 | `chore(deps): 升级fastapi到0.109.0` |
| `ci` | CI配置修改 | `ci(gitlab): 添加自动部署配置` |

**Scope列表**：

- `auth`：认证模块
- `user`：用户模块
- `asset`：资产模块
- `market`：市场模块
- `scheduling`：调度模块
- `order`：订单模块
- `payment`：支付模块
- `monitoring`：监控模块
- `earnings`：收益模块
- `carbon`：碳足迹模块
- `db`：数据库
- `deploy`：部署
- `docs`：文档
- `deps`：依赖

**示例提交消息**：

```
feat(scheduling): 实现智能报价生成服务

- 添加资源检索服务
- 实现多维度评分算法
- 添加碳减排计算逻辑

Closes #123
```

### 7.2 错误处理策略

#### 前端错误边界（Error Boundary）

```typescript
// src/components/Common/ErrorBoundary.tsx
import React from 'react';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('ErrorBoundary caught:', error, errorInfo);
    // 发送错误到监控服务
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return this.props.fallback || <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

**使用方式**：

```tsx
<ErrorBoundary fallback={<ErrorPage />}>
  <MyComponent />
</ErrorBoundary>
```

#### 后端全局异常处理器（FastAPI）

```python
# app/core/exceptions.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError
import logging

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理器"""
    
    # 参数验证错误
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": 400,
                "message": "参数验证失败",
                "data": exc.errors(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # 数据库错误
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "数据库错误",
                "data": None,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # Redis错误
    if isinstance(exc, RedisError):
        logger.error(f"Redis error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "缓存服务错误",
                "data": None,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    # 未知错误
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# 在main.py中注册
app.add_exception_handler(Exception, global_exception_handler)
```

#### 统一错误码设计

| 错误码范围 | 类别 | 示例 |
|------------|------|------|
| 400-499 | 客户端错误 | 400: 参数错误<br>401: 未认证<br>403: 无权限<br>404: 资源不存在<br>409: 冲突（如重复注册）<br>422: 验证错误 |
| 500-599 | 服务端错误 | 500: 服务器内部错误<br>502: 上游服务错误<br>503: 服务不可用<br>504: 网关超时 |
| 1000-1999 | 业务错误（认证） | 1001: Token过期<br>1002: Token无效<br>1003: 密码错误<br>1004: 用户未认证 |
| 2000-2999 | 业务错误（资产） | 2001: 资产不存在<br>2002: 资产已下线<br>2003: 审核未通过 |
| 3000-3999 | 业务错误（订单） | 3001: 订单不存在<br>3002: 订单状态错误<br>3003: 余额不足 |
| 4000-4999 | 业务错误（支付） | 4001: 支付失败<br>4002: 重复支付<br>4003: 退款失败 |

### 7.3 日志规范

#### 日志级别

| 级别 | 使用场景 | 示例 |
|------|----------|------|
| **DEBUG** | 详细的调试信息 | `logger.debug(f"Querying user: user_id={user_id}")` |
| **INFO** | 关键业务操作 | `logger.info(f"User logged in: user_id={user_id}")` |
| **WARNING** | 潜在问题但不影响系统 | `logger.warning(f"Cache miss: key={cache_key}")` |
| **ERROR** | 错误信息，影响功能 | `logger.error(f"Payment failed: order_id={order_id}, error={str(e)}")` |
| **CRITICAL** | 严重错误，系统不可用 | `logger.critical("Database connection lost")` |

#### 日志格式（JSON结构化日志）

```json
{
  "timestamp": "2026-05-11T02:00:00.000Z",
  "level": "INFO",
  "service": "calc-electric-backend",
  "module": "auth_service",
  "function": "login",
  "message": "User logged in successfully",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "ip_address": "192.168.1.100",
  "request_id": "req-123-456",
  "duration_ms": 45
}
```

**Python实现（Loguru）**：

```python
# app/core/logging.py
import sys
import json
from datetime import datetime
from loguru import logger

def serialize_record(record: dict) -> str:
    """将日志记录序列化为JSON"""
    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "service": "calc-electric-backend",
        "module": record["module"],
        "function": record["function"],
        "message": record["message"],
        **record["extra"]  # 额外字段（如user_id、request_id）
    }
    return json.dumps(log_entry, ensure_ascii=False)

# 配置Loguru
logger.remove()
logger.add(
    sys.stdout,
    format=serialize_record,
    serialize=True,
    level="INFO"
)
logger.add(
    "logs/app.log",
    rotation="100 MB",
    retention="30 days",
    compression="zip",
    format=serialize_record,
    serialize=True,
    level="DEBUG"
)

# 使用方式
from loguru import logger

logger.bind(user_id="123", request_id="req-456").info("User logged in")
```

#### 敏感信息脱敏规则

| 字段 | 脱敏规则 | 示例 |
|------|----------|------|
| 密码 | 不记录 | - |
| 身份证号 | 显示前4位和后4位 | `"id_card": "1101**********1234"` |
| 手机号 | 显示前3位和后4位 | `"phone": "138****1234"` |
| 银行卡号 | 显示后4位 | `"bank_card": "**** **** **** 1234"` |
| 邮箱 | 显示前1位和域名 | `"email": "u***@example.com"` |
| Token | 不记录完整Token | `"token": "eyJhbG...（截断）"` |
| 密码哈希 | 不记录 | - |

**实现方式**：

```python
# app/utils/sanitizer.py
import re

def sanitize_sensitive_data(data: dict) -> dict:
    """脱敏敏感信息"""
    sanitized = data.copy()
    
    # 身份证号脱敏
    if "id_card" in sanitized:
        id_card = sanitized["id_card"]
        sanitized["id_card"] = id_card[:4] + "*" * (len(id_card) - 8) + id_card[-4:]
    
    # 手机号脱敏
    if "phone" in sanitized:
        phone = sanitized["phone"]
        sanitized["phone"] = phone[:3] + "****" + phone[-4:]
    
    # 邮箱脱敏
    if "email" in sanitized:
        email = sanitized["email"]
        username, domain = email.split("@")
        sanitized["email"] = username[0] + "*" * (len(username) - 1) + "@" + domain
    
    # 删除密码字段
    sanitized.pop("password", None)
    sanitized.pop("password_hash", None)
    sanitized.pop("token", None)
    
    return sanitized
```

### 7.4 API设计规范

#### 统一响应格式

```json
{
  "code": 200,
  "message": "成功",
  "data": {
    // 业务数据
  },
  "timestamp": "2026-05-11T02:00:00.000Z",
  "request_id": "req-123-456"  // 用于链路追踪
}
```

**FastAPI实现**：

```python
# app/schemas/response.py
from datetime import datetime
from typing import Generic, TypeVar, Optional
from pydantic import Field

DataT = TypeVar("DataT")

class ApiResponse(Generic[DataT]):
    """统一API响应格式"""
    code: int = Field(..., description="状态码")
    message: str = Field(..., description="消息")
    data: Optional[DataT] = Field(None, description="业务数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    
    @classmethod
    def success(cls, data: DataT = None, message: str = "成功") -> "ApiResponse[DataT]":
        """成功响应"""
        return cls(code=200, message=message, data=data)
    
    @classmethod
    def error(cls, code: int, message: str) -> "ApiResponse[None]":
        """错误响应"""
        return cls(code=code, message=message, data=None)
```

#### 分页参数规范

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `page` | Integer | 1 | 页码（从1开始） |
| `page_size` | Integer | 20 | 每页数量（最大100） |
| `sort_by` | String | "created_at" | 排序字段 |
| `order` | String | "desc" | 排序方向（asc/desc） |

**响应格式**：

```json
{
  "code": 200,
  "message": "成功",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "timestamp": "2026-05-11T02:00:00.000Z"
}
```

#### 认证规范（JWT Token）

**Token获取**：

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

# 响应
{
  "code": 200,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800  // 30分钟
  }
}
```

**Token使用**：

```http
GET /api/v1/orders
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token刷新**：

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**JWT Payload结构**：

```json
{
  "sub": "123e4567-e89b-12d3-a456-426614174000",  // 用户ID
  "email": "user@example.com",
  "role": "consumer",
  "exp": 1700000000,  // 过期时间
  "iat": 1699998200,  // 签发时间
  "jti": "unique-token-id"  // JWT ID（用于黑名单）
}
```

---

## 八、待明确事项

### 8.1 技术决策待确认

| ID | 问题 | 影响范围 | 建议方案 | 需要确认 |
|----|------|----------|----------|----------|
| Q-001 | **Kubernetes自定义调度器的开发工作量评估？** | 调度引擎、K8s集成 | 预估需要3-5人周，建议使用Go语言基于K8s Scheduling Framework开发 | 确认是否Phase 1必须实现自定义调度器，还是可以用外部调度服务替代？ |
| Q-002 | **时序数据库选择InfluxDB还是TimescaleDB？** | 监控服务、数据存储 | InfluxDB：专为时序数据优化、压缩率高；TimescaleDB：基于PostgreSQL、查询灵活 | 建议选择InfluxDB，如团队更熟悉PostgreSQL可选TimescaleDB |
| Q-003 | **支付系统是自研还是接入第三方支付网关？** | 支付模块、合规 | 自研：可控性高、开发成本高；第三方：快速接入、有手续费 | Phase 1建议先接入支付宝/微信，降低合规风险 |
| Q-004 | **实时监控的数据采集频率（1秒/5秒/1分钟）？** | 监控服务、存储成本 | 1秒：实时性最好、存储量大；5秒：平衡方案；1分钟：存储量小、实时性差 | 建议：高频数据（5秒）存InfluxDB，低频数据（5分钟）归档 |
| Q-005 | **是否需要支持多租户隔离（Phase 1）？** | 架构设计、数据模型 | 需要：数据隔离、安全性高、开发成本高；不需要：简化开发、快速交付 | 建议Phase 1不支持多租户，所有用户共享平台 |
| Q-006 | **Kafka是否必须？能否用RabbitMQ替代？** | 消息队列、监控数据流 | Kafka：高吞吐、持久化、适合日志流；RabbitMQ：易用、适合任务队列 | 建议：监控数据流用Kafka，任务队列用RabbitMQ |
| Q-007 | **前端状态管理选择Zustand还是Redux Toolkit？** | 前端架构 | Zustand：轻量、API简洁；Redux Toolkit：生态成熟、调试工具完善 | 建议选择Zustand，降低学习成本 |
| Q-008 | **后端异步任务选择Celery还是RQ（Redis Queue）？** | 任务队列 | Celery：成熟、功能全面、复杂度高；RQ：轻量、易于上手 | 建议选择Celery，支持更复杂的场景 |

### 8.2 业务决策待确认

| ID | 问题 | 影响范围 | 建议方案 | 需要确认 |
|----|------|----------|----------|----------|
| Q-009 | **平台服务费比例：收取交易额的10%是否合理？** | 商业化、收益计算 | 建议：5-15%区间，根据提供者议价能力动态调整 | 需要财务/产品确认最终比例 |
| Q-010 | **预付费 vs 后付费：Phase 1是否支持后付费（月结）？** | 支付系统、风控 | 建议：Phase 1仅支持预付费，降低坏账风险 | 需要确认是否支持企业用户后付费 |
| Q-011 | **竞价实例的中断补偿：任务被中断后，是否补偿用户损失？** | 用户体验、成本控制 | 建议：补偿未使用时间的50%（吸引用户尝试竞价实例） | 需要确认补偿策略和预算 |
| Q-012 | **储能容量租赁的计费单位：按天计费是否合理？还是按小时更灵活？** | 商品设计、计费逻辑 | 建议：同时支持按小时和按天，满足不同场景 | 需要确认业务优先级 |
| Q-013 | **新手引导：首次使用的用户是否需要引导教程？** | 用户体验、留存率 | 建议：提供"快速上手"引导（3步完成首次下单） | 需要UI/UX设计确认 |

### 8.3 合规与法律风险待确认

| ID | 问题 | 影响范围 | 建议方案 | 需要确认 |
|----|------|----------|----------|----------|
| Q-014 | **电力交易的合规性：平台是否需要电力业务许可证？** | 法律风险、业务合法性 | 建议：咨询能源局，可能需要"增量配电网业务许可证" | 需要法务/合规团队确认 |
| Q-015 | **算力跨境交易：是否支持海外用户使用？数据出境是否合规？** | 合规、数据安全 | 建议：Phase 1仅限中国大陆用户，数据不出境 | 需要确认国际化路线图 |
| Q-016 | **碳足迹报告的法律效力：报告的审计方是谁？是否符合ISO标准？** | 信任度、市场需求 | 建议：Phase 1提供"参考报告"，Phase 2引入第三方审计 | 需要确认碳足迹报告的用途 |

### 8.4 性能与扩展性待确认

| ID | 问题 | 影响范围 | 建议方案 | 需要确认 |
|----|------|----------|----------|----------|
| Q-017 | **调度引擎的响应时间：3秒内生成报价是否可行？涉及哪些优化手段？** | 性能、用户体验 | 建议：使用缓存+异步计算，复杂场景可先返回预估价格 | 需要性能测试验证 |
| Q-018 | **资源绑定的技术实现：如何确保Pod只消耗指定源头的电力？需要K8s改造吗？** | 技术架构、K8s调度 | 建议：需要K8s调度器扩展（自定义Scheduler Plugin） | 需要确认技术可行性 |
| Q-019 | **碳足迹计算的数据来源：碳排放因子从哪里获取？实时还是离线计算？** | 数据准确性、计算性能 | 建议：使用国家发改委发布的区域电网基准线因子（每年更新） | 需要确认数据来源和更新频率 |
| Q-020 | **实时监控的数据采集频率：每秒采集一次功耗数据会不会太大？** | 存储成本、系统性能 | 建议：高频数据（1分钟）存时序数据库（InfluxDB），低频数据归档 | 需要确认存储预算 |

### 8.5 数据模型扩展性待确认

| ID | 问题 | 影响范围 | 建议方案 | 需要确认 |
|----|------|----------|----------|----------|
| Q-021 | **统一资产模型的扩展字段：目前的模型是否足够支撑未来5种商品类型？** | 系统扩展性、数据模型 | 建议：使用JSONB字段存储扩展属性，保持模型灵活性 | 需要确认未来商品类型的扩展需求 |
| Q-022 | **订单拆分逻辑：一个订单拆成"算力订单"和"能源订单"，如何保证事务一致性？** | 数据一致性、系统设计 | 建议：使用Saga模式（分布式事务），失败时自动回滚 | 需要确认分布式事务的实现方案 |

---

## 附录

### 附录A：技术架构评审检查清单

- [ ] 技术栈选型是否合理？是否满足性能和开发效率要求？
- [ ] 数据库表设计是否规范？索引是否合理？
- [ ] API设计是否符合RESTful规范？版本管理策略是否明确？
- [ ] 认证和授权机制是否安全？JWT过期策略是否合理？
- [ ] 错误处理是否完善？是否有全局异常处理器？
- [ ] 日志规范是否统一？敏感信息是否脱敏？
- [ ] 代码规范是否明确？是否有Lint工具配置？
- [ ] 测试策略是否清晰？单元测试覆盖率目标是否明确？
- [ ] 部署架构是否合理？是否有容器化配置？
- [ ] 监控和告警是否完善？关键指标是否覆盖？
- [ ] 文档是否完整？是否有API文档和部署文档？

### 附录B：参考资料

1. **FastAPI官方文档**：https://fastapi.tiangolo.com/
2. **React官方文档**：https://react.dev/
3. **Ant Design文档**：https://ant.design/docs/react/introduce
4. **PostgreSQL文档**：https://www.postgresql.org/docs/
5. **Kubernetes Scheduling Framework**：https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/
6. **OpenAPI 3.0规范**：https://swagger.io/specification/
7. **ISO 14064**：温室气体核算标准
8. **国家发改委区域电网基准线因子**：碳排放计算数据来源

---

**文档结束**

*本文档为Phase 1系统架构设计文档，后续Phase 2/3将根据技术演进和业务需求进行更新。*

**审批记录**：

| 角色 | 姓名 | 审批意见 | 日期 |
|------|------|----------|------|
| 产品经理 | 许清楚（Xu） | 待审批 | - |
| 架构师 | 高见远（Gao） | 已编写 | 2026-05-11 |
| 技术负责人 | 待定 | 待审批 | - |
| 项目经理 | 待定 | 待审批 | - |
