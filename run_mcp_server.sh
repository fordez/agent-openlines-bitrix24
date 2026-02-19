#!/bin/bash
# Wrapper script to run mcp_server.py with explicit environment variable debugging

# Export variables to ensure they are available (redundant if inherited, but good for clarity)
export REDIS_URL="$REDIS_URL"
export BITRIX_DOMAIN="$BITRIX_DOMAIN"

# Echo strictly to stderr to avoid breaking the JSON-RPC protocol on stdout
>&2 echo "Wrapper running for $0"
>&2 echo "REDIS_URL in wrapper: $REDIS_URL"
>&2 echo "BITRIX_DOMAIN in wrapper: $BITRIX_DOMAIN"

# Execute the python script, passing all arguments
exec python mcp_server.py "$@"
