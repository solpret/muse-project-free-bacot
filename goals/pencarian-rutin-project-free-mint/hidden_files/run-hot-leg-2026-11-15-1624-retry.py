#!/usr/bin/env python3
"""Hot-leg 16:24 retry: Boltbook via curl + leg-4 re-read in small chunks."""
import json, re, subprocess, time

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SEEN_P = BASE + "hot-leg-seen.json"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
t0 = time.time()
out = {"run": "hot-leg 2026-11-15 16:24 WIB retry", "boltbook": {}, "leg4": {}}

def curl(url, timeout=25, post=None):
    cmd = ["curl", "-sL", "--max-time", str(timeout), "-A", "Mozilla/5.0", url]
    if post is not None:
        cmd = ["curl", "-sL", "--max-time", str(timeout), "-X", "POST", url,
               "-H", "Content-Type: application/json", "-d", post]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
    return r.stdout

# Boltbook via curl
bb_addrs = set()
for lang, url in (("en", "https://boltbook.fun/?lang=en"),
                  ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html = curl(url)
        a = set(re.findall(r"0x[a-fA-F0-9]{40}", html))
        bb_addrs |= a
        out["boltbook"][lang] = {"ok": bool(html) and len(html) > 1000,
                                 "bytes": len(html), "addrs": len(a)}
    except Exception as e:
        out["boltbook"][lang] = {"ok": False, "error": str(e)[:120]}

seen = json.load(open(SEEN_P))
seen_keys = {k.lower() for k in seen}
new_bb = [a for a in sorted(bb_addrs)
          if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
out["boltbook"]["new_not_in_seen"] = new_bb
# shape-check any new Boltbook contracts (same logic as main script)
FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft",
              "freeused", "freeavailable", "freesharepoolexhausted",
              "freesharesclaimed", "freeminted", "freeremaining"}
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
out["boltbook"]["shape"] = []
for addr in new_bb:
    info = {"address": addr}
    try:
        import urllib.request
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8", "replace"))
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
    seen[addr] = {"first_seen_wib": "2026-11-15T16:24:38+07:00",
                  "source": "hot-leg-1624-boltbook-retry", "status": info["status"],
                  "note": json.dumps(info)[:500]}
    out["boltbook"]["shape"].append(info)
if new_bb:
    json.dump(seen, open(SEEN_P, "w"), indent=1)

# Leg 4: small chunks, endpoints in order, log raw failure head
from Crypto.Hash import keccak
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

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
leg4 = {"ok": False, "reads": {}, "attempts": []}
CH = 20
for ep in EPS:
    ok_all = True
    tmp = {}
    raw_head = ""
    for ci in range(0, len(calls), CH):
        chunk = calls[ci:ci + CH]
        try:
            r = curl(ep, timeout=30, post=json.dumps(chunk))
            res = json.loads(r)
            if not (isinstance(res, list) and len(res) == len(chunk)):
                ok_all = False
                raw_head = (r[:200] if isinstance(r, str) else str(r)[:200])
                break
            for (name, key), it in zip(meta[ci:ci + CH], res):
                v = to_int(it.get("result")) if isinstance(it, dict) and "result" in it else None
                tmp.setdefault(name, {})[key] = v
        except Exception as e:
            ok_all = False
            raw_head = str(e)[:200]
            break
    leg4["attempts"].append({"ep": ep, "ok": ok_all, "raw_head": raw_head})
    if ok_all and any(v is not None for views in tmp.values() for v in views.values()):
        leg4["ok"] = True
        leg4["reads"] = tmp
        leg4["ep"] = ep
        break
    elif ok_all:
        leg4["attempts"][-1]["note"] = "all-null reads"
try:
    r = curl("https://bsc-dataseed.binance.org/", timeout=20,
             post='{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}')
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
out["leg4"] = leg4
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-hot-leg-2026-11-15-1624-retry.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:5000])
print("ELAPSED", out["elapsed_s"])
