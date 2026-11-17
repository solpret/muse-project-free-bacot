#!/usr/bin/env python3
"""Trending backtest recorder — READ-ONLY, no wallet, no signing, no trading.

Purpose: measure, with real data, how early a pre-trending signal could
have fired BEFORE a token appeared on a trending list. It does NOT feed
the live trading loop, does NOT change any gate, score, or cron, and
its output is never a buy recommendation.

Per tick (intended cadence: 5 minutes) it snapshots:
  A. Binance Wallet trending (exact benchmark the user sees in-app):
     - token-rank rankType=10 (Trending), chain 56, period 1h and 24h,
       via the installed binance-web3 crypto-market-rank CLI (keyless,
       verified working from this VM 2026-11-01).
     - smart-money-inflow, chain 56, period 1h (net inflow rank).
     - social-hype, chain 56, timeRange 1 (24h social buzz
       leaderboard; added 2026-11-01 as step 2 of the signal-path
       improvement order). NARRATIVE ONLY: it is a buzz
       leaderboard (majors dominate the top), not money-flow
       confirmation and not a feed trigger. Its value for the
       later analysis is as a narrative first_seen timestamp to
       cross-match against new_pools.
  B. GeckoTerminal BSC (independent cross-check):
     - new_pools pages 1-3 (the pool-birth firehose).
     - trending_pools duration 1h and 24h.
  C. OKX DEX trending: NOT recorded per tick in v1 — its page is a
     Next.js RSC payload whose ranking order is not stably parseable
     from curl, and Binance's own page returns empty via curl. Adding
     either by browser would break the 5-minute cadence, so they are
     deferred, not faked.

Outputs (~/workspace/narrative-pulse/trending-backtest/):
  - ticks.jsonl: one JSON object per tick (append-only). Each tick
    carries, per source, the ordered CA list plus the key metrics
    needed for lead-time math (volume, tx count, price change,
    holders/liquidity where the source provides them).
  - first_seen.json: CA -> first tick it was seen in each source
    (new_pools, binance_trending_1h, binance_trending_24h,
    gecko_trending_1h, gecko_trending_24h, binance_smart_money,
    binance_social_hype_24h).
    This is what the later lead-time analysis reads: for a CA whose
    trending first_seen is T, the lead time of any candidate rule is
    T minus the first tick that rule would have fired on that CA.
  - latest.json: last tick summary (counts + errors per source).

Lead-time analysis (NOT done by this recorder; done later, read-only,
over ticks.jsonl + first_seen.json):
  For each CA that (a) appeared in new_pools and (b) later appeared
  in a trending list: lead = trending_first_seen - new_pool_first_seen.
  For a candidate velocity rule (e.g. holder growth, volume-m5
  acceleration, buy ratio): rule_first_fire = first tick the CA's
  recorded metrics satisfy the rule; rule_lead = trending_first_seen
  - rule_first_fire; false-positive rate = share of rule fires whose
  CA never reached any trending list within 48h. A rule is only
  adopted if its median rule_lead is positive AND its false-positive
  rate is measured, never guessed. Trending lists contain old tokens
  too, so (a) is required — a token already old when it trends is
  not a pre-trending catch.
"""
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
import sys
import time
import urllib.request

BASE = os.path.expanduser("~/workspace/narrative-pulse/trending-backtest")
CLI = os.path.expanduser("~/workspace/custom-skills/crypto-market-rank/scripts/cli.mjs")
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
os.makedirs(BASE, exist_ok=True)


WIB = timezone(timedelta(hours=7))


def now_iso():
    # FIX 2026-11-01: the old version used time.localtime() and then
    # hardcoded a +07:00 suffix. Cron worker processes run with TZ=UTC,
    # so every cron tick was stamped with its UTC wall time mislabelled
    # as WIB (7 hours early). Using an explicit WIB timezone makes the
    # stamp independent of the process environment (shell TZ, cron TZ,
    # or none). Historical cron ticks (2026-11-01, labelled before the
    # recorder existed at 09:30 WIB) were migrated +7h with a backup
    # kept at trending-backtest/backup-pre-tzfix-20261101/.
    return datetime.now(WIB).strftime("%Y-%m-%dT%H:%M:%S+07:00")


def get_json(url, timeout=20):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def run_cli(args, timeout=30):
    out = subprocess.run(
        ["node", CLI] + args, capture_output=True, text=True, timeout=timeout
    )
    if out.returncode != 0:
        raise IOError(f"cli exit {out.returncode}: {out.stderr[:300]}")
    d = json.loads(out.stdout)
    if d.get("code") not in ("000000", "00000", 0, None) and d.get("code") is not None:
        raise IOError(f"cli code {d.get('code')}: {str(d)[:300]}")
    return d.get("data", d)


def _f(v):
    try:
        return float(v) if v is not None else None
    except (TypeError, ValueError):
        return None


def binance_trending(period):
    data = run_cli(
        ["token-rank",
         json.dumps({"rankType": 10, "chainId": "56", "period": period,
                      "page": 1, "size": 50})]
    )
    toks = data.get("tokens", []) if isinstance(data, dict) else []
    rows = []
    for i, t in enumerate(toks):
        ca = t.get("contractAddress")
        if not ca:
            continue
        rows.append({
            "rank": i + 1, "ca": ca, "symbol": t.get("symbol"),
            "price": t.get("price"),
            "chg_1h": _f(t.get("percentChange1h")),
            "chg_24h": _f(t.get("percentChange24h")),
            "vol_1h": _f(t.get("volume1h")),
            "vol_24h": _f(t.get("volume24h")),
            "vol_1h_buy": _f(t.get("volume1hBuy")),
            "vol_1h_sell": _f(t.get("volume1hSell")),
            "tx_1h": t.get("count1h"),
            "holders": t.get("holders"),
            "liquidity": t.get("liquidity"),
            "market_cap": t.get("marketCap"),
        })
    return rows


