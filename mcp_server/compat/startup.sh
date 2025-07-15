#!/bin/bash

# Graphiti MCP OpenAI Compatible Version Startup Script

set -e

# Parse command line arguments
REBUILD=false
for arg in "$@"; do
    case $arg in
        -r|--rebuild)
            REBUILD=true
            shift
            ;;
        *)
            # Unknown option
            ;;
    esac
done

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

# Function to handle rebuild process
handle_rebuild() {
    echo "🔄 Rebuild mode enabled..."

    # Find and stop all graphiti-related containers
    echo "⏳ Checking for graphiti-related containers..."
    GRAPHITI_CONTAINERS=$(docker ps -a --format "{{.ID}} {{.Names}}" | grep -i graphiti | awk '{print $1}' || true)

    if [ -n "$GRAPHITI_CONTAINERS" ]; then
        echo "🛑 Found graphiti-related containers, stopping and removing them..."
        echo "$GRAPHITI_CONTAINERS" | while read -r container_id; do
            if [ -n "$container_id" ]; then
                CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$container_id" 2>/dev/null | sed 's/^\//' || echo "unknown")
                echo "🛑 Stopping and removing container: $CONTAINER_NAME ($container_id)"
                docker stop "$container_id" 2>/dev/null || true
                docker rm "$container_id" 2>/dev/null || true
            fi
        done
    else
        echo "ℹ️ No graphiti-related containers found"
    fi

    # Delete graphiti-related images
    echo "🗑️ Removing graphiti-related images..."
    GRAPHITI_IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -i graphiti || true)

    if [ -n "$GRAPHITI_IMAGES" ]; then
        echo "$GRAPHITI_IMAGES" | while read -r image; do
            if [ -n "$image" ]; then
                echo "🗑️ Deleting image: $image"
                docker rmi "$image" 2>/dev/null || echo "⚠️ Failed to delete image: $image (may be in use)"
            fi
        done
    else
        echo "ℹ️ No graphiti-related images found to delete"
    fi

    # Clean up docker networks
    echo "🧹 Cleaning up docker networks..."
    GRAPHITI_NETWORKS=$(docker network ls --format "{{.Name}}" | grep -i graphiti || true)
    if [ -n "$GRAPHITI_NETWORKS" ]; then
        echo "$GRAPHITI_NETWORKS" | while read -r network; do
            if [ -n "$network" ]; then
                echo "🗑️ Removing network: $network"
                docker network rm "$network" 2>/dev/null || echo "⚠️ Failed to remove network: $network (may be in use)"
            fi
        done
    else
        echo "ℹ️ No graphiti-related networks found to clean"
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

# Handle rebuild if requested
if [ "$REBUILD" = true ]; then
    handle_rebuild
    echo "🔄 Start with building..."
    docker compose up --build -d
else
    # Start services
    echo "🚀 Starting Graphiti MCP OpenAI Compatible version..."
    docker compose up -d
fi



# Get PORT environment variable for display
PORT_VALUE=$(get_env_var "PORT")
if [ -z "$PORT_VALUE" ]; then
    PORT_VALUE="8000"
fi

echo "✅ Services started successfully!"
echo "✨ MCP Server: http://localhost:${PORT_VALUE}"
echo "✨ Neo4j Browser: http://localhost:7474"
echo "✨ Use 'docker compose logs -f' to view logs"
echo "🛑 Use 'docker compose down' to stop services"