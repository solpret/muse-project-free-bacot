#!/usr/bin/env python3
"""Run 1401 Boltbook-new-contract verification (read-only).
Reads name/symbol/supply/free views/owner/registry + user slot via dataseed curl,
Sourcify match status, and owner vs same-owner-discards.json.
Writes run-2026-11-10-1401-new-verify.json."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
CANDS = {
    "ELSY AGENT": "0x9e2c16ee581e0d4f0a36ae70205c5599bbb9b22f",
}
VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeMinted()",
         "freeClaimed()", "freeLeft()", "paidMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
         "FREE_PER_WALLET()", "MAX_PER_WALLET()", "mintOpen()", "owner()",
         "agentRegistry()", "registry()", "AGENT_ID_REGISTRY()", "price()", "costOf()",
         "mintStart()", "freeStart()", "startTime()", "launched()", "freeClaimed(address)",
         "balanceOf(address)", "freeMinted(address)", "mintedBy(address)", "agentIdClaimed(uint256)"]

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
            headers={"User-Agent": "free-bacot/1401"})
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


# --- ABI agent-shape check ---
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
def abi_shape(addr):
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
            headers={"User-Agent": "free-bacot/1401"})
        with urllib.request.urlopen(req, timeout=30) as r:
            m = json.loads(r.read().decode())
        abi = m.get("abi", [])
        fns = [e.get("name","") for e in abi if e.get("type")=="function"]
        blob = json.dumps(abi).lower()
        return {"abi_len": len(abi),
                "registry_ref": REG in blob,
                "agent_gate_fn": [n for n in fns if "agent" in n.lower()],
                "mint_fns": [n for n in fns if n.lower().startswith("mint") or "free" in n.lower()],
                "time_views": [n for n in fns if any(w in n.lower() for w in ("start","launch","time","deadline","end"))],
                "fns": fns}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:100]}"}
out["ELSY AGENT"]["abi_shape"] = abi_shape("0x9e2c16ee581e0d4f0a36ae70205c5599bbb9b22f")
print("ABI_SHAPE", json.dumps(out["ELSY AGENT"]["abi_shape"]), flush=True)
# --- contractURI / tokenURI(1) pointer check (methods H/I) ---
def call0(addr, sig):
    import subprocess as sp
    k = keccak.new(digest_bits=256); k.update(sig.encode()); data = "0x" + k.hexdigest()[:8]
    for ep in EPS:
        try:
            o = sp.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})],capture_output=True,text=True,timeout=30).stdout
            r=json.loads(o).get("result")
            if r and r!="0x": return r
        except Exception: continue
    return None
for sig in ["contractURI()", "tokenURI(uint256)"]:
    raw = call0("0x9e2c16ee581e0d4f0a36ae70205c5599bbb9b22f", sig) if sig=="contractURI()" else None
    print("POINTER", sig, (raw or "")[:200], flush=True)
    out["ELSY AGENT"]["pointer_"+sig] = raw

json.dump(out, open(f"{BASE}/run-2026-11-10-1401-elsy-verify.json", "w"), indent=1)
print("DONE")
