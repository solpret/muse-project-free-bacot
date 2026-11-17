#!/usr/bin/env python3
"""Triage for free-mint-search run 2026-11-16 02:01 WIB.
New-to-this-job contracts:
- Voxel World Pixel 0x097E34c0A1657537aA0D94d171D39AB3954Fee57 (Boltbook front page EN+ZH + Sourcify feed verifiedAt 18:55:00Z; ~693-695/1000 free per Boltbook)
- 0x2664bbc1BDc9F079243adCb41Db5E2B2eB3b2FD2 (Sourcify feed newest verifiedAt 19:06:48Z; not in hot-leg-seen)
Plus Pacture 0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9 sold-out verification (Boltbook: sharesMinted 11,000/11,000, soldOut=1).
Read-only; no preview/mint. Writes run-2026-11-16-0201-triage.json.
"""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))
        else:
            d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def get_url(url, timeout=60):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 10)
    return r.stdout

U = [USER]
ITEMS = {
 "VoxelWorldPixel": ("0x097E34c0A1657537aA0D94d171D39AB3954Fee57", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintStart","mintStart()",[]),
    ("mintEnd","mintEnd()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U),
    ("owner","owner()",[]),("AGENT_ID","AGENT_ID()",[]),
    ("agentRegistry","agentRegistry()",[])]),
 "Pacture": ("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", [
    ("sharesMinted","sharesMinted()",[]),("soldOut","soldOut()",[]),
    ("freeMinted","freeMinted()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("mintedBy_user","mintedBy(address)",U)]),
}

def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                print("  chunk ep", ep, "bad shape", str(res)[:120], flush=True); continue
            out = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    out.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out, ep
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    return None, None

reads = {}
for name, item in ITEMS.items():
    r, ep = read_chunk([(name, item)])
    reads[name] = {"address": item[0], "views": r.get(name) if r else None, "via": ep}
    print(name, "via", ep, json.dumps(reads[name]["views"]), flush=True)

# Sourcify ABI shape-check for Voxel + 0x2664
def sourcify_shape(addr):
    out = {"address": addr}
    try:
        raw = get_url(f"https://sourcify.dev/server/v2/contracts/56/{addr}", timeout=60)
        j = json.loads(raw)
        out["match"] = j.get("match")
        std = j.get("stdJson", {})
        srcs = std.get("sources", {})
        blob = json.dumps(std)[:200000]
        abi = []
        for s in std.get("output", {}).get("contracts", {}).values():
            for c in s.values():
                abi = c.get("abi", abi)
        fns = sorted({e.get("name") for e in abi if isinstance(e, dict) and e.get("type") == "function" and e.get("name")})
        out["fns"] = fns
        out["registry_bytes"] = REGISTRY in blob.lower()
        out["has_mint"] = any(f.startswith("mint") for f in fns)
        out["has_quote"] = any(("quote" in f or "cost" in f or "price" in f.lower()) for f in fns)
        out["has_free_view"] = any(("free" in f.lower()) for f in fns)
        out["has_agent"] = any(("agent" in f.lower()) for f in fns)
        out["has_token_shape"] = all(x in fns for x in ("name", "symbol", "decimals", "totalSupply"))
    except Exception as e:
        out["error"] = str(e)[:200]
    return out

shapes = {}
for a in ["0x097E34c0A1657537aA0D94d171D39AB3954Fee57",
          "0x2664bbc1BDc9F079243adCb41Db5E2B2eB3b2FD2"]:
    shapes[a] = sourcify_shape(a)
    print("SHAPE", a, json.dumps(shapes[a])[:1200], flush=True)

blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
        if isinstance(r, dict) and r.get("result"): blk = int(r["result"], 16); break
    except Exception: continue
out = {"started_wib": "2026-11-16T02:01+07:00", "reads": reads, "shapes": shapes,
       "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-16-0201-triage.json", "w"), indent=1)
print("DONE block", blk, "elapsed", round(time.time() - t0, 1))
