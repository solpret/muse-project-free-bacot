#!/usr/bin/env python3
"""Verify 4 new Boltbook contracts, free-mint-search run 2026-11-15 14:01 WIB.
Frost Agent, Wuyuhive, VOXEL, Punch In Whitelist Pass.
Read-only: Sourcify ABI shape + on-chain views via eth_call batch. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
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
def get(url, timeout=60):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 10)
    return r.stdout

ITEMS = {
 "Frost Agent": ("0x09f893bab23d14ad296a17092c6611aac5a0932b", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),
    ("freeLeft","freeLeft()",[]),("mintOpen","mintOpen()",[]),
    ("price","price()",[]),("mintPrice","mintPrice()",[]),
    ("costOf_user_1","costOf(address,uint256)",[USER,1]),
    ("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
    ("mintedBy_user","mintedBy(address)",[USER]),
    ("freeClaimed_user","freeClaimed(address)",[USER]),
    ("balanceOf_user","balanceOf(address)",[USER]),
    ("AGENT_ID","AGENT_ID()",[]),("owner","owner()",[])]),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),
    ("freeLeft","freeLeft()",[]),("mintOpen","mintOpen()",[]),
    ("price","price()",[]),("mintPrice","mintPrice()",[]),
    ("costOf_user_1","costOf(address,uint256)",[USER,1]),
    ("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
    ("mintedBy_user","mintedBy(address)",[USER]),
    ("freeClaimed_user","freeClaimed(address)",[USER]),
    ("balanceOf_user","balanceOf(address)",[USER]),
    ("AGENT_ID","AGENT_ID()",[]),("owner","owner()",[])]),
 "VOXEL": ("0x2c93e68462f0d20ccc54a19d39d9ed25d9f3b9be", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),
    ("freeLeft","freeLeft()",[]),("mintOpen","mintOpen()",[]),
    ("price","price()",[]),("mintPrice","mintPrice()",[]),
    ("costOf_user_1","costOf(address,uint256)",[USER,1]),
    ("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
    ("mintedBy_user","mintedBy(address)",[USER]),
    ("freeClaimed_user","freeClaimed(address)",[USER]),
    ("balanceOf_user","balanceOf(address)",[USER]),
    ("AGENT_ID","AGENT_ID()",[]),("owner","owner()",[])]),
 "Punch In Whitelist Pass": ("0x71d4c3747296f2989cb472ed7efc9cca197d84d8", [
    ("name","name()",[]),("symbol","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),
    ("freeLeft","freeLeft()",[]),("mintOpen","mintOpen()",[]),
    ("price","price()",[]),("mintPrice","mintPrice()",[]),
    ("costOf_user_1","costOf(address,uint256)",[USER,1]),
    ("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
    ("mintedBy_user","mintedBy(address)",[USER]),
    ("freeClaimed_user","freeClaimed(address)",[USER]),
    ("balanceOf_user","balanceOf(address)",[USER]),
    ("AGENT_ID","AGENT_ID()",[]),("owner","owner()",[])]),
}

def decode_str(r):
    # string return: offset(32B) len(32B) data
    try:
        if not r or len(r) < 130: return None
        ln = int(r[66:130], 16)
        return bytes.fromhex(r[130:130+ln*2]).decode("utf-8", "replace")
    except Exception:
        return None

out = {}
for name, (addr, views) in ITEMS.items():
    # Sourcify ABI
    abi = None; verified = None
    try:
        raw = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=stdJson,abi")
        j = json.loads(raw)
        abi = j.get("stdJson", {}).get("abi") or j.get("abi")
        verified = j.get("match") or j.get("creationMatch")
    except Exception as e:
        abi = None; verified = f"ERR {e}"
    shape = {}
    if abi:
        fns = [f.get("name") for f in abi if f.get("type") == "function"]
        txt = json.dumps(abi).lower()
        shape = {"fns": fns,
                 "has_mint": any("mint" in f for f in fns),
                 "has_freeMint": "freeMint" in fns,
                 "free_views": [f for f in fns if f.lower().startswith("free")],
                 "registry_ref": REG[2:].lower() in txt.replace("0x", ""),
                 "agent_gate": any("agent" in f.lower() for f in fns)}
    # on-chain views
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    reads = {}
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            for it, key in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    reads[key] = None
                else:
                    r = it["result"]
                    if key in ("name", "symbol"):
                        reads[key] = decode_str(r)
                    elif len(r) >= 66 and r.startswith("0x"):
                        v = to_int(r[:66])
                        reads[key] = v if v is not None else r
                    else:
                        reads[key] = r
            break
        except Exception as e:
            print(f"  {name} ep {ep} exc {e}", flush=True); continue
    out[name] = {"address": addr, "sourcify_match": verified, "shape": shape, "views": reads}
    print(f"{name}: {json.dumps(reads)} | shape={json.dumps(shape)} | sourcify={verified}", flush=True)

blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
        if isinstance(r, dict) and r.get("result"): blk = int(r["result"], 16); break
    except Exception: continue
json.dump({"run": "free-mint-search 2026-11-15 14:01 WIB", "block": blk,
           "results": out, "elapsed_s": round(time.time()-t0, 1)},
          open(BASE + "run-2026-11-15-1401-newverify.json", "w"), indent=1)
print("DONE block", blk, "elapsed", round(time.time()-t0, 1))
