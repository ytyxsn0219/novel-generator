# AI 网文生成器设计文档

## 1. 项目概述

一个面向个人作者的 AI 辅助网文生成工具。用户只需提供一个主题或大致想法，系统自动生成小说设定（世界观、角色、大纲等），用户对齐细节后进入自动连载模式。用户在阅读过程中可随时对任意章节提出修改意见，系统由大模型自主判断影响范围（单章 / 后续章节 / 全局设定），并触发相应重写。

## 2. 核心特性

1. **全自动设定生成**：输入主题，AI 输出结构化设定文档。
2. **人机对齐**：用户在 Web 界面中审阅设定、提修改意见，AI 迭代调整。
3. **自动连载**：设定确认后，系统自动逐章生成网文。
4. **实时阅读与干预**：用户在阅读中随时选中章节写反馈，系统在后台响应。
5. **智能回溯重写**：AI 判断反馈影响范围，支持只改本章、从本章开始改未来走向，或回溯修改全局设定。
6. **章节锁定**：支持锁定开头/结尾等区间，仅重写中间部分并保持承上启下。
7. **双模式模型接入**：支持单模型直连和多模型按任务类型分工协作。
8. **零用户系统**：纯个人工具，无需登录注册。

## 3. 技术架构

### 3.1 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                         用户层                                │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐    │
│  │  React 前端  │   │  API 调用端  │   │  未来其他触发方式  │    │
│  │ (阅读/审稿)  │   │ (脚本/webhook)│   │   (队列/定时器等)  │    │
│  └──────┬──────┘   └──────┬──────┘   └─────────────────┘    │
└─────────┼─────────────────┼───────────────────────────────────┘
          │                 │
          └────────┬────────┘
                   ▼
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI 后端服务                         │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐    │
│  │  小说项目管理  │   │  生成任务调度  │   │  LLM 接入层      │    │
│  │             │   │             │   │ (单模型/多模型)  │    │
│  └─────────────┘   └──────┬──────┘   └─────────────────┘    │
└───────────────────────────┼──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                      Celery + Redis                           │
│              (异步队列：生成任务 / 改写任务)                    │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                      PostgreSQL                               │
│         (小说元数据 / 章节内容 / 生成历史 / 反馈记录)            │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 技术栈

- **前端**：React + TypeScript
- **后端**：Python + FastAPI
- **异步任务队列**：Celery + Redis
- **数据库**：PostgreSQL
- **部署**：Docker + Docker Compose（一键启动所有服务）

### 3.3 部署形态

整个项目通过 `docker-compose.yml` 编排：
- `web`：FastAPI 后端
- `worker`：Celery Worker（可水平扩展实例数）
- `redis`：任务队列
- `db`：PostgreSQL
- `frontend`：Nginx 托管 React 构建产物

## 4. 数据模型

### 4.1 Novel（小说项目）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| title | string | 小说标题 |
| theme | text | 用户输入的主题/想法 |
| settings | JSON | 结构化设定（世界观、角色、大纲、风格） |
| status | enum | `drafting` / `serializing` / `paused` / `completed` |
| created_at / updated_at | datetime | 时间戳 |

### 4.2 Chapter（章节）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| novel_id | FK | 所属小说 |
| number | int | 章节序号 |
| title | string | 章节标题 |
| content | text | 章节正文 |
| status | enum | `draft` / `reviewed` / `deprecated` |
| locked | bool | 是否被用户锁定（锁定后重写时不可改动） |
| summary | text | 本章摘要（用于后续章节上下文） |
| created_at / updated_at | datetime | 时间戳 |

### 4.3 GenerationJob（生成任务）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| novel_id | FK | 所属小说 |
| type | enum | `initial` / `rewrite_chapter` / `rewrite_future` / `rewrite_global` |
| start_chapter | int | 起始章节号 |
| end_chapter | int | 目标章节号 |
| current_chapter | int | 当前已生成到的章节号 |
| status | enum | `pending` / `running` / `paused` / `completed` / `cancelled` |
| feedback_id | FK (nullable) | 触发本次重写的反馈 |
| created_at / updated_at | datetime | 时间戳 |

### 4.4 Feedback（反馈/修改意见）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| novel_id | FK | 所属小说 |
| chapter_id | FK (nullable) | 针对的章节（null 表示针对整部小说） |
| content | text | 用户写的修改意见 |
| inferred_scope | enum | `chapter` / `future` / `global`（由 AI 判断） |
| accepted_scope | enum (nullable) | 用户最终确认的范围 |
| handled | bool | 是否已处理完成 |
| created_at | datetime | 时间戳 |

## 5. 核心流程

### 5.1 从主题到设定

1. 用户输入 `theme`。
2. 后端调用强模型，生成结构化设定：
   - 世界观
   - 主要角色（姓名、性格、目标、关系）
   - 主线大纲（起承转合、关键节点）
   - 风格/基调
