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
    "Orbit Atlas": "0xd455a3963bb7ae70f6a52a66d0c4bda306dbddee",
    "Hakuna Agent": "0x75f9e01af66a6b3b5f169d1d9c88e6f356a01e2f",
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


# --- ABI agent-shape check (Orbit Atlas only; Hakuna Sourcify-unverified) ---
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
                "agent_gate_fn": any("agent" in n.lower() and "gate" in n.lower() for n in fns),
                "free_mint_fn": [n for n in fns if n.lower().startswith("mint") or "free" in n.lower()],
                "free_consts": [n for n in fns if n in ("FREE_SUPPLY","FREE_PER_WALLET","FREE_SLOTS","FREE_CAP","MAX_SUPPLY")],
                "fns": fns}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:100]}"}
out["Orbit Atlas"]["abi_shape"] = abi_shape("0xd455a3963bb7ae70f6a52a66d0c4bda306dbddee")
print("ABI_SHAPE", json.dumps(out["Orbit Atlas"]["abi_shape"]), flush=True)

# --- first-mint probe: eth_getLogs Transfer from zero, last 4000 blocks, 1000-block chunks (nodereal) ---
def getlogs_probe(addr):
    import urllib.request as u
    head = None
    try:
        req = u.Request("https://bsc.nodereal.io/", data=json.dumps({"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}).encode(), headers={"Content-Type":"application/json"})
        with u.urlopen(req, timeout=25) as r: head = int(json.loads(r.read())["result"], 16)
    except Exception as e:
        return {"error": f"head fail {type(e).__name__}: {str(e)[:80]}"}
    res = {"head": head, "chunks": []}
    zero = "0x0000000000000000000000000000000000000000000000000000000000000000"
    topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    for i in range(4):
        to_b = head - i*1000; from_b = to_b - 999
        payload = {"jsonrpc":"2.0","method":"eth_getLogs","params":[{"fromBlock":hex(from_b),"toBlock":hex(to_b),"address":addr,"topics":[topic, zero]}],"id":1}
        try:
            req = u.Request("https://bsc.nodereal.io/", data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
            with u.urlopen(req, timeout=25) as r: body = json.loads(r.read())
            logs = body.get("result", [])
            res["chunks"].append({"from": from_b, "to": to_b, "n": len(logs) if isinstance(logs, list) else "ERR", "err": body.get("error")})
            if isinstance(logs, list) and logs:
                res["first_mint_block"] = int(logs[0]["blockNumber"], 16)
                break
        except Exception as e:
            res["chunks"].append({"from": from_b, "to": to_b, "error": f"{type(e).__name__}: {str(e)[:100]}"})
            break
    return res
out["Orbit Atlas"]["first_mint_probe"] = getlogs_probe("0xd455a3963bb7ae70f6a52a66d0c4bda306dbddee")
print("FIRST_MINT_PROBE", json.dumps(out["Orbit Atlas"]["first_mint_probe"]), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-10-1401-new-verify.json", "w"), indent=1)
print("DONE")
