# 算电协同产业互联网平台 Phase 2 增量 PRD

**版本**: v1.0
**日期**: 2026-05-12
**产品负责人**: 许清楚（Xu）
**文档状态**: 初稿

---

## 1. 产品定位与目标

### 1.1 核心定位

**Phase 1 定位**: 展示型平台框架（Demo/Standing）

**Phase 2 定位**: 真实交易平台（Production Trading Platform）

| 维度 | Phase 1 | Phase 2 |
|------|---------|---------|
| 交易真实性 | Mock 数据、Stub 支付 | 真实交易闭环、支付网关集成 |
| 监控真实性 | 随机数据生成 | 真实数据采集、时序数据库 |
| 定价机制 | 单一小时单价 | 多模式定价（Spot/预留/竞价/峰谷） |
| 能源联动 | 仅能源画像 | 绿电交易+需求响应+碳资产 |
| 结算体系 | 无 | 钱包体系+账单系统+发票管理 |

### 1.2 OKR 指标体系

| 目标 | 关键结果 |
|------|----------|
| **O1: 实现交易闭环** | KR1: 月度 GMV 突破 100 万元<br>KR2: 支付成功率 ≥ 95%<br>KR3: 订单履约率 ≥ 98% |
| **O2: 提升资源利用率** | KR1: 平台算力平均利用率 ≥ 60%（当前 Provider 侧 ~60-70%）<br>KR2: Spot 实例占比 30%+<br>KR3: 需求响应参与客户数 ≥ 10 家 |
| **O3: 打通能源交易** | KR1: 绿证交易量 ≥ 1000 张/月<br>KR2: 接入 ≥ 3 个电力交易市场<br>KR3: PUE 优化贡献 ≥ 5% |
| **O4: 建立信任体系** | KR1: 用户满意度 ≥ 4.5/5<br>KR2: 纠纷处理时效 ≤ 24h<br>KR3: 资质审核通过率 100% |

---

## 2. 用户痛点与需求分析

### 2.1 角色划分与权限体系

```
┌─────────────────────────────────────────────────────────────────┐
│                         平台运营方（Admin）                       │
│  - 用户管理（资质审核、角色分配）                                    │
│  - 价格管控（定价规则、折扣审批）                                    │
│  - 结算管理（账期结算、发票开具）                                    │
│  - 规则配置（交易规则、风控策略）                                    │
└─────────────────────────────────────────────────────────────────┘
         ▲                    ▲                    ▲
         │ 撮合/监管           │ 撮合/监管           │ 撮合/监管
         ▼                    ▼                    ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ 算力消费方     │  │ 算力提供方     │  │ 电力提供方     │
│ Consumer      │  │ Provider      │  │ Energy Provider│
│ (AI企业/科研)  │  │ (GPU集群/云)   │  │ (新能源/电网)  │
└───────────────┘  └───────────────┘  └───────────────┘
```

### 2.2 分角色痛点分析

#### 2.2.1 算力消费方（Consumer）

| 痛点 | Phase 1 表现 | Phase 2 需求 |
|------|-------------|--------------|
| 成本高昂 | 无成本分析 | 成本分解看板（算力+电力+调度成本） |
| 价格不透明 | 单一价格展示 | 竞价市场+历史价格走势 |
| 资源不稳定 | 任务无保障 | 预留实例+可用性 SLA |
| 峰谷成本差异 | 固定单价 | 谷时优惠+智能调度 |
| 算力与电力脱钩 | 无联动 | 绿电溢价+碳足迹追踪 |

**关键需求**:
1. AI 企业 GPU 成本占 OPEX 56%+，需要精细化成本管理
2. 科研机构需要 Spot 实例降低成本（可接受中断）
3. 企业用户需要可预测的月度账单

#### 2.2.2 算力提供方（Provider）

| 痛点 | Phase 1 表现 | Phase 2 需求 |
|------|-------------|--------------|
| 闲置率高 | 30-40% 闲置 | Spot 销售+竞价出清 |
| 定价单一 | 小时单价 | 动态定价+时段策略 |
| 收益不透明 | 简单汇总 | 收益明细+分润报表 |
| 资金回笼慢 | 无结算 | T+1 自动结算 |
| 峰谷利用差 | 无策略 | 需求响应激励 |

**关键需求**:
1. GPU 集群运营商需要提升利用率降低亏损
2. 云服务商需要动态定价应对峰谷
3. 超算中心需要精细化收益管理

#### 2.2.3 电力提供方（Energy Provider）

| 痛点 | Phase 1 表现 | Phase 2 需求 |
|------|-------------|--------------|
| 消纳压力 | 无入口 | 算力负荷聚合+绿电消纳 |
| 碳履约难 | 无机制 | 绿证+CCER 交易 |
| 价格波动 | 无对冲 | 长期合约+期货锁定 |
| 调度响应 | 无联动 | 需求响应接口 |

**关键需求**:
1. 新能源发电企业需要消纳算力负荷
2. 售电公司需要聚合可调负荷
3. 电网需要调度备用资源

#### 2.2.4 平台运营方（Admin）

