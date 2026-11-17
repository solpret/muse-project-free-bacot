#!/usr/bin/env python3
"""Probe run 2026-11-11 15:31 WIB: AgentRune (Boltbook new) + 0xB756 (feed early-shape).
Read-only: Sourcify ABI + bytecode registry grep + on-chain views + contractURI/tokenURI + owner + discards.
No preview, no mint (early leads are never previewed/minted)."""
import json, subprocess, urllib.request, sys
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
TARGETS = {
    "AgentRune": "0xc1fc0bb36d2be928809e4b3e6aa94b3dd2946f53",
    "0xB756": "0xB756267d8932b5d0c74CA49FC455309317b7B0B4",
}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None

def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

def eth_call(to, data, timeout=25):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": to, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                               capture_output=True, text=True, timeout=timeout + 5)
            res = json.loads(r.stdout)
            if isinstance(res, dict) and "result" in res:
                return res["result"]
        except Exception:
            continue
    return None

def batch_call(to, views):
    calls = []
    for i, sig in enumerate(views):
        data = sel(sig) + (enc(USER) if "(address)" in sig else "")
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": to, "data": data}, "latest"]})
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(calls)],
                               capture_output=True, text=True, timeout=30)
            res = json.loads(r.stdout)
            if isinstance(res, list) and len(res) == len(calls):
                return res
        except Exception:
            continue
    return None

def dec_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 96: return None
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode(errors="replace")
    except Exception:
        return None

VIEWS = ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "mintActive()",
         "mintStart()", "startTime()", "priceFor(address)", "quote(address,uint256)",
         "freeUsed(address)", "freeClaimed(address)", "freeTakenBy(address)",
         "balanceOf(address)", "owner()", "contractURI()", "name()", "symbol()",
         "agentRegistry()", "agentIdRegistry()", "freeLeft()", "status()"]

disc = json.load(open(BASE + "same-owner-discards.json"))
disc_addrs = set()
if isinstance(disc, list):
    disc_addrs = {str(x).lower() for x in disc if isinstance(x, str)}
elif isinstance(disc, dict):
    for v in disc.values():
        if isinstance(v, dict):
            for kk in ("address", "owner", "deployer"):
                if v.get(kk): disc_addrs.add(str(v[kk]).lower())
        elif isinstance(v, str):
            disc_addrs.add(v.lower())

out = {}
for name, addr in TARGETS.items():
    d = {"address": addr, "started_wib": "2026-11-11 15:31 WIB"}
    # 1. Sourcify
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi,metadata"))
        abi = meta.get("abi", [])
        fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
        d["sourcify"] = {"verified": True, "match": meta.get("match"), "fn_count": len(fns), "fns": fns}
        print(f"[{name}] SOURCIFY verified match={meta.get('match')} fns={len(fns)}", flush=True)
    except Exception as e:
        d["sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:150]}"}
        print(f"[{name}] SOURCIFY FAIL {e}", flush=True)
    # 2. bytecode registry grep
    try:
        code = eth_call(addr, "") if False else None
        payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]}
        for ep in EPS:
            try:
                r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                    "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                                   capture_output=True, text=True, timeout=30)
                res = json.loads(r.stdout)
                if isinstance(res, dict) and "result" in res:
                    code = res["result"]; break
            except Exception:
                continue
        if code:
            d["bytecode_len"] = (len(code) - 2) // 2
            d["registry_in_bytecode"] = REGISTRY[2:].lower() in code.lower()
            print(f"[{name}] bytecode {d['bytecode_len']} bytes registry_in_bytecode={d['registry_in_bytecode']}", flush=True)
    except Exception as e:
        d["bytecode"] = {"error": str(e)[:120]}
    # 3. views
    raw = batch_call(addr, VIEWS)
    vals = {}
    if raw is not None:
        for sig, item in zip(VIEWS, raw):
            key = sig.split("(")[0] + ("_user" if "(address)" in sig else "")
            res = item.get("result") if isinstance(item, dict) else None
            if res is None or res == "0x" or (isinstance(item, dict) and "error" in item):
                vals[key] = None
            else:
                vals[key] = res
        for k in ("contractURI", "name", "symbol"):
            if vals.get(k):
                vals[k + "_decoded"] = dec_str(vals[k])
        for k, v in list(vals.items()):
            if v and k not in ("owner", "agentRegistry", "agentIdRegistry", "contractURI", "name", "symbol") and not k.endswith("_decoded"):
                iv = to_int(v)
                if iv is not None:
                    vals[k + "_int"] = iv
        for k in ("owner", "agentRegistry", "agentIdRegistry"):
            if vals.get(k):
                vals[k + "_addr"] = "0x" + vals[k][-40:]
        d["views"] = vals
        print(f"[{name}] views:", json.dumps({k: v for k, v in vals.items() if k.endswith('_int') or k.endswith('_decoded') or k.endswith('_addr')}, indent=0), flush=True)
    else:
        d["views"] = {"error": "all RPC endpoints failed"}
        print(f"[{name}] VIEWS FAIL", flush=True)
    # 4. tokenURI(1)
    try:
        data = sel("tokenURI(uint256)") + format(1, "064x")
        res = eth_call(addr, data)
        d["tokenURI_1"] = dec_str(res) if res else None
        print(f"[{name}] tokenURI(1):", (d["tokenURI_1"] or "")[:200], flush=True)
    except Exception as e:
        d["tokenURI_1"] = None
    # 5. discards
    owner = (d.get("views") or {}).get("owner_addr")
    d["discards"] = {"contract_in_discards": addr.lower() in disc_addrs,
                     "owner": owner,
                     "owner_in_discards": (owner.lower() in disc_addrs) if owner else None}
    print(f"[{name}] DISCARDS:", d["discards"], flush=True)
    out[name] = d

json.dump(out, open(BASE + "run-2026-11-11-1531-probe.json", "w"), indent=1)
print("PROBE DONE", flush=True)
