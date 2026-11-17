#!/usr/bin/env python3
"""On-chain verification for free-mint-search run 2026-11-16 16:01 WIB.
Boltbook new leads: Volta Gent, HARBOR, Fira Agent, Orin Agent, HEXCOVEN, Punch Card.
Read-only; writes run-2026-11-16-1601-verify.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
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
def post_rpc(ep, payload, timeout=120):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

U = [USER]
ITEMS = {
 "Volta Gent": ("0x2703a2be75e0c470d83573badc6a1b1b86d1871e", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("AGENT_LIMIT","AGENT_LIMIT()",[]),("AGENT_PRICE","AGENT_PRICE()",[]),
    ("PUBLIC_PRICE","PUBLIC_PRICE()",[]),("agentPhaseActive","agentPhaseActive()",[]),
    ("mintOpen","mintOpen()",[]),("AGENT_ID_REGISTRY","AGENT_ID_REGISTRY()",[]),
    ("quoteFor_user_1","quoteFor(address,uint256)",[USER,1]),
    ("agentMintedByWallet_user","agentMintedByWallet(address)",U),
    ("mintedByWallet_user","mintedByWallet(address)",U),
    ("balanceOf_user","balanceOf(address)",U),
    ("hasAgentId_user","hasAgentId(address)",U),
    ("owner","owner()",[])]),
 "HARBOR": ("0xa5844f0539e289c9a477672818ee263ef862b517", [
    ("totalSupply","totalSupply()",[]),("TOTAL_SUPPLY","TOTAL_SUPPLY()",[]),
    ("FREE_SEATS","FREE_SEATS()",[]),("PAID_SEATS","PAID_SEATS()",[]),
    ("freeSold","freeSold()",[]),("paidSold","paidSold()",[]),
    ("PRICE","PRICE()",[]),("SHARE","SHARE()",[]),
    ("START","START()",[]),("POOL_DEADLINE","POOL_DEADLINE()",[]),
    ("website","website()",[]),("pair","pair()",[]),("poolOpen","poolOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),
    ("hasMinted_user","hasMinted(address)",U)]),
 "HEXCOVEN": ("0xd3d5d57e4942cedcb6864c1dce1e9808544dd30d", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[]),
    ("PRICE","PRICE()",[]),("freeLeft","freeLeft()",[]),("paidMinted","paidMinted()",[]),
    ("FIRST_FREE_CAP","FIRST_FREE_CAP()",[]),("X_FREE_CAP","X_FREE_CAP()",[]),
    ("firstFreeByWallet_user","firstFreeByWallet(address)",U),
    ("firstFreeUsed_user","firstFreeUsed(address)",U),
    ("balanceOf_user","balanceOf(address)",U),
    ("contractURI","contractURI()",[])]),
 "Punch Card": ("0x1d4ef0587dd3ff3875a141d4711c60bca40587c4", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("paidMinted","paidMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("remaining","remaining()",[]),
    ("mintOpen","mintOpen()",[]),("MINT_PRICE","MINT_PRICE()",[]),
    ("mintPriceFor_user_1","mintPriceFor(address,uint256)",[USER,1]),
    ("mintedCount_user","mintedCount(address)",U),
    ("balanceOf_user","balanceOf(address)",U),
    ("AGENT_REGISTRY","AGENT_REGISTRY()",[]),
    ("owner","owner()",[]),("contractURI","contractURI()",[])]),
 "Fira Agent": ("0x7d46023bf2c3732f5fd30321cfce1ca91684408d", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Orin Agent": ("0xf92e693f43428d5cd1a85acb2cd8e242a717e964", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
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
            res = post_rpc(ep, calls, timeout=120)
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

def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=60)
            if isinstance(r, dict) and r.get("result"):
                return r["result"]
        except Exception:
            continue
    return None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

reads, ok = {}, 0
items = list(ITEMS.items())
for ci in range(0, len(items), 2):
    ch = items[ci:ci+2]
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci//2+1} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk {ci//2+1} OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(3)

# bytecode registry check (HEXCOVEN + Volta + Punch + HARBOR): does runtime code contain registry address bytes?
regbytes = REGISTRY[2:].lower()
for name in ("HEXCOVEN", "Volta Gent", "Punch Card", "HARBOR"):
    code = get_code(ITEMS[name][0])
    has = bool(code) and regbytes in code.lower()
    reads[name]["codeHasRegistry"] = has
    reads[name]["codeLen"] = (len(code) - 2) // 2 if code else None
    print(f"{name} codeHasRegistry={has} codeLen={reads[name]['codeLen']}", flush=True)

blk = block_number()
out = {"started_wib": "2026-11-16T16:01+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-16-1601-verify.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
for k, v in reads.items():
    print(k, json.dumps(v.get("views")))
