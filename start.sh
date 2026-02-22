#!/bin/bash

# HZAUACMOJ 启动脚本
# 用于在Ubuntu系统上直接启动项目服务（不使用Docker）

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

# 服务端口配置
BACKEND_PORT=8000
FRONTEND_PORT=3000

# PID文件路径
BACKEND_PID="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID="$PROJECT_ROOT/.frontend.pid"
JUDGE_PID="$PROJECT_ROOT/.judge.pid"

# 日志文件路径
BACKEND_LOG="$PROJECT_ROOT/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/frontend.log"
JUDGE_LOG="$PROJECT_ROOT/judge.log"

# 版本要求
REQUIRED_PYTHON_VERSION="3.8"
REQUIRED_NODE_VERSION="14.0"

# 帮助信息
show_help() {
    echo "HZAUACMOJ 项目启动脚本（无Docker版本）"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help           显示帮助信息"
    echo "  -a, --all            启动所有服务（默认）"
    echo "  -b, --backend        只启动后端服务"
    echo "  -f, --frontend       只启动前端服务"
    echo "  -j, --judge          只启动评测机服务"
    echo "  -s, --services       指定要启动的服务，用空格分隔（如：backend frontend）"
    echo "  -d, --down           停止所有服务"
    echo "  -r, --restart        重启所有服务"
    echo "  --install-deps       只安装依赖（不启动服务）"
    echo "  --install-docker     安装Docker（用于评测功能）"
    echo "  --install-all        安装所有依赖和Docker"
    echo ""
    echo "示例:"
    echo "  $0                    # 启动所有服务"
    echo "  $0 --backend --frontend  # 只启动后端和前端"
    echo "  $0 --services backend judge  # 只启动后端和评测机"
    echo "  $0 --down            # 停止所有服务"
    echo "  $0 --install-deps    # 安装所有依赖"
    echo "  $0 --install-docker  # 安装Docker"
    echo "  $0 --install-all     # 安装依赖和Docker"
}

# 检查命令是否存在
check_command() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Python是否安装
check_python() {
    if ! check_command python3; then
        echo "错误: Python 3 未安装"
        echo "请运行: sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
        return 1
    fi

    # 检查Python版本
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    if ! version_check "$PYTHON_VERSION" "$REQUIRED_PYTHON_VERSION"; then
        echo "警告: Python 版本过低（当前: $PYTHON_VERSION, 要求: $REQUIRED_PYTHON_VERSION+）"
        echo "部分功能可能无法正常工作"
    fi

    echo "✓ Python 已安装"
    return 0
}

# 检查Node.js是否安装
check_node() {
    if ! check_command node; then
        echo "错误: Node.js 未安装"
        echo "请按照以下步骤安装 Node.js:"
        echo "  1. curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -"
        echo "  2. sudo apt-get install -y nodejs"
        return 1
    fi

    # 检查Node.js版本
    NODE_VERSION=$(node --version | sed 's/^v//')
    if ! version_check "$NODE_VERSION" "$REQUIRED_NODE_VERSION"; then
        echo "警告: Node.js 版本过低（当前: $NODE_VERSION, 要求: $REQUIRED_NODE_VERSION+）"
        echo "部分功能可能无法正常工作"
    fi

    echo "✓ Node.js 已安装"
    return 0
}

# 检查npm是否安装
check_npm() {
    if ! check_command npm; then
        echo "错误: npm 未安装"
        echo "请运行: sudo apt update && sudo apt install -y npm"
        return 1
    fi

    echo "✓ npm 已安装"
    return 0
}

# 安装Docker
install_docker() {
    echo "正在安装Docker..."
    
    # 检查Docker是否已安装
    if docker info > /dev/null 2>&1; then
        echo "✓ Docker已安装"
        return 0
    fi
    
    # 检查是否有sudo权限
    if ! sudo -v > /dev/null 2>&1; then
        echo "错误: 需要sudo权限来安装Docker"
        return 1
    fi
    
    # 更新包管理器
    echo "更新系统包..."
    sudo apt-get update -y
    
    # 安装Docker依赖
    echo "安装Docker依赖包..."
    sudo apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
    
    # 添加Docker GPG密钥
    echo "添加Docker GPG密钥..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    
    # 添加Docker仓库
    echo "添加Docker仓库..."
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    
    # 再次更新包管理器
    sudo apt-get update -y
    
    # 安装Docker
    echo "安装Docker CE..."
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # 启动Docker服务
    echo "启动Docker服务..."
    sudo systemctl start docker
    
    # 启用Docker开机自启
    sudo systemctl enable docker
    
    # 检查Docker是否安装成功
    if docker info > /dev/null 2>&1; then
        echo "✓ Docker安装成功"
        return 0
    else
        echo "✗ Docker安装失败"
        return 1
    fi
}

