#!/bin/bash

# 输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== HOJ项目重启脚本 ===${NC}"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误：Docker未安装！${NC}"
    echo -e "${YELLOW}请先安装Docker，然后再运行此脚本。${NC}"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误：Docker Compose未安装！${NC}"
    echo -e "${YELLOW}请先安装Docker Compose，然后再运行此脚本。${NC}"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}错误：未找到docker-compose.yml文件！${NC}"
    echo -e "${YELLOW}请在standAlone目录下运行此脚本。${NC}"
    exit 1
fi

# 检查Docker服务是否正在运行
if ! systemctl is-active --quiet docker; then
    echo -e "${YELLOW}Docker服务未运行，正在启动Docker服务...${NC}"
    systemctl start docker
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误：无法启动Docker服务！${NC}"
        exit 1
    fi
    echo -e "${GREEN}Docker服务已启动！${NC}"
fi

# 停止并移除所有容器
echo -e "${YELLOW}正在停止并移除所有容器...${NC}"
docker-compose down

if [ $? -ne 0 ]; then
    echo -e "${RED}错误：停止容器失败！${NC}"
    echo -e "${YELLOW}请检查容器状态和日志。${NC}"
    exit 1
fi

# 清理未使用的容器、网络和镜像
echo -e "${YELLOW}正在清理Docker资源...${NC}"
docker system prune -f

# 启动项目
echo -e "${YELLOW}正在重新启动HOJ项目服务...${NC}"
docker-compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}错误：项目重启失败！${NC}"
    echo -e "${YELLOW}请检查docker-compose.yml文件和容器日志。${NC}"
    exit 1
fi

# 检查容器启动状态
echo -e "${YELLOW}正在检查容器启动状态...${NC}"

# 等待一段时间让容器初始化
sleep 15

# 检查核心容器的健康状态
containers=("hoj-redis" "hoj-nacos" "hoj-backend" "hoj-frontend" "hoj-judgeserver")

for container in "${containers[@]}"; do
    if docker ps | grep -q "$container"; then
        status=$(docker inspect --format '{{.State.Status}}' "$container")
        echo -e "${GREEN}容器 $container 状态：$status${NC}"
    else
        echo -e "${RED}容器 $container 未启动！${NC}"
        echo -e "${YELLOW}查看容器日志：docker logs $container${NC}"
    fi
done

# 输出服务访问地址
echo -e "${GREEN}=== 项目重启完成！ ===${NC}"
echo -e "${YELLOW}前端访问地址：${GREEN}http://localhost:8081${NC}"
echo -e "${YELLOW}后端API地址：${GREEN}http://localhost:6688${NC}"
echo -e "${YELLOW}判题服务器地址：${GREEN}http://localhost:8090${NC}"
echo -e "${YELLOW}Nacos配置中心：${GREEN}http://localhost:8848/nacos${NC}"
echo -e "${YELLOW}使用以下命令查看容器状态：${GREEN}docker-compose ps${NC}"
echo -e "${YELLOW}使用以下命令查看容器日志：${GREEN}docker-compose logs -f${NC}"
