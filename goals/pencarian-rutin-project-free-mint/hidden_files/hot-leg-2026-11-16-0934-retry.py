#!/usr/bin/env python3
"""Retry for hot-leg run 0934: (a) 6 Sourcify shape-checks that failed on
transport errors (IncompleteRead/RemoteDisconnected) - retried via curl;
(b) 16 leg-4 calls that returned all-null in chunks 0-1 - one batch retry."""
import json, re, subprocess, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import fast_rpc
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "hot-leg 0934 retry", "shape_retry": [], "leg4_retry": {}}

FAILED = ["0x235beF9dB61972FF1b8C5556eAB7DFd9ed6DC744",
          "0x4F49Da88BB5b4CdA0e2997af5D74AAaB82861D3a",
          "0x86b6EF2E4c880a69a4bC1ce73b22638181C40D10",
          "0x1a439ab097109b02e55d8D9bE4bd2CC544A408cb",
          "0x7674D9b10F81B955A3B9016b19e35183425c19cB",
          "0xAf7B719B09D61bB797aCB4871E45ADf3462bF64e"]
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeCardsRemaining"}
for addr in FAILED:
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "20", url],
                           capture_output=True, text=True, timeout=25)
        meta = json.loads(r.stdout)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId", "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) \
            and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        out["shape_retry"].append({"address": addr, "S1": s1, "S2": s2,
            "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
            "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
            "status": "checked", "verifiedAt": meta.get("verifiedAt")})
    except Exception as e:
        out["shape_retry"].append({"address": addr, "status": "shape-check-failed",
            "error": f"{type(e).__name__}: {str(e)[:150]}"})

# (b) leg-4 null-chunk retry: JADE cost(user,1) + AgentBubble + Matrix + AGCLUB views
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def call(to, sig, arg=None):
    data = "0x" + sel(sig)
    if arg == "user": data += enc_addr(USER)
    return (to, data)
calls, meta = [], []
_cost = "0x" + sel("cost(address,uint256)") + "0"*24 + USER[2:].lower() + "%064x" % 1
calls.append(("0x1b8894391a3dcfe7e248c321103265ab52e273e0", _cost)); meta.append(("JADE","cost_user_1"))
PLAN = [
 ("AgentBubble", "0x0d72970046c056db90888351b739246f468bff0b",
  [("freeMinted","freeMinted()",None),("totalSupply","totalSupply()",None),
   ("totalMinted","totalMinted()",None),("MAX_SUPPLY","MAX_SUPPLY()",None),
   ("mintOpen","mintOpen()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("Matrix", "0x1F669b714337F3C2585072c53fdDD89581F928fF",
  [("freeMinted","freeMinted()",None),("freeRemaining","freeRemaining()",None),
   ("totalSupply","totalSupply()",None),("mintOpen","mintOpen()",None)]),
 ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75",
  [("totalMinted","totalMinted()",None),("freeMinted","freeMinted()",None),
   ("FREE_CAP","FREE_CAP()",None),("mintOpen","mintOpen()",None),
   ("balanceOf_user","balanceOf(address)","user")]),
]
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append(call(addr, sig, arg)); meta.append((name, label))
payload = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call",
            "params":[{"to":to,"data":data},"latest"]} for i,(to,data) in enumerate(calls)]
body = json.dumps(payload).encode()
res, ep_used = None, None
for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
    try:
        req = urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            outp = json.loads(r.read().decode())
        by_id = {it["id"]: it for it in outp if isinstance(it, dict)}
        res = []
        for i in range(len(calls)):
            it = by_id.get(i+1, {})
            if "result" in it and it["result"] not in (None, "0x"):
                try: res.append(int(it["result"], 16))
                except Exception: res.append(it["result"])
            else: res.append(None)
        ep_used = ep; break
    except Exception as e:
        continue
if res is None:
    out["leg4_retry"] = {"error": "all endpoints failed"}
else:
    for (name, label), val in zip(meta, res):
        out["leg4_retry"].setdefault(name, {})[label] = val
    out["leg4_retry"]["endpoint"] = ep_used
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-16-0934-retry.json","w"), indent=1)
print(json.dumps(out, indent=1))
