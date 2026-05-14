# K8s 部署指南 — 算电协同平台

本目录包含将「算电协同平台」部署到 Kubernetes（kind 本地集群）所需的所有配置文件和脚本。

## 目录结构

```
k8s/
├── namespace.yaml      # Namespace + ConfigMap + Secret
├── backend.yaml        # Backend Deployment + Service
├── frontend.yaml       # Frontend Deployment + Service
├── ingress.yaml        # Ingress 路由规则
└── kind-config.yaml    # kind 集群配置

deploy-kind.sh          # Linux/macOS 一键部署脚本
deploy-kind.bat         # Windows 一键部署脚本
```

## 快速开始

### 前提条件

| 工具 | 最低版本 | 安装说明 |
|------|----------|----------|
| Docker | 20.10+ | [docker.com](https://docs.docker.com/get-docker/) |
| kind | 0.20+ | `go install sigs.k8s.io/kind@latest` 或 [GitHub Releases](https://github.com/kubernetes-sigs/kind/releases) |
| kubectl | 1.25+ | [kubernetes.io](https://kubernetes.io/docs/tasks/tools/) |

### Linux / macOS

```bash
chmod +x deploy-kind.sh
./deploy-kind.sh
```

### Windows

```cmd
deploy-kind.bat
```

### 强制重建镜像

```bash
./deploy-kind.sh --rebuild
```

### 仅重新部署（不重建镜像）

```bash
./deploy-kind.sh --skip-build
```

## 访问应用

部署成功后，使用以下方式访问：

### 方式一：port-forward（推荐）

```bash
# 前端
kubectl port-forward -n compute-electric svc/frontend 8080:80
# 打开 http://localhost:8080

# 后端 API 文档
kubectl port-forward -n compute-electric svc/backend 8000:8000
# 打开 http://localhost:8000/docs
```

### 方式二：Ingress

```bash
# 1. 添加 hosts（需要管理员权限）
echo "127.0.0.1 compute-electric.local" | sudo tee -a /etc/hosts

# 2. 端口转发 ingress-nginx
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80

# 3. 打开 http://compute-electric.local:8080
```

## 架构说明

```
┌─────────────────────────────────────────────────────────┐
│                     Ingress (nginx)                      │
│                  compute-electric.local                  │
└────────────┬─────────────────────────┬─────────────────┘
             │                         │
     /api, /docs, /openapi.json       │  /* (SPA)
             │                         │
             ▼                         ▼
     ┌──────────────┐        ┌────────────────┐
     │  Backend svc │        │  Frontend svc  │
     │  :8000       │        │  :80           │
     └──────┬───────┘        └───────┬────────┘
            │                        │
            ▼                        ▼
     ┌──────────────┐        ┌────────────────┐
     │ Backend Pod  │        │ Frontend Pod   │
     │ (FastAPI)    │        │ (Nginx + SPA)  │
     │ replicas: 2  │        │ replicas: 2    │
     └──────────────┘        └────────────────┘
```

## 配置说明

### 环境变量（ConfigMap）

编辑 `k8s/namespace.yaml` 中的 `ConfigMap` 部分：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_ENV` | `production` | 应用环境 |
| `DATABASE_URL` | `sqlite:///data/app.db` | 数据库连接串 |
| `CORS_ORIGINS` | `http://localhost,...` | CORS 允许的源 |
| `LOG_LEVEL` | `info` | 日志级别 |

### 密钥（Secret）

**⚠️ 生产环境务必更换默认值！**

```bash
# 生成安全密钥
python -c "import secrets; print(secrets.token_hex(32))"
```

然后更新 `k8s/namespace.yaml` 中 `Secret` 的 `SECRET_KEY` 和 `JWT_SECRET_KEY`。

## 生产环境建议

当前配置适用于 **开发/测试**。生产部署请额外完成：

1. **数据库**：将 SQLite 替换为 PostgreSQL（建议云托管）
   - 修改 `DATABASE_URL` 指向外部数据库
   - 或使用 K8s PersistentVolume + PostgreSQL StatefulSet

2. **TLS 证书**：取消 `ingress.yaml` 中 TLS 部分的注释，并安装 cert-manager

3. **持久化存储**：将 `emptyDir` 替换为 `PersistentVolumeClaim`

4. **资源限制**：根据实际负载调整 `resources.requests/limits`

5. **镜像仓库**：将 `localhost:5001` 替换为私有仓库地址（如 `registry.example.com`）

6. **Secret 管理**：使用 sealed-secrets 或 Vault 管理敏感信息

## 常用命令

```bash
# 查看所有资源
kubectl get all -n compute-electric

# 查看 Pod 日志
kubectl logs -n compute-electric -l app=backend -f
kubectl logs -n compute-electric -l app=frontend -f

# 查看 Pod 状态
kubectl get pods -n compute-electric -w

# 进入 Pod 调试
kubectl exec -it -n compute-electric deploy/backend -- /bin/bash

# 删除集群
kind delete cluster --name compute-electric

# 重新构建并部署
./deploy-kind.sh --rebuild
```

## 故障排查

### Pod 无法启动

```bash
kubectl describe pod -n compute-electric <pod-name>
kubectl logs -n compute-electric <pod-name> --previous
```

### 镜像拉取失败

```bash
# 确认镜像已加载到 kind
kind load docker-image localhost:5001/compute-electric-backend:latest --name compute-electric
kind load docker-image localhost:5001/compute-electric-frontend:latest --name compute-electric
```

### Ingress 不工作

```bash
# 检查 ingress-nginx 是否运行
kubectl get pods -n ingress-nginx

# 查看 ingress 状态
kubectl describe ingress -n compute-electric
```
