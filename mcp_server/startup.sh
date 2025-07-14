#!/bin/bash

# Graphiti MCP OpenAI Compatible Version Startup Script

set -e

echo "=== Graphiti MCP OpenAI Compatible Version Startup ==="

# Function to get environment variable value from .env file or system
get_env_var() {
    local var_name="$1"
    local value=""

    # First check .env file if it exists
    if [ -f ".env" ]; then
        value=$(grep "^${var_name}=" .env 2>/dev/null | cut -d'=' -f2- | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    fi

    # If not found in .env file, check system environment
    if [ -z "$value" ]; then
        value="${!var_name}"
    fi

    echo "$value"
}

# Function to mask sensitive values (API keys)
mask_sensitive_value() {
    local value="$1"
    local length=${#value}

    if [ $length -le 7 ]; then
        # If too short, just show asterisks
        echo "****"
    else
        # Show first 3 and last 4 characters
        local prefix="${value:0:3}"
        local suffix="${value: -4}"
        echo "${prefix}****${suffix}"
    fi
}

# Check required environment variables
check_env_var() {
    local var_name="$1"
    local value=$(get_env_var "$var_name")

    if [ -z "$value" ]; then
        echo "❌ Error: Environment variable $var_name is not set in .env file or system environment"
        exit 1
    fi

    # Mask API keys for security
    if [[ "$var_name" == *"API_KEY"* ]]; then
        local masked_value=$(mask_sensitive_value "$value")
        echo "✅ $var_name: $masked_value"
    else
        echo "✅ $var_name: $value"
    fi
}

echo "⏳ Checking environment variables..."

# Check .env file first
if [ -f ".env" ]; then
    echo "📄 Found .env file, checking variables..."
else
    echo "⚠️ Warning: .env file not found, checking system environment variables"
fi

check_env_var "LLM_BASE_URL"
check_env_var "LLM_API_KEY"
check_env_var "LLM_MODEL_NAME"
check_env_var "EMBEDDING_BASE_URL"
check_env_var "EMBEDDING_MODEL_NAME"

echo "✅ All required environment variables are set"

# Start services
echo "🚀 Starting Graphiti MCP OpenAI Compatible version..."
docker compose -f docker-compose_compat.yml up -d

# Get PORT environment variable for display
PORT_VALUE=$(get_env_var "PORT")
if [ -z "$PORT_VALUE" ]; then
    PORT_VALUE="8000"
fi

echo "✅ Services started successfully!"
echo "✨ MCP Server: http://localhost:${PORT_VALUE}"
echo "✨ Neo4j Browser: http://localhost:7474"
echo "✨ Use 'docker compose -f docker-compose_compat.yml logs -f' to view logs"
echo "🟥 Use 'docker compose -f docker-compose_compat.yml down' to stop services"
