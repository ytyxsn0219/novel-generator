# AI 网文生成器 (Novel Generator)

一个基于 FastAPI + React + Celery + PostgreSQL 的个人小说创作工具，支持 AI 自动生成网文章节、设定管理和反馈驱动的重写。

## 架构概览

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Frontend      │      │    Backend      │      │   Worker        │
│   (React 18)    │──────▶│   (FastAPI)     │──────▶│   (Celery)      │
│   Port: 3000    │      │   Port: 8000    │      │                 │
└─────────────────┘      └────────┬────────┘      └─────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   PostgreSQL    │
                          │   Port: 5432    │
                          └─────────────────┘
                                   │
                          ┌─────────────────┐
                          │     Redis       │
                          │   Port: 6379    │
                          └─────────────────┘
```

## 技术栈

### 后端 (Backend)
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy 2.0** - ORM 数据库操作
- **PostgreSQL** - 数据持久化存储
- **Celery** - 异步任务队列
- **Redis** - 消息队列和缓存
- **Pydantic** - 数据验证和配置管理

### 前端 (Frontend)
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Nginx** - 生产环境静态资源服务

### 部署
- **Docker** - 容器化
- **Docker Compose** - 多服务编排

## 核心功能

### 1. 小说项目管理
- 创建小说项目（标题 + 主题）
- AI 自动生成小说设定（世界观、角色、大纲、风格）
- 设定确认后进入连载状态

### 2. 章节生成
- 基于设定自动生成章节内容
- 支持章节锁定（保护已确认的章节）
- 自动生成章节摘要用于上下文衔接

### 3. 反馈驱动重写
- 针对章节提交反馈
- AI 自动推断反馈波及范围：
  - `chapter` - 仅修改当前章节
  - `future` - 从当前章节开始修改后续走向
  - `global` - 需要修改全局设定

### 4. LLM 路由
- 支持单模型和多模型模式
- 可配置不同任务使用不同模型（如设定生成用 GPT-4，章节生成用 DeepSeek）

## 快速开始

### 前置要求
- Docker 20.10+
- Docker Compose 2.0+
- OpenAI API Key 或其他兼容 LLM 的 API Key

### 1. 克隆仓库

```bash
git clone git@github.com:ytyxsn0219/novel-generator.git
cd novel-generator
```

### 2. 配置环境变量

```bash
export OPENAI_API_KEY="your-openai-api-key"
# 或
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 3. 启动服务

```bash
docker compose up -d
```

首次启动会构建镜像并拉取依赖，可能需要 3-5 分钟。

### 4. 访问应用

- **前端界面**: http://localhost:3000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### 5. 查看日志

```bash
# 所有服务日志
docker compose logs -f

# 特定服务日志
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f frontend
```

### 6. 停止服务

```bash
docker compose down

# 同时删除数据卷
docker compose down -v
```

## 使用指南

### 创建小说

1. 打开 http://localhost:3000
2. 在 "Novels" 区域输入小说标题和主题/想法
3. 点击 "Create" 创建小说

### 生成设定

1. 点击 "Generate from Theme" 让 AI 根据主题生成小说设定
2. 在文本框中查看/编辑生成的设定（JSON 格式）
3. 点击 "Confirm Settings & Start" 确认设定并开始连载

### 生成章节

1. 确认设定后界面会切换到 "Chapters" 视图
2. 点击 "Start Serializing" 开始自动生成章节
3. 等待任务完成，章节会自动出现在列表中
4. 点击章节标题可查看内容

### 提交反馈

1. 点击章节查看内容
2. 在 "Feedback" 区域输入修改意见
3. 点击 "Submit Feedback"
4. 系统会在后台处理反馈并推断影响范围
5. 根据影响范围，系统可能会自动触发重写任务

## API 端点

### 小说管理
- `POST /novels` - 创建小说
- `GET /novels/{id}` - 获取小说详情
- `POST /novels/{id}/settings` - 生成设定
- `POST /novels/{id}/settings/confirm` - 确认设定

### 章节管理
- `GET /novels/{id}/chapters` - 列出章节

### 任务管理
- `POST /novels/{id}/jobs` - 创建生成任务
- `GET /novels/{id}/jobs/{job_id}` - 获取任务状态

