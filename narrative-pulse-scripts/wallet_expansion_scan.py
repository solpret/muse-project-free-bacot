#!/usr/bin/env python3
"""Idle wallet-expansion scan (read-only) — 2026-11-01.

Finds repeat early buyers across recent BSC/WBNB pools, classifies
smart wallet / whale (provisional) / cabal, and records funding source
+ cluster main wallet per candidate.

Discipline (same as the rest of the system):
- A failed read is NOT zero: failed pools are listed, never counted.
- A 1000-log page is flagged truncated (possible undercount).
- First pair-out block is a PROXY for pool creation (GeckoTerminal
  gives creation time, not block, and its timestamp can lag actual
  creation by hours — proven by MEG on 2026-11-01); the log window
  is [est-20000, est+1300] and the anchor is the earliest pair-out
  block found in it; early window = anchor + 1200 blocks (~60 min).
- USD sizes use scan-time GeckoTerminal prices (approximation, not
  buy-time value). Whale flag >= $1000 single early buy is a
  PROVISIONAL screening threshold, not a standing rule.
- Deployer check is NOT done here: candidates are candidates until
  a follow-up verifies they are not the token deployer.
"""
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.expanduser("~/workspace/fast_exec"))
import fast_rpc
import indexed_api

TRANSFER_TOPIC = ("0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f"
                  "55a4df523b3ef")
MONITORED = {
    "0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6",
    "0x13d1e9a96eba7906e1ede348c9bb604a03e46d02",
    "0x5b2f11cab406f580a7c6faf620ee35daaf8648a5",
    "0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
    "0x75642756e4ba4cc8fbe76df2239cada046cfc854",
    "0x8272c61cc59cc78d5fa06f3c2c0594def2e8db6a",
    "0x892200223bdfb11d2506c5ab1cae9222ce253acc",
    "0x93e7c78ab0db6f4961bfe7cf254422cbf7b82e1c",
    "0xaab80f45b97d9dc86d9bea56a3e98274ba81026e",
    "0xb787a5603d20e61585e20e7a13a1c0d6c03a1462",
    "0xbe5905cf7a8bebd97fdc5d69a120b0ea720d3cdf",
    "0xda91cefe240175e6fab56271110427a4195ab71f",
    "0xf6a8280c997c4b4daa606e2c8c37b5a79b8ae2cc",
    "0x2325f175975abdbcde555c79cc8e63381d28551b",
}
WHALE_USD = 1000.0
MAX_POOLS = 25
MAX_FUNDING = 15


def pad(addr):
    return "0x" + addr[2:].lower().rjust(64, "0")


def to_int(x):
    try:
        return int(x, 16) if isinstance(x, str) and x.startswith("0x") else int(x)
    except Exception:
        return None


def tier_e():
    txt = open(os.path.expanduser(
        "~/workspace/narrative-pulse/wallet-priority-full.md")).read()
    part = txt.split("## Tier E")[1] if "## Tier E" in txt else ""
    return {a.lower() for a in re.findall(r"0x[a-fA-F0-9]{40}", part)}


