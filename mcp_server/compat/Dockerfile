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

# Modify the build context to copy from the parent directory to include graphiti_core
COPY mcp_server/compat/pyproject.toml ./pyproject.toml
COPY mcp_server/compat/uv.lock ./
COPY graphiti_core/ ./graphiti_core/

# Modify the application file name
COPY mcp_server/compat/graphiti_mcp_server.py ./

# Modify startup command
CMD ["uv", "run", "graphiti_mcp_server.py"]
