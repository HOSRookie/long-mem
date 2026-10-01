# 使用流程

从零到跑通。以 Codex 为例，其他 agent 看模板目录。

## 前置

- macOS 或 Linux。Windows 得自己改 bash 脚本。
- Python 3.8+，系统自带就行，不用 pip 装东西。
- 你的 agent。

## 1. 装 engram

long_mem 不含记忆后端。先装：

```sh
brew install engram
engram --version   # 要 v1.19 以上
```

没 brew 去 [上游仓库](https://github.com/Gentleman-Programming/engram) 看别的装法。

## 2. 装 long_mem

Codex 走插件。在 `~/.codex/config.toml` 里加：

```toml
[marketplaces.long-mem]
source_type = "git"
source = "<仓库地址>"
ref = "main"

[plugins."long-mem@long-mem"]
enabled = true
```

刷新插件。

第一次开会话时，插件自己生成 `governance/registry.json`。它拿你启动时所在目录当项目根。不对就手动编辑那个文件。

registry.json 长这样：

```json
{
  "binary": "/path/to/engram",
  "database": "/path/to/engram.db",
  "native_probe_url": "http://127.0.0.1:7437/project/current",
  "shared_projects": [],
  "projects": {
    "myproject": { "roots": ["/path/to/myproject"], "aliases": [] }
  }
}
```

多项目就加多个条目。`shared_projects` 里填的项目，它的 pinned 约束会在启动时也注入进来。

## 3. 起 engram serve

```sh
ENGRAM_DATA_DIR=~/.engram engram serve &
```

治理层写入前要用它的本机探针核验项目归属。不起的话写入被拒，报 `native_project_binding_unverified`。

开机自启：macOS 写个 launchd 的 LaunchAgent，Linux 写 systemd user service。命令就是上面那条。

## 4. 验证

开新会话，进你登记的项目目录。说：

> 记住：这个项目的测试命令是 make test

让它 pin。关掉会话。开新会话，问测试命令是什么。它应该记得。

压缩续接单独验：跑长任务到触发压缩，压缩后它应该直接接着干，不重新问你。

## 5. 日常

机制本身不用管。记住三件事：

- 说「这个值得长期记住」。只有 pin 的是长期，其余 24 到 48 小时过期。
- 同主题更新同一条，别平行堆。堆多了会冲突。
- 只读的活开头说「这次只读，别写记忆」。

## 其他 agent

- Cline：把 `templates/cline/cline-rules.md` 追加到用户级规则文件。记忆读写走 CLI，看那个目录的 README。
- ZCode：看 `templates/zcode/README.md`。
- 其他支持 MCP 的：看 `templates/generic-agent/README.md`。核心是把 MCP server 指到 `governance/gateway.py`。

## 出问题

| 症状 | 原因 | 怎么办 |
|---|---|---|
| `native_project_binding_unverified` | serve 没起，或探针返回的项目跟 registry 不一致 | 起 serve；核对 registry.json 的根目录 |
| `explicit_project_required` | 当前目录没登记 | 显式传 project，或登记该目录 |
| 落错桶、搜不到 | 从 HOME 启动，项目标签没锁 | 设 `LONG_MEM_WORKSPACE` 为项目根 |
| 中文搜不到 | engram 的 FTS 对中文分词弱 | 用 `engram context <project>` 拉索引，再按 ID 读 |

## 常见问题

数据在哪？本机 SQLite 文件，默认 `~/.engram/engram.db`。云同步默认关。

能换别的记忆后端吗？能，但得改 `governance/gateway.py` 里的上游调用。方法论本身跟后端无关。

为什么第一次没有记忆？新库是空的。用几次就有了。