| 痛点 | Phase 1 表现 | Phase 2 需求 |
|------|-------------|--------------|
| 风控缺失 | 无审核 | 资质审核+交易风控 |
| 结算复杂 | 手动核算 | 自动分润+电子发票 |
| 定价混乱 | 无规则 | 定价规则引擎 |
| 数据缺失 | Mock 数据 | 真实数据看板 |

**关键需求**:
1. 合规性：能源交易资质、算力服务备案
2. 结算效率：自动化 T+1 分账
3. 风控能力：交易限额、异常预警

### 2.3 Phase 1 vs Phase 2 差距矩阵

| 功能领域 | Phase 1 现状 | Phase 2 目标 | 优先级 |
|----------|-------------|--------------|--------|
| 支付系统 | Stub（改状态） | 真实支付网关 | P0 |
| 监控数据 | Mock（随机） | 真实采集存储 | P0 |
| 算力市场 | search 返回空 | 完整搜索+推荐 | P0 |
| 钱包账单 | 无 | 钱包+账单+发票 | P0 |
| 订单管理 | 简单列表 | 全生命周期管理 | P0 |
| 绿证交易 | 有字段无交易 | 绿证买卖闭环 | P1 |
| 需求响应 | 无 | 负荷聚合+响应 | P1 |
| Spot 实例 | 无 | 竞价+Spot 机制 | P1 |
| 峰谷定价 | 固定单价 | 分时定价+策略 | P1 |
| 碳交易 | 无 | CCER/VCS 交易 | P2 |
| 移动端 | 无 | App/小程序 | P2 |
| API 开放 | 无 | 开放平台 | P2 |

---

## 3. 交易主体与业务模式

### 3.1 算力交易模式

#### 3.1.1 实例类型矩阵

| 类型 | 可用性 | 价格 | 适用场景 | Phase 2 实现 |
|------|--------|------|----------|--------------|
| **预留实例** | 99.5% | 标价 100% | 生产环境、长期任务 | P0 |
| **Spot 实例** | 中断风险 | 标价 20-50% | 批处理、训练任务 | P1 |
| **竞价实例** | 实时出清 | 供需定价 | 弹性需求 | P1 |
| **按量实例** | 99.9% | 标价 150% | 临时扩容 | P0 |

#### 3.1.2 定价机制

**基础定价公式**:
```
Total = Compute_Cost + Energy_Cost + Network_Cost + Storage_Cost

Compute_Cost = Base_Price × Duration × Spec_Multiplier × Time_Discount
Energy_Cost = Power_Consumption × Electricity_Price × PUE × Duration
```

**分时定价表**（参考行业数据）:

| 时段 | 时间范围 | 价格系数 | 说明 |
|------|----------|----------|------|
| 峰时 | 09:00-12:00, 18:00-21:00 | 1.5x | 高负荷 |
| 平段 | 07:00-09:00, 12:00-18:00, 21:00-23:00 | 1.0x | 正常 |
| 谷时 | 23:00-07:00 | 0.5x | 低负荷 |

**参考定价**（基于市场数据）:
- A100 8卡整机: ~1.8万元/月 → ~27元/小时
- 单卡 A100 小时价: ~3.5元/小时（平段）
- H100 8卡整机: ~3.2万元/月 → ~48元/小时
- V100 8卡整机: ~1.2万元/月 → ~18元/小时

### 3.2 电力交易模式

#### 3.2.1 绿电交易流程

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 新能源发电方  │────▶│ 交易中心      │────▶│ 平台（聚合） │────▶│ 算力消费者   │
│ (风电/光伏)   │     │ (电网/售电)   │     │              │     │ (数据中心)    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
     │                                        │
     │ 发电凭证                               │ 绿证
     ▼                                        ▼
┌──────────────┐                        ┌──────────────┐
│ 绿证平台     │                        │ 碳账户       │
│ (国家能源局) │                        │ (消费者)     │
└──────────────┘                        └──────────────┘
```

**2024 年新规要点**:
- 电证分离结算：电力交易与绿证分离
- 绿证价格：~4.99 元/张（1MWh/张）
- 跨省交易：支持但不强制

#### 3.2.2 需求响应机制

| 响应类型 | 激励方式 | 响应时间 | 适用场景 |
|----------|----------|----------|----------|
| 调峰响应 | 容量补贴 + 度电补贴 | 10-30min | 峰时减负荷 |
| 调频响应 | 容量备用费 | 秒级 | 频率调节 |
| 现货套利 | 峰谷价差收益 | 实时 | 蓄冷/蓄热+储能 |

### 3.3 算电协同三大模式

#### 3.3.1 电随算走（空间迁移）

**场景**: 算力需求迁移到电力充裕区域

```
消费者下单 ──▶ 调度引擎评估 ──▶ 推荐低成本区域 ──▶ 任务分发

评估因素:
- 区域电价差异（西部低 30-50%）
- PUE 差异（自然冷却 vs 强制冷却）
- 网络延迟（可接受范围 50ms）
```

**案例**: 宁夏模式
- 电价降低 50%（光伏直连 + 风电交易 + 电网备用）
- 适用：离线训练、批处理任务

#### 3.3.2 算随电走（时间迁移）

**场景**: 根据电力供应调整任务执行时间

```
消费者下单 ──▶ 调度引擎判断 ──▶ 非紧急任务排队 ──▶ 谷时执行

