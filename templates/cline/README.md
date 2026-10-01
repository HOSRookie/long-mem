# Cline

把 `cline-rules.md` 追到 Cline 的用户级规则文件。

记忆读写走 CLI，因为 Cline 不原生接 MCP stdio：

```sh
ENGRAM_DATA_DIR=<数据目录> engram context <project>      # 读
ENGRAM_DATA_DIR=<数据目录> engram save <标题> <内容> --project <project>   # 写
ENGRAM_DATA_DIR=<数据目录> engram search <关键词> --project <project>      # 搜
```

数据目录看治理 registry.json 的 database 字段。

## 注意

Cline 没有压缩后自动注入的钩子。能不能续接看 Cline 自己的规则持久化，以及 agent 守不守规则文件里的纪律。

中文搜索弱，召回靠 context 拉索引再按 ID 读。
