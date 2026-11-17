#!/usr/bin/env python3
"""Round-3 verify run 2026-11-09 0531 WIB — first-seen agent-shaped triage:
 LIFTCAT 0x53aA0c94 (10 mints), 0xc6ee7c22, 0x6D318F9e, 0x51D3C010 (S1, 1 mint each),
 0xCf8d6492 (5 mints, registry only), 0xF4F2A871 (1 mint, freePerWallet).
For each: Sourcify verifiedAt, name/symbol/totalSupply/free views/quote(user)/
owner (dataseed curl), plus ONE Ankr probe: any from-zero Transfer mint in
[132400000, first_block-1] (earlier-mint existence check, NOT a full first-mint proof).
Writes run-2026-11-09-0531-verify3.json.
"""
import json, subprocess, sys, time
sys.set_int_max_str_digits(100000)
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def eth_call(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(res, dict) and "result" in res:
                return res["result"]
        except Exception:
            continue
    return None

def call_int(addr, sig, args=""):
    return to_int(eth_call(addr, sel(sig) + args))
def call_addr(addr, sig):
    v = eth_call(addr, sel(sig))
    return ("0x" + v[-40:]) if v and len(v) >= 66 else None
def call_str(addr, sig, args=""):
    v = eth_call(addr, sel(sig) + args)
    try:
        if not v or v == "0x": return None
        b = bytes.fromhex(v[2:])
        if len(b) < 64: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off + 32], "big")
        return b[off + 32:off + 32 + ln].decode("utf-8", errors="replace")
    except Exception:
        return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

def sourcify_meta(addr):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "15",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=20)
        d = json.loads(r.stdout)
        return {"match": d.get("match"), "verifiedAt": d.get("verifiedAt")}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:120]}"}

def earlier_mints(addr, frm, to):
    try:
        res = ankr_post("ankr_getLogs", {
            "blockchain": "bsc", "address": addr,
            "fromBlock": str(frm), "toBlock": str(to),
            "topics": [TRANSFER, ZERO_TOPIC], "pageSize": 1000,
        }, timeout=55)
        logs = res.get("result", {}).get("logs", [])
        return {"any": len(logs) > 0, "count_page": len(logs)}
    except Exception as e:
        return {"any": None, "error": str(e)[:150]}

TARGETS = [
    ("LIFTCAT", "0x53aA0c94b9f670866a5EDbc42A66bf5cAB59c92a", 132475221),
    ("0xc6ee7c22", "0xc6ee7c22c5bDd919f5775ab38c53BD86c167D56f", 132475401),
    ("0x6D318F9e", "0x6D318F9e4147b7A9B1eC8196BA1799592e5ae44a", 132475524),
    ("0x51D3C010", "0x51D3C0101696956Baf928899D5BB57544F00C9B9", 132475903),
    ("0xCf8d6492", "0xCf8d64926c7299192794f6bbfe733A8f211Efe13", 132475207),
    ("0xF4F2A871", "0xF4F2A87100Bb8fECF562cF4cCaC6D615C424316c", 132475293),
]
out = {"run": "2026-11-09-0531", "block": get_block(), "targets": {}}
for label, addr, fb in TARGETS:
    d = {"address": addr, "first_block_in_window": fb}
    d["name"] = call_str(addr, "name()")
    d["symbol"] = call_str(addr, "symbol()")
    d["totalSupply"] = call_int(addr, "totalSupply()")
    d["totalMinted"] = call_int(addr, "totalMinted()")
    d["freeClaimed"] = call_int(addr, "freeClaimed()")
    d["freeMinted"] = call_int(addr, "freeMinted()")
    d["freeLeft"] = call_int(addr, "freeLeft()")
    d["FREE_SUPPLY"] = call_int(addr, "FREE_SUPPLY()")
    d["FREE_CAP"] = call_int(addr, "FREE_CAP()")
    d["MAX_SUPPLY"] = call_int(addr, "MAX_SUPPLY()")
    d["mintOpen"] = call_int(addr, "mintOpen()")
    d["balanceOf_user"] = call_int(addr, "balanceOf(address)", enc(USER))
    d["freeClaimed_user"] = call_int(addr, "freeClaimed(address)", enc(USER))
    d["owner"] = call_addr(addr, "owner()")
    d["sourcify"] = sourcify_meta(addr)
    d["earlier_mints_132400000_to_firstminus1"] = earlier_mints(addr, 132400000, fb - 1)
    out["targets"][label] = d
    print(label, json.dumps(d, default=str), flush=True)

json.dump(out, open(f"{HF}/run-2026-11-09-0531-verify3.json", "w"), indent=1)
print("VERIFY3 DONE block", out["block"])
