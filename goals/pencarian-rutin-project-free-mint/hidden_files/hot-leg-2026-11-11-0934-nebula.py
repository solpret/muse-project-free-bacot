#!/usr/bin/env python3
"""NEBULA 0x8269... verification follow-up for hot-leg 0934 run.
Read-only: Sourcify ABI + on-chain views. No preview/mint/claim."""
import json, time, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
SALE = "0x8269Ea1629644219a88dbB053D34E8e877596B00"
TOKEN = "0xBbDd8C7720d1EEB1d63738eaABB584a4b72C7777"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP_NODE = "https://bsc.nodereal.io/"
EP_DATA = "https://bsc-dataseed.binance.org/"

def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode()).get("abi", [])

try:
    abi = fetch_abi(SALE)
    print("ABI entries:", len(abi))
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            fns.setdefault(e["name"], []).append(e)
    names = set(fns)
    print("FNS:", sorted(names))
    FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
                  "freeAvailable","freeSharePoolExhausted","freeSharesClaimed",
                  "freeMinted","freeCardsRemaining"]
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    print(f"S1={s1} has_mint={has_mint} has_quote={has_quote} free_views={free_views} agent_ref={agent_ref} is_token={is_token}")
    json.dump(abi, open(BASE + "hot-leg-2026-11-11-0934-nebula-abi.json","w"), indent=1)
except Exception as e:
    print("ABI FETCH FAILED:", type(e).__name__, e)
    fns, names = {}, set()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x","").rjust(64,"0")
def enc_uint(n): return hex(n)[2:].rjust(64,"0")

def post(ep, payload, timeout=20):
    pr = subprocess.run(["curl","-s","--max-time",str(timeout),"-X","POST",ep,
                         "-H","Content-Type: application/json","--data",payload],
                        capture_output=True, text=True, timeout=timeout+5)
    return json.loads(pr.stdout)

# candidate view calls (only those present in ABI, else skip)
cands = [
 ("totalShares","totalShares()"), ("totalRaised","totalRaised()"),
 ("TOKENS_PER_SHARE","TOKENS_PER_SHARE()"), ("MAX_SHARES","MAX_SHARES()"),
 ("TOTAL_SHARES","TOTAL_SHARES()"), ("price","price()"),
 ("PRICE","PRICE()"), ("paidPrice","paidPrice()"),
 ("freeMinted","freeMinted()"), ("freeClaimed_user","freeClaimed(address)"),
 ("freeSharesRemaining","freeSharesRemaining()"),
 ("totalFreeShares","totalFreeShares()"), ("freeLeft","freeLeft()"),
 ("agentRegistry","agentRegistry()"), ("registry","registry()"),
 ("owner","owner()"), ("mintOpen","mintOpen()"),
 ("baseQuota","baseQuota()"), ("quota","quota(address)"),
 ("freeUsed_user","freeUsed(address)"), ("freeFor_user","freeFor(address)"),
 ("sharesOf_user","sharesOf(address)"), ("balanceOf_user","balanceOf(address)"),
 ("quote_user_1","quote(address,uint256)"),
 ("cost_user_1","cost(address,uint256)"),
 ("getQuote_user_1","getQuote(address,uint256)"),
]
calls = []
for fname, sig in cands:
    base = sig.split("(")[0]
    if base not in names:
        continue
    if sig.endswith("(address)"):
        data = sel(sig) + enc_addr(USER)
    elif sig.endswith("(address,uint256)"):
        data = sel(sig) + enc_addr(USER) + enc_uint(1)
    else:
        data = sel(sig)
    calls.append((fname, data))

block = None
for ep in (EP_NODE, EP_DATA):
    try:
        block = int(post(ep, '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}', 15)["result"], 16)
        break
    except Exception:
        continue
print("block:", block)

out = {}
payload = json.dumps([{"jsonrpc":"2.0","id":j,"method":"eth_call",
                       "params":[{"to":SALE,"data":d},"latest"]} for j,(_,d) in enumerate(calls)])
resps = []
for ep in (EP_NODE, EP_DATA):
    try:
        resps = post(ep, payload, 30)
        if resps: break
    except Exception:
        resps = []
if isinstance(resps, dict): resps = [resps]
for (fname,_), r in zip(calls, resps):
    raw = r.get("result") if isinstance(r, dict) else None
    val = None
    if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
        try: val = int(raw[:66], 16)
        except Exception: pass
        if len(raw) > 66 and val is None:
            val = raw
    out[fname] = val if val is not None else raw
print(json.dumps(out, indent=1))
json.dump({"block": block, "sale": SALE, "token": TOKEN, "values": out,
           "s1": s1 if 's1' in dir() else None},
          open(BASE + "hot-leg-2026-11-11-0934-nebula.json","w"), indent=1)
