#!/usr/bin/env bash
# long_mem 插件：MCP server 启动脚本。自定位治理 gateway，无需硬编码路径。
set -euo pipefail
PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$PLUGIN_ROOT/governance/gateway.py"
