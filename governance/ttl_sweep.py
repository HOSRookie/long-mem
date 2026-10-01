#!/usr/bin/env python3
"""UTC, update-aware cleaner. Preview is default; no implicit backlog deletion.

Usage:
  python3 ttl_sweep.py                  # dry-run preview
  python3 ttl_sweep.py --report out.json
  python3 ttl_sweep.py --apply          # currently refuses; requires per-ID review
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys
sys.dont_write_bytecode = True
from core import registry


def candidates(c):
    return [dict(r) for r in c.execute('''
      SELECT id,project,type,pinned,created_at,updated_at,revision_count
      FROM observations
      WHERE pinned=0 AND deleted_at IS NULL
        AND julianday('now')-max(coalesce(julianday(updated_at),julianday(created_at)),julianday(created_at))
          >= CASE WHEN type IN ('session_summary','passive') THEN 1.0 ELSE 2.0 END
      ORDER BY id
    ''')]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    path = Path(registry()['database'])
    if not path.is_file():
        print(json.dumps({'mode': 'skipped', 'reason': 'database_unavailable_no_fallback'}))
        return
    c = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA query_only=ON')
    rows = candidates(c)
    report = {'mode': 'dry-run', 'utc': datetime.now(timezone.utc).isoformat(),
              'candidate_count': len(rows), 'candidates': rows,
              'deleted': 0, 'apply_ready': False,
              'hold_reason': 'per-ID review and approval required before irreversible cleanup'}
    if args.apply:
        c.close()
        raise SystemExit('cleanup_apply_not_authorized; no data deleted')
    c.close()
    if args.report:
        p = Path(args.report)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix('.tmp')
        tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        tmp.replace(p)
    print(json.dumps({k: v for k, v in report.items() if k != 'candidates'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
