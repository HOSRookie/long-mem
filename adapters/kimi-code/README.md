# long_mem · Kimi Code 适配

Kimi Code（CLI / Desktop）的插件格式是 `kimi.plugin.json`：可以捆绑 Skills、系统提示词注入和 MCP 服务。

## 前提

1. 装了 engram：`brew install engram`
2. 克隆了 long_mem 仓库，并跑过一次 `scripts/bootstrap.sh`（生成 registry.json + 安装 `long-mem-gateway` 启动器到 `~/.local/bin`）
3. `~/.local/bin` 在 PATH 里（bootstrap 会提示）

> Kimi Code 的 MCP stdio `command` 必须在 PATH 上或以 `./` 开头，不接受绝对路径——所以用 PATH 上的 `long-mem-gateway` 启动器间接指向治理 gateway。

## 安装

```sh
/path/to/kimi-code /plugins install /Volumes/移动硬盘/long_mem/adapters/kimi-code
```

或在 Kimi Code 里 `/plugins` → Custom → 选择 `adapters/kimi-code` 目录。装完 `/reload` 或开新会话生效。

## 生效内容

| 组件 | 说明 |
|---|---|
| `SYSTEM.md` | 常驻系统提示：压缩直接续接、写入边界、fail-closed 规则 |
| `skills/long-mem-recover` | 会话开始自动加载 + 手动恢复入口 |
| `mcpServers.long_mem` | 治理 gateway（黑名单/绑定验证/内容上限全在） |

## 边界

- Kimi Code 的 lifecycle hooks 尚未稳定（开源 kimi-cli 里还是提案），本适配**不依赖 hooks**：会话上下文注入走 `sessionStart.skill` + `systemPromptPath`，恢复走 skill。
- 插件被复制到 `$KIMI_CODE_HOME/plugins/managed/` 运行——所以 MCP 走 PATH 启动器，不写相对路径。