触发条件:
- 电力现货价格 < 阈值
- 新能源出力高峰（弃风/弃光时段）
- 需求响应邀约
```

**案例**: 数据中心配合新能源出力曲线调度非紧急任务

#### 3.3.3 算优电（虚拟电厂）

**场景**: 算力负荷作为可调资源参与电网调度

```
┌─────────────────────────────────────────────────────┐
│                    虚拟电厂聚合商                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │ 算力负荷 │  │ 储能设备 │  │ 分布式源 │ ──▶ 电网调度  │
│  └─────────┘  └─────────┘  └─────────┘              │
└─────────────────────────────────────────────────────┘
```

**激励模型**:
- 需求响应补贴：~5-15 元/kW·次
- 调峰收益：~0.5-1 元/kWh
- 容量备用费：~100-300 元/kW·月

### 3.4 业务流程总览

#### 3.4.1 算力交易核心流程

```
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│ 选购   │───▶│ 下单   │───▶│ 支付   │───▶│ 执行   │───▶│ 结算   │
│ 资源   │    │ 算力   │    │ 钱包   │    │ 监控   │    │ 开票   │
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
     │             │             │             │             │
     ▼             ▼             ▼             ▼             ▼
  搜索/筛选    规格确认      余额预扣      真实监控      费用分解
  对比报价     时段选择      支付网关      告警通知      绿证抵扣
  Spot竞价    优惠叠加      退款处理      完成通知      发票申请
```

#### 3.4.2 钱包与结算流程

```
┌─────────────────────────────────────────────────────────────┐
│                         钱包体系                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │ 充值（T+0）  │     │ 消费（实时） │     │ 提现（T+1）  │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
│         │                  │                  │           │
│         ▼                  ▼                  ▼           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   账单中心                           │   │
│  │  - 消费明细  - 发票管理  - 对账管理  - 信用账期      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 需求池（按优先级）

### 4.1 P0 必须做（Phase 2 MVP）

| ID | 模块 | 需求描述 | 用户故事数 | 技术复杂度 |
|----|------|----------|-----------|------------|
| P0-01 | 支付系统 | 集成真实支付网关（支付宝/微信/银行） | 4 | 高 |
| P0-02 | 钱包体系 | 用户钱包（充值/消费/提现/退款） | 5 | 高 |
| P0-03 | 账单系统 | 月度账单生成、费用分解、发票申请 | 3 | 中 |
| P0-04 | 真实监控 | 数据采集、时序存储、可视化展示 | 4 | 高 |
| P0-05 | 订单完善 | 全生命周期管理（创建→执行→完成→评价） | 3 | 中 |
| P0-06 | 算力市场 | 资源搜索、详情页、筛选排序 | 4 | 中 |

### 4.2 P1 应该做（Phase 2.1）

| ID | 模块 | 需求描述 | 用户故事数 | 技术复杂度 |
|----|------|----------|-----------|------------|
| P1-01 | Spot 实例 | 竞价市场、实例中断保护 | 3 | 高 |
| P1-02 | 峰谷定价 | 分时定价策略、时段选择器 | 3 | 中 |
| P1-03 | 绿证交易 | 绿证购买、转让、核销 | 4 | 高 |
| P1-04 | 需求响应 | 负荷聚合、响应邀约、补贴计算 | 3 | 高 |
| P1-05 | 资质审核 | Provider 资质认证、审核流程 | 3 | 中 |

### 4.3 P2 可以做（Phase 2.2+）

| ID | 模块 | 需求描述 | 用户故事数 | 技术复杂度 |
|----|------|----------|-----------|------------|
| P2-01 | 碳交易 | CCER/VCS 账户、碳足迹追踪 | 3 | 高 |
| P2-02 | API 开放 | 开放平台、API Key 管理、用量统计 | 4 | 高 |
| P2-03 | 移动端 | App/小程序基础功能 | 5 | 高 |
| P2-04 | 数据分析 | 运营看板、成本优化建议 | 4 | 中 |
| P2-05 | 智能调度 | AI 调度引擎、策略市场 | 3 | 高 |

---

## 5. 用户故事（P0 核心需求）

### 5.1 支付系统（P0-01）

#### US-P0-01: 支付宝支付
```
作为 算力消费者，
我希望在订单确认时选择支付宝支付，
以便使用熟悉的支付方式完成算力购买。

验收标准:
- [ ] 展示支付宝收款码/跳转
- [ ] 支付成功后订单状态立即更新
- [ ] 支付失败时显示错误原因并允许重试
- [ ] 支付超时时自动取消订单并释放资源
```

#### US-P0-02: 微信支付
```
作为 算力消费者，
我希望在移动端使用微信支付，
以便快速完成小额算力购买。

验收标准:
- [ ] 微信内唤起支付
- [ ] 支付回调处理 < 3 秒
- [ ] 支付成功通知
```

#### US-P0-03: 银行卡支付（大额）
```
作为 企业算力消费者，
我希望使用企业对公账户支付，
以便完成大额算力采购（>10万）。

验收标准:
- [ ] 支持网银转账/企业支付宝
- [ ] 银行转账备注自动关联订单
- [ ] 对公发票自动开具
```

