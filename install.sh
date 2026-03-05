#!/bin/bash

# 项目安装脚本 - 全自动版本

# 输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 错误处理函数
handle_error() {
    echo -e "${RED}错误: $1${NC}"
    echo -e "${YELLOW}安装失败，请检查错误信息${NC}"
    exit 1
}

# 成功提示函数
success_msg() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 信息提示函数
info_msg() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 警告提示函数
warn_msg() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

echo -e "${GREEN}=== HOJ 项目全自动安装脚本 ===${NC}"
echo -e "${YELLOW}开始时间: $(date)${NC}\n"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    warn_msg "当前不是root用户，将使用sudo执行需要权限的命令"
    SUDO_CMD="sudo"
else
    SUDO_CMD=""
fi

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || handle_error "无法进入脚本目录"
info_msg "工作目录: $(pwd)"

# 更新系统包
info_msg "1. 更新系统包..."
$SUDO_CMD apt-get update -y || handle_error "系统包更新失败"

# 安装必要的系统依赖
info_msg "2. 安装系统依赖..."
$SUDO_CMD apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common || handle_error "系统依赖安装失败"

# 检查并安装Docker
info_msg "3. 检查Docker安装情况..."
if ! command -v docker &> /dev/null; then
    warn_msg "Docker未安装，正在安装Docker..."
    
    # 添加Docker官方GPG密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | $SUDO_CMD gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg || handle_error "Docker GPG密钥添加失败"
    
    # 添加Docker仓库
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | $SUDO_CMD tee /etc/apt/sources.list.d/docker.list > /dev/null || handle_error "Docker仓库添加失败"
    
    # 安装Docker
    $SUDO_CMD apt-get update -y
    $SUDO_CMD apt-get install -y docker-ce docker-ce-cli containerd.io || handle_error "Docker安装失败"
    
    # 启动Docker服务
    $SUDO_CMD systemctl start docker || handle_error "Docker服务启动失败"
    $SUDO_CMD systemctl enable docker || warn_msg "Docker服务自启动启用失败"
    
    success_msg "Docker安装成功！"
else
    success_msg "Docker已安装，版本：$(docker --version)"
fi

# 检查并安装Docker Compose
info_msg "4. 检查Docker Compose安装情况..."
if ! command -v docker-compose &> /dev/null; then
    warn_msg "Docker Compose未安装，正在安装Docker Compose..."
    
    # 下载Docker Compose二进制文件
    $SUDO_CMD curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose || handle_error "Docker Compose下载失败"
    
    # 给Docker Compose添加执行权限
    $SUDO_CMD chmod +x /usr/local/bin/docker-compose || handle_error "Docker Compose权限设置失败"
    
    success_msg "Docker Compose安装成功！版本：$($SUDO_CMD docker-compose --version)"
else
    success_msg "Docker Compose已安装，版本：$(docker-compose --version)"
fi

# 安装Node.js和npm
info_msg "5. 安装Node.js和npm..."
# 安装Node.js 16 LTS
curl -fsSL https://deb.nodesource.com/setup_16.x | $SUDO_CMD bash - || handle_error "NodeSource仓库添加失败"
$SUDO_CMD apt-get install -y nodejs || handle_error "Node.js安装失败"

# 检查Node.js和npm版本
success_msg "Node.js版本: $(node -v)"
success_msg "npm版本: $(npm -v)"

# 进入前端项目目录
info_msg "6. 进入前端项目目录..."
if [ ! -d "hoj-vue" ]; then
    handle_error "找不到hoj-vue目录，请确保在HOJ项目根目录运行此脚本"
fi
cd hoj-vue || handle_error "无法进入hoj-vue目录"

# 配置npm镜像源为淘宝源（加速下载）
info_msg "7. 配置npm镜像源..."
npm config set registry https://registry.npmmirror.com/ || warn_msg "npm镜像源设置失败"
success_msg "npm镜像源已设置为: $(npm config get registry)"

# 安装前端依赖
info_msg "8. 安装前端依赖..."
info_msg "这可能需要几分钟时间，请耐心等待..."

# 清理可能存在的旧依赖
if [ -d "node_modules" ]; then
    warn_msg "发现旧的node_modules目录，正在清理..."
    rm -rf node_modules
fi
if [ -f "package-lock.json" ]; then
    warn_msg "发现旧的package-lock.json，正在清理..."
    rm -f package-lock.json
fi

# 安装依赖
npm install --no-audit --no-fund || handle_error "前端依赖安装失败"
success_msg "前端依赖安装成功"

# 编译前端项目
info_msg "9. 编译前端项目..."
info_msg "正在编译，请稍候..."

# 设置Node.js内存限制
export NODE_OPTIONS="--max-old-space-size=4096"

npm run build || handle_error "前端项目编译失败"

# 检查编译结果
if [ -d "dist" ]; then
    success_msg "前端编译成功！"
    BUILD_SIZE=$(du -sh dist | cut -f1)
    info_msg "编译结果大小: $BUILD_SIZE"
