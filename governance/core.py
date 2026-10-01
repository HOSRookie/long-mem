#!/usr/bin/env python3
"""Canonical memory routing for long_mem.

No remote-name, HOME or launch-directory fallback. Everything a deployment
needs is injected via environment variables; no machine-specific path is
hard-coded here.
"""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
from contextlib import contextmanager

HOME = Path(__file__).resolve().parent


def registry():
    """Load the deployment registry. Resolve via LONG_MEM_REGISTRY first so a
    single checkout can serve several registries."""
    path = os.environ.get('LONG_MEM_REGISTRY', str(HOME / 'registry.json'))
    return json.loads(Path(path).read_text())


def canonical(name, reg=None):
    """Map a project name or alias to its single canonical ID.

    Fails closed: empty, unknown or ambiguous names raise instead of guessing.
    """
    reg = reg or registry()
    if not isinstance(name, str) or not name.strip():
        raise ValueError('explicit_project_required')
    name = name.strip().lower()
    matches = [p for p, v in reg['projects'].items()
               if name in {p, *(a.lower() for a in v.get('aliases', []))}]
    if len(matches) != 1:
        raise ValueError('unregistered_or_ambiguous_project')
    return matches[0]


def common_dir(path):
    try:
        s = subprocess.run(['git', '-C', str(path), 'rev-parse', '--git-common-dir'],
                           capture_output=True, text=True, timeout=2, check=True).stdout.strip()
        return (Path(path) / s).resolve()
    except (OSError, subprocess.SubprocessError):
        return None


def resolve(cwd, reg=None):
    """Resolve a working directory to a registered canonical project.

    A nested independent repository never inherits its parent's identity.
    """
    reg = reg or registry()
    p = Path(cwd).resolve(strict=True)
    if not p.is_dir():
        raise ValueError('workspace_not_directory')
    hits = []
    for project, spec in reg['projects'].items():
        for root in spec.get('roots', []):
            r = Path(root)
            if not r.is_dir():
                continue
            r = r.resolve()
            if p == r or r in p.parents:
                hits.append((len(r.parts), project, r))
    if hits:
        size = max(x[0] for x in hits)
        hits = [x for x in hits if x[0] == size]
        if len({x[1] for x in hits}) != 1:
            raise ValueError('ambiguous_registered_roots')
        local_common = common_dir(p)
        root_common = common_dir(hits[0][2])
        if local_common != root_common:
            raise ValueError('nested_unregistered_repository')
        return hits[0][1]
    common = common_dir(p)
    if common is not None:
        matches = {project for project, spec in reg['projects'].items()
                   for root in spec.get('roots', [])
                   if Path(root).is_dir() and common_dir(root) == common}
        if len(matches) == 1:
            return matches.pop()
    raise ValueError('explicit_project_required_no_workspace_binding')


@contextmanager
def db(reg=None):
    """Open the memory database strictly read-only."""
    reg = reg or registry()
    c = sqlite3.connect(Path(reg['database']).as_uri() + '?mode=ro', uri=True, timeout=3)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA query_only=ON')
    try:
        yield c
    finally:
        c.close()


def index(project, limit=100, max_bytes=18000, reg=None, scope=None):
    """Return a bounded pinned-title index for a project.

    Index only locates; bodies are read by ID elsewhere. No cross-project
    expansion by default.
    """
    reg = reg or registry()
    project = canonical(project, reg)
    if scope not in (None, 'project', 'personal'):
        raise ValueError('invalid_memory_scope')
    condition = 'project=? AND pinned=1 AND deleted_at IS NULL'
    params = [project]
    if scope:
        condition += ' AND scope=?'
        params.append(scope)
    with db(reg) as c:
        total = c.execute('SELECT count(*) FROM observations WHERE ' + condition, params).fetchone()[0]
        rows = c.execute(
            "SELECT id,type,title,scope,topic_key FROM observations WHERE " + condition +
            " ORDER BY CASE WHEN type IN ('constraint','preference','policy') THEN 0 ELSE 1 END,"
            "updated_at DESC,id DESC LIMIT ?", params + [limit]).fetchall()
    out = [f'memory project={project}; pinned_total={total}. Pin means retained, not verified or currently authoritative.']
    emitted = []
    for row in rows:
        title = ' '.join((row['title'] or '(untitled; review required)').split())[:90]
        line = f"- #{row['id']} [{row['type']}/{row['scope']}] {title} | {row['topic_key'] or '(no topic)'}"
        if len(('\n'.join(out + [line])).encode()) > max_bytes - 300:
            break
        out.append(line)
        emitted.append(row['id'])
    out.append(f'indexed={len(emitted)}; omitted={total - len(emitted)}. Read needed bodies by ID; no cross-project expansion by default.')
    return {'project': project, 'pinned_total': total, 'indexed_ids': emitted,
            'omitted': total - len(emitted), 'text': '\n'.join(out)}


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
