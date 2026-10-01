#!/usr/bin/env bash
# long_mem 插件自举：首次启用时自动运行，配置 registry.json。
# 插件的 session-start 钩子检测 registry.json 不存在时调用本脚本；也可以手动跑。
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GOVERNANCE_DIR="$PLUGIN_ROOT/governance"
REGISTRY="$GOVERNANCE_DIR/registry.json"

# MCP 启动器：让不接受绝对路径的 agent（如 Kimi Code）也能拉起治理 gateway。
# 幂等：shim 已指向本仓库 gateway 时跳过。
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"
SHIM="$BIN_DIR/long-mem-gateway"
if [ ! -x "$SHIM" ] || ! grep -q "$GOVERNANCE_DIR/gateway.py" "$SHIM" 2>/dev/null; then
    printf '#!/usr/bin/env bash\nexec python3 "%s" "$@"\n' "$GOVERNANCE_DIR/gateway.py" > "$SHIM"
    chmod +x "$SHIM"
    echo "long_mem: 已安装 MCP 启动器 $SHIM"
fi
case ":$PATH:" in
    *":$BIN_DIR:"*) : ;;
    *) echo "long_mem: 提示 — $BIN_DIR 不在 PATH 里，加入后 agent 才能找到 long-mem-gateway" >&2 ;;
esac

# 已配置过就直接退出
[ -f "$REGISTRY" ] && exit 0

# 需要 engram
ENGRAM_BIN="${ENGRAM_BIN:-}"
if [ -z "$ENGRAM_BIN" ]; then
    ENGRAM_BIN="$(command -v engram 2>/dev/null || true)"
fi
if [ -z "$ENGRAM_BIN" ] && [ -f "${HOME}/.engram/governance/active/registry.json" ]; then
    ENGRAM_BIN="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("binary", ""))' "${HOME}/.engram/governance/active/registry.json")"
fi
if [ -z "$ENGRAM_BIN" ] || [ ! -x "$ENGRAM_BIN" ]; then
    echo "long_mem: 需要 engram。先跑: brew install engram" >&2
    exit 1
fi

# 数据库默认位置
DB_DIR="${ENGRAM_DATA_DIR:-$HOME/.engram}"
DB_PATH="$DB_DIR/engram.db"
mkdir -p "$DB_DIR"

# 从当前目录猜项目（如果是 git 仓库）
CWD="${PWD:-$HOME}"
PROJ_ROOT="$CWD"
PROJ_ID="$(basename "$PROJ_ROOT" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')"

# 写 registry.json
cat > "$REGISTRY" <<EOF
{
  "version": 1,
  "binary": "$ENGRAM_BIN",
  "database": "$DB_PATH",
  "native_probe_url": "http://127.0.0.1:7437/project/current",
  "shared_projects": [],
  "projects": {
    "$PROJ_ID": {
      "roots": ["$PROJ_ROOT"],
      "aliases": []
    }
  }
}
EOF

echo "long_mem: 已生成 $REGISTRY（项目: $PROJ_ID → $PROJ_ROOT）"
echo "long_mem: 如需修改，直接编辑该文件"
