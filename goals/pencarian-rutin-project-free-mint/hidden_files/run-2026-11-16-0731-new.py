#!/usr/bin/env python3
"""Verify 2 new Boltbook addresses run 2026-11-16 07:31 WIB (read-only).
Golden Miner 0x0887 (GMC) + NIXIE 0x53cd. DualForge ForgeCore 0x4dc8 is
PAID per the Boltbook post itself (trial key 0.00011 BNB) -> excluded
paid-only, no on-chain verify needed beyond the post's own statement.
No preview/mint. Writes run-2026-11-16-0731-new.json."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
REG = "60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        else: d += enc_u(int(a))
    return d
def rpc(payload, timeout=60):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+10).stdout
    return json.loads(out)

def batch(addr, calls):
    payload = [{"jsonrpc":"2.0","id":i,"method":"eth_call",
                "params":[{"to":addr,"data":data(sig,args)},"latest"]} for i,(n,sig,args) in enumerate(calls)]
    r = rpc(payload)
    out = {}
    for i,(n,sig,args) in enumerate(calls):
        res = r[i].get("result") if isinstance(r, list) else None
        out[n] = res
    return out

def dec_int(h):
    try:
        return int(h,16) if h and h != "0x" else None
    except Exception: return None
def dec_str(h):
    # string return: offset(32B)+len(32B)+data
    try:
        if not h or len(h) < 138: return None
        ln = int(h[66:130],16)
        return bytes.fromhex(h[130:130+ln*2]).decode("utf-8","replace")
    except Exception: return None

U=[USER]
COMMON = [
 ("name","name()",[]),("symbol","symbol()",[]),
 ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
 ("freeMinted","freeMinted()",[]),("freeClaimed","freeClaimed()",[]),
 ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_CLAIM_SLOTS","FREE_CLAIM_SLOTS()",[]),
 ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),("mintActive","mintActive()",[]),
 ("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
 ("priceOf_user_1","priceOf(uint256)",[1]),
 ("mintedBy_user","mintedBy(address)",U),
 ("freeClaimed_user","freeClaimed(address)",U),
 ("balanceOf_user","balanceOf(address)",U),
 ("contractURI","contractURI()",[]),
 ("AGENT_ID","AGENT_ID()",[]),
 ("agentRegistry","agentRegistry()",[]),
 ("claimSigner","claimSigner()",[]),
 ("owner","owner()",[]),
]
TARGETS = {
 "GoldenMiner": "0x088708f79A71b82C14e1864FB0c63E53Cbf94243",
 "NIXIE": "0x53cdb9e6ee79d22a122270cc1bdedf125eded234",
}
result = {"block": None, "targets": {}}
blk = rpc({"jsonrpc":"2.0","id":0,"method":"eth_blockNumber","params":[]})
result["block"] = int(blk["result"],16) if blk.get("result") else None
for name, addr in TARGETS.items():
    raw = batch(addr, COMMON)
    code = rpc({"jsonrpc":"2.0","id":0,"method":"eth_getCode","params":[addr,"latest"]})
    codehex = (code.get("result") or "")[2:].lower()
    views = {}
    for k,v in raw.items():
        if k in ("name","symbol","contractURI"):
            views[k] = dec_str(v)
        else:
            views[k] = dec_int(v)
    # contractURI string may be short (bytes32-style) - keep raw too
    views["_contractURI_raw"] = raw.get("contractURI")
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contracts/56/{addr}",
            headers={"User-Agent":"curl/8"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            sj = json.load(resp)
            views["_sourcify"] = sj.get("stdJson",{}).get("status") if isinstance(sj,dict) else str(sj)[:100]
            views["_sourcify_match"] = sj.get("stdJson",{}).get("match") if isinstance(sj,dict) else None
    except Exception as e:
        views["_sourcify"] = f"ERROR {type(e).__name__}: {e}"
    views["_code_len_bytes"] = len(codehex)//2
    views["_registry_bytes_in_code"] = REG in codehex
    result["targets"][name] = {"address": addr, "views": views}
    print(name, json.dumps(views, indent=1, default=str))
json.dump(result, open(BASE+"run-2026-11-16-0731-new.json","w"), indent=1)
print("BLOCK", result["block"])