# 版本检查函数 (检查第一个版本是否大于等于第二个版本)
version_check() {
    local v1="$1"
    local v2="$2"
    
    if [[ "$v1" == "$v2" ]]; then
        return 0
    fi
    
    local IFS="."
    local -a ver1=($v1)
    local -a ver2=($v2)
    
    for ((i=0; i<${#ver1[@]} || i<${#ver2[@]}; i++)); do
        local num1=${ver1[i]:-0}
        local num2=${ver2[i]:-0}
        
        if ((num1 > num2)); then
            return 0
        elif ((num1 < num2)); then
            return 1
        fi
    done
    
    return 0
}

# 安装后端依赖
install_backend_deps() {
    echo "正在安装后端依赖..."
    
    cd "$PROJECT_ROOT/backend" || { echo "错误: 无法进入后端目录"; return 1; }
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        echo "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip（增加超时处理）
    echo "升级pip..."
    if ! pip install --upgrade pip --timeout 60; then
        echo "警告: pip升级失败，继续安装依赖..."
    fi
    
    # 安装依赖（增加超时处理）
    echo "安装Python依赖包..."
    if [ -f "requirements.txt" ]; then
        if pip install -r requirements.txt --timeout 60; then
            echo "✓ 后端依赖安装完成"
        else
            echo "✗ 后端依赖安装失败，可能是网络问题"
            echo "提示：可以尝试设置pip镜像源来加速下载"
            echo "例如：pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple"
            deactivate
            return 1
        fi
    else
        echo "错误: requirements.txt 文件不存在"
        deactivate
        return 1
    fi
    
    # 退出虚拟环境
    deactivate
    
    return 0
}

# 安装前端依赖
install_frontend_deps() {
    echo "正在安装前端依赖..."
    
    cd "$PROJECT_ROOT/frontend" || { echo "错误: 无法进入前端目录"; return 1; }
    
    # 安装npm依赖
    if [ -f "package.json" ]; then
        npm install
    else
        echo "错误: package.json 文件不存在"
        return 1
    fi
    
    echo "✓ 前端依赖安装完成"
    return 0
}

# 安装评测机依赖
install_judge_deps() {
    echo "正在安装评测机依赖..."
    
    cd "$PROJECT_ROOT/judge" || { echo "错误: 无法进入评测机目录"; return 1; }
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        echo "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip（增加超时处理）
    echo "升级pip..."
    if ! pip install --upgrade pip --timeout 60; then
        echo "警告: pip升级失败，继续安装依赖..."
    fi
    
    # 安装依赖（增加超时处理）
    echo "安装Python依赖包..."
    if [ -f "requirements.txt" ]; then
        if pip install -r requirements.txt --timeout 60; then
            echo "✓ 评测机依赖安装完成"
        else
            echo "✗ 评测机依赖安装失败，可能是网络问题"
            echo "提示：可以尝试设置pip镜像源来加速下载"
            echo "例如：pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple"
            deactivate
            return 1
        fi
    else
        echo "错误: requirements.txt 文件不存在"
        deactivate
        return 1
    fi
    
    # 退出虚拟环境
    deactivate
    
    return 0
}

# 安装所有依赖
install_all_deps() {
    install_backend_deps && install_frontend_deps && install_judge_deps
    return $?
}

# 检查服务是否运行
is_service_running() {
    local pid_file="$1"
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid >/dev/null 2>&1; then
            return 0  # 服务正在运行
        else
            rm -f "$pid_file"  # PID文件存在但进程不存在，删除PID文件
            return 1  # 服务未运行
        fi
    fi
    return 1  # 服务未运行
}

# 启动后端服务
start_backend() {
    if is_service_running "$BACKEND_PID"; then
        echo "后端服务已在运行"
        return 0
    fi
    
    echo "正在启动后端服务..."
    
    cd "$PROJECT_ROOT/backend" || { echo "错误: 无法进入后端目录"; return 1; }
    
    # 检查虚拟环境是否存在
    if [ ! -d "venv" ]; then
        echo "错误: 后端虚拟环境不存在，请先安装依赖"
        echo "请运行: ./start.sh --install-deps"
        return 1
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 运行Django开发服务器
    python manage.py runserver $BACKEND_PORT > "$BACKEND_LOG" 2>&1 &
    
    local pid=$!
    
    # 将PID写入PID文件
    echo $pid > "$BACKEND_PID"
    
    # 检查服务是否启动成功
    sleep 3
    if is_service_running "$BACKEND_PID"; then
        echo "✓ 后端服务启动成功（PID: $pid）"
        return 0
    else
        echo "✗ 后端服务启动失败"
        echo "查看日志: tail -n 50 $BACKEND_LOG"
        return 1
    fi
}

# 启动前端服务
start_frontend() {
    if is_service_running "$FRONTEND_PID"; then
        echo "前端服务已在运行"
        return 0
    fi
    
    echo "正在启动前端服务..."
    
    cd "$PROJECT_ROOT/frontend" || { echo "错误: 无法进入前端目录"; return 1; }
    
    # 检查依赖是否已安装
    if [ ! -d "node_modules" ]; then
        echo "错误: 前端依赖未安装，请先安装依赖"
        echo "请运行: ./start.sh --install-deps"
        return 1
    fi
    
    # 启动Vite开发服务器
    npm run dev > "$FRONTEND_LOG" 2>&1 &
    
    local pid=$!
    
    # 将PID写入PID文件
    echo $pid > "$FRONTEND_PID"
    
    # 检查服务是否启动成功
    sleep 5
    if is_service_running "$FRONTEND_PID"; then
        echo "✓ 前端服务启动成功（PID: $pid）"
        return 0
    else
        echo "✗ 前端服务启动失败"
        echo "查看日志: tail -n 50 $FRONTEND_LOG"
        return 1
    fi
}

# 启动评测机服务
start_judge() {
    if is_service_running "$JUDGE_PID"; then
        echo "评测机服务已在运行"
        return 0
    fi
    
    echo "正在启动评测机服务..."
    
    # 检查Docker是否可用
    if ! docker info > /dev/null 2>&1; then
        echo "⚠️  Docker不可用，评测机需要Docker支持"
        echo "提示：如果要使用评测功能，请安装Docker并启动Docker服务"
        echo "安装命令: sudo apt-get install docker-ce docker-ce-cli containerd.io"
        echo "启动服务: sudo systemctl start docker"
        return 1
    fi
    
    cd "$PROJECT_ROOT/judge" || { echo "错误: 无法进入评测机目录"; return 1; }
    
    # 检查虚拟环境是否存在
    if [ ! -d "venv" ]; then
        echo "错误: 评测机虚拟环境不存在，请先安装依赖"
        echo "请运行: ./start.sh --install-deps"
        return 1
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 运行评测机
    python judge.py > "$JUDGE_LOG" 2>&1 &
    
    local pid=$!
    
    # 将PID写入PID文件
    echo $pid > "$JUDGE_PID"
    
    # 检查服务是否启动成功
    sleep 3
    if is_service_running "$JUDGE_PID"; then
        echo "✓ 评测机服务启动成功（PID: $pid）"
        return 0
    else
        echo "✗ 评测机服务启动失败"
        echo "查看日志: tail -n 50 $JUDGE_LOG"
        return 1
    fi
}

# 启动服务
start_services() {
    local services="$1"
    local success=0
    
    echo "正在启动服务..."
    echo "项目目录: $PROJECT_ROOT"
    
    # 默认启动所有服务
    if [ -z "$services" ]; then
        echo "启动所有服务..."
        start_backend && start_frontend && start_judge
        success=$?
    else
        echo "启动指定服务: $services"
        for service in $services; do
            case "$service" in
                backend)
                    start_backend || success=1
                    ;;
                frontend)
                    start_frontend || success=1
                    ;;
                judge)
                    start_judge || success=1
                    ;;
                *)
                    echo "警告: 未知服务 '$service'"
                    success=1
                    ;;
            esac
        done
    fi
    
    if [ $success -eq 0 ]; then
        echo "✓ 服务启动成功"
        show_service_status
    else
        echo "✗ 部分服务启动失败"
        exit 1
    fi
}

