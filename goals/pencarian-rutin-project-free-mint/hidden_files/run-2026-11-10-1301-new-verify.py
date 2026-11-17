#!/usr/bin/env python3
"""Run 1301 Boltbook-new-contract verification (read-only).
Reads name/symbol/supply/free views/owner/registry + user slot via dataseed curl,
Sourcify match status, and owner vs same-owner-discards.json.
Writes run-2026-11-10-1301-new-verify.json."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
CANDS = {
    "NOVA AGENT (NOGENT)": "0x1b6e6f62528de674c12bc2c04c159336d3db049e",
    "Cinder Agents": "0x49966cf050a5a9cedd252184875267c0e93dbc00",
    "Pickgrid Pickaxe": "0x7f541bcc33abed0e64455565da723e949c6f76f0",
    "PanduAGENT Phase 2": "0x9e5dd59b5df1d36de02454a1fd6d77ee5b07778b",
    "Pixel Relay": "0x8f41960b7a6e6fb2423a426491d8a5ca6386ef47",
    "Binance Fleet Genesis": "0x5bc4fb61270c2628c93bf507c4ba125b868d34ff",
}
VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeMinted()",
         "freeClaimed()", "paidMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
         "FREE_PER_WALLET()", "MAX_PER_WALLET()", "mintOpen()", "owner()",
         "agentRegistry()", "registry()", "price()", "freeClaimed(address)",
         "balanceOf(address)", "freeMinted(address)"]

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

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                if isinstance(item, dict) and "error" in item:
                    outd[key] = None
                elif isinstance(item, dict):
                    outd[key] = item.get("result")
                else:
                    outd[key] = None
            return outd
        except Exception:
            continue
    return None

def decode_str(hexv):
    try:
        if not hexv or hexv == "0x": return None
        b = bytes.fromhex(hexv[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[64:96], "big")
        if off + 32 + ln > len(b) or ln > 200: return None
        return b[96:96+ln].decode("utf-8", errors="ignore") or None
    except Exception:
        return None

def sourcify(addr):
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contract/56/{addr}",
            headers={"User-Agent": "free-bacot/1301"})
        with urllib.request.urlopen(req, timeout=30) as r:
            m = json.loads(r.read().decode())
        return m.get("stdJson", {}).get("match") or m.get("match") or "verified?"
    except Exception as e:
        return f"ERR {type(e).__name__}: {str(e)[:80]}"

disc = json.load(open(f"{BASE}/same-owner-discards.json"))
disc_owners = {str(x.get("owner","")).lower() for x in disc if isinstance(x, dict)}
disc_contracts = {str(x.get("contract","")).lower() for x in disc if isinstance(x, dict)}

out = {}
for name, addr in CANDS.items():
    got = raw_batch(addr, VIEWS)
    d = {"address": addr}
    if got is None:
        d["_batch_fail"] = True
    else:
        for k, v in got.items():
            if k in ("name", "symbol"):
                d[k] = decode_str(v)
            elif k in ("owner", "agentRegistry", "registry"):
                d[k] = ("0x" + v[-40:]) if v and len(v) >= 42 else v
            else:
                d[k] = to_int(v)
    d["sourcify"] = sourcify(addr)
    o = str(d.get("owner") or "").lower()
    d["owner_in_discards"] = o in disc_owners if o else None
    d["contract_in_discards"] = addr.lower() in disc_contracts
    out[name] = d
    print(json.dumps(d), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-10-1301-new-verify.json", "w"), indent=1)
print("DONE")
