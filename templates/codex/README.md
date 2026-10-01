# Codex

走插件，别手动改配置。看仓库根目录的 [PLUGIN.md](../../PLUGIN.md)。

## 插件装不了的时候

手动接：

1. 把 `config-snippet.toml` 合到 `~/.codex/config.toml`，把 `<LONG_MEM_HOME>` 换成实际路径。
2. 把 `AGENTS-snippet.md` 追到 `~/.codex/AGENTS.md`。
3. 把 `compact-prompt.md` 的内容放到 `~/.codex/`，在 config 里指过去。
4. 起 engram serve。

## 验证

开新会话说一句话要它记住，pin，关掉，再开，问它。它应该记得。
