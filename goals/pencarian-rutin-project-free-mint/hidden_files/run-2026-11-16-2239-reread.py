#!/usr/bin/env python3
"""Hot-leg focused re-read run 2026-11-16 22:39 WIB. Read-only; writes run-2026-11-16-2239-reread.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed.binance.org/",
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

U = [USER]
ITEMS = {
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("mintOpen","mintOpen()",[]),("totalMinted","totalMinted()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("mintOpen","mintOpen()",[])]),
 "Matrix Agents": ("0x1F669b714337F3C2585072c53fdDD89581F928fF", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeRemaining","freeRemaining()",[]),("mintOpen","mintOpen()",[]),
    ("FREE_MAX","FREE_MAX()",[])]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("freeUsed_user","freeUsed(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "WANGCAI": ("0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "YUANBAO": ("0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "Bold Leonidas": ("0x84bcb8c16566e81ce902530c9da1e3de291f9941", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("mintOpen","mintOpen()",[]),("mintPriceFor_user_1","mintPriceFor(address,uint256)",[USER,1]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Punch Card": ("0x1d4ef0587dd3ff3875a141d4711c60bca40587c4", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("mintOpen","mintOpen()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "PXIO": ("0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab", [
    ("totalSupply","totalSupply()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "ALIEN": ("0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb", [
    ("totalSupply","totalSupply()",[]),("mintOpen","mintOpen()",[]),
    ("isFreePhase","isFreePhase()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
}

reads = {}
block = None
names = list(ITEMS)
for ci in range(0, len(names), 3):
    chunk = names[ci:ci+3]
    calls = []
    meta = []
    for name in chunk:
        addr, views = ITEMS[name]
        for vname, sig, args in views:
            calls.append({"jsonrpc":"2.0","id":len(calls),"method":"eth_call",
                          "params":[{"to":addr,"data":build_data(sig,args)},"latest"]})
            meta.append((name, vname))
    calls.append({"jsonrpc":"2.0","id":len(calls),"method":"eth_blockNumber","params":[]})
    ok = False
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if isinstance(res, list) and res and isinstance(res[0], dict) and "result" in res[0]:
                ok = True
                for (name, vname), r in zip(meta, res[:-1]):
                    val = to_int(r.get("result")) if isinstance(r, dict) else None
                    reads.setdefault(name, {"address": ITEMS[name][0], "views": {}})[ "views"][vname] = val
                block = to_int(res[-1].get("result")) if isinstance(res[-1], dict) else None
                print(f"chunk {ci//3+1} OK via {ep} ({time.time()-t0:.0f}s) {chunk}", flush=True)
                break
        except Exception as e:
            print(f"chunk ep {ep} exc {str(e)[:60]}", flush=True)
    if not ok:
        print(f"chunk {ci//3+1} FAILED all endpoints {chunk}", flush=True)
        for name in chunk:
            reads.setdefault(name, {"address": ITEMS[name][0], "views": {}, "error": "rpc-failed"})

out = {"started_wib": "2026-11-16T22:39+07:00", "block": block,
       "elapsed_s": round(time.time()-t0, 1), "reads": reads}
json.dump(out, open(BASE + "run-2026-11-16-2239-reread.json", "w"), indent=1)
print("DONE reads_ok", sum(1 for v in reads.values() if "error" not in v), "/", len(reads), "block", block, "elapsed", round(time.time()-t0, 1))
