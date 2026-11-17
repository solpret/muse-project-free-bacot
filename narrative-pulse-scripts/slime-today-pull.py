#!/usr/bin/env python3
"""Slime.today Flap-launch pull (read-only, no auth, no browser).

Verified 2026-11-06 ~20:10 WIB: the site's own frontend calls these
same-origin JSON endpoints; plain curl/urllib works, no login/cookies.
- GET https://slime.today/api/launches?chain=56[&cursor=<ts>]  (30/page, cursor paginated)
- GET https://slime.today/api/stats          (totals + indexer lag in blocks)
- GET https://slime.today/api/saltlocks?chain=56&limit=N  (pre-deploy salt locks)
- GET https://slime.today/api/insiders?chain=56&limit=N

The CSV/JSON export buttons on /launches are client-side only (the browser
serialises its in-memory list) - there is NO server CSV endpoint. The JSON
API above is richer than the CSV anyway (tax, floor, vault_official,
vault_risk, graduated_at, launcherStats).

Usage: python3 slime-today-pull.py [--out DIR]
Writes snapshots to DIR (default ~/workspace/narrative-pulse/slime-today/)
and prints a one-line summary + new launches since the previous pull.
Exit 0 on success, 2 on fetch failure (caller: log it, do not retry hard).
"""
import json
import os
import sys
import time
import urllib.request

BASE = "https://slime.today"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}
OUT = os.path.expanduser(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv \
    else os.path.expanduser("~/workspace/narrative-pulse/slime-today")


def get(path, timeout=30):
    req = urllib.request.Request(BASE + path, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    os.makedirs(OUT, exist_ok=True)
    now = int(time.time())
    try:
        stats = get("/api/stats")
        launches, cursor, seen = [], None, set()
        launcher_stats, gate_info = {}, {}
        for _ in range(5):  # ~150 launches max; site total ~96
            q = "/api/launches?chain=56" + (f"&cursor={cursor}" if cursor else "")
            page = get(q)
            if not launcher_stats:
                launcher_stats = page.get("launcherStats", {})
                gate_info = page.get("gate", {})
            batch = page.get("launches", [])
            if not batch:
                break
            for it in batch:
                if it["token"] not in seen:
                    seen.add(it["token"])
                    launches.append(it)
            cursor = page.get("nextCursor")
            if not cursor:
                break
        salt = get("/api/saltlocks?chain=56&limit=100")
    except Exception as e:  # noqa: BLE001 - fetch failure is a plain report
        print(f"FETCH_FAILED {e}")
        return 2

    snap = {"pulled_at": now, "stats": stats.get("56", {}),
            "launches": launches,
            "saltlocks": salt.get("saltLocks", []),
            "launcherStats": launcher_stats, "gate": gate_info}
    path = os.path.join(OUT, f"launches-{now}.json")
    with open(path, "w") as f:
        json.dump(snap, f, ensure_ascii=False)
    with open(os.path.join(OUT, "latest.json"), "w") as f:
        json.dump(snap, f, ensure_ascii=False)

    prev_tokens = set()
    prev_path = os.path.join(OUT, "previous.json")
    if os.path.exists(prev_path):
        try:
            prev_tokens = {x["token"] for x in json.load(open(prev_path))["launches"]}
        except Exception:
            prev_tokens = set()
    new = [x for x in launches if x["token"] not in prev_tokens]
    # rotate latest -> previous for the next run
    import shutil
    shutil.copy(path, prev_path)

    s = stats.get("56", {})
    newest = max((x.get("ts", 0) for x in launches), default=0)
    grad = sum(1 for x in launches if x.get("graduated"))
    print(f"OK launches={len(launches)} new={len(new)} graduated={grad} "
          f"total={s.get('totalLaunches')} grad_total={s.get('graduatedLaunches')} "
          f"last24h={s.get('launchesLast24h')} unused_saltlocks={s.get('unusedSaltLocks')} "
          f"index_lag_blocks={s.get('lag')} newest_ts_age_s={now - newest if newest else -1}")
    for x in sorted(new, key=lambda y: -y.get("ts", 0))[:10]:
        print(f"NEW {x.get('symbol')} {x['token']} mcap=${x.get('mcap_usd')} "
              f"graduated={x.get('graduated')} creator={x.get('creator')}")
    # STAGE A — data-only filters (known MODAL BACOT / BACOT DEGEN gates).
    # Tested 2026-11-06 on 69 graduated non-test launches: 5 passed.
    def _num(x, k):
        try:
            return float(x.get(k) or 0)
        except (TypeError, ValueError):
            return 0

    def stage_a(x):
        if not x.get("graduated") or x.get("isTest"):
            return "not-graduated-or-test"
        mcap, pool = _num(x, "mcap_usd"), _num(x, "pool_value_usd")
        if not (3000 <= mcap <= 1000000):
            return "mcap-out-of-range"
        if pool < 10000:  # POOL_MIN_BNB 14.5 ~ $10K
            return "pool<10K"
        if mcap and pool / mcap < 0.02:  # LIQ_MCAP_MIN 2%
            return "liq/mcap<2%"
        if _num(x, "tax_buy_bps") > 200 or _num(x, "tax_sell_bps") > 200:  # TAX_MAX 2%
            return "tax>2%"
        creator = (x.get("creator") or "").lower()
        ls = launcher_stats.get(creator) or launcher_stats.get(x.get("creator") or "")
        if ls and ls.get("launches", 0) >= 3 and ls.get("graduated", 0) == 0:
            return "creator-0-graduated-in-3+"
        # OG rule: same symbol, earliest launch wins; later same-name = copy
        sym = (x.get("symbol") or "").lower()
        for y in launches:
            if y is x or (y.get("symbol") or "").lower() != sym:
                continue
            if y.get("ts", 0) < x.get("ts", 0):
                return "same-name-copy-not-OG"
        return None

    for x in sorted(new, key=lambda y: -y.get("ts", 0)):
        reason = stage_a(x)
        if reason is None:
            print(f"🟢 PASS {x.get('symbol')} {x['token']} mcap=${x.get('mcap_usd')} "
                  f"pool=${x.get('pool_value_usd')} floor=${x.get('floor_usd')} "
                  f"tax={x.get('tax_buy_bps')}/{x.get('tax_sell_bps')} creator={x.get('creator')}")
        else:
            print(f"🔴 STAGEA-REJECT {x.get('symbol')} {x['token']} reason={reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
