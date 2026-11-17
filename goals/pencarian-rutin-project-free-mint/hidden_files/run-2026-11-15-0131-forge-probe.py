#!/usr/bin/env python3
"""Probe Forge Pass (FORG) 0xd4a038253d19E058a5653dFf177F7F21FeE59D52 for early-lead evaluation.
Reads: Sourcify ABI (registry/agent refs, free views, mint fns), name/symbol, owner,
freeMinted/freeRemaining/mintActive/getsFreeMint/freeUsed, contractURI, totalMinted.
Read-only. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0xd4a038253d19E058a5653dFf177F7F21FeE59D52"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def batch_read(calls):
    """calls: list of (name, sig, args). Returns dict name->int/str/None via race over endpoints."""
    payload = [{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                "params": [{"to": ADDR, "data": build_data(sig, args)}, "latest"]} for i, (_, sig, args) in enumerate(calls)]
    for ep in EPS:
        try:
            r = post_rpc(ep, payload, timeout=60)
            if isinstance(r, list) and r and all("result" in x for x in r):
                out = {}
                for (name, sig, args), resp in zip(calls, r):
                    v = resp.get("result")
                    if v in (None, "0x"):
                        out[name] = None; continue
                    if name in ("name", "symbol", "contractURI"):
                        try:
                            h = v[2:]
                            ln = int(h[64:128], 16); out[name] = bytes.fromhex(h[128:128 + ln*2]).decode(errors="replace")
                        except Exception:
                            out[name] = v
                    elif name == "owner":
                        out[name] = "0x" + v[-40:] if len(v) >= 42 else v
                    else:
                        try: out[name] = int(v, 16)
                        except Exception: out[name] = v
                out["_ep"] = ep
                return out
        except Exception as e:
            print("ep fail", ep, e)
    return {name: None for name, _, _ in calls}
# 1. Sourcify ABI
try:
    s = subprocess.run(["curl", "-sL", "--max-time", "60",
        f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=stdJson,metadata"],
        capture_output=True, text=True, timeout=70).stdout
    sj = json.loads(s)
    open(BASE + "run-2026-11-15-0131-forge-sourcify.json", "w").write(json.dumps(sj, indent=1)[:20000])
    abi = sj.get("stdJson", {}).get("output", {}).get("abi") or sj.get("stdJson", {}).get("abi") or []
    fns = [e.get("name") for e in abi if e.get("type") == "function"]
    src = json.dumps(sj)
    print("SOURCIFY verified:", bool(abi), "| n_fns:", len(fns))
    print("FNS:", fns)
    print("REGISTRY 0x60B9 in src:", "60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower() in src.lower())
    print("agentRegistry in fns:", "agentRegistry" in fns, "| AGENT_ID in fns:", "AGENT_ID" in fns)
    print("free views:", [f for f in fns if "free" in f.lower() or "Free" in f])
    print("mint fns:", [f for f in fns if "mint" in f.lower()])
except Exception as e:
    print("SOURCIFY ERROR:", e)
    abi = []
# 2. On-chain views
calls = [("name","name()",[]),("symbol","symbol()",[]),("totalSupply","totalSupply()",[]),
 ("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),
 ("freeRemaining","freeRemaining()",[]),("mintActive","mintActive()",[]),
 ("getsFreeMint_user","getsFreeMint(address)",[USER]),("freeUsed_user","freeUsed(address)",[USER]),
 ("contractURI","contractURI()",[]),("owner","owner()",[]),
 ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[])]
res = batch_read(calls)
print("ONCHAIN:", json.dumps(res, indent=1))
# 3. Block number
try:
    r = post_rpc(EPS[0], {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=30)
    print("BLOCK:", int(r["result"],16))
except Exception as e:
    print("BLOCK ERR:", e)
json.dump({"addr": ADDR, "onchain": res}, open(BASE + "run-2026-11-15-0131-forge-probe.json","w"), indent=1)