def gecko_price(ca):
    try:
        req = urllib.request.Request(
            f"https://api.geckoterminal.com/api/v2/networks/bsc/tokens/{ca}",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.loads(r.read().decode())
        return float(d["data"]["attributes"]["price_usd"])
    except Exception:
        return None


def main():
    now_utc = datetime.now(timezone.utc)
    state = json.load(open(os.path.expanduser(
        "~/workspace/narrative-pulse/fast_discovery_state.json")))
    pools = []
    for ca, v in state.items():
        if not isinstance(v, dict):
            continue
        name = v.get("name") or ""
        if not name.endswith("/ WBNB"):
            continue
        try:
            created = datetime.fromisoformat(
                v["pool_created_at"].replace("Z", "+00:00"))
        except Exception:
            continue
        if now_utc - created > timedelta(hours=24):
            continue
        try:
            vol = float(v.get("volume_h24") or 0)
        except Exception:
            vol = 0.0
        pools.append({"ca": ca, "pool": v.get("pool"), "name": name,
                      "created": created, "vol": vol})
    pools.sort(key=lambda p: -p["created"].timestamp())
    pools = pools[:MAX_POOLS]

    cur = fast_rpc.race("eth_blockNumber", [])
    cur_block = to_int(cur)
    print(f"pools selected: {len(pools)}, current block: {cur_block}")

    tier_e_set = tier_e()
    buyer_pools = {}   # buyer -> {pool_ca: [buy, ...]}
    pool_report = []
    for p in pools:
        pair = p["pool"]
        if not pair:
            pool_report.append({**p, "status": "no_pair"})
            continue
        age_s = (now_utc - p["created"]).total_seconds()
        est = cur_block - int(age_s / 3) if cur_block else None
        if est is None:
            pool_report.append({**p, "status": "no_block"})
            continue
        res = indexed_api.ankr_get_logs(
            p["ca"], est - 20000, est + 1300,
            topics=[TRANSFER_TOPIC, pad(pair)])
        if not isinstance(res, dict) or res.get("status") != "ok":
            pool_report.append({**p, "status": "logs_failed",
                                "detail": (res or {}).get("detail")})
            continue
        logs = res.get("value") or []
        outs = []
        for lg in logs:
            topics = lg.get("topics") or []
            if len(topics) < 3:
                continue
            if (topics[1] or "").lower() != pad(pair):
                continue
            blk = to_int(lg.get("blockNumber"))
            if blk is None:
                continue
            outs.append({"buyer": "0x" + topics[2][-40:].lower(),
                         "block": blk,
                         "amount": to_int(lg.get("data")) or 0})
        if not outs:
            pool_report.append({**p, "status": "no_pair_out_logs"})
            continue
        first_blk = min(o["block"] for o in outs)
        early = [o for o in outs if o["block"] <= first_blk + 1200]
        for o in early:
            buyer_pools.setdefault(o["buyer"], {}).setdefault(
                p["ca"], []).append(o)
        pool_report.append({**p, "status": "ok",
                            "truncated": len(logs) >= 1000,
                            "pair_out": len(outs), "early": len(early),
                            "first_block": first_blk})
        time.sleep(1)

    # Pattern candidates: >= 2 pools, not monitored, not Tier E, not contract
    cands = []
    for buyer, per_pool in buyer_pools.items():
        if len(per_pool) < 2 or buyer in MONITORED or buyer in tier_e_set:
            continue
        cands.append({"buyer": buyer, "pools": per_pool})
    cands.sort(key=lambda c: (-len(c["pools"]),
                              -sum(len(v) for v in c["pools"].values())))
    print(f"pattern buyers (>=2 pools): {len(cands)} "
          f"(before contract check)")

    kept = []
    for c in cands[:40]:
        code = fast_rpc.race("eth_getCode", [c["buyer"], "latest"])
        if code and code != "0x":
            c["excluded"] = "contract"
            continue
        kept.append(c)
    print(f"kept after contract check: {len(kept)}")

    # Decimals + prices for pools involved, then USD sizes
    pool_dec = {}
    pool_price = {}
    for c in kept:
        for ca in c["pools"]:
            if ca not in pool_dec:
                d = fast_rpc.race("eth_call", [
                    {"to": ca,
                     "data": "0x313ce567"}, "latest"])
                pool_dec[ca] = to_int(d) if d else 18
            if ca not in pool_price:
                pool_price[ca] = gecko_price(ca)
    for c in kept:
        max_usd = 0.0
        for ca, buys in c["pools"].items():
            dec = pool_dec.get(ca) or 18
            price = pool_price.get(ca)
            for b in buys:
                usd = (b["amount"] / (10 ** dec)) * price if price else None
                b["usd"] = usd
                if usd and usd > max_usd:
                    max_usd = usd
        c["max_usd"] = max_usd
        c["whale_provisional"] = bool(max_usd and max_usd >= WHALE_USD)
    kept.sort(key=lambda c: (-len(c["pools"]), -(c["max_usd"] or 0)))

    # Funding source for top candidates
    for c in kept[:MAX_FUNDING]:
        res = indexed_api.ankr_get_transactions_by_address(c["buyer"])
        txs = res.get("value") if isinstance(res, dict) else None
        if not txs:
            c["funder"] = None
            c["funder_note"] = f"tx history unavailable: {(res or {}).get('detail')}"
            continue
        incoming = []
        for tx in txs:
            to = (tx.get("to") or "").lower()
            frm = (tx.get("from") or "").lower()
            if to != c["buyer"] or frm == c["buyer"]:
                continue
            # Native BNB funding only: empty input (token transfers
            # have a method call in input and must not count as funding).
            inp = tx.get("input", tx.get("data"))
            if inp not in (None, "", "0x"):
                continue
            try:
                val = int(tx.get("value") or 0)
            except Exception:
                continue
            if val <= 0:
                continue
            blk = to_int(tx.get("blockNumber"))
            incoming.append({"from": frm, "block": blk, "value": val})
        incoming = [t for t in incoming if t["block"] is not None]
        if not incoming:
            c["funder"] = None
            c["funder_note"] = "no incoming native tx in page"
            continue
        incoming.sort(key=lambda t: t["block"])
        f = incoming[0]["from"]
        c["funder"] = f
        c["funder_truncated"] = len(txs) >= 1000
        code = fast_rpc.race("eth_getCode", [f, "latest"])
        if code and code != "0x":
            c["funder_type"] = "contract"
        elif f in tier_e_set:
            c["funder_type"] = "exchange"
        else:
            c["funder_type"] = "eoa"
        time.sleep(1)

    # Cabal grouping: shared EOA non-exchange funder
    groups = {}
    for c in kept:
        f = c.get("funder")
        if f and c.get("funder_type") == "eoa":
            groups.setdefault(f, []).append(c["buyer"])
    cabal_of = {}
    for f, members in groups.items():
        if len(members) >= 2:
            main_w = f if f in [c["buyer"] for c in kept] else sorted(
                members, key=lambda m: -len(
                    next(c["pools"] for c in kept if c["buyer"] == m)))[0]
            for m in members:
                cabal_of[m] = {"funder": f, "members": members,
                               "cluster_main": main_w}
    for c in kept:
        c["cabal"] = cabal_of.get(c["buyer"])

    out = {"scanned_at_wib": (datetime.now(
        timezone(timedelta(hours=7)))).isoformat(timespec="seconds"),
        "pools_selected": len(pools), "pools_ok": sum(
            1 for p in pool_report if p["status"] == "ok"),
        "pools_failed": [p for p in pool_report if p["status"] != "ok"],
        "buyers_total": len(buyer_pools),
        "pattern_candidates": len(kept),
        "candidates": [
            {"buyer": c["buyer"],
             "pool_count": len(c["pools"]),
             "pools": {ca: len(v) for ca, v in c["pools"].items()},
             "max_usd": c["max_usd"],
             "whale_provisional": c["whale_provisional"],
             "funder": c.get("funder"),
             "funder_type": c.get("funder_type"),
             "funder_truncated": c.get("funder_truncated"),
             "funder_note": c.get("funder_note"),
             "cabal": c["cabal"]} for c in kept],
        "cabal_groups": [
            {"funder": f, "members": m,
             "cluster_main": cabal_of[m[0]]["cluster_main"]}
            for f, m in groups.items() if len(m) >= 2],
        "excluded_contract": sum(1 for c in cands[:40]
                                 if c.get("excluded") == "contract"),
        "monitored_count": len(MONITORED),
        "new_threshold_if_all_promoted": None}
    # Threshold math: >25% => floor(0.25*n)+1, floor 4
    import math
    n_new = len(MONITORED) + len(kept)
    out["new_threshold_if_all_promoted"] = max(
        4, math.floor(0.25 * n_new) + 1)
    out["threshold_now"] = max(4, math.floor(0.25 * len(MONITORED)) + 1)

    md = []
    md.append("# Wallet expansion scan — idle (read-only) — "
              f"{out['scanned_at_wib']}\n")
    md.append(f"- Pools scanned: {len(pools)} (ok: {out['pools_ok']}, "
              f"failed: {len(out['pools_failed'])})")
    for p in out["pools_failed"]:
        md.append(f"  - gagal: {p['name']} ({p['ca']}) status={p['status']} "
                  f"detail={(p.get('detail') or '')[:100]}")
    md.append(f"- Total early buyers seen: {len(buyer_pools)}")
    md.append(f"- Pattern candidates (>=2 pools, EOA, bukan terpantau/Tier E): "
              f"{len(kept)}")
    md.append(f"- Cabal groups (shared EOA funder, >=2 members): "
              f"{len(out['cabal_groups'])}")
    md.append(f"- Ambang sinyal sekarang: >25% dari 14 = {out['threshold_now']}; "
              f"bila SEMUA kandidat dipromosikan ({n_new} entitas) "
              f"ambang menjadi {out['new_threshold_if_all_promoted']}.\n")
    md.append("## Kandidat\n")
    for c in out["candidates"]:
        md.append(f"- {c['buyer']} | pools: {c['pool_count']} | "
                  f"max buy ~${c['max_usd']:.0f}" if c["max_usd"] else
                  f"- {c['buyer']} | pools: {c['pool_count']} | max buy ?")
        md[-1] += (f" | whale_prov: {c['whale_provisional']} | "
                   f"funder: {c['funder']} ({c['funder_type']}) | "
                   f"cabal: {json.dumps(c['cabal']) if c['cabal'] else '-'}")
    md.append("\n## Batasan\n")
    md.append("- Blok pair-out pertama = proksi blok pembuatan pool; "
              "jendela awal = +1200 blok (~60 menit).")
    md.append("- USD = harga scan-time GeckoTerminal (aproksimasi, "
              "bukan nilai saat beli). Ambang whale $1000 = screening "
              "sementara, bukan aturan tetap.")
    md.append("- Deployer belum dicek: kandidat BUKAN monitor sampai "
              "verifikasi lanjutan + persetujuan user.")
    md.append("- Riwayat tx halaman penuh (1000) = kemungkinan terpotong; "
              "funder dari halaman itu tidak final.")
    path = os.path.expanduser(
        "~/workspace/narrative-pulse/wallet-expansion-scan-2026-11-01.md")
    open(path, "w").write("\n".join(md) + "\n")
    print(f"report: {path}")
    print(json.dumps({k: out[k] for k in (
        "pools_selected", "pools_ok", "buyers_total",
        "pattern_candidates", "threshold_now",
        "new_threshold_if_all_promoted")}, indent=1))
    print("cabal_groups:", len(out["cabal_groups"]),
          "| whale_prov:", sum(1 for c in out["candidates"]
                                if c["whale_provisional"]))


if __name__ == "__main__":
    main()
