#!/usr/bin/env python3
"""Hot-leg 2026-11-19 15:09 WIB re-read (read-only). Focused change-detection
re-read of the change-sensitive snapshot entries, reusing the 1501 run's
Quicknode batch helpers. Never writes the main snapshot."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

def curl_json(payload, timeout=40):
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200:
        raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    return json.loads(raw.decode())

def rpc_batch(calls, timeout=25):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    resp = curl_json(payload, timeout=timeout)
    if not isinstance(resp, list):
        raise IOError(f"non-list batch response: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                res.append(int(it["result"], 16))
            except Exception:
                res.append(it["result"])
        elif "error" in it:
            res.append(f"err:{str(it['error'])[:120]}")
        else:
            res.append(None)
    return res

PLAN = [
 ("STOCK AGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply", "totalSupply()", None), ("freeLeft", "freeLeft()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("quote_user_1", "quote(address,uint256)", "user1"),
   ("freeMintedByWallet_user", "freeMintedByWallet(address)", "user"),
   ("balanceOf_user", "balanceOf(address)", "user")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", "launched()", None), ("failed", "failed()", None),
   ("isRefundPhase", "isRefundPhase()", None), ("totalShares", "totalShares()", None),
   ("tokenClaimed_user", "tokenClaimed(address)", "user")]),
 ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
  [("freeSharesLeft", "freeSharesLeft()", None), ("openedAt", "openedAt()", None),
   ("freeClaimed", "freeClaimed()", None), ("freeBooked_user", "freeBooked(address)", "user")]),
 ("AONE-sale", "0x84D82E933D7781fe11245e7bbd3Eb23dbb963666",
  [("freeMinted", "freeMinted()", None), ("FREE_TOTAL", "FREE_TOTAL()", None),
   ("freeTaken_user", "freeTaken(address)", "user")]),
 ("bsccat", "0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
  [("freeMinted", "freeMinted()", None), ("totalSupply", "totalSupply()", None)]),
]

out = {"run": "hot-leg 2026-11-19 15:09 WIB re-read", "started_wib": "2026-11-19 15:09 WIB"}
try:
    blk = curl_json([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=40)
    out["block"] = int(blk[0]["result"], 16)
except Exception as e:
    out["block"] = f"ERR {type(e).__name__}: {e}"

calls, labels = [], []
for name, addr, items in PLAN:
    for key, sig, arg in items:
        calls.append((addr, encode(sig, arg)))
        labels.append((name, key))
try:
    res = rpc_batch(calls, timeout=40)
except Exception as e:
    out["error"] = f"{type(e).__name__}: {e}"
    res = [None] * len(calls)
for (name, key), v in zip(labels, res):
    out.setdefault(name, {})[key] = v

# extra: eth_getCode for 2 new Boltbook addresses (Sourcify 404 - unverified)
try:
    codes = curl_json([{"jsonrpc":"2.0","id":i+1,"method":"eth_getCode","params":[a,"latest"]} for i,a in enumerate(["0x16dE59897fDeE7F34377C2302dC4e9FDb12168C2","0xeb1036f9cd6ecc5afc403c4abe0574b36e0205f2"])], timeout=40)
    out["getCode"] = {a: (c.get("result","?")[:10] if isinstance(c,dict) else str(c)) for a,c in zip(["0x16dE59897fDeE7F34377C2302dC4e9FDb12168C2","0xeb1036f9cd6ecc5afc403c4abe0574b36e0205f2"], codes)}
    out["getCode_len"] = {a: (len(c.get("result","")) if isinstance(c,dict) and c.get("result") else 0) for a,c in zip(["0x16dE59897fDeE7F34377C2302dC4e9FDb12168C2","0xeb1036f9cd6ecc5afc403c4abe0574b36e0205f2"], codes)}
except Exception as e:
    out["getCode"] = f"ERR {type(e).__name__}: {e}"
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-19-1509-reread.json", "w"), indent=1)
print(json.dumps(out, indent=1))
