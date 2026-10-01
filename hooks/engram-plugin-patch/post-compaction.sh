#!/bin/bash
# long_mem: 压缩后恢复，注入"压实直接续接"指令。
# 把 <LONG_MEM_HOME> 替换为实际路径。
exec python3 "<LONG_MEM_HOME>/governance/hook.py" compact
