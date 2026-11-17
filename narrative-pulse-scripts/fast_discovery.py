#!/usr/bin/env python3
"""Fast BSC new-pair discovery probe (READ-ONLY, no wallet, no signing).

Problem it solves: the narrative-pulse cron opens ~11 live-browser
tabs every 15 minutes and timed out twice on 2026-11-01 (runs 07:59
and 08:14 WIB), so no source could be certified and no signal could
reach the feed. This script answers the "what just launched on BSC"
question in seconds via API, with no browser at all.

Primary source (tested 2026-11-01, 200 in ~1s):
  GeckoTerminal https://api.geckoterminal.com/api/v2/networks/bsc/new_pools?page=N
  Each pool gives: pool address, base-token CA (relationships.base_token),
  name, pool_created_at, FDV, volume h24, price changes m5/m15/h1.
  Page 1 = ~20 pools covering roughly the last 10 minutes, so pages
  1-3 cover ~30 minutes of launches with overlap for a 15-minute cadence.

Secondary (tested, low BSC yield at probe time):
  DexScreener token-profiles + token-boosts latest (200, ~1s) filtered
  to chainId=bsc: 0 BSC tokens on 2026-11-01, because that feed is
  dominated by paid profiles on other chains. Kept as a supplement,
  never as the only source.

NOT used (blocked/unreachable from this VM):
  BlockBeats RSS (403) and newsflash API (blocked), four.meme API
  (unreachable), GMGN trending API (404). Those still need the live
  browser when they are required.

Scope: this script does NOT write narrative state.json
reported_signals, runs, or any other signal field, and does NOT feed
the trading loop. Wiring it into a cron body or feed_loop.py needs
the user's explicit approval.
Exception (added 2026-11-02, user tap "Perbaiki penulisan
state.json"): it writes ONLY one additive heartbeat field,
last_heartbeat_wib, to state.json each run — because state.json had
no script writer at all (run records were appended only at worker
discretion), so its mtime went stale (last write 03:35 WIB
2026-11-02) while the monitor itself kept running, tripping the
trading-continuity watchdog. The heartbeat proves the script legs
ran; it never creates, changes, or duplicates a signal.
It only snapshots first_seen times to fast_discovery_state.json,
so a later run can distinguish a first sighting from a second one.
A token appearing here is NOT a candidate, NOT a signal, and NOT a
buy recommendation: it still needs the full gate + money-flow +
entry-confirmation pipeline before any trade.
"""
import json, os, sys, time, urllib.request
from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))

STATE = os.path.expanduser("~/workspace/narrative-pulse/fast_discovery_state.json")
NARRATIVE_STATE = os.path.expanduser("~/workspace/narrative-pulse/state.json")


def update_narrative_heartbeat(now_str):
    """Refresh ONLY last_heartbeat_wib in narrative state.json.

    Read-modify-write with atomic replace. If the file cannot be
    loaded, or is not a JSON object, it is left untouched — it must
    NEVER be overwritten from an empty default, which would destroy
    reported_signals and the runs history. No other field is touched.
    """
    try:
        with open(NARRATIVE_STATE) as f:
            st = json.load(f)
    except Exception as e:
        print(f"WARN narrative state.json not readable, heartbeat skipped: {e}")
        return
    if not isinstance(st, dict):
        print("WARN narrative state.json is not an object, heartbeat skipped")
        return
    st["last_heartbeat_wib"] = now_str
    tmp = NARRATIVE_STATE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f, indent=1)
    os.replace(tmp, NARRATIVE_STATE)
    print(f"narrative state.json heartbeat: {now_str}")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

def get_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def main():
    t0 = time.time()
    found = {}
    for page in (1, 2, 3):
        try:
            d = get_json(f"https://api.geckoterminal.com/api/v2/networks/bsc/new_pools?page={page}")
        except Exception as e:
            print(f"FAIL geckoterminal page {page}: {e}")
            continue
        for p in d.get("data", []):
            a = p.get("attributes", {})
            base = (p.get("relationships", {}).get("base_token", {})
                    .get("data", {}).get("id", ""))
            ca = base[4:] if base.startswith("bsc_") else base
            if not ca:
                continue
            found[ca] = {
                "name": a.get("name"), "pool": a.get("address"),
                "pool_created_at": a.get("pool_created_at"),
                "fdv_usd": a.get("fdv_usd"),
                "volume_h24": (a.get("volume_usd") or {}).get("h24"),
                "change_h1": (a.get("price_change_percentage") or {}).get("h1"),
            }
    try:
        prev = json.load(open(STATE))
    except Exception:
        prev = {}
    # FIX 2026-11-01 (same bug as backtest_recorder): time.localtime()
    # is UTC in cron workers, so the old line stamped UTC wall time
    # mislabelled as WIB. Explicit WIB timezone, independent of env.
    now = datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00")
    new, seen = [], []
    for ca, info in found.items():
        if ca in prev:
            seen.append(ca)
        else:
            new.append(ca)
            prev[ca] = {"first_seen": now, **info}
    json.dump(prev, open(STATE, "w"), indent=1)
    update_narrative_heartbeat(now)
    print(f"GeckoTerminal BSC new pools (3 pages): {len(found)} token, "
          f"{len(new)} baru, {len(seen)} sudah pernah terlihat, "
          f"{time.time()-t0:.1f} detik")
    for ca in new:
        i = found[ca]
        print(f"  BARU {ca} {i['name']} created={i['pool_created_at']} fdv={i['fdv_usd']}")
    if seen:
        print(f"  contoh sudah terlihat: {seen[:5]}")

if __name__ == "__main__":
    main()
