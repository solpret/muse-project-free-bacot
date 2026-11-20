#!/usr/bin/env python3
"""CAP7 re-verify with chunked batch (8) + list validation, proven pattern."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_u(n): return "%064x" % n
abi = json.load(open(f"{HF}/run-2026-11-17-0931-cap7-abi.json"))
fns = {}
for e in abi.get("abi", []):
    if e.get("type") == "function":
        fns.setdefault(e["name"], []).append(e)
out = {"contract": ADDR, "sourcify_verified": True,
       "verifiedAt": abi.get("verifiedAt"), "n_fns": len(fns),
       "functions": sorted(fns.keys())}
names = set(fns)
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted",
              "freeCardsRemaining"}
has_mint = any(n.lower().startswith("mint") or n.lower().startswith("claim") for n in names)
has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice","PRICE"})
free_views = sorted(names & FREE_VIEWS)
agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
is_token = bool(names & {"name","symbol","decimals","totalSupply"})
mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
claimfree_noarg = "claimFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["claimFree"])
s1 = has_mint and has_quote and bool(free_views) and agent_ref
s2 = is_token and (mintfree or claimfree_noarg) and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY","FREE_SHARES"}) and agent_ref
out["shape"] = {"S1": s1, "S2": s2, "has_mint_or_claim": has_mint, "has_quote": has_quote,
                "free_views": free_views, "agent_ref": agent_ref, "is_token": is_token,
                "claimFree_noarg": claimfree_noarg}
SIGS = ["freeMinted()", "FREE_SHARES()", "paidMinted()", "totalSupply()",
        "deadline()", "PRICE()", "mintOpen()", "saleOpen()",
        "totalMinted()", "MAX_SUPPLY()", "FREE_SUPPLY()", "freeSharesRemaining()",
        "freeLeft()", "freeClaimed(address)", "hasClaimed(address)",
        "freeClaimedBy(address)", "claimed(address)", "hasAgentId(address)",
        "agentId()", "agentRegistry()", "owner()", "name()", "symbol()",
        "decimals()", "quote(uint256)", "cost(uint256)", "costOf(uint256)",
        "claimable(address)", "balanceOf(address)", "mintedBy(address)",
        "poolOpen()", "opened()", "isOpen()", "soldOut()", "freePerWallet()",
        "maxPerWallet()", "MAX_PER_WALLET()", "claimAmount()", "SHARE_AMOUNT()",
        "TOKENS_PER_SHARE()", "tokensPerShare()", "poolReserve()"]
calls, labels = [], []
for s in SIGS:
    if "(address)" in s:
        calls.append((ADDR, "0x" + sel(s) + enc_addr(USER)))
    elif "(uint256)" in s:
        calls.append((ADDR, "0x" + sel(s) + enc_u(1)))
    else:
        calls.append((ADDR, "0x" + sel(s)))
    labels.append(s)
def batch_chunk(chunk, timeout=15):
    payload = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(chunk)]
    body = json.dumps(payload).encode()
    last = None
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                outp = json.loads(r.read().decode())
            if not isinstance(outp, list):
                raise IOError(f"non-list: {str(outp)[:150]}")
            res = []
            by_id = {it["id"]: it for it in outp if isinstance(it, dict)}
            for i in range(len(chunk)):
                it = by_id.get(i+1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    try: res.append(int(it["result"], 16))
                    except Exception: res.append(it["result"])
                else: res.append(None)
            return res, ep
        except Exception as e:
            last = e
            continue
    raise IOError(f"batch failed: {last}")
views, eps = {}, []
for i in range(0, len(calls), 8):
    res, ep = batch_chunk(calls[i:i+8])
    eps.append(ep)
    for lab, val in zip(labels[i:i+8], res):
        views[lab] = val
out["views"] = views
out["endpoints"] = sorted(set(eps))
json.dump(out, open(f"{HF}/run-2026-11-17-0931-cap7-verify.json", "w"), indent=1)
# block + bytecode registry
import subprocess as _sp
try:
    r = _sp.run(["curl","-s","--max-time","15",eps[0],"-H","Content-Type: application/json",
        "-d", json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])],
        capture_output=True, timeout=20)
    out["block"] = int(json.loads(r.stdout.decode())[0]["result"], 16)
except Exception as e:
    out["block_error"] = f"{type(e).__name__}: {str(e)[:120]}"
json.dump(out, open(f"{HF}/run-2026-11-17-0931-cap7-verify.json", "w"), indent=1)
import subprocess
try:
    r = subprocess.run(["curl","-s","--max-time","20",eps[0],"-H","Content-Type: application/json",
        "-d", json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]}])],
        capture_output=True, timeout=25)
    code = json.loads(r.stdout.decode())[0]["result"]
    out["bytecode_len"] = (len(code)-2)//2 if code else 0
    out["registry_bytes"] = REGISTRY[2:].lower() in code.lower()
except Exception as e:
    out["bytecode_error"] = f"{type(e).__name__}: {str(e)[:150]}"
# decode totalSupply human
ts = views.get("totalSupply()")
out["totalSupply_tokens"] = ts / 10**18 if isinstance(ts, int) else None
json.dump(out, open(f"{HF}/run-2026-11-17-0931-cap7-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
