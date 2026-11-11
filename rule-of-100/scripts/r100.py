#!/usr/bin/env python3
"""Rule of 100 tracker. Counts are facts, so a script keeps them, not the model.

  r100.py init   <run_dir> --action "..." --unit actions|minutes [--target 100] [--start YYYY-MM-DD] [--days 100]
  r100.py done   <run_dir> --who "..." [--medium email] [--proof "..."] [--version A] [--date D] [--follow-up]
                           record one action that was really done; refuses a second first contact
  r100.py check  <run_dir> --who "..."      has this person been contacted or blocked?
  r100.py block  <run_dir> --who "..." [--reason "said no"]      never contact this person again
  r100.py log    <run_dir> (--count N | --from-done) [--date D] [--source seen|person] [--add]
                           [--lead N] [--result N] [--note "..."]
  r100.py status <run_dir> [--today D] [--json]
  r100.py finish <run_dir> [--reason "..."]  end a run early
  r100.py list   <runs_root>

A run directory holds:
  run.json     the settings
  log.csv      one row per day: the count, the lead measure, the result
  done.csv     one row per action done (who, medium, proof), written by `done`
  blocked.csv  people never to contact again, written by `block`

A day counts for what was done on that day. A day with no row is a missed day. Extra on one
day never repairs another day. Reporting a past day late is allowed (the work was done then);
logging a future day is not. The script keeps the arithmetic honest. It cannot stop someone
typing a number that isn't true, so `--source` records whether the count was seen or reported.

Dates default to today on this computer's clock. Set R100_TZ (for example America/Chicago)
to count days in a different time zone.
"""
import argparse
import csv
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

LOG_FIELDS = ["date", "count", "lead", "result", "source", "note"]
DONE_FIELDS = ["date", "who", "medium", "proof", "version", "kind"]
BLOCK_FIELDS = ["date", "who", "reason"]


def today_local() -> date:
    tz = os.environ.get("R100_TZ")
    if not tz:
        return datetime.now().date()
    try:
        return datetime.now(ZoneInfo(tz)).date()
    except Exception:
        sys.exit(f"R100_TZ is set to '{tz}', which is not a time zone name. Use one like America/Chicago.")


def parse_day(s: str) -> date:
    try:
        return date.fromisoformat(s)
    except ValueError:
        sys.exit(f"'{s}' is not a date. Use YYYY-MM-DD.")


def norm(who: str) -> str:
    return " ".join(who.lower().split())


def load_run(run_dir: Path) -> dict:
    f = run_dir / "run.json"
    if not f.exists():
        sys.exit(f"No run here: {f} is missing. Start one with: r100.py init {run_dir} ...")
    return json.loads(f.read_text())


def read_csv(path: Path) -> list:
    if not path.exists():
        return []
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, fields: list, rows: list) -> None:
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def load_log(run_dir: Path) -> dict:
    return {r["date"]: r for r in read_csv(run_dir / "log.csv")}


def save_log(run_dir: Path, rows: dict) -> None:
    write_csv(run_dir / "log.csv", LOG_FIELDS, [rows[d] for d in sorted(rows)])


def day_in_run(run: dict, a_date) -> date:
    d = parse_day(a_date) if a_date else today_local()
    start, end = parse_day(run["start"]), parse_day(run["end"])
    if d < start or d > end:
        sys.exit(f"{d} is outside this run ({start} to {end}). Nothing recorded.")
    if d > today_local():
        sys.exit(f"{d} is in the future. Nothing recorded.")
    return d


