#!/usr/bin/env python3
"""Run 2001 triage: probe 3 true first-seen + 2 Sourcify near-passes; MERGEBORN first-mint (fixed topics). Read-only."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
RPCS = ["https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed1.bnbchain.org",
        "https://bsc.publicnode.com", "https://bsc-dataseed3.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=8):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception: continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def get_code(to):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                               "params": [to, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return json.load(r)["result"]
        except Exception: continue
    return None

def block_ts(blk):
    for rpc in RPCS:
        try:
            b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                            "params": [hex(blk), False]}).encode()
            req = urllib.request.Request(rpc, data=b, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"]["timestamp"], 16)
        except Exception: continue
    return None

def sourcify_plain(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{addr}",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r: d = json.load(r)
        return {"match": d.get("match"), "stdJson": bool(d.get("stdJson"))}
    except Exception as e:
        return {"error": str(e)[:150]}

def probe(addr, name):
    d = {"address": addr, "name": name}
    code = get_code(addr)
    d["code_len"] = len(code) - 2 if code else None
    d["registry_bytes"] = (REGISTRY[2:].lower() in code.lower()) if code else None
    d["sourcify_plain"] = sourcify_plain(addr)
    for sig in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "MAX_SUPPLY()",
                "FREE_SUPPLY()", "spotsLeft()", "mintOpen()", "paused()", "PRICE()", "mintPrice()",
                "agentRegistry()", "AGENT_ID()", "AGENT_REGISTRY()"]:
        d[sig] = call(addr, sig)
    d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
    d["freeClaimed_user"] = call(addr, "freeClaimed(address)", enc(USER))
    d["hasAgentId_user"] = call(addr, "hasAgentId(address)", enc(USER))
    d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
    d["costOf_user_1"] = call(addr, "costOf(address,uint256)", enc(USER) + enc_uint(1))
    print(name, json.dumps(d, default=str)[:1200], flush=True)
    return d

out = {}
for name, addr in [("Horus AI", "0x794aD67a5590C7e5848E49181297F9cC7C6CE00E"),
                   ("NestedNFT", "0xA9433C24aD72C0F513A69E02541aE09540c550a9"),
                   ("CuteWizard", "0x74C34496E469dd83991ea46AEbEfC59cF0A296D5"),
                   ("NearPass-1856", "0x185696fB3FFBe2ceDCaA85e3Ef6f75a9C7710ea3"),
                   ("NearPass-fe06", "0xfe06cFA0de86d21202a5f600027885fB5175230A")]:
    out[name] = probe(addr, name)

# MERGEBORN first-mint, FIXED topics: [Transfer, from=zero, to=contract]
M = "0x348455be18b700cae8aa425bd84e456e47f16e8b"
print("MERGEBORN sourcify_plain:", sourcify_plain(M), flush=True)
out["MERGEBORN_sourcify_plain"] = sourcify_plain(M)
topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
zero = "0x" + "00" * 32
to = "0x" + M[2:].lower().rjust(64, "0")
head = None
for rpc in RPCS:
    try:
        b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=b, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r: head = int(json.load(r)["result"], 16); break
    except Exception: continue
print("HEAD", head, flush=True)
end = head
found = None
for i in range(60):
    frm = max(0, end - 999)
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
            "toBlock": hex(end), "pageSize": 1000, "decodeLogs": False,
            "topics": [topic, zero, to]}, timeout=30)
        logs = body.get("result", {}).get("logs", [])
    except Exception as e:
        print(f"  chunk {frm}-{end} ERR {e}", flush=True)
        found = {"error": str(e)[:150], "searched_to": frm}
        break
    if logs:
        first = min(logs, key=lambda l: int(l["blockNumber"], 16))
        blk = int(first["blockNumber"], 16)
        found = {"first_block": blk, "first_ts": block_ts(blk), "n_logs_in_chunk": len(logs),
                 "searched_from": frm, "searched_to": end}
        break
    end = frm - 1
    if end <= 0:
        found = {"not_found_in_60000_blocks": True}
        break
print("MERGEBORN first mint:", found, flush=True)
out["MERGEBORN_first_mint"] = found
json.dump(out, open(f"{BASE}/run-2026-11-06-2001-triage.json", "w"), indent=1)
print("DONE", flush=True)
