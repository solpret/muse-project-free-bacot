#!/usr/bin/env python3
"""Hot-leg run 2026-11-07 16:34 WIB — legs 1+2 (read-only).
Leg1: Sourcify recently-verified feed (limit 20, sort desc); new addrs vs
hot-leg-seen.json shape-checked S1/S2 via Sourcify ABI.
Leg2: Boltbook front page en + zh (boltbook.fun), extract 0x addresses,
new ones shape-checked the same way.
Registry + excluded examples skipped. Newly seen recorded in hot-leg-seen.json."""
import json, re, urllib.request, urllib.error, concurrent.futures, datetime

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
NOW = "2026-11-07 16:34 WIB"
TS = "2026-11-07-1634"

seen = json.load(open(f"{HF}/hot-leg-seen.json"))
snap = json.load(open(f"{HF}/onchain-snapshot.json"))
snap_addrs = {a.lower() for a in snap.get("contracts", {})}
snap_addrs |= {a.lower() for a in snap.get("track_c", {})}

def get(url, timeout=15, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    return data if binary else data.decode("utf-8", "replace")

# ---- Leg 1: Sourcify feed ----
feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
json.dump({"feed_raw": feed}, open(f"{HF}/hot-leg-{TS}-sourcify.json", "w"), indent=1)
feed_addrs = [r["address"] for r in feed.get("results", [])]
print("leg1 feed_addrs:", len(feed_addrs))

# ---- Leg 2: Boltbook en + zh (curl — urllib chokes on chunked IncompleteRead) ----
import subprocess
def curl_get(url, timeout=20):
    r = subprocess.run(["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0", url],
                       capture_output=True, text=True, timeout=timeout + 5)
    if r.returncode != 0:
        raise RuntimeError(f"curl {url} rc={r.returncode}: {r.stderr[:200]}")
    return r.stdout
en_html = curl_get("https://boltbook.fun/?lang=en")
zh_html = curl_get("https://boltbook.fun/?lang=zh")
open(f"{HF}/hot-leg-{TS}-boltbook-en.html", "w").write(en_html)
open(f"{HF}/hot-leg-{TS}-boltbook-zh.html", "w").write(zh_html)
print("leg2 en_bytes:", len(en_html), "zh_bytes:", len(zh_html))
bb_addrs = list(dict.fromkeys(re.findall(r"0x[0-9a-fA-F]{40}", en_html + zh_html)))
print("leg2 boltbook addrs found:", len(bb_addrs))

# ---- New addresses (either leg) ----
def is_new(a):
    return (a.lower() not in {s.lower() for s in seen}
            and a.lower() != REGISTRY.lower()
            and a.lower() not in {e.lower() for e in EXCLUDED})

feed_new = [a for a in feed_addrs if is_new(a)]
bb_new = [a for a in bb_addrs if is_new(a) and a.lower() not in {f.lower() for f in feed_addrs}]
print("leg1 new:", feed_new)
print("leg2 new:", bb_new)

FREE_SHARE_VIEWS = ["freesharesremaining","freeclaimed","freefor","freeleft","freeused",
    "freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted",
    "freeremaining","free_slots","free_supply","free_amount"]
QUOTE_FNS = ["quote","quotefor","quotemint","quotemintfor","cost","costfor","getcost",
    "price","mintprice","feefor"]
GATE_WORDS = ["agentid","agentregistry","agentgate","hasagentid","isagent"]

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for _ in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                return ("verified", json.loads(resp.read().decode()).get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
        except Exception as e:
            last = str(e)
    return ("error:" + last[:80], None)

def classify(abi):
    funcs = [i.get("name", "") for i in abi if isinstance(abi, list) and i.get("type") == "function"]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "mint", "claimfree")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "S1": s1, "S2": s2}

def shape_check(addrs, source, outfile):
    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        for addr, (st, abi) in zip(addrs, ex.map(fetch_abi, addrs)):
            d = {"address": addr, "status": st, "source": source}
            if abi is not None:
                d.update(classify(abi))
            out.append(d)
    json.dump(out, open(f"{HF}/{outfile}", "w"), indent=1)
    for d in out:
        print(" ", d["address"], d["status"], "S1=", d.get("S1"), "S2=", d.get("S2"),
              "funcs=", d.get("functions"), "mint=", d.get("mint_fns"),
              "quote=", d.get("quote_fns"), "free=", d.get("free_views"), "gate=", d.get("gate_fns"))
    return out

s1_out = shape_check(feed_new, "sourcify-feed", f"hot-leg-{TS}-sourcify-shape.json")
s2_out = shape_check(bb_new, "boltbook-frontpage", f"hot-leg-{TS}-boltbook-shape.json")

# record newly seen (feed + boltbook), first-seen time
new_all = feed_new + bb_new
for a in new_all:
    seen[a] = NOW
json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"), indent=1)
print("seen_total:", len(seen), "| new recorded this run:", len(new_all))
print("new_sale_shape:", sum(1 for d in s1_out + s2_out if d.get("S1") or d.get("S2")))
