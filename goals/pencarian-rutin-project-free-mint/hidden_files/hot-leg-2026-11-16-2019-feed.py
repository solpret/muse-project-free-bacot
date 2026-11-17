#!/usr/bin/env python3
"""Hot-leg 2026-11-16 20:19 WIB — legs 1+2: Sourcify feed + Boltbook EN/ZH
+ shape-check of new contracts. Curl-based (urllib 400s seen at 19:01)."""
import json, re, subprocess, datetime

TAG = "hot-leg-2026-11-16-2019"
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
SEEN_F = f"{BASE}/hot-leg-seen.json"
NOW = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {
    "0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",  # long-agent.com sale (pool exhausted)
    "0x8b47354e7b76b1970a0d06365c8244a810d37493",  # 传火人 (pool exhausted)
}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedBy"]

def curl(url, timeout=30, data=None):
    cmd = ["curl", "-sS", "--max-time", str(timeout)]
    if data is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if p.returncode != 0 or not p.stdout.strip():
            return None, f"curl rc={p.returncode} err={p.stderr[:100]}"
        return p.stdout, None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:100]}"

# --- leg 1: Sourcify feed ---
raw, err = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 30)
feed_addrs = []
feed_top = None
if raw:
    try:
        feed = json.loads(raw)
        with open(f"{BASE}/{TAG}-sourcify.json", "w") as f:
            json.dump(feed, f, indent=1)
        items = feed if isinstance(feed, list) else feed.get("contracts", feed.get("results", []))
        for it in items:
            a = it.get("address") or it.get("contractAddress")
            if a:
                feed_addrs.append(a)
        if items:
            feed_top = items[0].get("verifiedAt") or items[0].get("creationMatch", {}).get("verifiedAt")
    except Exception as e:
        err = f"parse: {e}"
print("FEED:", len(feed_addrs), "addrs, top verifiedAt:", feed_top, "err:", err, flush=True)

# --- leg 2: Boltbook EN + ZH ---
def boltbook(lang):
    url = "https://boltbook.fun/" if lang == "en" else "https://boltbook.fun/?lang=zh"
    raw, err = curl(url, 30)
    addrs = []
    if raw:
        with open(f"{BASE}/{TAG}-boltbook-{lang}.html", "w") as f:
            f.write(raw)
        addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", raw)))
    print(f"BOLTBOOK-{lang.upper()}:", len(raw or ""), "bytes,", len(addrs), "addrs, err:", err, flush=True)
    return addrs, len(raw or "")

en_addrs, en_bytes = boltbook("en")
zh_addrs, zh_bytes = boltbook("zh")
bb = {"en_bytes": en_bytes, "en_addrs": en_addrs, "zh_bytes": zh_bytes, "zh_addrs": zh_addrs,
      "en_err": None, "zh_err": None}
json.dump(bb, open(f"{BASE}/{TAG}-boltbook.json", "w"), indent=1)

# --- dedupe vs seen ---
seen = json.load(open(SEEN_F))
seen_lower = {k.lower(): k for k in seen}
all_new = []
for a in feed_addrs + en_addrs + zh_addrs:
    al = a.lower()
    if al in seen_lower or al in EXCLUDED or al == REGISTRY.lower():
        continue
    if a not in all_new:
        all_new.append(a)
print("NEW vs seen:", len(all_new), all_new, flush=True)

# --- shape-check new ---
def get_code(addr):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                          "params": [addr, "latest"]})
    out, _ = curl("https://bsc-dataseed.binance.org/", 25, data=payload)
    try:
        return json.loads(out).get("result", "") or ""
    except Exception:
        return ""

res = {}
for a in all_new:
    d, err = None, None
    raw2, err = curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=metadata,abi", 30)
    if raw2:
        try:
            d = json.loads(raw2)
        except Exception as e:
            err = f"parse: {e}"
    if not d:
        res[a] = {"shape": "abi-unavailable", "err": err}
        print(a, "ABI UNAVAILABLE:", err, flush=True)
        continue
    abi = d.get("abi") or d.get("metadata", {}).get("output", {}).get("abi") or []
    names = [f.get("name", "") for f in abi if f.get("type") == "function"]
    has_mint = any(n.startswith("mint") for n in names)
    has_quote = any("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower() for n in names)
    free_views = [n for n in names if n in FREE_VIEWS]
    code = get_code(a)
    has_reg = REG in code.lower() or any("agentidregistry" in n.lower() or "agentgate" in n.lower() for n in names)
    is_token = any(n in names for n in ("name", "symbol", "decimals", "totalSupply"))
    has_mintfree = "mintFree" in names
    s1 = has_mint and has_quote and bool(free_views) and has_reg
    s2 = is_token and has_mintfree and bool(free_views) and has_reg
    shape = "S1" if s1 else ("S2" if s2 else "checked-not-sale-shape")
    print(a, "fns=", len(names), "mint=", has_mint, "quote=", has_quote,
          "free_views=", free_views, "reg=", has_reg, "token=", is_token,
          "mintFree=", has_mintfree, "=>", shape, flush=True)
    res[a] = {"shape": shape, "fns": len(names), "mint": has_mint, "quote": has_quote,
              "free_views": free_views, "registry": has_reg, "token": is_token,
              "mintFree": has_mintfree}
json.dump(res, open(f"{BASE}/{TAG}-feedshape.json", "w"), indent=1)

# --- update seen (new contracts only; excluded/registry never recorded) ---
n_before = len(seen)
for a in all_new:
    seen[a] = {"first_seen_wib": NOW, "source": TAG}
json.dump(seen, open(SEEN_F, "w"), indent=1)
print(f"SEEN: {n_before} -> {len(seen)} (+{len(all_new)})")
print("DONE")
