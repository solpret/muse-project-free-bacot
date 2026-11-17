#!/usr/bin/env python3
"""Main-run 2026-11-06 02:01 WIB re-read v2 (route 1) + track-C + BINANCEAI.
as_completed (no head-of-line block), 2 RPCs, 4s timeout.
Item set = run 0131 reread (69) + AgentX + PERSONA + Sourcify-new 0x857a.
Writes run-2026-11-06-0201-reread.json only. Never writes the main snapshot."""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0201"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=4) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

NFT_VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
             "FREE_SUPPLY()", "MAX_SUPPLY()", "balanceOf(address)",
             "quote(address,uint256)", "costOf(address,uint256)", "mintsLeft(address)",
             "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)",
             "claimedFree(address)", "owner()"]
TC_VIEWS = ["opened()", "launched()", "freeMinted()", "freeSharesRemaining()",
            "freeSharesClaimed(address)", "freeClaimed(address)", "hasFreeShare(address)",
            "totalMinted()", "sharesMinted()", "saleEnded()", "phase()"]
BINANCEAI_MINT_VIEWS = ["launched()", "isRefundPhase()", "failed()", "totalShares()",
                        "tokenClaimed(address)"]
BINANCEAI_TOKEN_VIEWS = ["balanceOf(address)"]

snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
prev = json.load(open(f"{BASE}/run-2026-11-06-0131-reread.json"))
names = sorted(prev["contracts"].keys())

items = {}
for name in names:
    if name == "BINANCEAI-mint":
        items[name] = ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", BINANCEAI_MINT_VIEWS)
        continue
    if name == "BINANCEAI-token":
        items[name] = ("0x209173F09aFbCA053C0de9e9763f503e9fb54a3c", BINANCEAI_TOKEN_VIEWS)
        continue
    addr = None; kind = "nft"
    if name in snap["contracts"] and snap["contracts"][name].get("address"):
        addr = snap["contracts"][name]["address"]
    elif name in snap.get("track_c", {}) and isinstance(snap["track_c"][name], dict):
        tc = snap["track_c"][name]
        addr = tc.get("sale") or tc.get("address")
        kind = "tc"
    if not addr:
        print("SKIP no-address", name, flush=True)
        continue
    items[name] = (addr, TC_VIEWS if (name.endswith("-sale") or kind == "tc") else NFT_VIEWS)

items["AgentX"] = ("0x59D96D8B4B82Abb350868E897F25F8e021360823", NFT_VIEWS)
items["PERSONA"] = ("0xA930C4466431B0331C911846f297D7D4e063249D", NFT_VIEWS)
items["Sourcify-new-857a"] = ("0x857aaFf19F716E7D7EC0231Bd6C0a8CD729fA84e", NFT_VIEWS)

def read_item(name, addr, views):
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1))
            key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER))
            key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, d, flush=True)
    return name, d

blk = block()
print("BLOCK", blk, "ITEMS", len(items), flush=True)
t0 = time.time()
out = {"block": blk, "contracts": {}}
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(read_item, n, a, v): n for n, (a, v) in items.items()}
    for fut in as_completed(futs):
        try:
            name, d = fut.result()
        except Exception as e:
            print("ERR", futs[fut], e, flush=True)
            continue
        out["contracts"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-reread.json", "w"), indent=1)
print("DONE in %.1fs block %s items %s" % (time.time() - t0, blk, len(out["contracts"])), flush=True)