#### US-P0-04: 支付安全与风控
```
作为 平台运营方，
我希望对支付进行风控监控，
以便防范欺诈交易和资金风险。

验收标准:
- [ ] 单笔限额 50 万
- [ ] 日累计限额可配置
- [ ] 异常交易自动拦截并告警
- [ ] 人工审核队列
```

### 5.2 钱包体系（P0-02）

#### US-P0-05: 钱包充值
```
作为 算力消费者，
我希望使用多种方式向钱包充值，
以便灵活管理资金。

验收标准:
- [ ] 支持支付宝/微信/银行卡充值
- [ ] 充值即时到账
- [ ] 充值赠送优惠券（可选）
- [ ] 充值记录可查询
```

#### US-P0-06: 消费扣款
```
作为 系统，
我希望在用户下单时自动从钱包扣款，
以便简化支付流程。

验收标准:
- [ ] 余额充足时自动扣款
- [ ] 余额不足时提示充值
- [ ] 扣款明细自动记录
- [ ] 支持预授权+后付费模式
```

#### US-P0-07: 提现申请
```
作为 算力提供方，
我希望将收益提现到银行卡，
以便资金回笼。

验收标准:
- [ ] 发起提现申请
- [ ] 平台 T+1 审核
- [ ] 银行处理 1-3 工作日
- [ ] 提现手续费透明展示
```

#### US-P0-08: 退款处理
```
作为 算力消费者，
我希望申请订单退款，
以便在资源不符合预期时挽回损失。

验收标准:
- [ ] 未使用资源可全额退款
- [ ] 部分使用按比例退款
- [ ] 退款原因为必填
- [ ] 退款到账时间 ≤ 3 工作日
```

#### US-P0-09: 钱包余额预警
```
作为 算力消费者，
我希望设置余额预警，
以便及时充值避免服务中断。

验收标准:
- [ ] 设置预警阈值（金额/百分比）
- [ ] 低于阈值时短信/邮件通知
- [ ] 余额为 0 时服务宽限期 1 小时
```

### 5.3 账单系统（P0-03）

#### US-P0-10: 月度账单生成
```
作为 算力消费者，
我希望查看月度消费账单，
以便了解算力成本构成。

账单结构:
┌────────────────────────────────────────┐
│           2026年5月账单                │
├────────────────────────────────────────┤
│ 算力费用        ¥45,230.00             │
│  ├─ 预留实例    ¥32,000.00             │
│  └─ 按量实例    ¥13,230.00             │
│ 电力费用        ¥8,450.00              │
│  ├─ 绿电附加    ¥2,100.00             │
│  └─ 基础电费    ¥6,350.00             │
│ 其他费用        ¥320.00                │
│  ├─ 存储费用    ¥280.00               │
│  └─ 网络费用    ¥40.00                │
├────────────────────────────────────────┤
│ 应付总额        ¥54,000.00             │
│ 已付            ¥54,000.00             │
│ 绿证抵扣        -¥2,100.00             │
├────────────────────────────────────────┤
│ 实际应付        ¥51,900.00             │
└────────────────────────────────────────┘

验收标准:
- [ ] 每月 1 日生成上月账单
- [ ] 账单 PDF 下载
- [ ] 费用同比环比分析
```

#### US-P0-11: 发票申请
```
作为 企业财务，
我希望在线申请电子发票，
以便完成财务报销。

验收标准:
- [ ] 支持普票/专票
- [ ] 发票内容自动归集
- [ ] 电子发票自动发送到邮箱
- [ ] 专票邮寄到家
```

#### US-P0-12: 对账管理
```
作为 平台财务，
我希望核查每日交易流水，
以便确保账目准确。

验收标准:
- [ ] 日终对账单生成
- [ ] 异常流水标记
- [ ] 差异追溯到原始订单
```

### 5.4 真实监控（P0-04）

#### US-P0-13: 实时资源监控
```
作为 算力消费者，
我希望实时查看算力资源使用情况，
以便了解任务执行状态。

监控指标:
- GPU 利用率（%）
- 显存使用（GB）
- CPU 使用率（%）
- 内存使用（GB）
- 网络 I/O（MB/s）
- 磁盘 I/O（MB/s）

验收标准:
- [ ] 数据采集间隔 ≤ 5 秒
- [ ] 监控面板实时更新
- [ ] 历史数据可查询 30 天
- [ ] 支持导出 CSV/Excel
```

#### US-P0-14: 告警配置
```
作为 算力消费者，
我希望配置资源使用告警，
以便及时发现异常。

告警规则:
- GPU 利用率持续 < 10% 超过 10 分钟
- 显存使用 > 95%
- 任务失败
- 资源即将到期（提前 1/24 小时）

验收标准:
- [ ] 支持多种触发条件
- [ ] 支持邮件/短信/站内通知
- [ ] 告警记录可查询
- [ ] 告警抑制（避免轰炸）
```

