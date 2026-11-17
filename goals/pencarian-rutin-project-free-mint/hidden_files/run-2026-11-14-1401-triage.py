#!/usr/bin/env python3
"""Boltbook-new triage for free-mint-search run 2026-11-14 14:01 WIB.
Read-only on-chain checks for 3 Boltbook-new contracts:
 CrossEyed 0x52903f070364ce6bb8d477c6751fa921079576b6 (crosseyed.app, 777 WL)
 Ledgera  0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d (2,324/5,555, 2,683 free left)
 MAMI     0xfe36c6d7a1e352cd0822c6818269d190e8e63c13 (Malware Mistletoe, #189)
Checks: Sourcify verified + ABI (registry/AgentGate/free-mint fns),
bytecode registry-bytes, name/symbol/supply/free views, user slot, owner,
Transfer-from-zero in last 2000 blocks via publicnode (first-mint evidence).
Writes run-2026-11-14-1401-triage.json. No preview/mint."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-rpc.publicnode.com/",
       "https://bsc-dataseed1.bnbchain.org/"]
t0 = time.time()
CONTRACTS = {
    "CrossEyed": "0x52903f070364ce6bb8d477c6751fa921079576b6",
    "Ledgera": "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
    "MAMI": "0xfe36c6d7a1e352cd0822c6818269d190e8e63c13",
}
VIEWS = [
    ("name", "name()", []), ("symbol", "symbol()", []),
    ("totalSupply", "totalSupply()", []), ("totalMinted", "totalMinted()", []),
    ("freeClaimed", "freeClaimed()", []), ("freeMinted", "freeMinted()", []),
    ("freeRemaining", "freeRemaining()", []), ("freeLeft", "freeLeft()", []),
    ("FREE_SUPPLY", "FREE_SUPPLY()", []), ("FREE_CAP", "FREE_CAP()", []),
    ("FREE_MAX", "FREE_MAX()", []), ("MAX_SUPPLY", "MAX_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []), ("price", "price()", []),
    ("costOf_user_1", "costOf(address,uint256)", [USER, 1]),
    ("priceFor_user", "priceFor(address)", [USER]),
    ("freeUsed_user", "freeUsed(address)", [USER]),
    ("mintedBy_user", "mintedBy(address)", [USER]),
    ("balanceOf_user", "balanceOf(address)", [USER]),
    ("owner", "owner()", []),
    ("AGENT_ID", "AGENT_ID()", []),
    ("agentRegistry", "agentRegistry()", []),
    ("mintStart", "mintStart()", []),
    ("genesisStart", "genesisStart()", []),
]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def get_url(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")

def sourcify(addr):
    try:
        raw = get_url(f"https://sourcify.dev/server/v2/contracts/56/{addr}?fields=abi,metadata", timeout=30)
        d = json.loads(raw)
        abi = d.get("abi") or (d.get("stdJson") or {}).get("abi") or []
        fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"]
        src = json.dumps(d)
        return {"verified": True, "fns": fns,
                "has_registry": REG in src.lower(),
                "has_free_fn": any(n in fns for n in
                    ["mintFree", "freeMint", "claimFree", "mint", "freeClaim", "claim"]),
                "has_quote": any(n in fns for n in ["costOf", "priceFor", "quote", "price", "getPrice"]),
                "has_free_view": any(n in fns for n in
                    ["freeClaimed", "freeMinted", "freeRemaining", "freeLeft", "freeSupply",
                     "freeUsed", "freeAvailable", "freeSharesRemaining", "FREE_SUPPLY", "FREE_CAP"])}
    except Exception as e:
        return {"verified": False, "error": str(e)[:200]}

def head_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=30)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

head = head_block()
out = {"started_wib": "2026-11-14T14:01+07:00", "head": head, "contracts": {}}
for name, addr in CONTRACTS.items():
    entry = {"address": addr}
    # bytecode registry bytes
    try:
        r = post_rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=30)
        code = (r.get("result") or "")
        entry["code_len"] = len(code)
        entry["registry_bytes_in_code"] = REG in code.lower()
    except Exception as e:
        entry["code_error"] = str(e)[:150]
    # Sourcify
    entry["sourcify"] = sourcify(addr)
    # views batch
    calls = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
              "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]}
             for i, (key, sig, args) in enumerate(VIEWS)]
    views = {}
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            for (key, sig, args), it in zip(VIEWS, res):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    views[key] = None
                else:
                    r = it["result"]
                    if key in ("name", "symbol"):
                        views[key] = r
                    else:
                        views[key] = to_int(r[:66]) if len(r) >= 66 else r
            entry["views_ep"] = ep
            break
        except Exception as e:
            entry.setdefault("views_errors", []).append(str(e)[:120])
    entry["views"] = views
    # Transfer-from-zero in last 2000 blocks (publicnode, topic0-only)
    try:
        logs = post_rpc("https://bsc-rpc.publicnode.com/",
            {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
             "params": [{"fromBlock": hex(head - 2000), "toBlock": hex(head), "address": addr,
                         "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                                    "0x0000000000000000000000000000000000000000000000000000000000000000"]}]},
            timeout=60)
        res = logs.get("result") if isinstance(logs, dict) else None
        if isinstance(res, list):
            entry["first_mints_2000blk"] = len(res)
            entry["first_mint_block"] = int(res[0]["blockNumber"], 16) if res else None
            minters = sorted({l["topics"][2][-40:] for l in res if len(l.get("topics", [])) > 2})
            entry["distinct_minters_2000blk"] = len(minters)
        else:
            entry["first_mints_2000blk"] = None
            entry["logs_error"] = str(logs)[:200]
    except Exception as e:
        entry["first_mints_2000blk"] = None
        entry["logs_error"] = str(e)[:200]
    out["contracts"][name] = entry
    print(name, json.dumps(entry)[:600], flush=True)
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-1401-triage.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
