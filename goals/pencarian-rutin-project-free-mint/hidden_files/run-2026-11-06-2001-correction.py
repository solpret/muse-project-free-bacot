#!/usr/bin/env python3
"""Run 2001 correction pass: correct Sourcify path (v2/contract singular) + registry bytes via
fast_rpc + MERGEBORN first-mint with CORRECT filter (address=contract, topics=[Transfer, zero]).
Read-only."""
import json, sys, subprocess, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed2.bnbchain.org", "https://bsc-dataseed1.bnbchain.org",
       "https://bsc.publicnode.com", "https://bsc-dataseed3.bnbchain.org"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")

def raw(to, data, timeout=8):
    for rpc in EPS:
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

def sourcify(addr):
    # curl first (per subagent B: ?fields=metadata works), path SINGULAR /contract/
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=metadata"],
            capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            d = json.loads(r.stdout)
            abi = d.get("metadata", {}).get("output", {}).get("abi", [])
            fns = sorted({f["name"] for f in abi if isinstance(f, dict) and f.get("type") == "function"})
            return {"match": d.get("match"), "n_fns": len(fns), "fns": fns}
        return {"error": f"curl rc={r.returncode} empty"}
    except Exception as e:
        return {"error": str(e)[:150]}

def registry_bytes(addr):
    for ep in EPS:
        try:
            code = _single(ep, "eth_getCode", [addr, "latest"], 8, retries=0)
            if isinstance(code, str) and len(code) > 2:
                return REGISTRY[2:].lower() in code[2:].lower()
            return None
        except Exception:
            continue
    return None

TARGETS = [("Horus AI", "0x794aD67a5590C7e5848E49181297F9cC7C6CE00E"),
           ("MERGEBORN", "0x348455be18b700cae8aa425bd84e456e47f16e8b"),
           ("TOPA", "0xd9cc8c95da13b0600df1b3f6879a1892a0631392"),
           ("Sidecoo", "0x409Cfe3747f1ac20f267B50BCbB6a4E9406DA3a8"),
           ("AgentVOLT-real", "0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771"),
           ("CuteWizard", "0x74C34496E469dd83991ea46AEbEfC59cF0A296D5"),
           ("NestedNFT", "0xA9433C24aD72C0F513A69E02541aE09540c550a9"),
           ("NearPass-1856", "0x185696fB3FFBe2ceDCaA85e3Ef6f75a9C7710ea3"),
           ("NearPass-fe06", "0xfe06cFA0de86d21202a5f600027885fB5175230A")]
GATE_WORDS = ["agentid", "agent_id", "agentregistry", "agent_registry", "agentgate", "agent_gate", "hasagentid", "isagent"]
out = {}
for name, addr in TARGETS:
    s = sourcify(addr)
    fns = s.get("fns", [])
    d = {"address": addr, "sourcify_match": s.get("match"), "n_fns": s.get("n_fns"),
         "error": s.get("error"),
         "gate_fns": [f for f in fns if any(g in f.lower() for g in GATE_WORDS)],
         "free_fns": [f for f in fns if "free" in f.lower()],
         "mint_fns": [f for f in fns if "mint" in f.lower()],
         "quote_fns": [f for f in fns if f.lower().startswith(("quote", "cost")) or f.lower() in ("price",)],
         "registry_bytes": registry_bytes(addr)}
    print(name, json.dumps(d, default=str)[:800], flush=True)
    out[name] = d

# MERGEBORN first mint: address=contract + topics [Transfer, from=zero]
M = "0x348455be18b700cae8aa425bd84e456e47f16e8b"
head = None
for rpc in EPS:
    try:
        b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
        req = urllib.request.Request(rpc, data=b, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as r: head = int(json.load(r)["result"], 16); break
    except Exception: continue
print("HEAD", head, flush=True)
topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
zero = "0x" + "00" * 32
end = head
found = None
for i in range(80):
    frm = max(0, end - 999)
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(frm),
            "toBlock": hex(end), "address": M, "pageSize": 1000, "decodeLogs": False,
            "topics": [topic, zero]}, timeout=30)
        logs = body.get("result", {}).get("logs", [])
    except Exception as e:
        print(f"  chunk {frm}-{end} ERR {e}", flush=True)
        found = {"error": str(e)[:150], "searched_to": frm}
        break
    if logs:
        first = min(logs, key=lambda l: int(l["blockNumber"], 16))
        blk = int(first["blockNumber"], 16)
        ts = None
        for rpc in EPS:
            try:
                b = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                                "params": [hex(blk), False]}).encode()
                req = urllib.request.Request(rpc, data=b, headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=8) as r: ts = int(json.load(r)["result"]["timestamp"], 16)
                break
            except Exception: continue
        found = {"first_block": blk, "first_ts": ts, "n_logs_in_chunk": len(logs),
                 "searched_from": frm, "searched_to": end}
        break
    end = frm - 1
    if end <= 0:
        found = {"not_found_in_80000_blocks": True}
        break
print("MERGEBORN first mint (fixed):", found, flush=True)
out["MERGEBORN_first_mint_fixed"] = found
# Horus AI free-path re-probe (quote variants + freeClaimed views that triage may have missed)
H = "0x794aD67a5590C7e5848E49181297F9cC7C6CE00E"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
h = {}
for sig in ["freeMinted()", "freeClaimed()", "totalMinted()", "totalSupply()", "mintOpen()"]:
    h[sig] = call(H, sig)
h["freeClaimed_user"] = call(H, "freeClaimed(address)", enc(USER))
h["freeUsed_user"] = call(H, "freeUsed(address)", enc(USER))
h["canFreeMint_user"] = call(H, "canFreeMint(address)", enc(USER))
h["quote_user_1"] = call(H, "quote(address,uint256)", enc(USER) + format(1, "064x"))
h["costOf_user_1"] = call(H, "costOf(address,uint256)", enc(USER) + format(1, "064x"))
print("Horus re-probe:", json.dumps(h, default=str), flush=True)
out["Horus_reprobe"] = h
json.dump(out, open(f"{BASE}/run-2026-11-06-2001-correction.json", "w"), indent=1)
print("DONE", flush=True)
