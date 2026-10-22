# Where the numbers come from

The figure in the README is generated from Codex's own session database, not from a hand-kept log.

## Source

`~/.codex/thread_history_1.sqlite`, table `thread_items`. Compactions are stored as `item_type = 'contextCompaction'` with a millisecond timestamp in `created_at_ms`.

```sql
SELECT thread_id, created_at_ms
FROM thread_items
WHERE item_type = 'contextCompaction'
ORDER BY created_at_ms;
```

## The session in the figure

`01a04e60-b4b2-7843-870c-ddcaa0d5fe67`, 2026-08-30 00:37 → 2026-09-01 12:42 (UTC+8).

- 49 compactions
- 60.09 h wall clock
- median gap between compactions: 0.608 h
- longest unbroken run: 17.20 h
- 134 messages from the user

"Unbroken run" means no gap longer than 30 minutes between recorded events. It is a threshold, not a measurement of continuous execution. Change the threshold and the number changes.

The grey bars are recorded events per hour — reasoning, command execution, file changes, messages. They are an activity proxy, not token usage.

## Recovery after compaction

For each compaction, look for an engram tool call (`mem_context`, `mem_get_observation`, `mem_search`, `mem_timeline`) that happened after the compaction and before the next user message.

In this session: 46 of 49, median 1.6 minutes after the compaction.

Across the 22 sessions that used the memory tools at all, the same check matches 228 of 504 compactions.

## What this does not show

- It does not measure whether the model's context was complete. A memory read before the next prompt shows the store was consulted, not that nothing was lost.
- It is correlation, not causation. `mem_context` may be called at turn start for reasons unrelated to compaction.
- The 5d21h run is not in this data. Its rollout is no longer on disk; local session history starts 2026-08-30.
- One machine, one user. This is a field report, not a benchmark.
