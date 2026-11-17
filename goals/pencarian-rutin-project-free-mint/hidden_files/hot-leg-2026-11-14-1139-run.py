#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 11:39 WIB (scheduled 11:39:38).
Legs: (1) Sourcify feed poll + ABI shape-check new; (2) Boltbook EN+ZH;
(3) on-chain verify only if new sale-shape; (4) focus re-read of snapshot
items (batched eth_call, endpoint fallback); bridge read-only.
Read-only except hot-leg-seen.json (new addresses) + run JSON outputs.
No preview/mint/claim. No snapshot writes."""
import json, subprocess, time, os, re
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
t0 = time.time()
def log(*a): print(f"[{time.time()-t0:6.1f}s]", *a, flush=True)

def curl(url, timeout=30):
    try:
        p = subprocess.run(["curl","-sS","-m",str(timeout),"-A","Mozilla/5.0",url],
                           capture_output=True, text=True, timeout=timeout+10)
        return p.stdout if p.returncode == 0 else ""
    except Exception:
        return ""

# ---- leg 1: Sourcify feed ----
feed_raw = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 30)
feed = []
try:
    feed = json.loads(feed_raw).get("results", []) if feed_raw else []
except Exception:
    feed = []
log("feed n=", len(feed), "top=",
    feed[0].get("address") if feed else None,
    feed[0].get("verifiedAt") if feed else None)

# ---- leg 2: Boltbook EN + ZH ----
en = curl("https://boltbook.fun/", 30)
zh = curl("https://boltbook.fun/?lang=zh", 30)
open(BASE+"run-2026-11-14-1139-boltbook-en.html","w").write(en)
open(BASE+"run-2026-11-14-1139-boltbook-zh.html","w").write(zh)
addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
def bb_addrs(html):
    return sorted(set(a for a in addr_re.findall(html or "")))
en_addrs, zh_addrs = bb_addrs(en), bb_addrs(zh)
log("boltbook EN bytes", len(en), "addrs", len(en_addrs),
    "| ZH bytes", len(zh), "addrs", len(zh_addrs))

# ---- seen dedupe ----
seen = json.load(open(BASE+"hot-leg-seen.json"))
seen_n0 = len(seen)
now_iso = "2026-11-14T11:39+07:00"
feed_addrs = [(c.get("address"), c.get("verifiedAt")) for c in feed if c.get("address")]
new_feed = [(a, v) for a, v in feed_addrs
            if a.lower() not in {k.lower() for k in seen}
            and a.lower() != REGISTRY.lower() and a.lower() not in EXCLUDED]
bb_new = [a for a in sorted(set(en_addrs+zh_addrs))
          if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED]
log("new feed", len(new_feed), "new boltbook", len(bb_new), bb_new)

# ---- shape-check new (ABI only) ----
def shape_check(addr, vat):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    raw = curl(url, 30)
    try:
        abi = json.loads(raw).get("abi", []) if raw else []
    except Exception:
        return {"address": addr, "verifiedAt": vat, "S1": None, "S2": None,
                "status": "abi-fetch-failed"}
    names = set(); fns = {}
    for e in abi:
        if e.get("type") == "function":
            names.add(e["name"]); fns.setdefault(e["name"], []).append(e)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & FREE_VIEWS)
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId",
                              "agentGate","AgentGate","AGENT_ID_REGISTRY",
                              "agentIdRegistry","AGENT_ID"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = bool(has_mint and has_quote and free_views and agent_ref)
    s2 = bool(is_token and mintfree and (names & {"freeClaimed","freeMinted"})
              and (names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref)
    return {"address": addr, "verifiedAt": vat, "S1": s1, "S2": s2,
            "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
            "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
            "status": "checked"}

to_check = [(a, v) for a, v in new_feed] + [(a, None) for a in bb_new]
shapes = []
with ThreadPoolExecutor(max_workers=8) as ex:
    for r in ex.map(lambda t: shape_check(t[0], t[1]), to_check):
        shapes.append(r)
        log("shape", r["address"][:10], "S1", r.get("S1"), "S2", r.get("S2"),
            "mint", r.get("has_mint"), "quote", r.get("has_quote"),
            "free", r.get("free_views"), "agent", r.get("agent_ref"),
            "n", r.get("n_fns"), r.get("status"))
hits = [s for s in shapes if s.get("S1") or s.get("S2")]
log("shape hits:", [h["address"] for h in hits])

# ---- leg 4: focus re-read (batched eth_call) ----
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
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
                          "-H","Content-Type: application/json","-d",json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout+10).stdout
    return json.loads(out)

U = [USER]
ITEMS = {
 "WANGCAI": ("0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "YUANBAO": ("0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "B77D-Kryntar": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("standardRemaining","standardRemaining()",[]),("legendaryRemaining","legendaryRemaining()",[]),
    ("hasAgentId_user","hasAgentId(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("mintOpen","mintOpen()",[])]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "DragonAgents": ("0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",U)]),
 "AngelEye-77D9": ("0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
 "NOTV": ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("FREE_SHARES","FREE_SHARES()",[]),
    ("freeStart","freeStart()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "AbsurdAgentNFT": ("0x72c14121681F1133545947B0735563835CC07B67", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("mintStartTime","mintStartTime()",[]),("isEligible_user","isEligible(address)",U)]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U)]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("freeClaimed","freeClaimed()",[]),("totalSupply","totalSupply()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "ZephyrAgent": ("0x010597f2e8723cde9e92d234cbdf23b47cc5504a", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "CPASS": ("0x5877d2bb9f226cc3e438f4d656caeb27deafc576", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
}
def chunked(items, n=5):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]
def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, views) in chunk:
        for key, sig, args in views:
            calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call",
                          "params":[{"to":addr,"data":build_data(sig,args)},"latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                log("  chunk ep", ep, "bad shape"); continue
            out = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    out.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out, ep
        except Exception as e:
            log("  chunk ep", ep, "exc", str(e)[:100]); continue
    return None, None
def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=60)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

reads, ok = {}, 0
for ci, ch in enumerate(chunked(ITEMS, 5)):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        log(f"chunk {ci+1} FAIL {names}")
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    log(f"chunk {ci+1} OK via {ep} {names}")
blk = block_number()
log("reread ok", ok, "/", len(ITEMS), "block", blk)

# ---- bridge (read-only) ----
bridge = json.load(open(BASE+"scan-bridge.json"))
snap = json.load(open(BASE+"onchain-snapshot.json"))
bcontracts = bridge.get("contracts", {})
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict) and v.get("address"): snap_addrs.add(v["address"].lower())
snap_addrs |= {str(v.get("address","")).lower() if isinstance(v, dict) else str(v).lower()
               for v in snap.get("track_c", {}).values()}
not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
same_owner = [a for a, v in bcontracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
bridge_info = {"contracts": len(bcontracts), "same_owner_discarded": len(same_owner),
               "not_in_snapshot": len(not_in_snap),
               "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(BASE+"scan-bridge.json")))}
log("bridge", bridge_info)

# ---- update seen ----
for a, v in new_feed:
    seen[a] = {"first_seen": now_iso, "verifiedAt": v, "source": "sourcify-feed"}
for a in bb_new:
    seen[a] = {"first_seen": now_iso, "source": "boltbook"}
json.dump(seen, open(BASE+"hot-leg-seen.json", "w"))
log("seen", seen_n0, "->", len(seen))

out = {"run": "free-mint-hot-leg 2026-11-14 11:39 WIB",
       "started_wib": "2026-11-14T11:39+07:00",
       "seen_n": len(seen), "seen_n_prev": seen_n0,
       "sourcify_feed": {"total": len(feed),
                         "new": len(new_feed),
                         "new_contracts": [a for a, _ in new_feed],
                         "top": feed[0].get("address") if feed else None,
                         "top_verifiedAt": feed[0].get("verifiedAt") if feed else None},
       "boltbook_en": {"bytes": len(en), "full_address_contracts": len(en_addrs),
                       "new": len([a for a in en_addrs if a in bb_new]),
                       "new_contracts": [a for a in en_addrs if a in bb_new]},
       "boltbook_zh": {"bytes": len(zh), "full_address_contracts": len(zh_addrs),
                       "new": len([a for a in zh_addrs if a in bb_new]),
                       "new_contracts": [a for a in zh_addrs if a in bb_new]},
       "shape_check": shapes,
       "shape_hits": [h["address"] for h in hits],
       "reread": {"reads": reads, "reads_ok": ok, "reads_total": len(ITEMS), "block": blk},
       "bridge": bridge_info,
       "elapsed_s": round(time.time()-t0, 1)}
json.dump(out, open(BASE+"hot-leg-run-2026-11-14-1139.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
