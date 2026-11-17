#!/usr/bin/env python3
"""COSO v2 track-C verification, run 0131 (2026-11-10 01:31 WIB). Read-only.
Source: Boltbook front page, post bangwi.ai ~14m ago: COSO v2 sale
0x7020368e5421008b92C16798589ac6d91812307e, totalShares 488/5000,
freeMinted 488/1000, 512 free left, 0 paid.
Also light-checks AGENT 888 S2 + Genesis Tx from the 1328.ai post.
"""
import json, urllib.request, urllib.error, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed2.bnbchain.org",
        "https://bsc-dataseed.binance.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
COSO = "0x7020368e5421008b92C16798589ac6d91812307e"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def rpc(method, params, timeout=25):
    for u in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(u, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.load(r)
            if "error" in out: continue
            return out["result"]
        except Exception:
            continue
    return None

def call(addr, sig, args=""):
    v = rpc("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"])
    if v is None or v == "0x": return None
    try: return int(v, 16)
    except Exception: return v

def call_multi(addr, sig, args=""):
    # for quote(address,uint256) -> (uint256,uint256)
    v = rpc("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"])
    if v is None or v == "0x": return None
    h = v[2:]
    try:
        return [int(h[i:i+64], 16) for i in range(0, len(h) - 63, 64)]
    except Exception:
        return v

blk = rpc("eth_blockNumber", [])
out = {"block": int(blk, 16) if blk else None, "address": COSO}
VIEWS = ["totalShares()", "totalFreeShares()", "totalPaidShares()", "freeMinted()",
         "freeSharesRemaining()", "MAX_SHARES()", "PRICE()", "TOKENS_PER_SHARE()",
         "totalRaised()", "totalSupply()", "agentIdRegistry()", "owner()",
         "saleStart()", "saleEnd()", "startTime()", "endTime()", "mintOpen()",
         "isAgent(address)", "freeUsed(address)", "sharesOf(address)",
         "freeClaimed(address)", "quotaOf(address)"]
for sig in VIEWS:
    if "(address)" in sig:
        out[sig] = call(COSO, sig, enc(USER))
    else:
        out[sig] = call(COSO, sig)
out["quote_user_1"] = call_multi(COSO, "quote(address,uint256)", enc(USER) + str(1).rjust(64, "0"))
# Sourcify ABI
def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404: return {"_not_verified": True}
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return {"_error": "retry-exhausted"}
abi_doc = sourcify_abi(COSO)
out["sourcify_verified"] = "_not_verified" not in abi_doc and "_error" not in abi_doc
abi = abi_doc.get("abi") if isinstance(abi_doc, dict) else None
fns = [it.get("name", "") for it in abi if it.get("type") == "function"] if isinstance(abi, list) else []
out["functions"] = fns
json.dump(out, open(f"{BASE}/run-2026-11-10-0131-coso.json", "w"), indent=1)
print(json.dumps(out, indent=1))

# Light checks: AGENT 888 S2 + Genesis Tx
for name, addr in [("AGENT888-S2", "0x1c963acf3743a2b2a3ee8359100e9cbeca82d424"),
                   ("GenesisTx", "0xce43adb0b4bd650d410feb2eafdda3e1d30ca49e")]:
    d = {"address": addr}
    for sig in ["totalSupply()", "totalMinted()", "mintOpen()", "owner()", "agentIdRegistry()"]:
        d[sig] = call(addr, sig)
    print(name, json.dumps(d))
