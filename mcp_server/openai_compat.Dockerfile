# syntax=docker/dockerfile:1.9
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the installer script
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Add uv to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Configure uv for optimal Docker usage
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    MCP_SERVER_HOST="0.0.0.0" \
    PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd -r app && useradd -r -d /app -g app app

# 修改构建上下文，从上级目录复制以包含 graphiti_core
COPY mcp_server/pyproject-openai_compat.toml ./pyproject.toml
COPY mcp_server/uv.lock ./
COPY graphiti_core/ ./graphiti_core/

# Install dependencies first (better layer caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 修改应用程序文件名
COPY mcp_server/graphiti_mcp_server-openai_compat.py ./

# Change ownership to app user
RUN chown -Rv app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# 修改启动命令
CMD ["uv", "run", "graphiti_mcp_server-openai_compat.py"]