#### US-P0-15: Provider 监控看板
```
作为 算力提供方，
我希望查看资源整体运行状态，
以便优化资源分配。

看板内容:
- GPU 集群总览（数量、型号、状态）
- 利用率热力图（按时段/按节点）
- 收益统计（今日/本周/本月）
- 异常告警列表

验收标准:
- [ ] 平台整体视图
- [ ] 单节点详情下钻
- [ ] 数据刷新 ≤ 30 秒
```

#### US-P0-16: 能源监控
```
作为 算力消费者，
我希望查看任务执行的能源指标，
以便评估碳足迹。

能源指标:
- 实时功耗（kW）
- PUE 值
- 电力来源（绿电/火电占比）
- 碳排放量（kgCO2）

验收标准:
- [ ] 实时功耗曲线
- [ ] PUE 历史走势
- [ ] 绿电消费证明（绿证编号）
```

### 5.5 订单完善（P0-05）

#### US-P0-17: 订单创建
```
作为 算力消费者，
我希望快速创建算力订单，
以便节省操作时间。

订单要素:
- 资源规格（GPU型号/数量）
- 时长（小时/天/月）
- 时段（峰/谷/全时）
- 能源偏好（绿电优先/不限）
- 预算上限（可选）

验收标准:
- [ ] 快速下单入口
- [ ] 订单预览确认
- [ ] 价格自动计算
- [ ] 优惠自动叠加
```

#### US-P0-18: 订单状态追踪
```
作为 算力消费者，
我希望追踪订单全生命周期状态，
以便了解任务进展。

状态流转:
pending → paid → allocating → running → completed
                ↓           ↓           ↓
             cancelled    failed     cancelled

验收标准:
- [ ] 状态变更实时推送
- [ ] 状态历史可查询
- [ ] 异常状态可反馈
```

#### US-P0-19: 订单评价
```
作为 算力消费者，
我希望对完成的订单进行评价，
以便帮助其他用户决策。

评价维度:
- 性能满意度（1-5星）
- 稳定性（1-5星）
- 响应速度（1-5星）
- 综合评价（文字）

验收标准:
- [ ] 仅已完成订单可评价
- [ ] 匿名评价选项
- [ ] 差评触发客服跟进
```

### 5.6 算力市场完善（P0-06）

#### US-P0-20: 资源搜索
```
作为 算力消费者，
我希望按多维度筛选算力资源，
以便找到性价比最高的资源。

筛选条件:
- GPU 型号（A100/H100/V100/L40S...）
- GPU 数量（1/4/8/16...）
- 显存大小（80G/40G/32G...）
- 地域（华北/华东/华南/西部）
- 价格区间
- PUE 范围
- 绿电比例

验收标准:
- [ ] 搜索结果 < 1 秒
- [ ] 支持组合筛选
- [ ] 结果排序（价格/性能/评分）
- [ ] 相似资源推荐
```

#### US-P0-21: 资源详情页
```
作为 算力消费者，
我希望查看资源完整详情，
以便做出购买决策。

详情信息:
- 基础配置（GPU/CPU/内存/存储）
- 网络条件（带宽/延迟）
- 能源指标（PUE/绿电比例/碳强度）
- 价格构成（算力+电力+服务）
- 可用性 SLA
- 用户评价

验收标准:
- [ ] 信息完整真实
- [ ] 价格计算器
- [ ] 在线咨询入口
```

#### US-P0-22: Spot 实例抢购
```
作为 成本敏感的消费者，
我希望参与 Spot 实例竞价，
以便以更低价格获取算力。

流程:
1. 浏览可用 Spot 实例
2. 设置最高出价
3. 竞价成功则立即启动
4. 中断前 5 分钟通知

验收标准:
- [ ] 实时竞价价格展示
- [ ] 出价队列可视化
- [ ] 中断保护机制
- [ ] 进度保存（checkpoint）
```

#### US-P0-23: Provider 资源发布
```
作为 算力提供方，
我希望快速发布闲置算力资源，
以便及时变现。

发布要素:
- 资源规格
- 可用时段
- 定价策略（固定/竞价）
- 最小起购量
- 服务条款

验收标准:
- [ ] 快速发布向导
- [ ] 批量发布支持
- [ ] 发布前预览确认
- [ ] 立即上线/定时上线
```

---

## 6. 功能模块设计

### 6.1 新增模块总览

```
┌─────────────────────────────────────────────────────────────────┐
│                     Phase 2 系统架构                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  支付网关   │  │  钱包服务   │  │  账单系统   │   P0 新增     │
│  │  (Payment)  │  │  (Wallet)  │  │  (Billing)  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  真实监控   │  │  算力市场   │  │  绿证交易   │   P0/P1 新增  │
│  │  (Monitor) │  │ (Marketplace│  │ (GreenPower)│              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  需求响应   │  │  资质审核   │  │  智能调度   │   P1/P2 新增  │
│  │(DemandResp) │  │(Qualify)   │  │  (Scheduler) │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 模块详细设计

#### 6.2.1 支付网关模块（Payment Gateway）

**职责**: 聚合多渠道支付能力，提供统一支付接口

**接口设计**:
```yaml
POST /api/v1/payments/create
  Request:
    order_id: string
    amount: decimal
    channel: alipay | wechat | bankcard
    callback_url: string
  Response:
    payment_id: string
    payment_url: string
    qr_code: string (base64)