# 停止单个服务
stop_service() {
    local service_name="$1"
    local pid_file=""
    
    case "$service_name" in
        backend)
            pid_file="$BACKEND_PID"
            ;;
        frontend)
            pid_file="$FRONTEND_PID"
            ;;
        judge)
            pid_file="$JUDGE_PID"
            ;;
        *)
            echo "警告: 未知服务 '$service_name'"
            return 1
            ;;
    esac
    
    if is_service_running "$pid_file"; then
        local pid=$(cat "$pid_file")
        echo "正在停止$service_name服务（PID: $pid）..."
        kill $pid
        
        # 等待进程终止
        for i in {1..10}; do
            if ! is_service_running "$pid_file"; then
                break
            fi
            sleep 1
        done
        
        if is_service_running "$pid_file"; then
            echo "✗ $service_name服务停止失败，强制终止..."
            kill -9 $pid
        fi
        
        # 确保PID文件被删除
        rm -f "$pid_file"
        echo "✓ $service_name服务已停止"
    else
        echo "$service_name服务未在运行"
    fi
}

# 停止服务
stop_services() {
    local services="$1"
    
    echo "正在停止服务..."
    
    # 默认停止所有服务
    if [ -z "$services" ]; then
        echo "停止所有服务..."
        stop_service backend
        stop_service frontend
        stop_service judge
    else
        echo "停止指定服务: $services"
        for service in $services; do
            stop_service "$service"
        done
    fi
    
    echo "✓ 服务停止完成"
}

