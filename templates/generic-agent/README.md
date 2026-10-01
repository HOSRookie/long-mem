# 任何支持 MCP 的 agent

三样东西：

## 1. 一份常驻规则

告诉它：唯一长期记忆是 long_mem；压缩后直接续接；写入边界。精简，每轮都计费。

抄 `templates/cline/cline-rules.md` 或 `templates/codex/AGENTS-snippet.md`。

## 2. 压缩笔记模板

抄 `templates/codex/compact-prompt.md`。

## 3. MCP server 配置

```json
{
  "mcpServers": {
    "long_mem": {
      "command": "python3",
      "args": ["<长路径>/long_mem/governance/gateway.py"],
      "env": {
        "LONG_MEM_REGISTRY": "<长路径>/long_mem/governance/registry.json",
        "ENGRAM_DATA_DIR": "/你的/engram/数据目录"
      }
    }
  }
}
```

## 防落错桶

从固定主目录启动的 agent，设 `LONG_MEM_WORKSPACE` 为项目根。否则同一份库会被按启动目录名切成分区。

## 有钩子系统的

把 `governance/hook.py` 挂上去：

- 会话开始 → `python3 hook.py start`
- 压缩后 → `python3 hook.py compact`

hook.py 从 stdin 读 JSON（带 `cwd`），往 stdout 吐要注入的文本。