POST /api/v1/payments/callback
  Request:
    payment_id: string
    status: success | failed
    amount: decimal
    trade_no: string

GET /api/v1/payments/{payment_id}
  Response:
    status: pending | success | failed
    amount: decimal
    paid_at: datetime
```

**数据模型**:
```python
class Payment:
    id: str
    order_id: str
    user_id: str
    channel: str  # alipay/wechat/bankcard
    amount: Decimal
    status: str  # pending/success/failed/refunded
    trade_no: str  # 第三方交易号
    created_at: datetime
    paid_at: datetime
```

#### 6.2.2 钱包模块（Wallet）

**职责**: 用户资金账户管理，支持充值、消费、提现、退款

**接口设计**:
```yaml
GET /api/v1/wallet/balance
  Response:
    balance: decimal
    frozen: decimal
    total_recharge: decimal
    total_consume: decimal

POST /api/v1/wallet/recharge
  Request:
    amount: decimal
    channel: alipay | wechat | bankcard
  Response:
    recharge_id: string
    payment_url: string

POST /api/v1/wallet/withdraw
  Request:
    amount: decimal
    bank_card_id: string
  Response:
    withdraw_id: string
    status: pending

POST /api/v1/wallet/refund
  Request:
    order_id: string
    amount: decimal (optional, partial refund)
    reason: string
  Response:
    refund_id: string
    refund_amount: decimal
```

**数据模型**:
```python
class Wallet:
    id: str
    user_id: str
    balance: Decimal  # 可用余额
    frozen: Decimal   # 冻结金额（提现中/预授权）
    total_recharge: Decimal
    total_withdraw: Decimal
    total_consume: Decimal
    credit_limit: Decimal  # 信用额度（可选）
    created_at: datetime
    updated_at: datetime

class Transaction:
    id: str
    wallet_id: str
    type: str  # recharge/consume/withdraw/refund/freeze/unfreeze
    amount: Decimal
    balance_after: Decimal
    order_id: str (optional)
    remark: str
    created_at: datetime
```

#### 6.2.3 账单模块（Billing）

**职责**: 账单生成、费用分解、发票管理

**接口设计**:
```yaml
GET /api/v1/bills/monthly
  Query: year=2026&month=5
  Response:
    bill_id: string
    total_amount: decimal
    compute_fee: decimal
    energy_fee: decimal
    network_fee: decimal
    storage_fee: decimal
    green_cert_discount: decimal
    invoice_status: str

POST /api/v1/bills/{bill_id}/invoice
  Request:
    type: vat_normal | vat电子 | 普通发票
    title: string
    tax_no: string
    address: string
  Response:
    invoice_id: string
    status: pending

GET /api/v1/bills/reconciliation
  Query: start_date=2026-05-01&end_date=2026-05-31
  Response:
    total_orders: int
    total_amount: decimal
    transactions: list
    discrepancies: list
```

**数据模型**:
```python
class MonthlyBill:
    id: str
    user_id: str
    year: int
    month: int
    total_amount: Decimal
    compute_fee: Decimal
    energy_fee: Decimal
    network_fee: Decimal
    storage_fee: Decimal
    green_cert_discount: Decimal
    actual_pay: Decimal
    status: str  # generated/paid/overdue
    generated_at: datetime

class Invoice:
    id: str
    bill_id: str
    user_id: str
    type: str  # vat_normal/vat_digital/normal
    title: str
    tax_no: str
    amount: Decimal
    status: str  # pending/issued/sent
    issued_at: datetime
```

#### 6.2.4 监控模块（Monitoring）

**职责**: 真实数据采集、存储、可视化、告警

**架构设计**:
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Agent 采集 │───▶│ 消息队列     │───▶│ 时序数据库   │───▶│ Dashboard  │
│ (Prometheus)│    │  (Kafka)    │    │ (InfluxDB)  │    │  (Grafana)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

**接口设计**:
```yaml
GET /api/v1/monitor/resources/{resource_id}
  Query: metric=gpu_util|memory|power&from=timestamp&to=timestamp
  Response:
    data_points: list
    aggregates:
      avg: decimal
      max: decimal
      min: decimal

POST /api/v1/monitor/alerts
  Request:
    resource_id: string
    metric: string
    condition: gt|lt|eq
    threshold: decimal
    duration: int (seconds)
    notify_channels: [email|sms|webhook]
  Response:
    alert_id: string

GET /api/v1/monitor/alerts
  Query: status=triggered|resolved
  Response:
    alerts: list
```

**数据模型**:
```python
class MetricSample:
    resource_id: str
    metric_name: str  # gpu_util/power/pue/...
    value: float
    timestamp: datetime
    tags: dict  # region=nx, provider=xxx

class AlertRule:
    id: str
    user_id: str
    resource_id: str
    metric: str
    condition: str  # gt 95
    duration: int  # seconds
    notify_channels: list
    status: str  # active/paused
    created_at: datetime
```

#### 6.2.5 算力市场模块（Marketplace）

**职责**: 资源发布、搜索、订单撮合

**接口设计**:
```yaml
GET /api/v1/marketplace/resources
  Query:
    gpu_model: string
    gpu_count: int
    region: string
    min_price: decimal
    max_price: decimal
    green_power_ratio: int (0-100)
    sort: price|performance|rating
    page: int
    page_size: int
  Response:
    total: int
    items: list[ResourceSummary]
    pagination: dict

