#!/usr/bin/env python3
"""Verify new Boltbook contracts (KAGE, FACES, CMPN) + shape-check new Sourcify feed contracts. Read-only."""
import json, subprocess, time, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
RPC = "https://bsc-dataseed.binance.org/"
def curl(url, timeout=25):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),url], capture_output=True, timeout=timeout+5)
    return r.stdout.decode(errors="replace")
def rpc_json(payload, timeout=25):
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, timeout=timeout+5)
    return json.loads(r.stdout.decode())
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def call(to, sig, arg=None):
    data = "0x"+sel(sig)
    if arg=="user": data += enc_addr(USER)
    elif arg=="one": data += "%064x"%1
    elif arg=="user1": data += enc_addr(USER)+"%064x"%1
    p=[{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}]
    try:
        res = rpc_json(p)
        r = res[0].get("result")
        if r in (None,"0x"): return None
        return int(r,16)
    except Exception as e:
        return f"err:{type(e).__name__}"
def sourcify(addr):
    try:
        raw = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,creationMatch,match")
        d = json.loads(raw)
        if isinstance(d, dict) and d.get("stdJson") is None and "abi" not in d and d.get("message"):
            return {"verified": False, "note": d.get("message","")[:120]}
        abi = d.get("abi") if isinstance(d, dict) else None
        return {"verified": True, "match": d.get("match"), "creationMatch": d.get("creationMatch"),
                "verifiedAt": (d.get("creationMatch") or ""), "abi_len": len(abi) if abi else 0, "abi": abi}
    except Exception as e:
        return {"verified": "error", "note": f"{type(e).__name__}: {str(e)[:120]}"}
FREE_VIEWS = ["freeMinted()","freeClaimed()","freeLeft()","freeSupply()","freeRemaining()","FREE_SUPPLY()","MAX_SUPPLY()","totalMinted()","totalSupply()","mintOpen()","mintedBy(address)","freeMintedBy(address)","balanceOf(address)","name()","symbol()","owner()","AGENT_ID()","agentRegistry()"]
def shape(abi):
    if not abi: return {"S1": False, "S2": False, "reason": "no abi"}
    names = set()
    for e in abi:
        if e.get("type")=="function": names.add(e.get("name",""))
    has_mint = any(n.startswith("mint") for n in names)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower()) for n in names)
    free_views = [n for n in names if n.lower().startswith("free")]
    has_registry = ("agentId" in names or "AGENT_ID" in names or "agentRegistry" in names or "agentGate" in names or "agentID" in names)
    s1 = has_mint and has_quote and len(free_views)>0 and has_registry
    is_token = all(n in names for n in ("name","symbol","decimals","totalSupply"))
    noarg_free = "mintFree" in names
    s2 = is_token and noarg_free and len(free_views)>0 and has_registry
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
            "has_registry_ref": has_registry, "is_token": is_token, "fns": sorted(names)[:60]}
out = {}
# --- Boltbook new contracts ---
for name, addr in [("Kageveil", "0xf79860f419be7b604d909e254785400d9edbd9d0"),
                    ("FACES", "0x8653b09bdad22c99915910962167f132e514331f"),
                    ("Compasyn", "0xCd1bb8013E924E26Ed4131A69304f2969c4f8D28")]:
    s = sourcify(addr)
    entry = {"address": addr, "sourcify_verified": s.get("verified"), "match": s.get("match")}
    abi = s.get("abi")
    entry["shape"] = shape(abi) if abi else {"S1": False, "S2": False, "reason": "no abi"}
    if abi:
        abis = json.dumps(abi)
        entry["registry_bytes_in_abi"] = REG.lower()[2:] in abis.lower()
    views = {}
    for sig in FREE_VIEWS:
        arg = "user" if "(address)" in sig else None
        views[sig.split("(")[0]] = call(addr, sig, arg)
    entry["views"] = views
    # code size
    try:
        res = rpc_json([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}])
        code = res[0].get("result","")
        entry["code_bytes"] = (len(code)-2)//2 if code.startswith("0x") else None
        entry["registry_bytes_in_code"] = REG.lower()[2:] in code.lower()
    except Exception as e:
        entry["code_bytes"] = f"err:{e}"
    out[name] = entry
    print(name, json.dumps({k:v for k,v in entry.items() if k!="shape"}, default=str)[:900])
    print("  shape:", json.dumps(entry["shape"], default=str)[:400])
# --- Sourcify feed new contracts (vs hot-leg 0154 seen) ---
feed = json.load(open(f"{HF}/run-2026-11-18-0201.json"))
addrs = feed["sourcify_feed"]["addresses"]
hot = json.load(open(f"{HF}/hot-leg-seen.json")) if True else {}
# hot-leg-seen.json structure unknown; just shape-check all 20 feed addrs (cheap, Sourcify only)
seen = set()
try:
    hl = json.load(open(f"{HF}/hot-leg-seen.json"))
    if isinstance(hl, dict): seen = set(hl.keys())
    elif isinstance(hl, list): seen = set(hl)
except Exception:
    pass
print("hot-leg seen count:", len(seen))
new_feed = [a for a in addrs if a.lower() not in {s.lower() for s in seen}]
print("feed addrs not in hot-leg-seen:", len(new_feed), new_feed)
feed_out = {}
for a in new_feed:
    s = sourcify(a)
    sh = shape(s.get("abi")) if s.get("abi") else {"S1": False, "S2": False, "reason": "no abi"}
    feed_out[a] = {"verified": s.get("verified"), "match": s.get("match"), "S1": sh.get("S1"), "S2": sh.get("S2"),
                   "has_mint": sh.get("has_mint"), "has_quote": sh.get("has_quote"), "free_views": sh.get("free_views"),
                   "has_registry_ref": sh.get("has_registry_ref"), "is_token": sh.get("is_token")}
    print("FEED", a, json.dumps(feed_out[a], default=str))
out["feed_shape"] = feed_out
json.dump(out, open(f"{HF}/run-2026-11-18-0201-verify.json","w"), indent=1)
print("DONE")
