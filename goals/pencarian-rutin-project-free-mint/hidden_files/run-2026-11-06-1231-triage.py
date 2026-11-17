#!/usr/bin/env python3
"""Triage run 1231: 2 first-seen (Standboy, Stickman) + 5c ERC20 shape-check."""
import json, urllib.request, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1231"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com", "https://bsc-dataseed2.bnbchain.org"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def rpc(method, params, timeout=8):
    for r in RPCS:
        try:
            body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req = urllib.request.Request(r, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                out = json.load(resp)
            if "error" in out: continue
            return out["result"]
        except Exception:
            continue
    return None
def raw(to, data, timeout=8):
    v = rpc("eth_call", [{"to": to, "data": data}, "latest"], timeout)
    if not v or v == "0x": return None
    try: return int(v, 16)
    except Exception: return v
def call(to, sig, args=""): return raw(to, sel(sig) + args)
def block_ts(b):
    v = rpc("eth_getBlockByNumber", [hex(b), False], 10)
    if v and v.get("timestamp"):
        return int(v["timestamp"], 16)
    return None
out = {"first_seen": []}
for name, addr, fb in [
    ("Standboy", "0x6043a590F315B9fF44aD3b3298198f89b6b4b548", 131955675),
    ("Stickman", "0x345b0eb3180ae510cB2f05EfD49085E79477b330", 131955654)]:
    ts = block_ts(fb)
    import datetime
    wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") if ts else None
    d = {"name": name, "address": addr, "first_block": fb, "first_mint_wib": wib}
    for sig in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "PRICE()", "spotsLeft()", "agentRegistry()", "agentGateOn()", "mintOpen()"]:
        d[sig.split("(")[0]] = call(addr, sig)
    d["name()"] = call(addr, "name()")
    d["symbol()"] = call(addr, "symbol()")
    d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
    d["costOf_user_1"] = call(addr, "costOf(address,uint256)", enc(USER) + enc_uint(1))
    d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    print(name, json.dumps(d), flush=True)
    out["first_seen"].append(d)
# 5c: ERC20 mint_count>=10, max 20 new
scan = json.load(open(f"{BASE}/onchain-scan-2026-11-06-1231.json"))
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_l = {k.lower() for k in checked}
erc = sorted(scan["erc20_mint_contracts_list"], key=lambda x: -x.get("mint_count", 0))
cands = [e for e in erc if e.get("mint_count", 0) >= 10 and e["address"].lower() not in checked_l][:20]
print("5c candidates:", len(cands), [e["address"] for e in cands], flush=True)
FREE_SHARE_VIEWS = ["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freeremaining","free_slots","free_supply","free_amount"]
QUOTE_FNS = ["quote","quotefor","quotemint","quotemintfor","cost","costfor","getcost","price","mintprice","feefor"]
GATE_WORDS = ["agentid","agent_id","agentregistry","agent_registry","agentgate","agent_gate","hasagentid","isagent"]
def classify(abi):
    funcs = [it.get("name","") for it in abi if isinstance(abi,list) and isinstance(it,dict) and it.get("type")=="function"]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name","symbol","decimals","totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree","mint","claimfree")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns, "free_views": free_views, "gate_fns": gate, "token_fns": token_fns, "S1": s1, "S2": s2}
def fast_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for i in range(2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                return ("verified", json.loads(resp.read().decode()).get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404: return ("not_verified", None)
        except Exception:
            time.sleep(1)
    return ("error", None)
res5c = []
for e in cands:
    st, abi = fast_abi(e["address"])
    r = {"address": e["address"], "mint_count": e["mint_count"], "sourcify": st}
    if abi is not None: r.update(classify(abi))
    else: r["S1"] = False; r["S2"] = False
    res5c.append(r)
    print("5c", r["address"], st, "S1=", r.get("S1"), "S2=", r.get("S2"), "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"), "free=", r.get("free_views"), "agent=", r.get("gate_fns"), flush=True)
out["track_c_5c"] = res5c
json.dump(out, open(f"{BASE}/run-{TS}-triage.json", "w"), indent=1)
print("TRIAGE DONE", flush=True)
