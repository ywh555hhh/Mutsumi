#!/usr/bin/env bash
# demo.sh — Demonstrate Mutsumi's live-reload by adding tasks via CLI
#
# Run this in the LEFT pane while Mutsumi runs in the RIGHT pane.
# Watch tasks appear in real-time!
#
# Usage:
#   bash scripts/demo.sh

set -euo pipefail

echo "=== Mutsumi Demo ==="
echo "Adding tasks... watch the TUI update in real-time!"
echo ""

# Initialize tasks.json (skip if exists)
mutsumi init --force 2>/dev/null || true
sleep 1

echo "[1/4] Adding high-priority task..."
mutsumi add "Refactor Auth module" -P high -s day -t "dev,backend"
sleep 1

echo "[2/4] Adding normal-priority task..."
mutsumi add "Write unit tests" -P normal -s day -t "test"
sleep 1

echo "[3/4] Adding low-priority task..."
mutsumi add "Update README" -P low -s week -t "docs"
sleep 1

echo "[4/4] Adding inbox task..."
mutsumi add "Buy coffee beans" -P low -s inbox -t "life"
sleep 1.5

echo ""
echo "Demo complete! All tasks should be visible in Mutsumi."
echo "Try: mutsumi done <id-prefix> to complete a task."
