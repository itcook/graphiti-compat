# Graphiti MCP Server - OpenAI Compatible Version

[中文](README_CN.md) | **English**

> ⚠️ **Important Notice**: This OpenAI-compatible version has not been thoroughly tested. Please use with caution.

Graphiti is a framework for building and querying temporally-aware knowledge graphs, specifically tailored for AI agents operating in dynamic environments. Due to its characteristics, it is particularly suitable as a memory repository for AI Coding Agents. This is an enhanced OpenAI-compatible version of the Graphiti MCP server implementation, designed to support a broader range of LLMs (OpenAI API-like) and local embeddings.

## What's New in This Compatible Version

This branch (`compat`) introduces significant enhancements to support OpenAI API-compatible LLM providers beyond the officially implemented GPT/Gemini/Claude and Azure OpenAI (AI cloud service) models.

### New Files Added

> To facilitate synchronization with the upstream repository, all files are newly added except for the project README.md documentation

**Core Compatibility Clients:**

- **`graphiti_core/llm_client/openai_compat_client.py`** - OpenAI-compatible LLM client with instructor library integration
- **`graphiti_core/cross_encoder/openai_compat_reranker_client.py`** - Compatible reranker client with separated LLM configuration

**MCP Server Components:**

- **`mcp_server/compat/graphiti_mcp_server.py`** - Enhanced MCP server with OpenAI API compatibility
- **`mcp_server/compat/Dockerfile`** - Docker configuration for the compatible version
- **`mcp_server/compat/docker-compose.yml`** - Docker Compose setup for the compatible version
- **`mcp_server/compat/pyproject.toml`** - Updated dependencies including instructor library and local `graphiti-core` package dependency configuration
- **`mcp_server/compat/.env.example`** - Environment configuration template for compatible version
- **`mcp_server/compat/startup.sh`** - Convenient startup script with environment validation and service management

### Core Improvements

1. **Enhanced LLM Integration**

   - **Instructor Library Integration**: Solves LLM JSON standardized output issues with automatic Pydantic model conversion, built-in retry mechanisms, and better error handling
   - **OpenAICompatClient**: New LLM client based on instructor library for improved structured output generation
   - **Separated Model Configuration**: Independent configuration for LLM and embedding models

2. **New Environment Variables**

   - `LLM_BASE_URL` - Base URL for LLM API endpoint
   - `LLM_API_KEY` - API key for LLM service
   - `LLM_MODEL_NAME` - Primary LLM model name
   - `LLM_SMALL_MODEL_NAME` - Small LLM model name for lightweight operations
   - `LLM_TEMPERATURE` - Temperature setting for LLM responses
   - `EMBEDDING_BASE_URL` - Base URL for embedding API endpoint
   - `EMBEDDING_API_KEY` - API key for embedding service
   - `EMBEDDING_MODEL_NAME` - Embedding model name
   - `PORT` - Service port

3. **Development Improvements**
   - **Startup Script**: `startup.sh` provides convenient service management with environment validation, API key masking, and automatic Docker Compose orchestration

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository and switch to compat branch**

   ```bash
   git clone https://github.com/itcook/graphiti.git
   cd graphiti
   git checkout compat
   ```

2. **Configure environment variables**

   ```bash
   cd mcp_server/compat
   cp .env.example .env
   # Edit .env file with your API keys and model configurations
   ```

3. **Start the compatible version using the startup script (Recommended)**

   ```bash
   chmod +x startup.sh
   ./startup.sh

   # If you need to rebuild Docker image (after version updates)
   # ./startup.sh -r
   # or
   # ./startup.sh --rebuild
   ```

   **The startup script provides:**

   - Environment variable validation (checks .env file first, then system environment)
   - Automatic Docker Compose service orchestration
   - Service status reporting with URLs and management commands

   Or manually using Docker Compose:

   ```bash
   docker compose up -d
   ```

4. **Access the server**
   - SSE endpoint: `http://localhost:8000/sse`
   - Neo4j Browser: `http://localhost:7474`
   - Default port can be changed via `PORT` environment variable

### Non-Docker Installation

> All operations should be performed in the `graphiti/mcp_server/compat` directory

1. **Prerequisites**

   - Python 3.10 or higher
   - Neo4j database (version 5.26 or later)
   - OpenAI API-compatible LLM service
   - `uv` package manager

2. **Install dependencies**

   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # macOS users
   # brew install uv

   # Install dependencies using compatible configuration
   uv sync
   ```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the server**
   ```bash
   uv run graphiti_mcp_server.py --transport sse
   ```

## Configuration

### Required Environment Variables

```bash
# LLM Configuration
LLM_BASE_URL=http://localhost:11434/v1  # Your OpenAI-compatible API endpoint
LLM_API_KEY=your_api_key_here           # API key for LLM service
LLM_MODEL_NAME=llama3.2:latest          # Primary model name
LLM_SMALL_MODEL_NAME=llama3.2:latest    # Small model for lightweight tasks
LLM_TEMPERATURE=0.0                     # Temperature for LLM responses

# Embedding Configuration
EMBEDDING_BASE_URL=http://localhost:11434/v1  # Embedding API endpoint
EMBEDDING_API_KEY=your_api_key_here            # API key for embedding service
EMBEDDING_MODEL_NAME=nomic-embed-text          # Embedding model name

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphiti

# Optional Settings
SEMAPHORE_LIMIT=10                      # Concurrency limit
PORT=8000                              # Server port
```

### Supported LLM Providers

This compatible version works with any OpenAI API-compatible service, including:

- **OpenAI API-compatible LLMs** (such as DeepSeek, Qwen, etc.)
- **Ollama** (local models)
- **LM Studio** (local models)
- **vLLM** (self-hosted)

> For **OpenAI** and **Azure OpenAI**, please use the [original repository](https://github.com/getzep/graphiti)

## MCP Client Integration

### For SSE Transport (Cursor, etc.)

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

### For STDIO Transport (Claude Desktop, etc.)

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

## Available Tools

The compatible version provides the same tools as the original:

- `add_memory` - Add memory to the knowledge graph
- `search_memory_nodes` - Search for memory nodes
- `search_memory_facts` - Search for relationships between memories
- `delete_entity_edge` - Delete entity relationships
- `delete_episode` - Delete episodes
- `get_entity_edge` - Retrieve specific entity edges
- `get_episodes` - Get recent episodes
- `clear_graph` - Clear all graph data

## Troubleshooting

### Common Issues

1. **JSON Output Problems**: The instructor library integration should resolve most structured output issues, but compatibility issues with certain LLMs' structured output cannot be ruled out
2. **Rate Limiting**: Adjust `SEMAPHORE_LIMIT` to control LLM rate limiting
3. **Model Compatibility**: Ensure your model supports the required features for structured output

### Logging

Enable detailed logging by setting log levels in your environment or checking the server logs for debugging information.

## Migration from Original Version

To migrate from the original version:

1. Update environment variables to use the new naming convention
2. Use the compatible Docker Compose file
3. Update your MCP client configuration if needed
4. Test thoroughly before production use

## License

This project is licensed under the same license as the parent Graphiti project.

---

**Assisted by 🤖[Augment Code](https://augmentcode.com)** - AI-powered development assistance
