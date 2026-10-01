# long_mem

[English](README.md) | 简体中文

**Compaction-proof memory for AI coding agents.**

> 对话不是存储介质。
> 窗口里的东西会丢，那就别放窗口里——写到外部持久存储，窗口里只放指针。

![License](https://img.shields.io/badge/license-MIT-blue)
![Agents](https://img.shields.io/badge/agents-Codex·ClaudeCode·ZCode·KimiCode-8A2BE2)
![实测](https://img.shields.io/badge/实测-5天21小时·40%2B次压缩·零丢失-green)
![X](https://img.shields.io/badge/X-%40Rylie1933-black?logo=x)

**long_mem** 让 AI 编码代理在上下文压缩、会话重置、隔天续开之后照样接着干——不用你重复说一遍。

实证：Codex CLI 连续跑了 **5 天 21 小时**，压缩 **40 多次**，没丢过上下文。全程公开记录：[polars-log](https://github.com/nextAgentPolars/polars-log)。

构建过程与动态长期更新于 X：**[@Rylie1933](https://x.com/Rylie1933)**。

## 为什么需要它

所有 AI 编码代理（Claude Code、Codex、ZCode、Kimi Code……）都有同一个病：**对话就是它的全部记忆**。于是：

- 窗口满了 → 压缩 → agent 失忆，忘掉你给过的授权和约束
- 隔天续开 → 重来一遍，重做已经做完的活
- 更糟的：一些上下文插件开始**采集你的提示词**、被动捕获子代理输出、强制生成摘要——把你的对话变成它的数据源

常见的补救是更好的摘要——那只是**更好的有损压缩**。

long_mem 的做法是一个反转：**对话不是存储介质。**唯一长期记忆住在外部持久存储（engram + agent 自身 history），窗口里只放指针。压缩毁掉的是"对话"，而对话里没有唯一状态——所以压缩成了非事件。

## 工作原理

```text
┌─ 会话启动 ────────────▶ 注入治理协议 + pinned 记忆索引
│
├─ 会话中 ……  agent 把"值得记的判断"写入 engram（经治理 gateway）
│              窗口里只有指针，按 ID 回读正文
│
├─ 上下文压缩 ──────────▶ 注入"直接续接"指令；按指针恢复，不重存摘要
│
└─ 会话结束/隔天续开 ──▶ 从 engram + history 按需重建，不靠对话
```

**两层存储：**

| 层 | 管什么 | 靠什么 |
|---|---|---|
| 历史召回 | 发生了什么 | agent 自带 history（如 Codex 的 SQLite history） |
| 判断沉淀 | 为什么这么定 | [engram](https://github.com/Gentleman-Programming/engram) |

**治理层是这个项目的重点。**上游记忆插件的三个自动口子——提示词采集、被动捕获、强制摘要——被焊死，只留启动注入和压缩恢复。防的是 agent 自己把记忆库搞脏：

| 上游钩子 | 上游行为 | long_mem |
|---|---|---|
| UserPromptSubmit | 采集每次提示词 | ❌ 焊死（可能带凭据） |
| SubagentStop | 被动捕获子代理输出 | ❌ 焊死 |
| SessionEnd | 强制生成摘要 | ❌ 焊死 |
| SessionStart | 注入记忆 | ✅ 保留 |
| 压缩后 | 恢复上下文 | ✅ 保留 |

## 快速开始

前置：安装 [engram](https://github.com/Gentleman-Programming/engram)：

```sh
brew install engram
```

然后按你的 agent 选一行：

| Agent | 安装 |
|---|---|
| **Codex** | 见 [PLUGIN.md](PLUGIN.md)（config.toml 加 marketplace） |
| **Claude Code** | `claude plugin marketplace add HOSRookie/long-mem` → install long-mem |
| **ZCode** | 插件市场 → 添加 → 粘贴本仓库地址 |
| **Kimi Code** | `/plugins install <本仓库>/adapters/kimi-code`，见[适配说明](adapters/kimi-code/README.md) |
| **Gemini / Qwen / MiniMax / 其他** | 克隆本仓库 → `scripts/inject-rules.sh` + 按[兼容矩阵](#兼容矩阵)配 MCP |

装完之后：开新会话，agent 自动看到治理协议和你项目的 pinned 记忆索引。压缩之后它会直接续接——试一下就懂了。

## 兼容矩阵

| Agent | MCP | 常驻规则 | 生命周期钩子 | 手动恢复 |
|---|---|---|---|---|
| Codex | ✓ | AGENTS.md | ✓ 插件 hooks | compact-prompt |
| Claude Code | ✓ | CLAUDE.md 注入 | ✓ SessionStart（含 compact） | skill long-mem-recover |
| ZCode | ✓ | rules 模板 | ✓ SessionStart（compact matcher 待实测） | skill long-mem-recover |
| Kimi Code | ✓ 插件捆绑 | systemPrompt 注入 | sessionStart.skill ✓（hooks 待验证） | skill |
| Gemini / Qwen / 其他 | ✓ | inject-rules.sh | —（规则 + 手动恢复） | skill |

原则：**MCP 是最大公约数，钩子是加分项。**没有钩子的 agent 用常驻规则 + 手动恢复 skill 也能拿到 90% 的价值；有钩子的 agent 额外获得零操作注入。

## 治理与安全

记忆库的信任模型是 fail-closed：

- 写入唯一入口是治理 gateway：工具黑名单（`mem_delete` / `mem_capture_passive` / `mem_save_prompt` / `mem_merge_projects`）
- 上游二进制 sha256 身份门：漂移即拒
- 会话 ↔ 项目双重绑定（DB 属主检查 + 本机探针独立验证）
- 记忆内容 16KB 上限——正文放外面，记忆里存证据引用
- 数据库读取强制只读；云同步默认关；凭证明文不进记忆

完整协议见 [governance/POLICY.md](governance/POLICY.md)。

## 已知限制

- engram 的中文全文搜索弱：召回靠索引 + 按 ID 读，不靠搜索
- 单信任域：多 agent 共库时，权限靠行为规范而非访问控制
- 什么该存靠 agent 判断：机制保证存了的不丢，不保证判断本身正确

## 反馈与贡献

- 建议与反馈：欢迎开 [Issue](https://github.com/HOSRookie/long-mem/issues)，每条都会看。
- 代码贡献：先开 Issue 对齐方向；main 分支受保护，PR 由作者审核后合并——**防投毒是第一原则**。

## 文档

[PLUGIN.md](PLUGIN.md) · [docs/USAGE.md](docs/USAGE.md) · [adapters/](adapters/) · [templates/](templates/) · [governance/POLICY.md](governance/POLICY.md)

## 生态

long_mem 是一套更大工程体系的冰山一角：

- **北极星**（进行中）— 面向严肃开发场景的 agent 任务治理系统，long_mem 只是从它拆出来的一个微不足道的小功能。可以透露的一点：我在用结构化治理层抑制 LLM 的幻觉——**不是消灭幻觉，是让幻觉没有可以生效的场景**。公开过程记录：[polars-log](https://github.com/nextAgentPolars/polars-log)。
- **蓝色空间号**（保密中）— 名字很浪漫，东西还在验证。等它值得说的时候，这里会有链接。

如果这个方向对你有吸引力，欢迎点个 Star——对长周期项目来说，Star 是为数不多的燃料。

## 赞赏

开发这个项目烧的是真金白银的 token。如果 long_mem 实实在在帮到了你，厚着脸皮讨一份打赏——每一份都会变成下一轮实验的上下文窗口。

海外：[GitHub Sponsors](https://github.com/sponsors/HOSRookie)

国内：扫码请作者喝杯咖啡。

| 支付宝 | 微信 |
|---|---|
| <img src="docs/images/donate-alipay.jpg" width="240"/> | <img src="docs/images/donate-wechat.jpg" width="240"/> |

## 许可

[MIT](LICENSE)
