#!/usr/bin/env python3
"""JINLI 0x0f45... parent verification run 0701 (read-only).
1) single-call views (dataseed, lean - one call per batch so a revert only kills that view)
2) eth_getCode: registry-address bytes + free-mint selector scan
3) Ankr getLogs Transfer from zero address in the unscanned gap 132290411-132292962
   (3 chunks <=1000) to check whether any mint predates the in-window first mint 132292963.
"""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from ankr import ankr_post
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def single(method, params):
    for ep in EPS:
        try:
            return batch([(method, params)], endpoint=ep, timeout=10)[0]
        except Exception:
            continue
    return None

out = {"address": ADDR, "checked_wib": "2026-11-08 ~07:28 WIB"}
VIEWS = {"totalSupply": "totalSupply()", "totalMinted": "totalMinted()",
         "freeClaimed": "freeClaimed()", "freeMinted": "freeMinted()",
         "FREE_SUPPLY": "FREE_SUPPLY()", "MAX_SUPPLY": "MAX_SUPPLY()",
         "mintOpen": "mintOpen()", "owner": "owner()", "AGENT_ID": "AGENT_ID()",
         "agentRegistry": "agentRegistry()",
         "balanceOf_user": "balanceOf(address)",
         "quote_user1": "quote(address,uint256)",
         "freeLeft_user": "freeLeft(address)", "freeUsed_user": "freeUsed(address)",
         "mintedBy_user": "mintedBy(address)", "freeFor_user1": "freeFor(address,uint256)"}
for key, sig in VIEWS.items():
    if "(address)" in sig and "uint256" not in sig:
        data = sel(sig) + enc(USER)
    elif sig in ("quote(address,uint256)", "freeFor(address,uint256)"):
        data = sel(sig) + enc(USER) + "1".rjust(64, "0")
    else:
        data = sel(sig)
    v = single("eth_call", [{"to": ADDR, "data": data}, "latest"])
    if key in ("owner", "AGENT_ID", "agentRegistry"):
        out[key] = ("0x" + v[-40:]) if isinstance(v, str) and len(v) >= 42 else v
    else:
        out[key] = to_int(v) if isinstance(v, str) and v.startswith("0x") else v
    print(key, "=", out[key], flush=True)
    time.sleep(0.3)

# --- bytecode scan ---
code = single("eth_code", [ADDR, "latest"]) or single("eth_getCode", [ADDR, "latest"])
if isinstance(code, str):
    c = code.lower()
    out["code_len"] = (len(c) - 2) // 2
    out["registry_bytes_in_code"] = REGISTRY in c
    sels = {}
    for s in ["freeMint()", "freeMint(uint256)", "mintFree()", "freeClaimed()",
              "freeClaimed(address)", "freeMinted()", "freeLeft(address)",
              "freeFor(address,uint256)", "quote(address,uint256)",
              "mint(address,uint256)", "mint(uint256)", "claim()"]:
        sels[s] = sel(s)[2:] in c
    out["selectors_in_code"] = sels
    print("code_len =", out["code_len"], "registry_bytes =", out["registry_bytes_in_code"], flush=True)
    print("selectors:", {k: v for k, v in sels.items() if v}, flush=True)
else:
    out["code_len"] = None
    print("getCode FAILED", flush=True)

# --- gap getLogs: Transfer from zero address, contract = JINLI ---
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
def ankr_logs(from_block, to_block, topics, address=None, max_pages=10):
    logs = []; page_token = None; pages = 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(from_block),
                  "toBlock": hex(to_block), "pageSize": 1000,
                  "decodeLogs": False, "topics": topics}
        if address: params["address"] = address
        if page_token: params["pageToken"] = page_token
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                time.sleep(30); body = ankr_post("ankr_getLogs", params, timeout=30)
            else:
                raise
        result = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend(result.get("logs", []))
        page_token = result.get("nextPageToken")
        pages += 1
        if not page_token or pages >= max_pages:
            break
        time.sleep(2.2)
    return logs, pages

gap = []
for (f, t) in [(132290411, 132291410), (132291411, 132292410), (132292411, 132292962)]:
    try:
        logs, pages = ankr_logs(f, t, [TRANSFER, ZERO], address=ADDR.lower())
        print(f"gap chunk {f}-{t}: {len(logs)} Transfer-from-zero logs (pages {pages})", flush=True)
        gap.extend(logs)
    except Exception as e:
        print(f"gap chunk {f}-{t}: ERROR {e}", flush=True)
        gap.append({"error": str(e), "chunk": [f, t]})
out["gap_transfer_from_zero"] = gap
out["gap_mint_count_before_window"] = len([g for g in gap if isinstance(g, dict) and "blockNumber" in g])
if out["gap_mint_count_before_window"]:
    blocks = sorted(int(g["blockNumber"], 16) for g in gap if "blockNumber" in g)
    out["gap_earliest_mint_block"] = blocks[0]
    print("EARLIEST gap mint block:", blocks[0], flush=True)
try:
    out["block"] = int(single("eth_blockNumber", []) or "0x0", 16)
except Exception:
    pass
json.dump(out, open("run-2026-11-08-0701-jinli-verify.json", "w"), indent=1)
print("DONE block", out.get("block"))
