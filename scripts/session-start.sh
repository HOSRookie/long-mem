#!/usr/bin/env bash
# long_mem 插件：会话开始钩子。
# registry.json 不存在时先自举，再注入上下文。
set -euo pipefail
PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 首次运行：自动生成 registry.json
if [ ! -f "$PLUGIN_ROOT/governance/registry.json" ]; then
    "$PLUGIN_ROOT/scripts/bootstrap.sh" || true
fi

exec python3 "$PLUGIN_ROOT/governance/hook.py" start
