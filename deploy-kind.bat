@echo off
REM deploy-kind.bat - Windows deployment script for kind cluster
REM Usage: deploy-kind.bat [--rebuild] [--skip-build] [--help]

setlocal EnableDelayedExpansion

set CLUSTER_NAME=compute-electric
set BACKEND_IMAGE=localhost:5001/compute-electric-backend:latest
set FRONTEND_IMAGE=localhost:5001/compute-electric-frontend:latest
set REBUILD=false
set SKIP_BUILD=false
set SCRIPT_DIR=%~dp0
set K8S_DIR=%SCRIPT_DIR%k8s

:parse_args
if "%~1"=="" goto :main
if "%~1"=="--rebuild" (
    set REBUILD=true
    shift
    goto :parse_args
)
if "%~1"=="--skip-build" (
    set SKIP_BUILD=true
    shift
    goto :parse_args
)
if "%~1"=="--help" goto :usage
if "%~1"=="-h" goto :usage
echo [ERROR] Unknown option: %~1
goto :usage

:usage
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --rebuild       Force rebuild Docker images
echo   --skip-build    Skip Docker build (use existing images)
echo   --help          Show this help
echo.
echo Examples:
echo   %0                    - Full deploy
echo   %0 --rebuild          - Force rebuild
echo   %0 --skip-build       - Deploy only
goto :eof

:main
echo [INFO] Checking prerequisites...

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH.
    exit /b 1
)
echo [INFO]   ✓ Docker found

REM Check kind
kind --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] kind is not installed or not in PATH.
    echo         Install: go install sigs.k8s.io/kind@latest
    echo         Or download: https://github.com/kubernetes-sigs/kind/releases
    exit /b 1
)
echo [INFO]   ✓ kind found

REM Check kubectl
kubectl version --client >nul 2>&1
if errorlevel 1 (
    echo [ERROR] kubectl is not installed or not in PATH.
    exit /b 1
)
echo [INFO]   ✓ kubectl found

REM Check Docker daemon
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker daemon is not running. Please start Docker Desktop.
    exit /b 1
)
echo [INFO]   ✓ Docker daemon is running

REM Step 1: Create or reuse kind cluster
echo [INFO] Step 1: Ensuring kind cluster '%CLUSTER_NAME%' exists...
kind get clusters 2>nul | findstr /C:"%CLUSTER_NAME%" >nul
if errorlevel 1 (
    echo [INFO] Creating kind cluster from %K8S_DIR%\kind-config.yaml...
    kind create cluster --name %CLUSTER_NAME% --config "%K8S_DIR%\kind-config.yaml"
) else (
    echo [WARN] Cluster '%CLUSTER_NAME%' already exists. Reusing it.
)

REM Set kubectl context
kubectl config use-context kind-%CLUSTER_NAME%
echo [INFO]   ✓ kubectl context set to kind-%CLUSTER_NAME%

REM Step 2: Build Docker images
if "%SKIP_BUILD%"=="false" (
    echo [INFO] Step 2: Building Docker images...

    if "%REBUILD%"=="true" (
        echo [INFO]   Building backend image...
        docker build -t %BACKEND_IMAGE% "%SCRIPT_DIR%backend"
        echo [INFO]   Building frontend image...
        docker build -t %FRONTEND_IMAGE% "%SCRIPT_DIR%frontend"
    ) else (
        docker image inspect %BACKEND_IMAGE% >nul 2>&1
        if errorlevel 1 (
            echo [INFO]   Building backend image...
            docker build -t %BACKEND_IMAGE% "%SCRIPT_DIR%backend"
        ) else (
            echo [WARN]   Backend image already exists. Use --rebuild to force.
        )
        docker image inspect %FRONTEND_IMAGE% >nul 2>&1
        if errorlevel 1 (
            echo [INFO]   Building frontend image...
            docker build -t %FRONTEND_IMAGE% "%SCRIPT_DIR%frontend"
        ) else (
            echo [WARN]   Frontend image already exists. Use --rebuild to force.
        )
    )

    REM Step 3: Load images into kind
    echo [INFO] Step 3: Loading images into kind cluster...
    kind load docker-image %BACKEND_IMAGE% --name %CLUSTER_NAME%
    kind load docker-image %FRONTEND_IMAGE% --name %CLUSTER_NAME%
    echo [INFO]   ✓ Images loaded
) else (
    echo [WARN] Skipping image build (--skip-build set)
)

REM Step 4: Deploy to Kubernetes
echo [INFO] Step 4: Deploying to Kubernetes...

echo [INFO]   Applying namespace & config...
kubectl apply -f "%K8S_DIR%\namespace.yaml"

echo [INFO]   Applying backend deployment...
kubectl apply -f "%K8S_DIR%\backend.yaml"

echo [INFO]   Applying frontend deployment...
kubectl apply -f "%K8S_DIR%\frontend.yaml"

REM Install ingress-nginx if not present
kubectl get namespace ingress-nginx >nul 2>&1
if errorlevel 1 (
    echo [INFO]   Installing ingress-nginx...
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
    echo [INFO]   Waiting for ingress-nginx to be ready...
    kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=120s
)
echo [INFO]   Applying ingress...
kubectl apply -f "%K8S_DIR%\ingress.yaml"

REM Step 5: Wait for rollout
echo [INFO] Step 5: Waiting for deployments to roll out...
kubectl rollout status deployment/backend -n compute-electric --timeout=120s
kubectl rollout status deployment/frontend -n compute-electric --timeout=120s

REM Step 6: Show status
echo [INFO] Step 6: Deployment status
kubectl get all -n compute-electric

REM Step 7: Access instructions
echo.
echo ===================================================
echo   Deployment complete!
echo.
echo   Access the application:
echo.
echo   Option 1 - kubectl port-forward:
echo     kubectl port-forward -n compute-electric svc/frontend 8080:80
echo     Then open: http://localhost:8080
echo.
echo   Option 2 - Ingress:
echo     kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
echo     Then open: http://localhost:8080
echo.
echo   Backend API docs:
echo     kubectl port-forward -n compute-electric svc/backend 8000:8000
echo     Then open: http://localhost:8000/docs
echo.
echo   To tear down: kind delete cluster --name %CLUSTER_NAME%
echo ===================================================
