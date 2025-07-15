# Graphiti MCP Server - OpenAI 兼容版本

**中文** | [English](README.md)

> ⚠️ **重要提示**: 此 OpenAI 兼容版本尚未经过充分测试，请谨慎使用。

这是 Graphiti MCP 服务器实现的增强 OpenAI 兼容版本，旨在支持更广泛的 LLM (OpenAI API like)和本地文本嵌入服务。Graphiti 是一个专为在动态环境中运行的 AI 代理构建和查询时间感知知识图谱的框架，由于其特性，它特别适合作为 AI Coding Agent 的 MCP 记忆库。

## 兼容版本的新特性

此分支 (`compat`) 引入了重要的增强功能，以支持除官方实现的 GPT/Gemini/Claude 和 Azure OpenAI(AI 云服务)模型之外的 OpenAI API 兼容 LLM 提供商。

### 新增文件

> 为了方便与上游仓库同步，除项目 README.md 文档外，所有的文件均为新增

**核心兼容性客户端：**

- **`graphiti_core/llm_client/openai_compat_client.py`** - 集成 instructor 库的 OpenAI 兼容 LLM 客户端
- **`graphiti_core/cross_encoder/openai_compat_reranker_client.py`** - 具有分离 LLM 配置的兼容重排序客户端

**MCP 服务器组件：**

- **`mcp_server/compat/graphiti_mcp_server.py`** - 具有 OpenAI API 兼容性的增强 MCP 服务器
- **`mcp_server/compat/Dockerfile`** - 兼容版本的 Docker 配置
- **`mcp_server/compat/docker-compose.yml`** - 兼容版本的 Docker Compose 设置
- **`mcp_server/compat/pyproject.toml`** - 包含 instructor 库的更新依赖项，以及使用本地 `graphiti-core` 包的依赖配置
- **`mcp_server/compat/.env.example`** - 兼容版本的环境配置模板
- **`mcp_server/compat/startup.sh`** - 具有环境验证和服务管理功能的便捷启动脚本

### 核心改进

1. **增强的 LLM 集成**

   - **Instructor 库集成**: 通过自动 Pydantic 模型转换、内置重试机制和更好的错误处理解决 LLM JSON 标准化输出问题
   - **OpenAICompatClient**: 基于 instructor 库的新 LLM 客户端，用于改进结构化输出生成
   - **分离的模型配置**: LLM 和嵌入模型的独立配置

2. **新环境变量**

   - `LLM_BASE_URL` - LLM API 端点的基础 URL
   - `LLM_API_KEY` - LLM 服务的 API 密钥
   - `LLM_MODEL_NAME` - 主要 LLM 模型名称
   - `LLM_SMALL_MODEL_NAME` - 轻量级操作的小型 LLM 模型名称
   - `LLM_TEMPERATURE` - LLM 响应的温度设置
   - `EMBEDDING_BASE_URL` - 嵌入 API 端点的基础 URL
   - `EMBEDDING_API_KEY` - 嵌入服务的 API 密钥
   - `EMBEDDING_MODEL_NAME` - 嵌入模型名称
   - `PORT` - 服务端口

3. **开发改进**
   - **启动脚本**: `startup.sh` 提供便捷的服务管理，包含环境验证、API 密钥掩码和自动 Docker Compose 编排

## 快速开始

### Docker 运行（推荐）

1. **克隆仓库并切换到 compat 分支**

   ```bash
   git clone https://github.com/itcook/graphiti.git
   cd graphiti
   git checkout compat
   ```

2. **配置环境变量**

   ```bash
   cd mcp_server/compat
   cp .env.example .env
   # 使用您的 API 密钥和模型配置编辑 .env 文件
   ```

3. **使用启动脚本启动兼容版本（推荐）**

   ```bash
   chmod +x startup.sh
   ./startup.sh

   # 如果您需要重新构建 Docker 镜像（如版本更新后）
   # ./startup.sh -r
   # 或者
   # ./startup.sh --rebuild
   ```

   **启动脚本提供以下功能：**

   - 环境变量验证（优先检查 .env 文件，然后检查系统环境）
   - 自动 Docker Compose 服务编排
   - 服务状态报告，包含 URL 和管理命令

   或手动使用 Docker Compose：

   ```bash
   docker compose up -d
   ```

4. **访问服务器**
   - SSE 端点: `http://localhost:8000/sse`
   - Neo4j 浏览器: `http://localhost:7474`
   - 默认端口可通过 `PORT` 环境变量更改