def binance_smart_money():
    data = run_cli(["smart-money-inflow",
                    json.dumps({"chainId": "56", "period": "1h"})])
    items = data if isinstance(data, list) else data.get("data", [])
    rows = []
    for i, t in enumerate(items):
        ca = t.get("ca") or t.get("contractAddress")
        if not ca:
            continue
        rows.append({
            "rank": i + 1, "ca": ca, "symbol": t.get("tokenName"),
            "price": t.get("price"), "market_cap": t.get("marketCap"),
            "volume": _f(t.get("volume")),
            "chg": _f(t.get("priceChangeRate")),
        })
    return rows


def binance_social_hype():
    data = run_cli(["social-hype",
                    json.dumps({"chainId": "56",
                                "targetLanguage": "en",
                                "timeRange": 1})])
    items = []
    if isinstance(data, dict):
        items = data.get("leaderBoardList", []) or []
    rows = []
    for i, t in enumerate(items):
        meta = t.get("metaInfo") or {}
        market = t.get("marketInfo") or {}
        social = t.get("socialHypeInfo") or {}
        ca = meta.get("contractAddress")
        if not ca:
            continue
        rows.append({
            "rank": i + 1, "ca": ca, "symbol": meta.get("symbol"),
            "token_age_ms": meta.get("tokenAge"),
            "market_cap": _f(market.get("marketCap")),
            "chg_24h": _f(market.get("priceChange")),
            "social_hype": _f(social.get("socialHype")),
            "sentiment": social.get("sentiment"),
        })
    return rows


def gecko_new_pools():
    rows = []
    for page in (1, 2, 3):
        d = get_json(
            f"https://api.geckoterminal.com/api/v2/networks/bsc/new_pools?page={page}")
        for p in d.get("data", []):
            a = p.get("attributes", {})
            base = (p.get("relationships", {}).get("base_token", {})
                    .get("data", {}).get("id", ""))
            ca = base[4:] if base.startswith("bsc_") else base
            if not ca:
                continue
            rows.append({
                "ca": ca, "name": a.get("name"), "pool": a.get("address"),
                "pool_created_at": a.get("pool_created_at"),
                "fdv_usd": _f(a.get("fdv_usd")),
                "volume_h24": _f((a.get("volume_usd") or {}).get("h24")),
                "change_h1": _f((a.get("price_change_percentage") or {}).get("h1")),
                "change_m5": _f((a.get("price_change_percentage") or {}).get("m5")),
                "txns_h24": (a.get("txns") or {}).get("h24"),
            })
    return rows


def gecko_trending(duration):
    d = get_json(
        f"https://api.geckoterminal.com/api/v2/networks/bsc/trending_pools?duration={duration}")
    rows = []
    for i, p in enumerate(d.get("data", [])):
        a = p.get("attributes", {})
        base = (p.get("relationships", {}).get("base_token", {})
                .get("data", {}).get("id", ""))
        ca = base[4:] if base.startswith("bsc_") else base
        if not ca:
            continue
        rows.append({
            "rank": i + 1, "ca": ca, "name": a.get("name"),
            "pool": a.get("address"),
            "pool_created_at": a.get("pool_created_at"),
            "fdv_usd": _f(a.get("fdv_usd")),
            "volume_h24": _f((a.get("volume_usd") or {}).get("h24")),
            "change_h1": _f((a.get("price_change_percentage") or {}).get("h1")),
            "txns_h24": (a.get("txns") or {}).get("h24"),
        })
    return rows


def main():
    t0 = time.time()
    tick = {"ts": now_iso(), "sources": {}, "errors": {}}
    jobs = [
        ("binance_trending_1h", lambda: binance_trending(30)),
        ("binance_trending_24h", lambda: binance_trending(50)),
        ("binance_smart_money_1h", binance_smart_money),
        ("binance_social_hype_24h", binance_social_hype),
        ("gecko_new_pools", gecko_new_pools),
        ("gecko_trending_1h", lambda: gecko_trending("1h")),
        ("gecko_trending_24h", lambda: gecko_trending("24h")),
    ]
    for name, fn in jobs:
        try:
            tick["sources"][name] = fn()
        except Exception as e:
            tick["sources"][name] = []
            tick["errors"][name] = f"{type(e).__name__}: {e}"[:300]
    tick["elapsed_s"] = round(time.time() - t0, 1)

    # Append tick (append-only log).
    with open(os.path.join(BASE, "ticks.jsonl"), "a") as f:
        f.write(json.dumps(tick) + "\n")

    # Update first_seen per source.
    fs_path = os.path.join(BASE, "first_seen.json")
    try:
        fs = json.load(open(fs_path))
    except Exception:
        fs = {}
    for name, rows in tick["sources"].items():
        bucket = fs.setdefault(name, {})
        for r in rows:
            ca = r.get("ca")
            if ca and ca not in bucket:
                bucket[ca] = tick["ts"]
    json.dump(fs, open(fs_path, "w"), indent=1)

    summary = {
        "last_tick": tick["ts"],
        "elapsed_s": tick["elapsed_s"],
        "counts": {k: len(v) for k, v in tick["sources"].items()},
        "errors": tick["errors"],
        "first_seen_counts": {k: len(v) for k, v in fs.items()},
    }
    json.dump(summary, open(os.path.join(BASE, "latest.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
