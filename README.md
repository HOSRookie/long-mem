# long_mem

AI 编码代理干着活就失忆。这个让它不失忆。

窗口被压缩、被重置、隔几天再开，它照样接着干，不用你重复说。

实证：Codex CLI 连续跑了 5 天 21 小时，压缩 40 多次，没丢过上下文。

这玩意是从一个更大的 AI 任务治理项目里拆出来的。那个项目由 AI 代理自己推进，多天连续运行，全程有公开记录：[nextAgentPolars/polars-log](https://github.com/nextAgentPolars/polars-log)。

---

## 问题

你用 Claude Code、Codex、Cline 还是别的，都碰过：

- 上下文满了，压缩，agent 失忆
- 忘了你给过的授权，重做已经做完的活
- 或者直接说「我丢了上下文，你再说一遍」

long_mem 的做法：窗口里的东西会丢，那就别放窗口里。写到外面的持久存储，窗口里只放指针。压缩后按指针把原文读回来。

两层存储：

| 层 | 管什么 | 靠什么 |
|---|---|---|
| 历史召回 | 发生了什么 | agent 自己的 history 工具（如 Codex 的 SQLite history） |
| 判断沉淀 | 为什么这么定 | [engram](https://github.com/Gentleman-Programming/engram) |

治理层是这个项目的重点。把上游记忆插件的提示词采集、被动捕获、强制摘要三个自动口子焊死，只留启动注入和压缩恢复。防的是 agent 自己把记忆库搞脏。

## 装

### 先说清楚：engram 要单独装

long_mem 不含记忆后端。必须先装 [engram](https://github.com/Gentleman-Programming/engram)：

```sh
brew install engram
```

没 brew 的去上游仓库看别的装法。

### 装 long_mem（Codex 插件）

先拿到代码：

```sh
# 用 marketplace 直接加，不用手动 clone
```

在 `~/.codex/config.toml` 里加：

```toml
[marketplaces.long-mem]
source_type = "git"
source = "<这个仓库的地址>"
ref = "main"

[plugins."long-mem@long-mem"]
enabled = true
```

刷新 Codex 插件。完事。

第一次开会话时，插件自己生成配置（`governance/registry.json`），你不用管。

### 起 engram serve

```sh
ENGRAM_DATA_DIR=~/.engram engram serve &
```

治理层写入前要用它的本机探针核验项目归属。不起的话写入会被拒。

建议配成开机自启（macOS 用 launchd，Linux 用 systemd）。命令就是这个。

## 用

### 第一次

插件会拿你启动时所在的项目目录自动登记。如果不对，直接编辑 `governance/registry.json`。

### 日常

三件事：

- 告诉它「这个值得长期记住」。只有 pin 的才是长期资产，其余 24 到 48 小时自动过期。
- 同主题让它更新同一条，别平行堆。
- 只读的活开头说一句「这次只读，别写记忆」。

其他时间不用管机制本身。

### 验证它到底有没有用

1. 开新会话，说「记住：这个项目的测试命令是 make test」。
2. 让它 pin。
3. 关掉会话，开新会话，问它测试命令是什么。
4. 它应该记得。

压缩续接单独验：跑个长任务到触发压缩，压缩后它应该直接接着干，不重新问你。

## 其他 agent

| Agent | 看哪 |
|---|---|
| Cline | [templates/cline](templates/cline/) |
| ZCode | [templates/zcode](templates/zcode/) |
| 其他支持 MCP 的 | [templates/generic-agent](templates/generic-agent/) |

## 目录

```
governance/     治理层：项目路由、只读索引、钩子、MCP 写入口
templates/      各 agent 接入模板
hooks/          上游 engram 插件补丁（禁掉采集钩子）
scripts/        插件脚本（启动注入、压缩恢复、自举）
docs/           使用流程
```

## 出问题

| 症状 | 原因 | 怎么办 |
|---|---|---|
| 写入报 `native_project_binding_unverified` | engram serve 没起，或探针返回的项目跟 registry 不一致 | 起 serve；核对 registry.json 的根目录 |
| 写入报 `explicit_project_required` | 当前目录没登记 | 显式传 project，或在 registry.json 里登记 |
| 记忆落错桶、搜不到 | 从 HOME 启动，项目标签没锁 | 设 `LONG_MEM_WORKSPACE` 为项目根 |
| 中文搜不到 | engram 的 FTS 对中文分词弱 | 用 `engram context <project>` 拉索引，再按 ID 读正文 |

## 已知限制

- engram 的中文全文搜索弱。召回靠索引加按 ID 读，不靠搜索。
- 单信任域。多 agent 共用同一库时，权限靠行为规范，不是访问控制。
- 什么该存、什么不该存，靠 agent 判断。机制只保证存了的不丢。

## 安全

- 数据库读取只读。
- 写入唯一入口是治理 gateway，写前用本机 HTTP 探针核验项目。
- `mem_delete`、`mem_capture_passive`、`mem_save_prompt` 被封禁。
- 云同步默认关。
- 不采集提示词，不做被动捕获。

## 多端兼容

核心是同一个 MCP gateway + engram；各家的差异只在清单格式和钩子能力。

| Agent | MCP | 常驻规则 | 生命周期钩子 | 手动恢复 | 安装入口 |
|---|---|---|---|---|---|
| **Codex** | ✓ | AGENTS.md 模板 | ✓ 插件 hooks（startup/resume/clear + compact） | compact-prompt 模板 | [PLUGIN.md](PLUGIN.md) |
| **Claude Code** | ✓ | `inject-rules.sh` 注入 CLAUDE.md | ✓ SessionStart（startup/resume/clear/compact） | skill `long-mem-recover` | 市场：`.claude-plugin/marketplace.json` |
| **ZCode** | ✓ | rules 模板 | ✓ SessionStart（compact matcher 待实测） | skill `long-mem-recover` | 市场：根目录 [marketplace.json](marketplace.json) |
| **Kimi Code** | ✓ 插件捆绑 | SYSTEM.md 系统提示注入 | sessionStart.skill ✓（hooks 待官方稳定） | skill | `/plugins install adapters/kimi-code`，见 [adapters/kimi-code](adapters/kimi-code/README.md) |
| **Gemini CLI / Qwen Code** | ✓ | `inject-rules.sh` 注入 GEMINI.md / QWEN.md | ✗ 无钩子 → 规则 + 手动 | 规则指令 | `scripts/inject-rules.sh` |
| **DeepSeek Harness** | 大概率兼容 Claude 插件格式（官方定位为 Claude Code 对标，未验证） | 同上 | 未验证 | 同上 | 试 `.claude-plugin` 市场 |
| **MiniMax / 其他支持 MCP 的 agent** | ✓（MCP 标准） | `inject-rules.sh` | 视各家 | `inject-rules.sh` | generic 模板 |

原则：**MCP 是最大公约数，钩子是加分项。**没有钩子的 agent 用常驻规则 + 手动恢复 skill 也能拿到 90% 的价值；有钩子的 agent 额外获得零操作注入。

## 捐赠

海外：[GitHub Sponsors](https://github.com/sponsors/HOSRookie)

国内：扫码请作者喝杯咖啡。

| 支付宝 | 微信 |
|---|---|
| <img src="docs/images/donate-alipay.jpg" width="240"/> | <img src="docs/images/donate-wechat.jpg" width="240"/> |

## 许可

[MIT](LICENSE)