else
    handle_error "编译失败！dist目录不存在"
fi

# 返回项目根目录
cd ..

# 安装MySQL客户端（用于后续可能的数据库操作）
info_msg "10. 安装MySQL客户端..."
$SUDO_CMD apt-get install -y mysql-client || warn_msg "MySQL客户端安装失败（非必需）"

# 进入Docker Compose目录
info_msg "11. 进入Docker Compose配置目录..."
if [ ! -d "hoj-deploy/standAlone" ]; then
    handle_error "找不到hoj-deploy/standAlone目录"
fi
cd hoj-deploy/standAlone || handle_error "无法进入Docker Compose目录"

# 配置环境变量
info_msg "12. 配置环境变量..."

# 如果.env不存在，从示例创建
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        success_msg "已从.env.example创建.env文件"
        
        # 生成随机密码（可选）
        RANDOM_PASSWORD=$(openssl rand -base64 12)
        # 替换默认密码（如果需要）
        sed -i "s/123456/$RANDOM_PASSWORD/g" .env
        info_msg "已生成随机数据库密码"
    else
        warn_msg "找不到.env.example文件，将使用默认配置"
    fi
else
    success_msg ".env文件已存在"
fi

# 确保Docker服务正在运行
info_msg "13. 确保Docker服务正在运行..."
$SUDO_CMD systemctl start docker 2>/dev/null || warn_msg "Docker服务启动失败，可能已经运行"

# 拉取必要的Docker镜像
info_msg "14. 拉取Docker镜像（这可能需要一些时间）..."
$SUDO_CMD docker-compose pull || warn_msg "镜像拉取失败，将尝试使用本地缓存"

# 停止可能正在运行的旧容器
info_msg "15. 停止可能存在的旧容器..."
$SUDO_CMD docker-compose down 2>/dev/null || true

# 启动所有服务
info_msg "16. 启动所有HOJ服务..."
info_msg "正在启动，请稍候..."
$SUDO_CMD docker-compose up -d || handle_error "服务启动失败"

# 等待服务启动
info_msg "17. 等待服务完全启动（30秒）..."
sleep 30

# 检查服务状态
info_msg "18. 检查服务运行状态..."
SERVICE_STATUS=$($SUDO_CMD docker-compose ps --services --filter "status=running")
SERVICE_COUNT=$(echo "$SERVICE_STATUS" | wc -l)
TOTAL_SERVICES=$($SUDO_CMD docker-compose config --services | wc -l)

if [ "$SERVICE_COUNT" -eq "$TOTAL_SERVICES" ]; then
    success_msg "所有服务都已成功运行！"
else
    warn_msg "部分服务可能未正常运行"
    info_msg "运行中的服务:"
    $SUDO_CMD docker-compose ps
fi

# 获取访问地址
info_msg "19. 获取服务访问地址..."
# 尝试获取IP地址
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="localhost"
fi

# 检查前端端口（默认8081）
FRONTEND_PORT="8081"
# 尝试从docker-compose配置中获取端口
if grep -q "80:80" docker-compose.yml 2>/dev/null; then
    FRONTEND_PORT="80"
fi

# 最终输出
echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                  🎉 HOJ 安装完成！ 🎉${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}📱 访问地址:${NC}"
echo -e "   ${YELLOW}http://$SERVER_IP:$FRONTEND_PORT${NC}"
if [ "$FRONTEND_PORT" = "80" ]; then
    echo -e "   ${YELLOW}http://$SERVER_IP${NC} (默认80端口可省略)"
fi
echo ""

echo -e "${BLUE}🔧 服务管理命令:${NC}"
echo -e "   查看状态:  ${YELLOW}cd $(pwd) && sudo docker-compose ps${NC}"
echo -e "   查看日志:  ${YELLOW}cd $(pwd) && sudo docker-compose logs -f${NC}"
echo -e "   停止服务:  ${YELLOW}cd $(pwd) && sudo docker-compose down${NC}"
echo -e "   重启服务:  ${YELLOW}cd $(pwd) && sudo docker-compose restart${NC}"
echo ""

echo -e "${BLUE}📂 重要目录:${NC}"
echo -e "   前端编译结果: ${YELLOW}$SCRIPT_DIR/hoj-vue/dist${NC}"
echo -e "   Docker配置:   ${YELLOW}$(pwd)${NC}"
echo ""

echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✨ 所有服务已自动启动，无需额外操作！${NC}"
echo -e "${YELLOW}完成时间: $(date)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}\n"

# 尝试自动打开浏览器（如果是在桌面环境）
if command -v xdg-open &> /dev/null; then
    info_msg "尝试在浏览器中打开项目..."
    xdg-open "http://$SERVER_IP:$FRONTEND_PORT" 2>/dev/null || true
elif command -v open &> /dev/null; then
    info_msg "尝试在浏览器中打开项目..."
    open "http://$SERVER_IP:$FRONTEND_PORT" 2>/dev/null || true
fi