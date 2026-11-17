#!/usr/bin/env python3
"""Run 2001 deep-dive: MERGEBORN age+slot+shape, WeZards/BOBBIE verify, new-name shape checks.
Read-only. Uses public RPCs for eth_call and Ankr module for first-mint getLogs.
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed1.bnbchain.org",
        "https://bsc.publicnode.com", "https://bsc-dataseed3.bnbchain.org",
        "https://bsc-dataseed.binance.org"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

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
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

def sourcify(addr):
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contracts/56/{addr}?fields=metadata",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r: d = json.load(r)
        abi = d.get("metadata", {}).get("output", {}).get("abi", [])
        return {"match": d.get("match"), "n_fns": len([f for f in abi if f.get("type") == "function"]),
                "fns": sorted({f["name"] for f in abi if f.get("type") == "function"})}
    except Exception as e:
        return {"error": str(e)[:200]}

def first_mint(addr, head):
    """Walk back in 1000-block chunks via Ankr getLogs (Transfer to contract, from zero)."""
    topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    zero = "0x" + "00" * 32
    to = "0x" + addr[2:].lower().rjust(64, "0")
    end = head
    for i in range(40):
        frm = max(0, end - 999)
        try:
            body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
                "toBlock": hex(end), "pageSize": 1000, "decodeLogs": False,
                "topics": [topic, zero, None, to]}, timeout=30)
            logs = body.get("result", {}).get("logs", [])
        except Exception as e:
            print(f"  firstmint chunk {frm}-{end} ERR {e}", flush=True)
            return {"error": str(e)[:150], "searched_to": frm}
        if logs:
            first = min(logs, key=lambda l: int(l["blockNumber"], 16))
            blk = int(first["blockNumber"], 16)
            # block timestamp
            ts = None
            for rpc in RPCS:
                try:
                    b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                    "params": [hex(blk), False]}).encode()
                    req = urllib.request.Request(rpc, data=b, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=8) as r: ts = int(json.load(r)["result"]["timestamp"], 16)
                    break
                except Exception: continue
            return {"first_block": blk, "first_ts": ts, "n_logs_in_chunk": len(logs),
                    "searched_from": frm, "searched_to": end}
        end = frm - 1
        if end <= 0: break
    return {"not_found_in_40000_blocks": True, "searched_to": end}

out = {}
head = block()
print("HEAD", head, flush=True)
out["head"] = head

# ---- MERGEBORN ----
M = "0x348455be18b700cae8aa425bd84e456e47f16e8b"
print("== MERGEBORN ==", flush=True)
m = {}
m["sourcify"] = sourcify(M)
print(" sourcify:", json.dumps(m["sourcify"])[:600], flush=True)
for sig in ["freeMinted()", "totalMinted()", "totalSupply()", "MAX_SUPPLY()", "FREE_SUPPLY()",
            "freeSupply()", "mintOpen()", "paused()", "mintPrice()", "PRICE()"]:
    m[sig] = call(M, sig)
for sig in ["freeClaimed(address)", "freeUsed(address)", "freeMintedBy(address)", "mintedBy(address)",
            "hasClaimedFree(address)", "claimedFree(address)", "canFreeMint(address)", "eligible(address)",
            "freeFor(address)", "freeLeft(address)"]:
    m[sig + "_user"] = call(M, sig, enc(USER))
for sig in ["quote(address,uint256)", "costOf(address,uint256)", "mintCost(address,uint256)"]:
    m[sig + "_user_1"] = call(M, sig, enc(USER) + enc_uint(1))
print(" views:", json.dumps(m, default=str)[:1500], flush=True)
out["MERGEBORN"] = m
print(" first-mint walk...", flush=True)
out["MERGEBORN_first_mint"] = first_mint(M, head)
print(" first mint:", out["MERGEBORN_first_mint"], flush=True)

# ---- WeZards verify ----
W = "0xe4d7Ec33Fcf7D93cBE7F4D46d0ef35F437956aab"
print("== WeZards ==", flush=True)
w = {}
for sig in ["totalMinted()", "totalSupply()", "remainingFreeAllocation()", "freeClaimed()",
            "freeMinted()", "MAX_SUPPLY()", "mintOpen()", "FREE_SUPPLY()"]:
    w[sig] = call(W, sig)
w["hasClaimedFree_user"] = call(W, "hasClaimedFree(address)", enc(USER))
w["balanceOf_user"] = call(W, "balanceOf(address)", enc(USER))
print(" views:", json.dumps(w, default=str), flush=True)
out["WeZards"] = w

# ---- BOBBIE verify ----
B = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
print("== BOBBIE ==", flush=True)
b = {}
b["sourcify"] = sourcify(B)
for sig in ["totalMinted()", "totalSupply()", "freeClaimed()", "freeMinted()", "MAX_SUPPLY()",
            "FREE_SUPPLY()", "spotsLeft()", "mintOpen()", "paused()", "PRICE()"]:
    b[sig] = call(B, sig)
b["mintedBy_user"] = call(B, "mintedBy(address)", enc(USER))
b["quote_user_1"] = call(B, "quote(address,uint256)", enc(USER) + enc_uint(1))
print(" views:", json.dumps(b, default=str)[:1200], flush=True)
out["BOBBIE"] = b

# ---- New names: TOPA / Sidecoo / AgentVOLT shape ----
for name, addr in [("TOPA", "0xd9cc8c95da13b0600df1b3f6879a1892a0631392"),
                   ("Sidecoo", "0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8"),
                   ("AgentVOLT-real", "0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771"),
                   ("AgentVOLT-lookalike", "0xc58e00000000000000000000000000000000000000")]:
    if addr.endswith("00"*20):
        out[name] = {"skipped": "address incomplete in post (0xc58e... truncated)"}
        continue
    print(f"== {name} ==", flush=True)
    d = {"sourcify": sourcify(addr)}
    fns = set(d["sourcify"].get("fns", []))
    d["agent_gate_words"] = [f for f in fns if any(w in f.lower() for w in
        ["agentid", "agent_id", "agentregistry", "agent_registry", "agentgate", "agent_gate", "hasagentid", "isagent"])]
    d["free_views"] = [f for f in fns if "free" in f.lower()]
    for sig in ["totalMinted()", "totalSupply()", "freeClaimed()", "freeMinted()", "MAX_SUPPLY()",
                "FREE_SUPPLY()", "mintOpen()", "paused()"]:
        d[sig] = call(addr, sig)
    d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
    d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
    print(f" {name}:", json.dumps(d, default=str)[:1200], flush=True)
    out[name] = d

json.dump(out, open(f"{BASE}/run-2026-11-06-2001-deepdive.json", "w"), indent=1)
print("DONE", flush=True)
