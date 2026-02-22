# HZAUACM OJ与社区网站

集在线评测(OJ)、校内竞赛、算法学习社区于一体的综合性网站。

## 功能特性

- 用户账户管理
- 题库与题目展示
- 在线评测与提交记录
- 比赛与作业管理
- 博客系统
- 资源分享系统
- 管理后台

## 技术栈

- **后端**：Django + Django REST Framework
- **前端**：Vue.js 3 + Vite
- **数据库**：PostgreSQL
- **缓存/消息队列**：Redis
- **任务队列**：Celery
- **评测沙箱**：Docker
- **部署方式**：Docker Compose 或 直接部署

## 快速开始

### 环境要求

- **使用Docker部署**：
  - Docker 20.0+
  - Docker Compose 1.29+

- **直接部署**：
  - Python 3.8+
  - Node.js 14.0+
  - npm 6.0+
  - PostgreSQL
  - Redis
  - Docker (用于评测功能)

### 部署方式

#### 1. Docker部署 (推荐)

```bash
# 启动所有服务
docker-compose up -d

# 只启动特定服务
docker-compose up -d backend frontend judge
```

#### 2. 直接部署 (无Docker)

```bash
# 安装依赖
./start.sh --install-deps

# 安装依赖和Docker (用于评测功能)
./start.sh --install-all

# 启动所有服务
./start.sh

# 只启动特定服务
./start.sh --backend --frontend
./start.sh --services backend judge

# 停止服务
./start.sh --down

# 重启服务
./start.sh --restart
```

### 开发流程

1. 克隆仓库
2. 配置环境变量
3. 启动开发环境
4. 进行开发和测试
5. 提交代码

## 项目结构

```
HZAUACMOJ/
├── backend/           # Django后端
├── frontend/          # Vue前端
├── judge/             # 评测机
├── docker-compose.yml # Docker Compose配置
├── start.sh           # 无Docker启动脚本
├── .gitignore
└── README.md
```

## 开发文档

- [后端开发文档](backend/README.md)
- [前端开发文档](frontend/README.md)
- [评测机开发文档](judge/README.md)