#!/usr/bin/env bash
# long_mem 插件：压缩后恢复钩子。注入治理协议 + "直接续接"指令。
set -euo pipefail
PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$PLUGIN_ROOT/governance/hook.py" compact
