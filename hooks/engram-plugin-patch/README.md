# engram 上游插件补丁

上游 engram 的 Codex 插件默认有 5 个钩子，3 个会采你的数据：

| 钩子 | 上游干什么 | 风险 |
|---|---|---|
| UserPromptSubmit | 采你每次提交的提示词 | 可能带凭据 |
| SubagentStop | 被动捕获子代理输出 | 可能存下不该存的 |
| SessionEnd | 强制生成会话摘要 | 同上 |

补丁把这 3 个改成 `exit 0`，只留会话开始和压缩恢复。

## 用

1. 先装上游插件：`engram setup codex`
2. 找到它的脚本目录，一般在 `~/.codex/plugins/cache/engram/engram/<版本>/scripts/`
3. 覆盖：

```sh
cp user-prompt-submit.sh <脚本目录>/
cp subagent-stop.sh <脚本目录>/
cp session-end.sh <脚本目录>/
```

4. 把 `session-start.sh` 和 `post-compaction.sh` 换成指到 long_mem 治理 hook 的版本。

## 注意

插件升级会覆盖补丁，升级后重新打。
