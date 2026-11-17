#!/usr/bin/env python3
"""Run 100 rotation analysis (read-only): for each of the 4 new 27-wallet tokens,
first buy (buyer/tx/block/time/value/pair from raw receipt Transfer log),
buy-size stats from sent tx values of PCS buys to that token, wallet-set
overlap vs the run-98 machine set, and sell counts. No preview/mint/sign."""
import json
from pathlib import Path
from collections import defaultdict

HOME = Path.home()
SR = HOME / "workspace/narrative-pulse/scan-runs"
paid = json.load(open(SR / "run100-paid.json"))
parsed = json.load(open(SR / "run100-receipts.json"))
raw = json.load(open(SR / "run100-receipts-partial.json"))
sent = json.load(open(SR / "run100-sent.json"))
paid99 = json.load(open(SR / "run99-paid.json"))

TOKS = ["0x6f31f7cf4a3fe26f1b849d71c146e4fc08ea7777",
        "0x0d7e74c412c3bb4b32459f0f25efbe49c43e7777"]
# run-99 machine set = wallet set of any run-99 rotation token (50e4)
set98 = set(paid99.get("0x50e4506e76e816ed5e74557b4b8a57037d927777", []))
print(f"run99 machine set size={len(set98)}")

# map tx hash -> sent info (value, block, time, wallet)
sent_tx = {}
for w, r in sent["results"].items():
    if not r.get("ok"):
        continue
    for t in r["in_window"]:
        sent_tx[t["hash"].lower()] = (w, t)

BUY_SEL = "0xb6f9de95"
SELL_SEL = "0x791ac947"

out = {}
for tok in TOKS:
    wallets = set(paid.get(tok, []))
    overlap = len(wallets & set98)
    # buys: parsed entries whose receipt logs contain a Transfer of tok to the wallet
    buys = []
    sells = 0
    sell_wallets = set()
    for h, v in parsed.items():
        r = raw.get(h)
        if not r:
            continue
        logs = r.get("logs") or []
        if not any((lg.get("address") or "").lower() == tok for lg in logs):
            continue
        if v.get("selector") == SELL_SEL:
            sells += 1
            sell_wallets.add(v.get("wallet"))
            continue
        for lg in logs:
            if (lg.get("address") or "").lower() != tok:
                continue
            topics = lg.get("topics") or []
            if len(topics) < 3:
                continue
            to = "0x" + topics[2][-40:]
            if to.lower() not in wallets:
                continue
            # token amount in data
            try:
                amt = int(lg.get("data") or "0x0", 16) / 1e18
            except Exception:
                amt = None
            if v.get("selector") == BUY_SEL:
                w, t = sent_tx.get(h.lower(), (v.get("wallet"), {}))
                val = None
                try:
                    val = int(t.get("value") or "0x0", 16) / 1e18
                except Exception:
                    pass
                buys.append({"wallet": w, "hash": h, "block": t.get("block"),
                             "time": t.get("time_wib"), "value_bnb": val,
                             "tokens": amt,
                             "pair": "0x" + topics[1][-40:] if len(topics) >= 2 else None})
    buys.sort(key=lambda b: (b["block"] or 0))
    vals = sorted(b["value_bnb"] for b in buys if b["value_bnb"] is not None)
    first = buys[0] if buys else None
    follow = vals[1:] if len(vals) > 1 else []
    med = follow[len(follow)//2] if follow else None
    out[tok] = {"wallets": sorted(wallets), "n_wallets": len(wallets),
                "overlap_run98_set": overlap, "n_buys": len(buys), "n_sells": sells,
                "n_sell_wallets": len(sell_wallets), "sell_wallets": sorted(sell_wallets),
                "first_buy": first, "first_value": vals[0] if vals else None,
                "median_followup": med, "max_value": vals[-1] if vals else None,
                "total_bnb": sum(vals) if vals else None}
    print(f"{tok[:8]} wallets={len(wallets)} overlap98={overlap}/27 buys={len(buys)} sells={sells} sell_wallets={len(sell_wallets)} "
          f"first_val={vals[0] if vals else None} med_follow={med} max={vals[-1] if vals else None} "
          f"total={sum(vals) if vals else None:.4f}" if vals else f"{tok[:8]} no buys", flush=True)
    if first:
        print(f"   first: {first['time']} buyer={first['wallet'][:10]} tx={first['hash'][:12]}... "
              f"block={first['block']} pair={first['pair']} tokens={first['tokens']}", flush=True)
json.dump(out, open(SR / "run100-rotation-analysis.json", "w"), indent=1)
print("saved run100-rotation-analysis.json")
