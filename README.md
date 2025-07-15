# Graphiti - OpenAI Compatible Version

> ⚠️ **Important Notice**: This is an OpenAI-compatible fork/branch that has not been thoroughly tested. Please use with caution

## English / [中文](#中文--english)

This branch contains an enhanced OpenAI-compatible version of [Graphiti](https://github.com/getzep/graphiti), a framework for building and querying temporally-aware knowledge graphs for AI agents. This fork extends the original functionality to support a broader range of OpenAI API-compatible LLM providers beyond the officially supported models.

### What's Different

- **Enhanced LLM Support**: Works with OpenAI API-compatible services like DeepSeek, Qwen, Ollama, LM Studio, vLLM, etc.
- **Instructor Library Integration**: Solves LLM JSON standardized output issues with automatic Pydantic model conversion
- **Separated Model Configuration**: Independent configuration for LLM and embedding models

### Getting Started

For detailed installation and usage instructions, please refer to the comprehensive documentation:

📖 **[Compatible-MCPServer Documentation](mcp_server/compat/README.md)**

### Quick Start

```bash
# Clone and setup
git clone git://github.com/itcook/graphiti.git
cd graphiti/mcp_server
git checkout compat

# Configure and start
cd compat
cp .env.example .env
# Edit .env with your API keys and model configurations
chmod +x startup.sh
./startup.sh
```

### Original Project

For the official Graphiti project with full GPT/Gemini/Claude and Azure OpenAI support, please visit:

📚 **[Original Graphiti Repository](https://github.com/getzep/graphiti)**  
📚 **[Original README Documentation](<README(origin).md>)**

---

## 中文 / [English](#english--中文)

> ⚠️ **重要提示**: 本分支未经过充分测试，请谨慎使用

本分支包含 [Graphiti](https://github.com/getzep/graphiti) 的增强 OpenAI 兼容版本，[Graphiti](https://github.com/getzep/graphiti) 是一个为 AI 代理构建和查询时间感知知识图谱的框架。此分支扩展了原始功能，支持除官方支持模型之外的更广泛的 OpenAI API 兼容 LLM 提供商。

### 主要差异

- **增强的 LLM 支持**: 支持 OpenAI API 兼容服务，如 DeepSeek、Qwen、Ollama、LM Studio、vLLM 等
- **Instructor 库集成**: 通过自动 Pydantic 模型转换解决 LLM JSON 标准化输出问题
- **分离的模型配置**: LLM 和嵌入模型的独立配置

### 开始使用

详细的安装和使用说明，请参考完整文档：

📖 **[兼容型 MCP Server 文档](mcp_server/compat/README_CN.md)**

### 快速开始

```bash
# 克隆和设置
git clone git://github.com/itcook/graphiti.git
cd graphiti/mcp_server
git checkout compat

# 配置和启动
cd compat
cp .env.example .env
# 使用您的 API 密钥和模型配置编辑 .env
chmod +x startup.sh
./startup.sh
```

### 原项目

如需使用官方 Graphiti 项目（完整的 GPT/Gemini/Claude 和 Azure OpenAI 支持），请访问：

📚 **[原 Graphiti 仓库](https://github.com/getzep/graphiti)**  
📚 **[原项目 README 文档](<README(origin).md>)**
