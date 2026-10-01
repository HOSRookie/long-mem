#!/usr/bin/env python3
"""Read-only lifecycle hooks. Never capture prompts, auto-import, start servers or save.

Modes:
  start   -> inject policy + the current project's pinned-title index.
  compact -> inject policy + the "continue directly" rule after compaction.
"""
import json
import sys
sys.dont_write_bytecode = True
from core import HOME, index, registry, resolve

POLICY_PATH = HOME / 'POLICY.md'


def render(payload, mode):
    policy = POLICY_PATH.read_text()
    if mode == 'compact':
        return (policy + '\nAfter compaction, continue directly; do not force a summary, '
                'do not re-run a full recall. Read by ID only if the thread actually broke.')
    try:
        project = resolve(payload.get('cwd', ''))
        view = index(project)
        context = policy + '\n\n' + view['text']
        for shared in registry().get('shared_projects', []):
            if shared != project:
                context += '\n\nShared constraints index:\n' + index(shared, limit=30, max_bytes=3000)['text']
        return context
    except (ValueError, OSError):
        return (policy + '\nCurrent cwd is not bound to a registered project. '
                'Do not fall back to another project; pass an explicit verified project before writing.')


if __name__ == '__main__':
    try:
        payload = json.load(sys.stdin)
        mode = sys.argv[1] if len(sys.argv) > 1 else 'start'
        print(render(payload, mode))
    except Exception:
        print('Memory context unavailable; do not guess a project or write automatically.')
