#!/usr/bin/env python3
"""Hot-leg 16:14 retry (single bounded retry after egress IncompleteRead on
legs 1/2/4). curl-based; updates run-hot-leg-2026-11-15-1614.json in place."""
import json, re, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SEEN_P = BASE + "hot-leg-seen.json"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
t0 = time.time()
out = json.load(open(BASE + "run-hot-leg-2026-11-15-1614.json"))
retry = {}

def curl(url, timeout=25):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "Mozilla/5.0", url],
                       capture_output=True, text=True, timeout=timeout + 10)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"curl rc={r.returncode} err={r.stderr[:80]}")
    return r.stdout

def addrs(text):
    return set(a for a in re.findall(r"0x[a-fA-F0-9]{40}", text))

# Leg 1 retry: Sourcify feed
feed_addrs = []
try:
    feed = json.loads(curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
    items = feed if isinstance(feed, list) else feed.get("results", [])
    feed_addrs = [it.get("address") for it in items if it.get("address")]
    retry["sourcify"] = {"ok": True, "count": len(feed_addrs),
                         "verifiedAt": [it.get("verifiedAt") for it in items[:3]]}
except Exception as e:
    retry["sourcify"] = {"ok": False, "error": str(e)[:120]}

# Leg 2 retry: Boltbook EN + ZH
bb_addrs = set()
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html = curl(url)
        a = addrs(html)
        bb_addrs |= a
        retry[f"boltbook-{lang}"] = {"ok": True, "bytes": len(html), "addrs": len(a)}
    except Exception as e:
        retry[f"boltbook-{lang}"] = {"ok": False, "error": str(e)[:120]}

seen = json.load(open(SEEN_P))
seen_keys = {k.lower() for k in seen}
new = [a for a in (feed_addrs + sorted(bb_addrs))
       if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
new = list(dict.fromkeys(new))
retry["new_contracts"] = new
FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "freeremaining"}
shape = []
for addr in new:
    info = {"address": addr}
    try:
        data = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata", 25))
        abi = data.get("abi") or []
        fns = [f.get("name", "").lower() for f in abi if f.get("type") == "function"]
        has_mint = any("mint" in f or "claim" in f for f in fns)
        has_quote = any("quote" in f or "cost" in f or "price" in f for f in fns)
        free = [f for f in fns if f in FREE_VIEWS]
        meta = json.dumps(data.get("metadata") or data)
        agent = REG in meta.lower() or "agentgate" in meta.lower() or any("agent" in f for f in fns)
        s1 = has_mint and has_quote and bool(free) and agent
        s2 = ("mintfree" in fns or "claimfree" in fns) and bool(free) and agent
        info.update({"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
                     "free": free, "agent": agent, "n_fns": len(fns),
                     "status": "sale-shape" if (s1 or s2) else "checked-not-sale-shape"})
    except Exception as e:
        info.update({"status": "shape-check-failed", "error": str(e)[:120]})
    seen[addr] = {"first_seen_wib": "2026-11-15T16:14:00+07:00",
                  "source": "hot-leg-1614-retry", "status": info["status"],
                  "note": json.dumps(info)[:500]}
    shape.append(info)
retry["shape"] = shape
if new:
    json.dump(seen, open(SEEN_P, "w"), indent=1)
retry["seen_total_after"] = len(seen)

# Leg 4 retry: focused re-read via curl batch
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))
        else:
            d += enc_u(int(a))
    return d
src = open(BASE + "run-2026-11-15-1601-reread.py").read()
i = src.index("ITEMS = {")
j = i; depth = 0
while True:
    c = src[j]
    if c == "{": depth += 1
    elif c == "}":
        depth -= 1
        if depth == 0:
            j += 1; break
    j += 1
ns = {"U": [USER], "USER": USER}
exec(src[i:j], ns)
ITEMS = ns["ITEMS"]
FOCUS = ["AGCLUB", "Ledgera", "RAVE", "REOPIR", "Matrix Agents", "ORBIT",
         "BinanceAI-mint", "RigForge", "RaceAgents", "Pengu", "Zephyra"]
base = json.load(open(BASE + "run-2026-11-15-1601-reread.json"))
calls, meta = [], []
for name in FOCUS:
    addr, views = ITEMS[name]
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append((name, key))
leg4 = {"ok": False, "reads": {}}
for ep in ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]:
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "60", "-X", "POST", ep,
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps(calls)],
                           capture_output=True, text=True, timeout=70).stdout
        res = json.loads(r)
        if isinstance(res, list) and len(res) == len(calls):
            ok_any = any(isinstance(it, dict) and it.get("result") not in (None, "0x") for it in res)
            for (name, key), it in zip(meta, res):
                v = to_int(it.get("result")) if isinstance(it, dict) and "result" in it else None
                leg4["reads"].setdefault(name, {})[key] = v
            leg4["ok"] = ok_any
            leg4["ep"] = ep
            if ok_any:
                break
    except Exception as e:
        leg4["error"] = str(e)[:120]
try:
    r = subprocess.run(["curl", "-sL", "--max-time", "20", "-X", "POST",
                        "https://bsc-dataseed.binance.org/",
                        "-H", "Content-Type: application/json",
                        "-d", '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}'],
                       capture_output=True, text=True, timeout=30).stdout
    leg4["block"] = int(json.loads(r)["result"], 16)
except Exception:
    leg4["block"] = None
diffs = {}
for name, views in leg4["reads"].items():
    old = base["reads"].get(name, {}).get("views", {})
    for k, v in views.items():
        if old.get(k) != v:
            diffs.setdefault(name, {})[k] = {"1601": old.get(k), "now": v}
leg4["diffs_vs_1601"] = diffs
leg4["base_block"] = base.get("block")
retry["leg4"] = leg4
retry["elapsed_s"] = round(time.time() - t0, 1)
out["retry"] = retry
out["elapsed_s"] = round(out.get("elapsed_s", 0) + retry["elapsed_s"], 1)
json.dump(out, open(BASE + "run-hot-leg-2026-11-15-1614.json", "w"), indent=1)
print(json.dumps(retry, indent=1)[:4500])
