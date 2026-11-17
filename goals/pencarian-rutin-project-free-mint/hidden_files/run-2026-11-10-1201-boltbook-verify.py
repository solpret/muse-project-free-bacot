#!/usr/bin/env python3
"""Run 1201 focused verify: Thetavox / Sora Agent / Kora Agent (Boltbook front page 12:06 WIB).
Read-only. Writes run-2026-11-10-1201-boltbook-verify.json + .log lines."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
TARGETS = {
    "Thetavox": "0x37d39fcc21addbb753e9366216e494d7956bd859",
    "SoraAgent": "0x5aaa9dcae9d548cf7118b1d2c21be27313f1ae1d",
    "KoraAgent": "0x5c32d38ca59cdc469cd7f064a41f3b845614bd2b",
}
VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeClaimed()",
         "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()",
         "owner()", "balanceOf(address)", "freeClaimed(address)",
         "freeMinted(address)", "priceFor(uint256)", "quote(address,uint256)",
         "agentRegistry()", "agentId()", "contractURI()"]
T0 = time.time()

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

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

def decode_str(hexstr):
    try:
        b = bytes.fromhex(hexstr[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

def read_contract(addr):
    calls, keys = [], []
    for i, sig in enumerate(VIEWS):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        elif "(uint256)" in sig:
            data = sel(sig) + "0"*63 + "1"; key = base + "_1"
        elif "(address,uint256)" in sig:
            data = sel(sig) + enc(USER) + "0"*63 + "1"; key = base + "_user1"
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
                if not isinstance(item, dict) or "error" in item:
                    outd[key] = None
                else:
                    raw = item.get("result")
                    if key in ("name", "symbol", "contractURI"):
                        outd[key] = decode_str(raw) if raw else None
                    elif key in ("owner", "agentRegistry", "agentId"):
                        outd[key] = ("0x" + raw[-40:]) if raw and len(raw) >= 42 else raw
                    else:
                        outd[key] = to_int(raw)
            outd["_ep"] = ep
            return outd
        except Exception:
            continue
    return {"_batch_fail": True}

def sourcify(addr):
    for url in [f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                f"https://sourcify.dev/server/v2/contract/56/{addr}"]:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1201"})
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode())
            abi = d.get("abi") or []
            fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
            return {"verified": True, "match": d.get("match"), "verifiedAt": d.get("verifiedAt"),
                    "fns": fns}
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:100]}"
    return {"verified": False, "error": last}

out = {"block": get_block(), "targets": {}}
print("BLOCK", out["block"], flush=True)
discards = set()
try:
    dj = json.load(open(f"{BASE}/same-owner-discards.json"))
    discards = {str(x).lower() for x in (dj if isinstance(dj, list) else dj.get("owners", []))}
except Exception as e:
    print("discards read fail:", e, flush=True)

for name, addr in TARGETS.items():
    t = time.time()
    reads = read_contract(addr)
    sc = sourcify(addr)
    out["targets"][name] = {"address": addr, "reads": reads, "sourcify": sc}
    owner = (reads.get("owner") or "").lower()
    print(f"{name} {addr} owner={reads.get('owner')} in_discards={owner in discards} "
          f"totalSupply={reads.get('totalSupply')} freeClaimed={reads.get('freeClaimed')} "
          f"freeMinted={reads.get('freeMinted')} FREE_SUPPLY={reads.get('FREE_SUPPLY')} "
          f"MAX={reads.get('MAX_SUPPLY')} open={reads.get('mintOpen')} bal_user={reads.get('balanceOf_user')} "
          f"freeClaimed_user={reads.get('freeClaimed_user')} priceFor1={reads.get('priceFor_1')} "
          f"quote_user1={reads.get('quote_user1')} contractURI={str(reads.get('contractURI'))[:120]} "
          f"sourcify_verified={sc.get('verified')} ({time.time()-t:.1f}s)", flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-10-1201-boltbook-verify.json", "w"), indent=1)
print(f"DONE in {time.time()-T0:.1f}s", flush=True)
