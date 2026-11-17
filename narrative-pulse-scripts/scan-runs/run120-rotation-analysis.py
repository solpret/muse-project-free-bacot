#!/usr/bin/env python3
"""Run 114 rotation analysis (read-only): generic version.
- Finds tokens with >=12 wallets in run120-paid.json (signal threshold).
- For each such NEW token (not in run103-paid at >=12), first buy / size stats /
  sell counts / overlap vs run-103 machine set (wallets of 4263).
- Continuation checks for stalled rotations: sells/buys this run.
No preview/mint/sign."""
import json
from pathlib import Path

HOME = Path.home()
SR = HOME / "workspace/narrative-pulse/scan-runs"
paid = json.load(open(SR / "run120-paid.json"))
parsed = json.load(open(SR / "run120-receipts.json"))
raw = json.load(open(SR / "run120-receipts-partial.json"))
sent = json.load(open(SR / "run120-sent.json"))
paid_prev = json.load(open(SR / "run119-paid.json"))

# run-103 machine set = wallet set of run-102 rotation token 4263, from its DEBUT run
# (run102-paid.json) - the previous run's paid file is quiet for it (fix of the run-105 quirk)
set102 = set(json.load(open(SR / "run102-paid.json")).get("0x42637d6471cd50286a0801060d88e05007197777", []))
print(f"run103 machine set size={len(set102)}")

sent_tx = {}
for w, r in sent["results"].items():
    if not r.get("ok"):
        continue
    for t in r["in_window"]:
        sent_tx[t["hash"].lower()] = (w, t)

BUY_SEL = "0xb6f9de95"
SELL_SEL = "0x791ac947"

def analyze(tok):
    wallets = set(paid.get(tok, []))
    overlap = len(wallets & set102)
    buys, sells, sell_wallets = [], 0, set()
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
    return {"wallets": sorted(wallets), "n_wallets": len(wallets),
            "overlap_run103_set": overlap, "n_buys": len(buys), "n_sells": sells,
            "n_sell_wallets": len(sell_wallets), "sell_wallets": sorted(sell_wallets),
            "first_buy": first, "first_value": vals[0] if vals else None,
            "median_followup": med, "max_value": vals[-1] if vals else None,
            "total_bnb": sum(vals) if vals else None}

big = {k: v for k, v in paid.items() if len(v) >= 12}
print(f"tokens >=12 wallets this run: {len(big)}")
for k, v in sorted(big.items(), key=lambda kv: -len(kv[1])):
    print(f"  {k} wallets={len(v)} prev_run_wallets={len(paid_prev.get(k, []))}")

out = {}
for tok in big:
    res = analyze(tok)
    out[tok] = res
    if res['total_bnb'] is not None:
        print(f"{tok[:8]} wallets={res['n_wallets']} overlap102={res['overlap_run103_set']}/27 buys={res['n_buys']} sells={res['n_sells']} sell_wallets={res['n_sell_wallets']} "
              f"first_val={res['first_value']} med_follow={res['median_followup']} max={res['max_value']} total={res['total_bnb']:.4f}", flush=True)
    else:
        print(f"{tok[:8]} no buys", flush=True)
    if res["first_buy"]:
        f = res["first_buy"]
        print(f"   first: {f['time']} buyer={f['wallet'][:10]} tx={f['hash'][:12]}... block={f['block']} pair={f['pair']} tokens={f['tokens']}", flush=True)
json.dump(out, open(SR / "run120-rotation-analysis.json", "w"), indent=1)
print("saved run120-rotation-analysis.json")

# Stalled-rotation continuation: buys/sells this run per known rotation token
STALLED = {
    "1e9c Seatbelt": "0x1e9c6d463a096320df3ad60754344b2735a37777",
    "4727 Laura": "0x4727e091d34665249bfbdc1575c7180d19527777",
    "1153": "0x1153607e323c42f93c82b80e1772f9cc626b7777",
    "79cd": "0x79cd174ca3ec25c06ff5fddae365643f73d77777",
    "cfdb": "0xcfdb66667d0ced8bff240e17547c7bef1ca97777",
    "0cf8": "0x0cf896204bf1bd8a9b2a5bf07879ead17b7f7777",
    "e68b": "0xe68bdc90fee5a233bb054a3c89854a5b50d27777",
    "31e4": "0x31e43b72f14fea00a576e84c4e3605d98a317777",
    "43c8": "0x43c8f55b12391671d1f00b04ba1ef6d1842e7777",
    "3d12": "0x3d1201ea0d559e7071bc42d24e1494c6d7547777",
    "eae0": "0xeae0936e2f9ecb0a1acac8c5b9e43f86d3d37777",
    "889a": "0x889a76e4d48169d0398828a36c57b64298577777",
    "4249": "0x42491efdffe0aea61799d12b79cfe6ad2a977777",
    "2bfb": "0x2bfb481d4812f329b6244450137096157a6b7777",
    "c459": "0xc4599c77985efd0353b688b6127ad4f3399e7777",
    "2717": "0x2717a156b86c3c8894bb2dea9a34c514e8fc7777",
    "6a25": "0x6a2590934e55671a6fab9fa8edca8da4960e7777",
    "9f7e": "0x9f7ea7a4eaa7f39782caeb1ecab8176187e97777",
    "8c64": "0x8c64aa82e861393bf760ee6d0eb29c0c60f07777",
    "c1ab": "0xc1ab1e832da23f85a27aa2778f555d00319e7777",
    "7809 PEPE69": "0x780967274cca69ee9e64cf6546488830c03f7777",
    "7f0a BTC": "0x7f0a67b94ee0faf41d0ee352a44f0fc94e8e7777",
    "f3bd PROPFUN": "0xf3bdc9ef1343fa3ef7c555414e9cc2a5e5537777",
    "0x8b run102": "0x8b19cdca84f9e57cbb2946f1c8d27be25ef87777",
    "0xd8 run102": "0xd826883c65bd3b760ee1b0720c8c31cc2b177777",
    "0x07 run102": "0x07b225cecc3733f71fd613dbf80a275dfd5a7777",
    "0x42 run102": "0x42637d6471cd50286a0801060d88e05007197777",
}
for label, tok in STALLED.items():
    w = set(paid.get(tok, []))
    ns, sw, nb = 0, set(), 0
    for h, v in parsed.items():
        r = raw.get(h)
        if not r:
            continue
        logs = r.get("logs") or []
        if not any((lg.get("address") or "").lower() == tok for lg in logs):
            continue
        if v.get("selector") == SELL_SEL:
            ns += 1; sw.add(v.get("wallet"))
        elif v.get("selector") == BUY_SEL:
            nb += 1
    if w or ns or nb:
        print(f"STALLED {label} {tok[:10]} paid_wallets={len(w)} buys={nb} sells={ns} sell_wallets={len(sw)}")
    else:
        print(f"STALLED {label} {tok[:10]} 0 wallets (quiet)")
