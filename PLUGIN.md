# 插件说明

Codex 用户走插件，别手动改一堆配置。

## 前提

1. 装了 engram：`brew install engram`
2. engram serve 在跑。不起的话写入会被拒。

## 装

在 `~/.codex/config.toml` 里加：

```toml
[marketplaces.long-mem]
source_type = "git"
source = "<这个仓库的地址>"
ref = "main"

[plugins."long-mem@long-mem"]
enabled = true
```

刷新插件。

本地测的时候把 source_type 改成 local，source 填本地路径。

## 插件干什么

| 什么时候 | 干什么 |
|---|---|
| 会话开始（startup/resume/clear） | 注入治理协议加当前项目的 pinned 索引 |
| 压缩后（compact） | 注入「直接续接」指令加治理协议 |
| MCP 连接 | 起治理 gateway，提供受控的记忆读写 |
| 第一次启动 | 自动生成 `governance/registry.json` |

## 插件不干什么

- 不采集你的提示词（没 UserPromptSubmit 钩子）
- 不被动捕获输出（没 SubagentStop 钩子）
- 不强制生成摘要（没 SessionEnd 钩子）
- 不自动云同步（gateway 里写死关）
- 不删记忆（`mem_delete` 被禁）

## 文件

```
.codex-plugin/plugin.json   插件声明
.mcp.json                   MCP 声明
hooks/hooks.json            两个钩子
scripts/session-start.sh    启动注入（首次会自举配置）
scripts/post-compaction.sh  压缩恢复
scripts/mcp-gateway.sh      MCP 启动（自己定位路径）
scripts/bootstrap.sh        首次配置生成
```

## 验证

1. 启用后开新会话，看有没有加载记忆的提示。
2. 说一句要记住的话，让它 pin。
3. 关会话，开新会话，问它。它应该记得。
4. 跑到压缩，压缩后应该直接接着干。

没反应先看「出问题」表，在 README 里。
