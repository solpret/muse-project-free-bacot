#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 10:49 WIB (started ~10:55 WIB).
Legs: (1) Sourcify feed poll + shape-check genuinely-new contracts;
(2) Boltbook EN+ZH front pages; (3) on-chain verify for new sale-shape;
(4) read-only re-read of main snapshot active watchlist for changes;
bridge leg per 2026-11-03 amendment. Read-only except own state files
hot-leg-seen.json / hot-leg-reported.json. No preview/mint. Target <2 min."""
import json, subprocess, time, re, os
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
t0 = time.time()
RUN = "free-mint-hot-leg 2026-11-14 10:49 WIB"

def now_wib():
    return time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))
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
def decode_str(r):
    try:
        h = bytes.fromhex(r[2:])
        ln = int.from_bytes(h[32:64], "big")
        return h[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return None
def post_rpc(ep, payload, timeout=120):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def curl(url, timeout=60):
    try:
        p = subprocess.run(["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=timeout + 10)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

out = {"run": RUN, "started_wib": now_wib()}
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower(): k for k in seen}
reported = json.load(open(BASE + "hot-leg-reported.json"))
out["seen_n"] = len(seen)

# ---- leg 1: Sourcify feed (already fetched to run-2026-11-14-1055-feed.json) ----
feed = json.load(open(BASE + "run-2026-11-14-1055-feed.json"))
items = feed.get("results", [])
feed_addrs = [it.get("address") for it in items]
new_feed = [a for a in feed_addrs if a and a.lower() not in seen_lower]
out["sourcify_feed"] = {"total": len(feed_addrs), "new": len(new_feed),
                        "new_contracts": new_feed,
                        "top": feed_addrs[0] if feed_addrs else None,
                        "note": "feed fetched 10:55 WIB; top verifiedAt 2026-11-14T03:53:36Z - new verifications since 10:34 run"}

# ---- leg 2: Boltbook EN+ZH (already fetched) ----
bb_new = []
for tag in ("en", "zh"):
    try:
        h = open(BASE + f"run-2026-11-14-1055-boltbook-{tag}.html", errors="ignore").read()
    except Exception as e:
        out[f"boltbook_{tag}"] = {"crawl": f"read-failed: {e}"}; continue
    addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", h)))
    new = [a for a in addrs if a.lower() not in seen_lower]
    bb_new += new
    out[f"boltbook_{tag}"] = {"bytes": len(h), "full_address_contracts": len(addrs),
                              "new": len(new), "new_contracts": new}
out["boltbook_new_total"] = len(set(a.lower() for a in bb_new))

# ---- shape-check any genuinely new contract (feed or boltbook) ----
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCardsRemaining"]
def fetch_abi(addr):
    body = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=60)
    if not body: return None, "fetch-failed"
    try: return json.loads(body).get("abi", []), None
    except Exception as e: return None, str(e)[:100]
def shape(addr, verified_at):
    abi, err = fetch_abi(addr)
    if abi is None:
        return {"address": addr, "verifiedAt": verified_at, "S1": None, "S2": None,
                "error": err, "status": "shape-check-failed"}
    names = {e["name"] for e in abi if e.get("type") == "function"}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                              "agentGate", "AgentGate", "AGENT_ID_REGISTRY", "agentIdRegistry"})
    is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"} and
                    names & {"transfer", "transferFrom", "balanceOf"})
    fns = {}
    for e in abi:
        if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = bool(has_mint and has_quote and free_views and agent_ref)
    s2 = bool(is_token and mintfree and (names & {"freeClaimed", "freeMinted"})
              and (names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
    r = {"address": addr, "verifiedAt": verified_at, "S1": s1, "S2": s2,
         "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
         "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
         "functions": sorted(names), "status": "checked"}
    if (not s1 and not s2) and "AGENT_ID" in names:
        try:
            res = post_rpc(EPS[0], [{"jsonrpc": "2.0", "id": 0, "method": "eth_call",
                "params": [{"to": addr, "data": sel("AGENT_ID()")}, "latest"]}], timeout=60)
            rr = res[0].get("result") if isinstance(res, list) else res.get("result")
            r["AGENT_ID_value"] = rr[-40:] if rr and len(rr) >= 42 else rr
            r["AGENT_ID_is_registry"] = bool(rr and rr[-40:].lower() == REG[2:].lower())
        except Exception as e:
            r["AGENT_ID_error"] = str(e)[:100]
    return r

to_shape = []
for a in new_feed:
    to_shape.append((a, next((it.get("verifiedAt") for it in items if it.get("address") == a), "feed")))
for a in set(bb_new):
    if a not in [x[0] for x in to_shape]:
        to_shape.append((a, "boltbook"))
shapes = []
for a, src in to_shape:
    shapes.append(shape(a, src))
    seen[a] = {"first_seen": now_wib(), "source": f"hot-leg 1049 {src}"}
    seen_lower[a.lower()] = a
out["shape_check"] = shapes
out["s1_pass"] = [s["address"] for s in shapes if s.get("S1")]
out["s2_pass"] = [s["address"] for s in shapes if s.get("S2")]

# ---- bridge leg (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for v in snap.get(sec, {}).values():
            if isinstance(v, dict) and v.get("address"): snap_addrs.add(v["address"].lower())
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
    discarded = [a for a, v in bcontracts.items()
                 if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"n": len(bcontracts), "not_in_snapshot": len(not_in_snap),
                     "same_owner_discarded": len(discarded),
                     "note": "unchanged vs 10:29 run (116/109/7) unless counts differ"}
except Exception as e:
    out["bridge"] = {"error": str(e)[:120], "note": "bridge unreadable - run continues, bridge never fails a run"}

# ---- leg 4: re-read active watchlist (read-only, batched eth_call) ----
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
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
    ("mintedBy_user","mintedBy(address)",U),("hasAgentId_user","hasAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "LumenFindings": ("0x4158B701EaA30E8FaDBaA526F70780A38318c1C4", [
    ("totalSpecimens","totalSpecimens()",[]),("currentExperiment","currentExperiment()",[]),
    ("genesisStart","genesisStart()",[]),("genesisOpen","genesisOpen()",[]),
    ("priceFor_user","priceFor(address)",U),("holdsAgentId_user","holdsAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("mintsBy_user","mintsBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "ACARD": ("0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69", [
    ("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U)]),
 "Boltbook-8d292d": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("name_str","name()",[]),("symbol_str","symbol()",[]),
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("freeLeft_user","freeLeft(address)",U),
    ("freeUsed_user","freeUsed(address)",U),
    ("quote_user_1","quote(address,uint256)",[USER,1])]),
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
            outd = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    outd.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    if key.endswith("_str"):
                        outd.setdefault(name, {})[key] = decode_str(r)
                    else:
                        outd.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return outd, ep
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

items_l = list(ITEMS.items())
reads, ok = {}, 0
for ci in range(0, len(items_l), 3):
    ch = items_l[ci:ci+3]
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci//3+1} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk {ci//3+1} OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(3)
blk = block_number()
out["reads"] = reads
out["reads_ok"] = ok
out["reads_total"] = len(ITEMS)
out["block"] = blk
out["elapsed_s"] = round(time.time() - t0, 1)

# ---- decisions vs baselines (10:34 run) ----
flags = {}
def v(name, key):
    return (reads.get(name) or {}).get("views", {}) .get(key) if reads.get(name) else None
def pct(a, b):
    return round(100.0 * a / b, 1) if a is not None and b else None

w = v("WANGCAI", "freeClaimed"); wf = v("WANGCAI", "FREE_SUPPLY")
flags["WANGCAI_freeClaimed"] = w; flags["WANGCAI_FREE_SUPPLY"] = wf
flags["WANGCAI_pct"] = pct(w, wf)
flags["WANGCAI_mintedBy_user"] = v("WANGCAI", "mintedBy_user")
flags["WANGCAI_decision"] = (
    "STRONG-LEAD PROMOTION (>70%): age verified <24h + slot open + gate FAILED (no website) -> report once as gate-blocked promotion, NEVER preview/mint"
    if w is not None and wf and w * 100 > 70 * wf else
    "below 70% strong-lead line (132/188) - gate-blocked legs-met item, silent unless promotion")
y = v("YUANBAO", "freeClaimed"); yf = v("YUANBAO", "FREE_SUPPLY")
flags["YUANBAO_freeClaimed"] = y; flags["YUANBAO_FREE_SUPPLY"] = yf
flags["YUANBAO_pct"] = pct(y, yf)
flags["YUANBAO_mintedBy_user"] = v("YUANBAO", "mintedBy_user")
flags["YUANBAO_decision"] = (
    "crossed >70% (132/188) BUT age UNVERIFIED separately -> not a strong lead; gate FAILED (no website) -> report once as crossing note only if not already reported, NEVER preview/mint"
    if y is not None and yf and y * 100 > 70 * yf else
    "below 70% line (132/188), age unverified, gate-blocked - silent")
ra = v("RaceAgents", "freeMinted"); raf = v("RaceAgents", "FREE_MAX")
flags["RaceAgents_freeMinted"] = ra; flags["RaceAgents_FREE_MAX"] = raf
flags["RaceAgents_pct"] = pct(ra, raf)
flags["RaceAgents_decision"] = (
    "SELLOUT 1000/1000 - report once as change" if ra == raf and ra is not None else
    "above 50% but velocity FAILED in main runs + age/website/X unverified -> not candidate/strong lead, watchlist-only, silent")
ac = v("ACARD", "freeMinted"); acf = v("ACARD", "FREE_CAP")
flags["ACARD_freeMinted"] = ac; flags["ACARD_FREE_CAP"] = acf
flags["ACARD_decision"] = "free pool exhausted 345/345 since 0909, NOT in snapshot, NOT reported by design (ERC-721 NFT; early-lead stays with main job) - log only"
dg = v("DragonAgents", "freeClaimed"); dgf = v("DragonAgents", "FREE_SUPPLY")
flags["DragonAgents_pct"] = pct(dg, dgf)
flags["DragonAgents_decision"] = "age-excluded (>46h) - moot, silent"
z = v("Zero", "freeClaimed")
flags["Zero_decision"] = "age-excluded 0904 (recorded) - silent"
pg = v("Pengu", "freeMinted"); pgf = v("Pengu", "FREE_CAP")
flags["Pengu_freeMinted"] = pg; flags["Pengu_FREE_CAP"] = pgf; flags["Pengu_pct"] = pct(pg, pgf)
flags["Pengu_freeClaimed_user"] = v("Pengu", "freeClaimed_user")
flags["Pengu_decision"] = "early lead (main job 1001); age UNVERIFIED strict; far below 50%/70% - watchlist-only, main-job follow-up, NEVER preview/mint"
b8 = reads.get("Boltbook-8d292d", {}).get("views") or {}
flags["Boltbook-8d292d"] = b8
flags["Boltbook-8d292d_decision"] = "agent-shaped variant (AGENT_ID()=registry exact, 10:29 run); age UNVERIFIED -> watchlist-only, main-job follow-up, NEVER preview/mint"
flags["Kryntar_totalMinted"] = v("B77D", "totalMinted")
flags["Kryntar_decision"] = "early lead; launch verified <24h, website verified kryntar.xyz, slot open; free% UNVERIFIED (no global free counter) -> NOT strong lead, silent"
flags["binanceai"] = {"launched": v("BinanceAI-mint", "launched"), "failed": v("BinanceAI-mint", "failed"),
                     "isRefundPhase": v("BinanceAI-mint", "isRefundPhase"),
                     "tokenClaimed_user": v("BinanceAI-mint", "tokenClaimed_user")}
flags["binanceai_decision"] = "still pending (launched=0, refund phase) - no change, silent"
flags["AngelEye-77D9"] = {"freeMinted": v("AngelEye-77D9", "freeMinted"), "totalSupply": v("AngelEye-77D9", "totalSupply"),
                          "freeRemaining": v("AngelEye-77D9", "freeRemaining")}
flags["AngelEye-07bD"] = {"freeMinted": v("AngelEye-07bD", "freeMinted"), "totalSupply": v("AngelEye-07bD", "totalSupply")}
flags["NOTV_totalSupply"] = v("NOTV", "totalSupply")
flags["NOTV_decision"] = "totalSupply still 0 -> no first mint, age UNVERIFIED - watchlist-only, silent"
flags["AbsurdAgentNFT_totalMinted"] = v("AbsurdAgentNFT", "totalMinted")
flags["AbsurdAgentNFT_decision"] = "pre-launch (mintStartTime 1794650400 = 17:00 WIB 14 Nov) - watchlist-only, silent"
flags["Zephyra_totalMinted"] = v("Zephyra", "totalMinted")
flags["Zephyra_decision"] = "early lead; age UNVERIFIED, website null - watchlist-only, silent"
flags["AgentBubble_pct_of_max"] = pct(v("AgentBubble", "freeMinted"), v("AgentBubble", "MAX_SUPPLY"))
flags["AgentBubble_decision"] = "free pool (FREE_SUPPLY) unknown - pct is of MAX_SUPPLY, not free quota - watchlist re-read only, silent"
flags["Agentx"] = "thread CLOSED (user declined override 13 Nov) - NO re-check, NO report, NEVER preview/mint."
out["flags"] = flags

# ---- reportable promotions (only if a threshold actually crossed) ----
out["promotions_recorded"] = []
if w is not None and wf and w * 100 > 70 * wf:
    key = "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd#strong-lead-20261114"
    if key not in reported:
        reported[key] = {"what": "blocked",
            "reported_wib": now_wib(), "run": "hot-leg 1049",
            "detail": f"WANGCAI (Lucky Dog Agents) PROMOTED to STRONG LEAD: freeClaimed {w}/{wf}={pct(w,wf)}% (>70%), first mint verified 2026-11-14 06:08:01 WIB (age <24h), slot user TERBUKA (mintedBy=0), mintOpen=1, block {blk}. MANDATORY WEBSITE GATE FAILED (no verified project website; tokenURI/contractURI carry no URL, name search nil - recorded 07:22/07:31). NOT previewed, NOT minted. Promotion report once; do not re-report unless gate evidence appears or state changes (sellout/slot lost)."}
        out["promotions_recorded"].append(key)
if y is not None and yf and y * 100 > 70 * yf:
    key = "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E#crossed-70-20261114"
    if key not in reported:
        reported[key] = {"what": "blocked",
            "reported_wib": now_wib(), "run": "hot-leg 1049",
            "detail": f"YUANBAO (Yuanbao Agents) crossed >70%: freeClaimed {y}/{yf}={pct(y,yf)}%, slot user TERBUKA (mintedBy=0), mintOpen=1, block {blk}. Age UNVERIFIED separately (same deployer as WANGCAI) so NOT a strong lead; website gate FAILED (no verified project website). NOT previewed, NOT minted. Crossing note once; do not re-report unless gate evidence appears or state changes."}
        out["promotions_recorded"].append(key)
if ra is not None and raf and ra >= raf:
    key = "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f#sellout-20261114"
    if key not in reported:
        reported[key] = {"what": "change", "reported_wib": now_wib(), "run": "hot-leg 1049",
            "detail": f"RaceAgents free pool SOLD OUT: freeMinted {ra}/{raf} at block {blk}; slot user open={v('RaceAgents','mintOpen')}. Was watchlist-only (velocity failed + age/website unverified). Change report only, not a new lead, no preview/mint."}
        out["promotions_recorded"].append(key)

json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
json.dump(reported, open(BASE + "hot-leg-reported.json", "w"), indent=1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-14-1049.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk,
      "elapsed", round(time.time() - t0, 1), "s1_pass", out["s1_pass"],
      "promotions", out["promotions_recorded"])
print("WANGCAI", w, "/", wf, pct(w, wf), "%  YUANBAO", y, "/", yf, pct(y, yf),
      "%  RaceAgents", ra, "/", raf, " Pengu", pg, "/", pgf, " ACARD", ac, "/", acf)
print("8d292d", json.dumps(b8))
