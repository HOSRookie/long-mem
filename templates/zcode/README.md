# ZCode

把 `zcode-rules.md` 追到 ZCode 的用户级规则文件。

## 接 MCP

ZCode 支持 MCP 的话，照 `templates/codex/config-snippet.toml` 里 `[mcp_servers.long_mem]` 那段的写法配。

从固定目录启动的，设 `LONG_MEM_WORKSPACE` 为项目根，防落错桶。

## 注意

ZCode 的钩子系统跟 Codex 不一样，可能没有压缩钩子。压缩后能不能续接，靠规则文件里的纪律。
