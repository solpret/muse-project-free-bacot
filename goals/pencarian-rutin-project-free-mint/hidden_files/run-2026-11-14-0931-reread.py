#!/usr/bin/env python3
"""Re-read for free-mint-search run 2026-11-14 09:31 WIB.
Focus set only (degraded egress; small batches, curl timeout 150s).
Read-only; writes run-2026-11-14-0931-reread.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=150):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)

U = [USER]
ITEMS = {
 "WoozCode": ("0xfF172b79d040faefA1Bf34B47151edc87130246E", [
    ("totalSnippets","totalSnippets()",[]),("currentCommit","currentCommit()",[]),
    ("genesisOpen","genesisOpen()",[]),("genesisStart","genesisStart()",[]),
    ("commitEnd_1","commitEnd(uint256)",[1]),
    ("priceFor_user","priceFor(address)",U),("holdsAgentId_user","holdsAgentId(address)",U),
    ("snippetsOf_1_user","snippetsOf(uint256,address)",[1, USER])]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[])]),
 "NOISE": ("0xBA5352A3A05Ec637394810D791a412E78A349247", [
    ("totalMinted","totalMinted()",[]),("remainingSupply","remainingSupply()",[]),
    ("mintOpen","mintOpen()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("priceFor_user","priceFor(address)",U),("freeUsed_user","freeUsed(address)",U)]),
 "DragonAgents": ("0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintedBy_user","mintedBy(address)",U),
    ("price","price()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "AngelEye-77D9": ("0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
 "AngelEye-07bD": ("0x07bD6DbbEf508ad83BA2C557ED979732488894A1", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
 "NovaRemnants": ("0x38C1695eb72B7522c8d6452a4CE27122532A0d69", [
    ("totalRemnants","totalRemnants()",[]),("genesisOpen","genesisOpen()",[]),
    ("genesisStart","genesisStart()",[]),("currentCycle","currentCycle()",[]),
    ("priceFor_user","priceFor(address)",U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("mintOpen","mintOpen()",[])]),
 "AbsurdAgentNFT": ("0x72c14121681F1133545947B0735563835CC07B67", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("mintStartTime","mintStartTime()",[]),("isEligible_user","isEligible(address)",U)]),
 "B77D": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("standardRemaining","standardRemaining()",[]),("legendaryRemaining","legendaryRemaining()",[]),
    ("freeCount","freeCount()",[]),("hasAgentId_user","hasAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Zero": ("0x89B340435e4fD27e00442f7F1b3a3b3244b4E647", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "HIVE": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", [
    ("totalSupply","totalSupply()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "AgentZENITH": ("0x699b6397986cc6c444069efe692023b1253dc26d", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("freeMintedPerWallet_user","freeMintedPerWallet(address)",U),
    ("mintedPerWallet_user","mintedPerWallet(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "AgentNOVA": ("0x43462d7f269fde4914b03e1e07067a61b62b9540", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("freeMintedPerWallet_user","freeMintedPerWallet(address)",U),
    ("mintedPerWallet_user","mintedPerWallet(address)",U),
    ("balanceOf_user","balanceOf(address)",U),("TOKEN_PRICE","TOKEN_PRICE()",[])]),
 "SPARKS": ("0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("hasAgentId_user","hasAgentId(address)",U),
    ("paused","paused()",[]),("mintedByWallet_user","mintedByWallet(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U)]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "WANGCAI": ("0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("AGENT_ID","AGENT_ID()",[]),
    ("balanceOf_user","balanceOf(address)",U),("owner","owner()",[])]),
 "YUANBAO": ("0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("AGENT_ID","AGENT_ID()",[]),
    ("balanceOf_user","balanceOf(address)",U),("owner","owner()",[])]),
 "NOTV": ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("FREE_SHARES","FREE_SHARES()",[]),
    ("freeStart","freeStart()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
}

def chunked(items, n=15):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]

def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=150)
            if not isinstance(res, list) or len(res) != len(calls):
                print("  chunk ep", ep, "bad shape", type(res), str(res)[:120], flush=True); continue
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

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=150)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

reads, ok = {}, 0
chunks = list(chunked(ITEMS, 3))  # ~3 contracts per chunk => <=18 calls
for ci, ch in enumerate(chunks):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci+1}/{len(chunks)} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk {ci+1}/{len(chunks)} OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(5)
blk = block_number()
out = {"started_wib": "2026-11-14T09:31+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-14-0931-reread.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