# 显示服务状态
show_service_status() {
    echo ""
    echo "服务状态:"
    echo "- 后端服务: $(is_service_running "$BACKEND_PID" && echo "运行中" || echo "已停止")"
    echo "- 前端服务: $(is_service_running "$FRONTEND_PID" && echo "运行中" || echo "已停止")"
    echo "- 评测机服务: $(is_service_running "$JUDGE_PID" && echo "运行中" || echo "已停止")"
    
    echo ""
    echo "访问地址:"
    echo "- 后端API: http://localhost:$BACKEND_PORT"
    echo "- 前端: http://localhost:$FRONTEND_PORT"
    
    echo ""
    echo "查看日志:"
    echo "- 后端日志: tail -n 50 $BACKEND_LOG"
    echo "- 前端日志: tail -n 50 $FRONTEND_LOG"
    echo "- 评测机日志: tail -n 50 $JUDGE_LOG"
}

# 主函数
main() {
    local services=""
    local action="start"
    local install_deps=false
    local install_docker=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -a|--all)
                services=""
                shift
                ;;
            -b|--backend)
                services="$services backend"
                shift
                ;;
            -f|--frontend)
                services="$services frontend"
                shift
                ;;
            -j|--judge)
                services="$services judge"
                shift
                ;;
            -s|--services)
                if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                    services="$2"
                    shift 2
                else
                    echo "错误: --services 需要指定服务名称"
                    show_help
                    exit 1
                fi
                ;;
            -d|--down)
                action="down"
                shift
                ;;
            -r|--restart)
                action="restart"
                shift
                ;;
            --install-deps)
                install_deps=true
                shift
                ;;
            --install-docker)
                install_docker=true
                shift
                ;;
            --install-all)
                install_deps=true
                install_docker=true
                shift
                ;;
            *)
                echo "错误: 未知选项 '$1'"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查系统依赖
    echo "检查系统依赖..."
    check_python || exit 1
    
    # 如果需要安装前端依赖，检查Node.js和npm
    if [ "$install_deps" = true ] || [[ "$services" =~ "frontend" || -z "$services" ]]; then
        check_node || exit 1
        check_npm || exit 1
    fi
    
    echo ""
    
    # 执行依赖安装
    if [ "$install_deps" = true ]; then
        install_all_deps
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ 所有依赖安装完成！"
        else
            echo ""
            echo "✗ 部分依赖安装失败，请查看上面的错误信息"
            exit 1
        fi
    fi
    
    # 执行Docker安装
    if [ "$install_docker" = true ]; then
        install_docker
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ Docker安装完成！"
        else
            echo ""
            echo "✗ Docker安装失败，请查看上面的错误信息"
            exit 1
        fi
    fi
    
    # 如果只是安装依赖或Docker，退出程序
    if [ "$install_deps" = true ] || [ "$install_docker" = true ]; then
        echo ""
        echo "所有安装任务完成！"
        echo "可以使用 ./start.sh 命令启动服务"
        exit 0
    fi
    
    # 执行动作
    case "$action" in
        start)
            start_services "$services"
            ;;
        down)
            stop_services "$services"
            ;;
        restart)
            stop_services "$services"
            echo ""
            start_services "$services"
            ;;
    esac
}

# 执行主函数
main "$@"