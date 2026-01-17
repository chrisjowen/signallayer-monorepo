#!/bin/bash

# Script to kill processes running on specified ports
# Usage: ./kill-ports.sh [port1] [port2] ...
# If no ports specified, uses default ports from Procfile

# Default ports (uvicorn default is 8000)
DEFAULT_PORTS=(8000)

# Use provided ports or default
PORTS=("${@:-${DEFAULT_PORTS[@]}}")

echo "🔍 Checking for processes on ports: ${PORTS[*]}"
echo ""

for PORT in "${PORTS[@]}"; do
    echo "Checking port $PORT..."
    
    # Find process ID using lsof
    PID=$(lsof -ti :$PORT)
    
    if [ -z "$PID" ]; then
        echo "  ✓ No process found on port $PORT"
    else
        echo "  ⚠️  Found process(es) with PID: $PID"
        echo "  🔫 Killing process(es)..."
        
        # Kill the process
        kill -9 $PID 2>/dev/null
        
        if [ $? -eq 0 ]; then
            echo "  ✅ Successfully killed process on port $PORT"
        else
            echo "  ❌ Failed to kill process on port $PORT (may require sudo)"
        fi
    fi
    echo ""
done

echo "✨ Done!"