GET /api/v1/marketplace/resources/{resource_id}
  Response:
    id: string
    provider_id: string
    specs: dict
    pricing: dict
    energy_profile: dict
    availability: float
    rating: float
    reviews: list

POST /api/v1/marketplace/resources
  Request:
    specs: dict
    available_slots: int
    pricing_type: fixed|spot|auction
    base_price: decimal
    spot_configs: dict (optional)
  Response:
    resource_id: string
    status: published
```

**数据模型**:
```python
class ComputeResource:
    id: str
    provider_id: str
    name: str
    specs: dict:
        gpu_model: str
        gpu_count: int
        vram_total: int
        cpu: str
        memory: int
        storage: int
        network_bandwidth: int
    location: dict:
        region: str
        datacenter: str
        country: str
    energy_profile: dict:
        power_source: str  # solar/wind/hydro/grid
        green_ratio: int  # 0-100
        pue: float
        carbon_intensity: float
    pricing: dict:
        type: str  # fixed/spot/auction
        unit_price: Decimal  # 元/小时
        spot_min_price: Decimal
        spot_max_price: Decimal
    availability_sla: float
    rating: float
    status: str  # online/offline/maintenance

class SpotConfig:
    resource_id: str
    min_price: Decimal
    max_price: Decimal
    interruptible: bool
    checkpoint_enabled: bool
    notification_minutes: int  # 中断前通知分钟数
```

#### 6.2.6 绿证交易模块（Green Certificate）

**职责**: 绿证购买、转让、核销、溯源

**接口设计**:
```yaml
GET /api/v1/green-cert/catalog
  Query: source_type=solar|wind|hydro
  Response:
    certificates: list
    total_capacity: int
    price_range: dict

POST /api/v1/green-cert/purchase
  Request:
    quantity: int (张，1张=1MWh)
    source_id: string (optional，指定绿电源)
    certificate_type: gec (国内绿证)| ves (国际绿证)
  Response:
    order_id: string
    total_amount: decimal
    certificates: list[cert_id]

GET /api/v1/green-cert/my-certificates
  Query: status=available|used|expired
  Response:
    certificates: list
    total_available: int
    total_used: int

POST /api/v1/green-cert/consume
  Request:
    cert_ids: list
    order_id: string (关联到算力订单)
  Response:
    consumption_id: string
    carbon_savings: decimal

GET /api/v1/green-cert/trace/{cert_id}
  Response:
    generation_time: datetime
    generation_location: string
    energy_type: string
    capacity: int
    current_holder: string
    chain_of_custody: list
```

**数据模型**:
```python
class GreenCertificate:
    id: str
    cert_type: str  # gec/ves
    source_id: str  # 绿电源ID
    capacity_mwh: int  # 容量（1张=1MWh）
    generation_time: datetime
    expiration_time: datetime  # 国内绿证2年有效期
    status: str  # available/transferred/consumed/expired
    current_owner_id: str
    original_owner_id: str
    price: Decimal
    created_at: datetime

class CertificateTransaction:
    id: str
    cert_id: str
    from_user_id: str
    to_user_id: str
    type: str  # purchase/transfer/consume
    order_id: str (optional)
    price: Decimal
    created_at: datetime
```

### 6.3 交互流程设计

#### 6.3.1 支付流程

```
用户下单 ──▶ 余额检查 ──┬─ 充足 ──▶ 钱包预扣款 ──▶ 资源分配 ──▶ 订单执行
                       │                    │
                       │ 不足 ──▶ 支付网关 ──┘                    │
                       │                    │                    ▼
                       │                    │              订单完成 ──▶ 解冻余额
                       │                    │                    │
                       ▼                    ▼                    ▼
                   充值引导           第三方支付              退款处理（如取消）
```

#### 6.3.2 Spot 实例竞价流程

```
用户浏览 Spot 市场
       │
       ▼
设置最高出价 & 选择规格
       │
       ▼
加入出价队列
       │
       ▼
┌──────┴──────┐
│ 出价 ≥ 当前价 │
└──────┬──────┘
   是          否
   │           │
   ▼           ▼
竞价成功      排队等待
   │           │
   ▼           ▼
资源分配      价格变化
（启动计时）  │
             ▼
       重新竞价 / 退出队列
```

#### 6.3.3 绿证溯源流程

```
发电企业发电 ──▶ 绿证发行 ──▶ 平台展示待售绿证
                                      │
消费者选购 ──▶ 支付购买 ──▶ 绿证过户 ──▶ 我的绿证账户
                                      │
