#!/usr/bin/env bash
# deploy-kind.sh — One-click deployment script for kind cluster
# Usage: ./deploy-kind.sh [--rebuild] [--skip-build] [--help]
#
# Prerequisites (auto-checked):
#   - Docker (running)
#   - kind CLI
#   - kubectl
#   - (optional) helm 3.x

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="${SCRIPT_DIR}/k8s"
CLUSTER_NAME="compute-electric"
BACKEND_IMAGE="localhost:5001/compute-electric-backend:latest"
FRONTEND_IMAGE="localhost:5001/compute-electric-frontend:latest"
REBUILD=false
SKIP_BUILD=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }

usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Options:
  --rebuild       Force rebuild Docker images even if they exist
  --skip-build    Skip Docker build (use existing images in kind)
  --help          Show this help message

Examples:
  $0                    # Full deploy (build + deploy)
  $0 --rebuild          # Force rebuild images
  $0 --skip-build       # Deploy only (no rebuild)
EOF
    exit 0
}

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --rebuild)    REBUILD=true; shift ;;
        --skip-build)  SKIP_BUILD=true; shift ;;
        --help|-h)    usage ;;
        *)             err "Unknown option: $1"; usage ;;
    esac
done

# ── Prerequisite checks ──────────────────────────────────────────
log "Checking prerequisites..."

check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        err "'$1' is not installed. Please install it and retry."
        exit 1
    fi
    log "  ✓ $1 found: $(command -v "$1")"
}

check_cmd docker
check_cmd kind
check_cmd kubectl

# Check Docker daemon
if ! docker info &>/dev/null; then
    err "Docker daemon is not running. Please start Docker Desktop / Docker Engine."
    exit 1
fi
log "  ✓ Docker daemon is running"

# ── Step 1: Create / reuse kind cluster ────────────────────────
log "Step 1: Ensuring kind cluster '${CLUSTER_NAME}' exists..."

if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    warn "Cluster '${CLUSTER_NAME}' already exists. Reusing it."
    warn "To delete and recreate, run: kind delete cluster --name ${CLUSTER_NAME}"
else
    log "Creating kind cluster from ${K8S_DIR}/kind-config.yaml..."
    kind create cluster --name "${CLUSTER_NAME}" --config "${K8S_DIR}/kind-config.yaml"
fi

# Set kubectl context
kubectl cluster-info --context "kind-${CLUSTER_NAME}"
log "  ✓ kubectl context set to kind-${CLUSTER_NAME}"

# ── Step 2: Build Docker images ─────────────────────────────────
if [ "$SKIP_BUILD" = false ]; then
    log "Step 2: Building Docker images..."

    # Backend
    if [ "$REBUILD" = true ] || ! docker image inspect "${BACKEND_IMAGE}" &>/dev/null; then
        log "  Building backend image..."
        docker build -t "${BACKEND_IMAGE}" "${SCRIPT_DIR}/backend"
    else
        warn "  Backend image already exists. Use --rebuild to force rebuild."
    fi

    # Frontend
    if [ "$REBUILD" = true ] || ! docker image inspect "${FRONTEND_IMAGE}" &>/dev/null; then
        log "  Building frontend image..."
        docker build -t "${FRONTEND_IMAGE}" "${SCRIPT_DIR}/frontend"
    else
        warn "  Frontend image already exists. Use --rebuild to force rebuild."
    fi

    # ── Step 3: Load images into kind ───────────────────────────
    log "Step 3: Loading images into kind cluster..."
    kind load docker-image "${BACKEND_IMAGE}" --name "${CLUSTER_NAME}"
    kind load docker-image "${FRONTEND_IMAGE}" --name "${CLUSTER_NAME}"
    log "  ✓ Images loaded"
else
    warn "Skipping image build (--skip-build set)"
fi

# ── Step 4: Deploy to Kubernetes ───────────────────────────────
log "Step 4: Deploying to Kubernetes..."

log "  Applying namespace & config..."
kubectl apply -f "${K8S_DIR}/namespace.yaml"

log "  Applying backend deployment..."
kubectl apply -f "${K8S_DIR}/backend.yaml"

log "  Applying frontend deployment..."
kubectl apply -f "${K8S_DIR}/frontend.yaml"

log "  Applying ingress..."
# Install ingress-nginx if not present
if ! kubectl get namespace ingress-nginx &>/dev/null; then
    log "  Installing ingress-nginx..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    log "  Waiting for ingress-nginx to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s
fi
kubectl apply -f "${K8S_DIR}/ingress.yaml"

# ── Step 5: Wait for rollout ────────────────────────────────────
log "Step 5: Waiting for deployments to roll out..."

kubectl rollout status deployment/backend -n compute-electric --timeout=120s
kubectl rollout status deployment/frontend -n compute-electric --timeout=120s

# ── Step 6: Show status ─────────────────────────────────────────
log "Step 6: Deployment status"
echo ""
kubectl get all -n compute-electric
echo ""

# ── Step 7: Access instructions ────────────────────────────────
log "Deployment complete! 🎉"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Access the application:"
echo ""
echo "  Option 1 — kubectl port-forward:"
echo "    kubectl port-forward -n compute-electric svc/frontend 8080:80"
echo "    Then open: http://localhost:8080"
echo ""
echo "  Option 2 — Add to /etc/hosts and use Ingress:"
echo "    echo '127.0.0.1 compute-electric.local' | sudo tee -a /etc/hosts"
echo "    kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80"
echo "    Then open: http://compute-electric.local:8080"
echo ""
echo "  Backend API docs:"
echo "    kubectl port-forward -n compute-electric svc/backend 8000:8000"
echo "    Then open: http://localhost:8000/docs"
echo ""
echo "  Cluster dashboard:"
echo "    kubectl get pods -n compute-electric -w"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
log "To tear down: kind delete cluster --name ${CLUSTER_NAME}"
