#!/usr/bin/env python3
"""Run 1931 parent Mossminds reconciliation (read-only).
Decisive check: list Mossminds Transfer-from-zero logs with tokenIds in
131821105-131822500 and fresh supply reads, to settle B (age verified,
first mint 131821105) vs A (IDs 4-15 pre-exist, age unverified)."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

MOSS = "0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def ankr_logs(from_block, to_block, topics, max_pages=10):
    logs = []
    page_token = None
    pages = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(from_block),
                  "toBlock": hex(to_block), "pageSize": 1000,
                  "decodeLogs": False, "topics": topics}
        if page_token:
            params["pageToken"] = page_token
        body = ankr_post("ankr_getLogs", params, timeout=30)
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend(result.get("logs", []))
        page_token = result.get("nextPageToken")
        pages += 1
        if not page_token or pages >= max_pages:
            break
    return logs, pages

topics = [TRANSFER, ZERO_TOPIC, None, None]
logs, pages = ankr_logs(131821105, 131822500, topics)
moss = [l for l in logs if l.get("address", "").lower() == MOSS.lower()]
tids = sorted(int(l["topics"][3], 16) for l in moss if len(l.get("topics", [])) > 3)
blocks = sorted(int(l["blockNumber"], 16) for l in moss)
out = {
    "logs_in_range_total": len(logs),
    "moss_logs": len(moss),
    "pages": pages,
    "tokenIds": tids,
    "first_block": blocks[0] if blocks else None,
    "last_block": blocks[-1] if blocks else None,
    "sequential_from_1": tids == list(range(1, len(tids) + 1)),
    "missing_ids_below_max": [i for i in range(1, (max(tids) + 1) if tids else 1) if i not in tids],
}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: o = json.load(r)
            if "error" in o: return None
            v = o["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None
def call(to, sig, args=""):
    v = raw(to, sel(sig) + args)
    if v is None: return None
    try: return int(v, 16)
    except Exception: return v

out["totalSupply_now"] = call(MOSS, "totalSupply()")
out["freeMinted_now"] = call(MOSS, "freeMinted()")
out["paidMinted_now"] = call(MOSS, "paidMinted()")
out["canFreeMint_user"] = call(MOSS, "canFreeMint(address)", enc(USER))
out["claimedFree_user"] = call(MOSS, "claimedFree(address)", enc(USER))
out["ownerOf_4"] = raw(MOSS, sel("ownerOf(uint256)") + format(4, "064x"))
out["ownerOf_15"] = raw(MOSS, sel("ownerOf(uint256)") + format(15, "064x"))
print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1931-mossminds-reconcile.json", "w"), indent=1)
