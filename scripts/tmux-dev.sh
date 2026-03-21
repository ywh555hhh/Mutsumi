#!/usr/bin/env bash
# tmux-dev.sh — Launch a split-pane tmux session with Mutsumi
#
# Usage:
#   bash scripts/tmux-dev.sh [session-name]
#
# Environment:
#   MUTSUMI_WIDTH  — right pane width percentage (default: 30)

set -euo pipefail

SESSION="${1:-dev}"
PANE_PCT="${MUTSUMI_WIDTH:-30}"

# Kill existing session with same name (ignore errors)
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create new session
tmux new-session -d -s "$SESSION"

# Split: left = shell, right = mutsumi
tmux split-window -h -p "$PANE_PCT" -t "$SESSION" "mutsumi"

# Focus on the left pane (your working shell)
tmux select-pane -t "$SESSION":0.0

# Attach
tmux attach -t "$SESSION"