### 反馈管理
- `POST /novels/{id}/feedbacks` - 提交反馈

## 项目结构

```
novel-generator/
├── docker-compose.yml          # Docker Compose 配置
├── README.md                   # 本文档
├── backend/                    # 后端服务
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── models.py          # SQLAlchemy 模型
│   │   ├── schemas.py         # Pydantic 模型
│   │   ├── api/               # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── novels.py      # 小说路由
│   │   │   ├── chapters.py    # 章节路由
│   │   │   ├── jobs.py        # 任务路由
│   │   │   └── feedback.py    # 反馈路由
│   │   ├── llm/               # LLM 客户端
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # 基础抽象类
│   │   │   ├── openai_client.py
│   │   │   └── router.py      # 模型路由
│   │   └── services/          # 业务服务
│   │       ├── __init__.py
│   │       ├── prompt_builder.py
│   │       ├── settings_generator.py
│   │       ├── chapter_generator.py
│   │       └── feedback_handler.py
│   ├── worker/                # Celery Worker
│   │   ├── __init__.py
│   │   ├── celery_app.py      # Celery 配置
│   │   └── tasks.py           # 异步任务
│   └── tests/                 # 测试
│       ├── test_llm.py
│       ├── test_services.py
│       ├── test_schemas.py
│       └── ...
└── frontend/                   # 前端应用
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api.ts               # API 客户端
        ├── types.ts             # TypeScript 类型
        └── components/          # React 组件
            ├── NovelList.tsx
            ├── SettingEditor.tsx
            ├── Reader.tsx
            └── FeedbackPanel.tsx
```

## 配置说明

### 后端配置 (环境变量)

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DATABASE_URL` | postgresql://novel_user:novel_password@db:5432/novel_generator | 数据库连接 |
| `REDIS_URL` | redis://redis:6379/0 | Redis 连接 |
| `OPENAI_API_KEY` | - | OpenAI API Key |
| `ANTHROPIC_API_KEY` | - | Anthropic API Key |
| `LLM_MODE` | single | single 或 multi |
| `DEFAULT_LLM_PROVIDER` | openai | 默认 LLM 提供商 |
| `DEFAULT_LLM_MODEL` | gpt-4o | 默认模型 |

### 多模型路由配置

设置 `LLM_MODE=multi` 和 `MULTI_LLM_ROUTER_JSON` 环境变量：

```bash
export LLM_MODE=multi
export MULTI_LLM_ROUTER_JSON='{"writing": {"provider": "deepseek", "model": "deepseek-chat", "api_key": "sk-xxx"}}'
```

## 开发指南

### 本地开发 (不使用 Docker)

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --port 8000

# 启动 Celery Worker
celery -A worker.celery_app worker --loglevel=info
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 运行测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_llm.py -v
pytest tests/test_services.py -v
```

## 数据模型

### Novel (小说)
- `id`: UUID 主键
- `title`: 标题
- `theme`: 主题/想法
- `settings`: JSON 格式设定
- `status`: drafting | serializing

### Chapter (章节)
- `id`: UUID 主键
- `novel_id`: 外键
- `number`: 章节序号
- `title`: 章节标题
- `content`: 章节内容
- `summary`: 摘要
- `locked`: 是否锁定

### GenerationJob (生成任务)
- `id`: UUID 主键
- `novel_id`: 外键
- `job_type`: 任务类型
- `start_chapter`: 起始章节
- `end_chapter`: 结束章节
- `current_chapter`: 当前章节
- `status`: pending | running | completed | cancelled

### Feedback (反馈)
- `id`: UUID 主键
- `novel_id`: 外键
- `chapter_id`: 章节外键 (可选)
- `content`: 反馈内容
- `inferred_scope`: 推断范围
- `handled`: 是否已处理

## 常见问题

### 1. 服务启动失败

检查端口占用：
```bash
lsof -i :3000  # frontend
lsof -i :8000  # backend
lsof -i :5432  # postgres
lsof -i :6379  # redis
```

### 2. 数据库连接错误

确保 PostgreSQL 容器已健康启动：
```bash
docker compose ps
docker compose logs db
```

### 3. LLM API 调用失败

检查 API Key 是否设置：
```bash
echo $OPENAI_API_KEY
```

## 贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

MIT License
