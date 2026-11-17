#!/usr/bin/env python3
"""Probe S1 hit 0xB8b7 (leg 3) + shape-check 4 new Boltbook mentions. Read-only."""
import json, re, subprocess, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-hot-leg/1924-probe"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout+10).stdout
    return json.loads(out)

FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=20).decode())
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in names
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "n_fns": len(names), "names": sorted(names), "status": "checked"}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}

out = {}
# --- Boltbook shape checks ---
bb = ["0x23c1bf5333de12bc43ada5fb58aef188929cc139",
      "0x44a6c3b3769d7526eabe1f5e631dbd35a7a7874c",
      "0x6dd26c79f9c570c48b93370ec73de382c243f19f",
      "0xedc6a6891ebf3dc05a6d256e960c7d08efa66617"]
out["boltbook_shapes"] = [shape(a) for a in bb]

# --- S1 hit ABI + on-chain leg 3 ---
HIT = "0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb"
hit = shape(HIT)
out["hit_shape"] = {k: v for k, v in hit.items() if k != "names"}
names = set(hit.get("names", []))
out["hit_names"] = sorted(names)
# code check
code = post_rpc(EPS[0], {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[HIT,"latest"]}, timeout=30)
out["hit_code_len"] = len(code.get("result","")) if isinstance(code, dict) else None
# build view calls from what's present
views = []
def add(key, sig, args):
    views.append((key, sig, args))
# identity
for fn in ("name","symbol","totalSupply","MAX_SUPPLY","FREE_SUPPLY","FREE_MAX","FREE_SHARES","FREE_TOTAL","FREE_CAP","FREE_POOL"):
    if fn in names: add(fn, fn+"()", [])
for fn in ("mintOpen","saleActive","claimOpen","launched","mintActive","paused","genesisOpen"):
    if fn in names: add(fn, fn+"()", [])
for fn in ("freeLeft","freeSharesRemaining","freeAvailable","freeMinted","freeClaimed","freeSharesClaimed","freeUsed","totalMinted","totalSupply"):
    if fn in names: add(fn, fn+"()", [])
for fn in ("mintStart","mintStartTime","startTime","genesisStart","freeStart","openedAt","launchTime","launchStart"):
    if fn in names: add(fn, fn+"()", [])
for fn in ("owner",):
    if fn in names: add(fn, fn+"()", [])
# user slot views
if "freeClaimed" in names: add("freeClaimed_user","freeClaimed(address)",[USER])
if "freeUsed" in names: add("freeUsed_user","freeUsed(address)",[USER])
if "freeFor" in names: add("freeFor_user","freeFor(address)",[USER])
if "mintedBy" in names: add("mintedBy_user","mintedBy(address)",[USER])
if "balanceOf" in names: add("balanceOf_user","balanceOf(address)",[USER])
if "holdsAgentId" in names: add("holdsAgentId_user","holdsAgentId(address)",[USER])
if "hasAgentId" in names: add("hasAgentId_user","hasAgentId(address)",[USER])
# quote(user,1) variants
for q in ("quote","cost","getQuote","priceFor","price"):
    if q in names:
        # try (address,uint256) first
        add("quote_user_1", q+"(address,uint256)", [USER, 1])
        break
if "contractURI" in names: add("contractURI","contractURI()",[])
calls, meta = [], []
for key, sig, args in views:
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a)==42 else enc_u(int(a))
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call","params":[{"to":HIT,"data":d},"latest"]})
    meta.append(key)
res = None
for ep in EPS:
    try:
        r = post_rpc(ep, calls, timeout=60)
        if isinstance(r, list) and len(r)==len(calls): res=r; break
    except Exception as e:
        out.setdefault("rpc_errors", []).append(str(e)[:100])
vals = {}
if res:
    for it, key in zip(res, meta):
        if isinstance(it, dict) and "result" in it and it["result"] not in (None,"0x"):
            v = it["result"]
            vals[key] = to_int(v[:66]) if len(v)>=66 and key not in ("name","symbol","contractURI") else v
        else:
            vals[key] = None
out["hit_views"] = vals
# block
try:
    b = post_rpc(EPS[0], {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=30)
    out["block"] = int(b["result"],16) if isinstance(b,dict) and b.get("result") else None
except Exception as e:
    out["block_error"] = str(e)[:100]
json.dump(out, open(BASE+"probe-1924-b8b7.json","w"), indent=1)
print(json.dumps(out, indent=1))