3. 用户在前端查看设定，逐条写修改意见。
4. 后端调用模型更新设定，循环直到用户点击"确认设定"。
5. `Novel.status` 从 `drafting` 变为 `serializing`。

### 5.2 自动连载

1. 用户确认设定后，创建 `GenerationJob(type=initial, start=1, end=N)`。
2. Celery Worker 开始逐个消费章节生成任务：
   - 构造 Prompt：小说设定 + 相邻锁定章节摘要/约束 + 上一章摘要 + 当前大纲节点。
   - 调用 LLM Client 生成一章正文。
   - 写入 `Chapter` 并自动生成 `summary`。
   - 更新 `GenerationJob.current_chapter`。
   - 继续下一章。
3. 前端轮询 `GenerationJob` 状态和最新章节列表，用户可以开始阅读。
4. 用户可以主动"暂停"连载，或让它一直写到 `end_chapter`（可设为很大，如 9999）。

### 5.3 实时反馈与回溯重写

1. 用户阅读到某一章（或全局视角），写 `Feedback`。
2. 后端调用强模型（如 DeepSeek-R1 / Claude），根据反馈内容判断影响范围：
   - `chapter`：仅修改本章内容。
   - `future`：从本章开始，后续按新走向重写。
   - `global`：涉及设定层，需要修改设定后再重新生成。
3. 用户确认影响范围（如果是 `global`，先进入设定修改流程）。
4. 后端根据确认的范围创建新的 `GenerationJob`：
   - `chapter` → `rewrite_chapter`，只改这一章.
   - `future` → `rewrite_future`，从该章开始往后重写（旧的后续章节标记为 `deprecated`）。
   - `global` → `rewrite_global`，按新设定从指定位置开始重写。
5. Worker 执行新任务，旧任务如有冲突则自动 `cancelled`。

### 5.4 章节锁定与中间重写

- 用户可以在章节列表中勾选任意章节，标记 `locked=true`。
- 当存在锁定的前后章节时，重写中间部分的 Prompt 会额外包含：
  - 前面锁定章节的结尾摘要（承上）。
  - 后面锁定章节的开头约束（启下）。
- 这样可以保证仅修改中间部分时，故事不会脱节。

## 6. LLM 接入层

### 6.1 统一接口

所有模型调用封装在统一的 `LLMClient` 接口下：

```python
class LLMClient:
    def generate(self, prompt: str, config: ModelConfig) -> str:
        ...
```

提供具体实现：
- `OpenAIClient`
- `DeepSeekClient`
- `AnthropicClient`
- `OllamaClient`（预留本地模型）
- 未来可继续扩展

### 6.2 单模型模式

配置文件中指定一个默认模型：

```yaml
llm:
  mode: single
  default:
    provider: deepseek
    model: deepseek-chat
    api_key: ${DEEPSEEK_API_KEY}
```

所有任务（设定生成、章节写作、范围判断）都走这个模型。

### 6.3 多模型协作模式

```yaml
llm:
  mode: multi
  router:
    planning:        # 设定生成 / 范围判断
      provider: anthropic
      model: claude-3-7-sonnet
      api_key: ${ANTHROPIC_API_KEY}
    writing:         # 章节写作
      provider: deepseek
      model: deepseek-chat
      api_key: ${DEEPSEEK_API_KEY}
    polishing:       # 局部润色（可选）
      provider: openai
      model: gpt-4o-mini
      api_key: ${OPENAI_API_KEY}
```

后端初始化时按 `ModelRouter` 分发，统一走 `LLMClient` 接口。

### 6.4 API Key 管理

- 所有 Key 通过环境变量注入，不进入代码仓库。
- 前端只传递抽象的 `provider_alias` 或任务类型，不接触真实 Key。

## 7. API 触发支持

除了 React 前端，系统暴露标准 RESTful API，方便脚本、Webhook、未来的自动化流程调用：

- `POST /novels` — 创建小说项目
- `GET /novels/{id}` — 获取小说详情
- `POST /novels/{id}/settings/generate` — 基于主题生成设定
- `POST /novels/{id}/settings/confirm` — 确认设定
- `POST /novels/{id}/jobs` — 启动/暂停生成任务
- `GET /novels/{id}/chapters` — 获取章节列表
- `POST /novels/{id}/chapters/{num}/feedback` — 提交反馈
- `GET /novels/{id}/jobs/{job_id}` — 查询任务进度

## 8. 非功能性需求

1. **无状态后端**：FastAPI 服务本身无状态，方便多实例部署和迁移。
2. **Worker 可扩展**：Celery Worker 可以在多台机器上启动，加快生成吞吐。
3. **Docker 一键部署**：提供 `docker-compose.yml`，一条命令启动全部服务。
4. **零登录**：纯个人工具，去掉认证体系以降低复杂度。
5. **可观测性**：预留结构化日志和基础的 `/health` 探端点。