算力消费 ──▶ 绿证核销 ──▶ 碳足迹计算 ──▶ 消费证明生成
```

---

## 7. 对比分析

### 7.1 Phase 1 vs Phase 2 架构差异

| 维度 | Phase 1 | Phase 2 |
|------|---------|---------|
| **前端** | 静态页面 + Mock | 动态渲染 + 实时数据 |
| **后端** | Stub 服务 | 真实业务逻辑 |
| **数据库** | Mock 数据 | PostgreSQL + InfluxDB |
| **监控** | 随机数生成 | Prometheus + Kafka |
| **支付** | 状态修改 | 支付网关集成 |
| **钱包** | 无 | 完整钱包体系 |
| **调度** | 简单分配 | 智能调度引擎 |
| **能源** | 画像展示 | 绿证交易 + 需求响应 |

### 7.2 技术栈对照

| 组件 | Phase 1 | Phase 2 |
|------|---------|---------|
| 前端框架 | Bootstrap + jQuery | Vue3/React + Ant Design |
| 后端框架 | Express (stub) | Node.js + 业务服务 |
| 数据库 | MySQL (mock) | PostgreSQL (生产) |
| 监控存储 | 无 | InfluxDB + Kafka |
| 监控可视化 | ECharts (mock) | Grafana (真实) |
| 支付集成 | 无 | 支付宝/微信 SDK |
| 钱包 | 无 | 独立钱包服务 |
| 缓存 | 无 | Redis |
| 消息队列 | 无 | Kafka |
| 容器 | 无 | Docker + K8s |

### 7.3 竞品差异化定位

| 平台 | 定位 | Phase 2 差异化 |
|------|------|---------------|
| **国家算力互联网** | 全国统一调度 | 市场化交易 + 绿电联动 |
| **宁夏算力交易平台** | 政府主导试点 | 更丰富定价模式 + 完整钱包 |
| **超算互联网** | 超算资源共享 | 普惠算力 + 按需调度 |
| **上海算力平台** | 规模扩张 | 算电协同 + 碳交易 |
| **Phase 2（我们）** | 产业互联网平台 | 算力+电力+碳资产三合一 + 智能调度 |

### 7.4 Phase 2 核心竞争优势

1. **算电联动**: 全国首个真正实现"算随电走"的商业平台
2. **绿电直供**: 打通绿证交易全链路，支持碳足迹溯源
3. **灵活定价**: 支持 Spot/预留/竞价/峰谷多种模式
4. **智能调度**: AI 驱动的资源匹配和任务调度
5. **完整闭环**: 从资源发布到结算开票的全链路服务

---

## 8. 待确认问题

### 8.1 商业模式相关

| # | 问题 | 选项 | 建议 |
|---|------|------|------|
| Q1 | 平台收费模式 | A. 抽佣（3-5%） B. 会员费 C. 混合 | 建议 A+基础服务免费 |
| Q2 | 绿证定价策略 | A. 平台统一定价 B. 市场化竞价 | 建议 A+B（固定+竞价） |
| Q3 | Spot 中断补偿 | A. 免单 B. 优惠券 C. 余额退还 | 建议按比例退还 |
| Q4 | 账期结算周期 | A. T+0 B. T+1 C. 月结 | 建议 T+1 结算+月对账 |

### 8.2 技术实现相关

| # | 问题 | 选项 | 建议 |
|---|------|------|------|
| Q5 | 支付网关选型 | A. 聚合支付 B. 独立对接 | 建议聚合支付（Ping++） |
| Q6 | 监控数据采集 | A. Agent 推送 B. 平台拉取 C. 混合 | 建议 Provider 安装 Agent |
| Q7 | 能源数据来源 | A. 手动填报 B. 电表对接 C. 估算 | 建议 V2 手动+V3 电表对接 |
| Q8 | 调度策略引擎 | A. 规则引擎 B. AI 优化 | 建议 V2 规则+V3 AI |

### 8.3 合规相关

| # | 问题 | 选项 | 建议 |
|---|------|------|------|
| Q9 | 支付资质 | A. 自有牌照 B. 第三方服务 | 必须第三方（支付宝/微信） |
| Q10 | 能源交易资质 | A. 平台持牌 B. 合作模式 | 建议合作模式（售电公司） |
| Q11 | 数据跨境 | A. 不涉及 B. 需要评估 | 如涉及国际绿证需评估 |
| Q12 | 实名认证 | A. 基础认证 B. 高级认证 | 建议消费≥1万需高级认证 |

---

## 附录

### A. 术语表

| 术语 | 定义 |
|------|------|
| **PUE** | Power Usage Effectiveness，数据中心能效比，理想值 1.0 |
| **Spot 实例** | 可中断实例，价格低廉但可能随时被回收 |
| **绿证** | 绿色电力证书，1MWh 绿电对应 1 张绿证 |
| **CCER** | 中国核证自愿减排量 |
| **VCS** | Verra Carbon Standard，国际自愿碳标准 |
| **需求响应** | 电力用户根据电网信号调整用电行为的机制 |
| **虚拟电厂** | 聚合分布式能源形成可调度的"虚拟"发电厂 |

### B. 参考数据来源

1. 国家能源局：绿证相关政策（2024）
2. 国家发改委：绿色电力交易规则（2023）
3. 中国信通院：算力发展白皮书（2024）
4. 行业调研：A100/H100 租赁市场价格（2024Q2）
5. 宁夏算力平台：实际运营数据参考

### C. 版本历史

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v0.1 | 2026-05-12 | 许清楚 | 初稿完成 |
| v1.0 | 2026-05-12 | 许清楚 | PRD 正式版 |

---

**文档结束**
