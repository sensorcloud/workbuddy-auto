# 算电协同产业互联网平台 (Phase 1)

> Computing-Electricity Collaborative Industrial Internet Platform

## 项目简介

算电协同产业互联网平台是面向算力与电力协同调度场景的一体化平台，第一期实现了核心功能框架，包括算力市场、调度中心、资产管理、监控中心、订单管理和用户中心等模块。

## 技术栈

### 前端
- **React 18** + **TypeScript**
- **Ant Design 5** - UI 组件库
- **Vite** - 构建工具
- **Zustand** - 状态管理
- **ECharts** - 数据可视化
- **React Router v6** - 路由

### 后端
- **FastAPI** - Web 框架
- **SQLAlchemy 2.0** - ORM
- **Pydantic V2** - 数据验证
- **JWT** - 身份认证
- **SQLite** - 数据库（开发环境）

## 项目结构

```
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── components/      # 公共组件
│   │   ├── pages/           # 页面组件
│   │   │   ├── Home/        # 首页
│   │   │   ├── Marketplace/ # 算力市场
│   │   │   ├── Scheduling/  # 调度中心
│   │   │   ├── AssetManagement/ # 资产管理
│   │   │   ├── Monitoring/  # 监控中心
│   │   │   ├── Orders/      # 订单管理
│   │   │   └── UserCenter/  # 用户中心（登录/注册）
│   │   ├── router/          # 路由配置
│   │   ├── services/        # API 服务
│   │   ├── store/           # 状态管理
│   │   └── types/           # TypeScript 类型
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── schemas/         # 数据验证
│   │   └── services/        # 业务逻辑
│   ├── requirements.txt
│   └── test_api.py
├── PRD-算电协同平台-Phase1.md      # 产品需求文档
├── Architecture-算电协同平台-Phase1.md # 架构设计文档
├── TestReport-算电协同平台-Phase1.md   # 测试报告
└── VerificationReport-Phase1.md       # 验收报告
```

## 快速启动

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

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

| 模块 | 说明 |
|------|------|
| 首页 | 平台概览、数据统计、快捷入口 |
| 算力市场 | 算力资源浏览、筛选、下单 |
| 调度中心 | 任务调度、资源分配、执行监控 |
| 资产管理 | 数字资产管理、收益统计 |
| 监控中心 | 实时监控、告警、性能指标 |
| 订单管理 | 订单列表、状态追踪、历史记录 |
| 用户中心 | 登录注册、个人信息管理 |

## License

Proprietary - All rights reserved.