### 非 Docker 运行

> 均需在 `graphiti/mcp_server/compat` 目录下操作

1. **先决条件**

   - Python 3.10 或更高版本
   - Neo4j 数据库（版本 5.26 或更高）
   - OpenAI API 兼容的 LLM 服务
   - `uv` 包管理器

2. **安装依赖项**

   ```bash
   # 如果尚未安装 uv，请安装
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # macOS 用户
   # brew install uv

   # 使用兼容配置安装依赖项
   uv sync
   ```

3. **配置环境**

   ```bash
   cp .env.example .env
   # 使用您的配置编辑 .env
   ```

4. **运行服务器**
   ```bash
   uv run graphiti_mcp_server.py --transport sse
   ```

## 配置

### 必需的环境变量

```bash
# LLM 配置
LLM_BASE_URL=http://localhost:11434/v1  # 您的 OpenAI 兼容 API 端点
LLM_API_KEY=your_api_key_here           # LLM 服务的 API 密钥
LLM_MODEL_NAME=llama3.2:latest          # 主要模型名称
LLM_SMALL_MODEL_NAME=llama3.2:latest    # 轻量级任务的小型模型
LLM_TEMPERATURE=0.0                     # LLM 响应的温度

# 嵌入配置
EMBEDDING_BASE_URL=http://localhost:11434/v1  # 嵌入 API 端点
EMBEDDING_API_KEY=your_api_key_here            # 嵌入服务的 API 密钥
EMBEDDING_MODEL_NAME=nomic-embed-text          # 嵌入模型名称

# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphiti

# 可选设置
SEMAPHORE_LIMIT=10                      # 并发限制
PORT=8000                              # 服务器端口
```

### 支持的 LLM 提供商

此兼容版本适用于任何 OpenAI API 兼容服务，包括：

- **OpenAI API 兼容的大模型** (如 DeepSeek, Qwen 等)
- **Ollama**（本地模型）
- **LM Studio**（本地模型）
- **vLLM**（自托管）

> **OpenAI**, **Azure OpenAI** 请使用[原仓库](https://github.com/getzep/graphiti)

## MCP 客户端集成

### SSE 传输（Cursor 等）

```json
{
  "mcpServers": {
    "graphiti-memory": {
      "type": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

### STDIO 传输（Claude Desktop 等）

```json
{
  "mcpServers": {
    "graphiti-memory": {
      "transport": "stdio",
      "command": "/path/to/uv",
      "args": [
        "run",
        "--project",
        "/path/to/graphiti/mcp_server/pyproject.toml",
        "graphiti_mcp_server-compat.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "LLM_BASE_URL": "http://localhost:11434/v1",
        "LLM_API_KEY": "your_key",
        "LLM_MODEL_NAME": "llama3.2:latest",
        "EMBEDDING_BASE_URL": "http://localhost:11434/v1",
        "EMBEDDING_MODEL_NAME": "nomic-embed-text"
      }
    }
  }
}
```

## 可用工具

兼容版本提供与原版本相同的工具：

- `add_memory` - 向知识图谱添加记忆
- `search_memory_nodes` - 搜索记忆节点
- `search_memory_facts` - 搜索记忆之间的关系
- `delete_entity_edge` - 删除实体关系
- `delete_episode` - 删除情节
- `get_entity_edge` - 检索特定实体边
- `get_episodes` - 获取最近的情节
- `clear_graph` - 清除所有图数据

## 故障排除

### 常见问题

1. **JSON 输出问题**: instructor 库集成应该解决大多数结构化输出问题，但不排除某些大模型结构化输出的兼容性问题
2. **速率限制**: 调整 `SEMAPHORE_LIMIT` 来控制大模型速率限制
3. **模型兼容性**: 确保您的模型支持结构化输出所需的功能

### 日志记录

通过在环境中设置日志级别或检查服务器日志来启用详细日志记录以进行调试。

## 从原版本迁移

要从原版本迁移：

1. 更新环境变量以使用新的命名约定
2. 使用兼容的 Docker Compose 文件
3. 如需要，更新您的 MCP 客户端配置
4. 在生产使用前进行充分测试

## 许可证

此项目采用与父 Graphiti 项目相同的许可证。

---

**由 🤖[Augment Code](https://augmentcode.com) 协助** - AI 驱动的开发辅助
