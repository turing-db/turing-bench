#!/bin/bash

# open_tmux_session.sh

if [ $# -lt 2 ]; then
    echo "Usage: $0 SESSION_NAME SCRIPT_PATH [READY_MESSAGE]"
    echo "Example: $0 turingdb ~/scripts/spawn_turingdb.sh 'Server listening'"
    exit 1
fi

SESSION_NAME="$1"
SCRIPT_PATH="$2"
READY_MESSAGE="${3:-Server listening}"  # Default to "Server listening" if not provided

if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Script not found at $SCRIPT_PATH"
    exit 1
fi

chmod +x "$SCRIPT_PATH"

tmux has-session -t "$SESSION_NAME" 2>/dev/null

if [ $? != 0 ]; then
    tmux new-session -d -s "$SESSION_NAME"
    tmux send-keys -t "$SESSION_NAME" "bash $SCRIPT_PATH" C-m
    
    echo "✓ Created tmux session: $SESSION_NAME"
    echo "  Waiting for server to start (looking for: '$READY_MESSAGE')..."
    
    # Wait for the ready message in tmux session output
    timeout 300 bash -c "until tmux capture-pane -t '$SESSION_NAME' -p | grep -q '$READY_MESSAGE'; do sleep 0.2; done"
    
    if [ $? -eq 0 ]; then
        echo "✓ Server is ready!"
        echo "  To attach: tmux a -t $SESSION_NAME"
    else
        echo "✗ Server failed to start within 30 seconds"
        tmux kill-session -t "$SESSION_NAME"
        exit 1
    fi
else
    echo "⚠ Session $SESSION_NAME already exists"
    echo "  To attach: tmux a -t $SESSION_NAME"
    echo "  To kill: tmux kill-session -t $SESSION_NAME"
fi