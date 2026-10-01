#!/bin/bash
# long_mem: 会话开始，注入治理 POLICY + 项目 pinned 索引。
# 把 <LONG_MEM_HOME> 替换为实际路径。
exec python3 "<LONG_MEM_HOME>/governance/hook.py" start