def cmd_init(a) -> None:
    run_dir = Path(a.run_dir)
    if (run_dir / "run.json").exists():
        sys.exit(f"A run already exists in {run_dir}. Not overwriting it.")
    if a.target < 1 or a.days < 1:
        sys.exit("Target and days must be 1 or more.")
    start = parse_day(a.start) if a.start else today_local()
    run_dir.mkdir(parents=True, exist_ok=True)
    run = {
        "slug": run_dir.name,
        "action": a.action,
        "unit": a.unit,
        "target": a.target,
        "days": a.days,
        "start": start.isoformat(),
        "end": (start + timedelta(days=a.days - 1)).isoformat(),
    }
    (run_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    save_log(run_dir, {})
    write_csv(run_dir / "done.csv", DONE_FIELDS, [])
    write_csv(run_dir / "blocked.csv", BLOCK_FIELDS, [])
    print(json.dumps(run, indent=2))


def cmd_done(a) -> None:
    run_dir = Path(a.run_dir)
    run = load_run(run_dir)
    d = day_in_run(run, a.date)
    who = norm(a.who)
    if any(norm(r["who"]) == who for r in read_csv(run_dir / "blocked.csv")):
        sys.exit(f"'{a.who}' is blocked. Nothing recorded, and they should not be contacted.")
    rows = read_csv(run_dir / "done.csv")
    earlier = [r for r in rows if norm(r["who"]) == who]
    if earlier and not a.follow_up:
        sys.exit(f"'{a.who}' was already contacted on {earlier[0]['date']}. "
                 "Nothing recorded. Use --follow-up if this is a follow-up.")
    if not earlier and a.follow_up:
        sys.exit(f"'{a.who}' has no first contact on record, so this can't be a follow-up.")
    rows.append({"date": d.isoformat(), "who": a.who, "medium": a.medium or "", "proof": a.proof or "",
                 "version": a.version or "", "kind": "follow-up" if a.follow_up else "first"})
    write_csv(run_dir / "done.csv", DONE_FIELDS, rows)
    n = sum(1 for r in rows if r["date"] == d.isoformat())
    print(f"Recorded: {a.who} on {d} ({'follow-up' if a.follow_up else 'first contact'}). {n} rows for that day.")


def cmd_check(a) -> None:
    run_dir = Path(a.run_dir)
    load_run(run_dir)
    who = norm(a.who)
    blocked = [r for r in read_csv(run_dir / "blocked.csv") if norm(r["who"]) == who]
    if blocked:
        print(f"BLOCKED since {blocked[0]['date']}: {blocked[0].get('reason', '')}".rstrip(": "))
        return
    seen = [r for r in read_csv(run_dir / "done.csv") if norm(r["who"]) == who]
    if seen:
        print(f"CONTACTED {len(seen)} time(s), first on {seen[0]['date']}, last on {seen[-1]['date']}.")
    else:
        print("NEW: no contact on record.")


def cmd_block(a) -> None:
    run_dir = Path(a.run_dir)
    load_run(run_dir)
    rows = read_csv(run_dir / "blocked.csv")
    if any(norm(r["who"]) == norm(a.who) for r in rows):
        print(f"'{a.who}' was already blocked.")
        return
    rows.append({"date": today_local().isoformat(), "who": a.who, "reason": a.reason or ""})
    write_csv(run_dir / "blocked.csv", BLOCK_FIELDS, rows)
    print(f"Blocked: {a.who}.")


def cmd_log(a) -> None:
    run_dir = Path(a.run_dir)
    run = load_run(run_dir)
    d = day_in_run(run, a.date)
    key = d.isoformat()
    rows = load_log(run_dir)
    old = rows.get(key, {})
    source = a.source
    if a.from_done:
        counts_follow_ups = run.get("count_follow_ups", False)
        count = sum(1 for r in read_csv(run_dir / "done.csv")
                    if r["date"] == key and (counts_follow_ups or r.get("kind") != "follow-up"))
        source = source or "seen"
    else:
        if a.count < 0:
            sys.exit("Count can't be negative.")
        count = a.count + (int(old.get("count") or 0) if a.add else 0)
        source = source or "person"

    def merged(name, new):
        if new is None:
            return old.get(name, "")
        if new < 0:
            sys.exit(f"{name} can't be negative.")
        return str(new + (int(old.get(name) or 0) if a.add else 0))

    rows[key] = {"date": key, "count": str(count), "lead": merged("lead", a.lead),
                 "result": merged("result", a.result), "source": source,
                 "note": a.note if a.note is not None else old.get("note", "")}
    save_log(run_dir, rows)
    hit = "hit" if count >= run["target"] else f"short by {run['target'] - count}"
    print(f"Logged {key}: {count} {run['unit']} ({hit}), source: {source}.")


def status(run: dict, rows: dict, today: date) -> dict:
    start, end = parse_day(run["start"]), parse_day(run["end"])
    target = run["target"]
    if today < start:
        return {**run, "state": "not started", "day": 0, "starts_in_days": (start - today).days}
    stopped = parse_day(run["finished"]) if run.get("finished") else None
    last = min(today, end, stopped) if stopped else min(today, end)
    running = not stopped and today <= end
    hit = partial = missed = total = lead_total = result_total = 0
    cur = longest = 0
    missed_dates = []
    d = start
    while d <= last:
        r = rows.get(d.isoformat())
        c = int(r["count"]) if r else 0
        total += c
        lead_total += int(r.get("lead") or 0) if r else 0
        result_total += int(r.get("result") or 0) if r else 0
        still_open = running and d == today and c < target  # today isn't over, so it can't be a miss yet
        if c >= target:
            hit += 1
            cur += 1
            longest = max(longest, cur)
        elif not still_open:
            if c > 0:
                partial += 1
            else:
                missed += 1
            missed_dates.append(d.isoformat())
            cur = 0
        d += timedelta(days=1)
    today_row = rows.get(today.isoformat())
    today_count = int(today_row["count"]) if today_row else 0
    day_no = (last - start).days + 1
    return {
        **run,
        "state": "stopped early" if stopped else ("finished" if today > end else "running"),
        "today": today.isoformat(),
        "day": day_no,
        "days_left": max((end - today).days, 0) if running else 0,
        "today_count": today_count if running else None,
        "today_left": max(target - today_count, 0) if running else None,
        "days_hit": hit,
        "days_partial": partial,
        "days_missed": missed,
        "short_or_missed_dates": missed_dates,
        "current_streak": cur,
        "longest_streak": longest,
        "total_done": total,
        "total_possible_so_far": day_no * target,
        "lead_total": lead_total,
        "result_total": result_total,
        "reported_by_person_days": sum(1 for r in rows.values() if r.get("source") == "person"),
    }


def cmd_status(a) -> None:
    run_dir = Path(a.run_dir)
    run = load_run(run_dir)
    s = status(run, load_log(run_dir), parse_day(a.today) if a.today else today_local())
    if a.json:
        print(json.dumps(s, indent=2))
        return
    if s["state"] == "not started":
        print(f"{s['slug']}: starts {s['start']} (in {s['starts_in_days']} days).")
        return
    print(f"{s['slug']}: {s['action']}")
    print(f"Day {s['day']} of {s['days']} ({s['start']} to {s['end']}), {s['state']}, {s['days_left']} days left.")
    if s["today_count"] is not None:
        print(f"Today: {s['today_count']} of {s['target']} {s['unit']}, {s['today_left']} to go.")
    print(f"Days hit: {s['days_hit']}. Short: {s['days_partial']}. Missed: {s['days_missed']}.")
    print(f"Streak: {s['current_streak']} now, {s['longest_streak']} longest.")
    print(f"Total: {s['total_done']} of {s['total_possible_so_far']} possible so far. "
          f"Lead measure: {s['lead_total']}. Results: {s['result_total']}.")
    if s["reported_by_person_days"]:
        print(f"Days reported by the person, not seen: {s['reported_by_person_days']}.")
    if s["short_or_missed_dates"]:
        print("Short or missed: " + ", ".join(s["short_or_missed_dates"]))


def cmd_finish(a) -> None:
    run_dir = Path(a.run_dir)
    run = load_run(run_dir)
    if run.get("finished"):
        sys.exit(f"This run was already stopped on {run['finished']}.")
    run["finished"] = today_local().isoformat()
    run["finish_reason"] = a.reason or ""
    (run_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"Run stopped on {run['finished']}. Its log is kept.")


def cmd_list(a) -> None:
    root = Path(a.runs_root)
    found = sorted(p.parent for p in root.glob("*/run.json")) if root.exists() else []
    if not found:
        print("No runs yet.")
        return
    t = today_local()
    for run_dir in found:
        s = status(load_run(run_dir), load_log(run_dir), t)
        print(f"{run_dir.name}: {s['state']}, day {s['day']} of {s['days']}, {s.get('days_hit', 0)} days hit")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init")
    i.add_argument("run_dir")
    i.add_argument("--action", required=True)
    i.add_argument("--unit", required=True, choices=["actions", "minutes"])
    i.add_argument("--target", type=int, default=100)
    i.add_argument("--days", type=int, default=100)
    i.add_argument("--start")
    i.set_defaults(fn=cmd_init)

    dn = sub.add_parser("done")
    dn.add_argument("run_dir")
    dn.add_argument("--who", required=True)
    dn.add_argument("--medium")
    dn.add_argument("--proof")
    dn.add_argument("--version")
    dn.add_argument("--date")
    dn.add_argument("--follow-up", action="store_true")
    dn.set_defaults(fn=cmd_done)

    c = sub.add_parser("check")
    c.add_argument("run_dir")
    c.add_argument("--who", required=True)
    c.set_defaults(fn=cmd_check)

    b = sub.add_parser("block")
    b.add_argument("run_dir")
    b.add_argument("--who", required=True)
    b.add_argument("--reason")
    b.set_defaults(fn=cmd_block)

    l = sub.add_parser("log")
    l.add_argument("run_dir")
    g = l.add_mutually_exclusive_group(required=True)
    g.add_argument("--count", type=int)
    g.add_argument("--from-done", action="store_true", help="count that day's first-contact rows in done.csv")
    l.add_argument("--lead", type=int)
    l.add_argument("--result", type=int)
    l.add_argument("--date")
    l.add_argument("--source", choices=["seen", "person"])
    l.add_argument("--note")
    l.add_argument("--add", action="store_true", help="add to that day's numbers instead of replacing them")
    l.set_defaults(fn=cmd_log)

    s = sub.add_parser("status")
    s.add_argument("run_dir")
    s.add_argument("--today")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_status)

    f = sub.add_parser("finish")
    f.add_argument("run_dir")
    f.add_argument("--reason")
    f.set_defaults(fn=cmd_finish)

    ls = sub.add_parser("list")
    ls.add_argument("runs_root")
    ls.set_defaults(fn=cmd_list)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
