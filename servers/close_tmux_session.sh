#!/bin/bash

# close_tmux_session.sh

# Usage: ./close_tmux_session.sh SESSION_NAME SCRIPT_PATH [STOP_MESSAGE]
# Example: ./close_tmux_session.sh turingdb ~/scripts/stop_turingdb.sh "Terminating server"

if [ $# -lt 2 ]; then
    echo "Usage: $0 SESSION_NAME SCRIPT_PATH [STOP_MESSAGE]"
    echo "Example: $0 benchmark-turingdb-server /path/to/stop_turingdb.sh 'Terminating server'"
    exit 1
fi

SESSION_NAME="$1"
SCRIPT_PATH="$2"
STOP_MESSAGE="${3:-}"

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

chmod +x "$SCRIPT_PATH"

tmux has-session -t "$SESSION_NAME" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Stopping server..."
    
    # Run the stop script
    bash "$SCRIPT_PATH"
    
    # Wait for the stop message if provided
    if [ -n "$STOP_MESSAGE" ]; then
        echo "Waiting for graceful shutdown (looking for: '$STOP_MESSAGE')..."
        while ! tmux capture-pane -t "$SESSION_NAME" -p | grep -q "$STOP_MESSAGE"; do
            sleep 0.2
        done
    else
        # If no message provided, wait a bit for graceful shutdown
        sleep 2
    fi
    
    # Kill the tmux session
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
        tmux kill-session -t "$SESSION_NAME"
        echo "✓ Server stopped and session closed"
    fi
else
    echo "⚠ Session $SESSION_NAME not running"
fi