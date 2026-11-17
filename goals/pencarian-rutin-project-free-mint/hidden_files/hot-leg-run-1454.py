#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 14:54 WIB. Legs: (1) Sourcify feed poll,
(2) Boltbook EN+ZH front pages, (3) shape-check new sale-shape contracts,
(4) batched on-chain re-read of snapshot watchlist/track_c/pending_claims.
Read-only except hot-leg-seen.json / hot-leg-reported.json (own state).
Never writes the main snapshot."""
import json, re, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
PAD = "0" * 24 + USER[2:].lower()
RUN = "2026-11-14-1454"
log = {"run": RUN, "started_wib": "2026-11-14 14:54 WIB", "legs": {}}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def enc_addr():
    return PAD

def enc_u(n):
    return "%064x" % n

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def to_int(x):
    if x is None: return None
    if isinstance(x, int): return x
    try:
        s = str(x)
        if s.startswith("0x"):
            if len(s) <= 2: return None
            return int(s, 16)
        return int(s)
    except Exception:
        return None

# ---------- leg 1: Sourcify feed ----------
seen = json.load(open(HF + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 20)
    feed = json.loads(raw)
    items = feed if isinstance(feed, list) else feed.get("contracts", feed.get("results", []))
    addrs = []
    for it in items:
        a = it.get("address") or it.get("contractAddress")
        if a: addrs.append(a)
    new = [a for a in addrs if a.lower() not in seen_lower]
    log["legs"]["feed"] = {"ok": True, "n": len(addrs), "new": new,
        "verifiedAt": [it.get("verifiedAt") or it.get("verificationTime") for it in items][:20]}
except Exception as e:
    log["legs"]["feed"] = {"ok": False, "error": str(e)[:200]}

# ---------- leg 2: Boltbook EN+ZH ----------
bb_addrs = set()
for lang, url in [("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")]:
    try:
        html = fetch(url, 20)
        found = set(re.findall(r"0x[0-9a-fA-F]{40}", html))
        bb_addrs |= found
        log["legs"][f"boltbook_{lang}"] = {"ok": True, "bytes": len(html), "addrs": len(found)}
    except Exception as e:
        log["legs"][f"boltbook_{lang}"] = {"ok": False, "error": str(e)[:200]}
bb_new = [a for a in sorted(bb_addrs) if a.lower() not in seen_lower]
log["legs"]["boltbook_new_vs_seen"] = bb_new

# ---------- leg 3: shape-check genuinely new contracts ----------
new_all = list(dict.fromkeys([a for a in log["legs"]["feed"].get("new", [])] + bb_new))
shape = {}
for a in new_all:
    try:
        meta = json.loads(fetch(f"https://sourcify.dev/server/v2/contract/56/{a}?metadata=true", 15))
        std = meta.get("stdJson", {})
        abi = std.get("abi") or meta.get("abi") or []
        fns = [f.get("name") for f in abi if f.get("type") == "function"]
        names = set(fns)
        mint = [f for f in fns if "mint" in f.lower()]
        quote = [f for f in fns if "quote" in f.lower() or "cost" in f.lower() or "price" in f.lower()]
        free = [f for f in fns if any(k in f for k in ("freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","FREE_SLOTS","FREE_SUPPLY"))]
        agent = [f for f in fns if "agent" in f.lower() or "AgentGate" in f]
        token = [f for f in fns if f in ("name","symbol","decimals","totalSupply")]
        s1 = bool(mint and quote and free and agent)
        s2 = bool(len(token) == 4 and ("mintFree" in names) and free and agent)
        shape[a] = {"fns": len(fns), "mint": mint[:8], "quote": quote[:8], "free": free[:8],
                    "agent": agent[:8], "S1": s1, "S2": s2}
    except Exception as e:
        shape[a] = {"error": str(e)[:150]}
log["legs"]["shapecheck"] = shape

# ---------- leg 4: batched on-chain re-read ----------
# (label, contract, [(view, [args])])
def C(addr, fn, args=()):
    data = sel(fn)
    for a in args:
        data += a
    return (addr, data)

U = enc_addr()
Q1 = enc_u(1)
READS = []
def add(label, addr, fn, args=()):
    READS.append((label, C(addr, fn, args)))

WANG = "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd"
add("wang_freeClaimed", WANG, "freeClaimed()")
add("wang_FREE_SUPPLY", WANG, "FREE_SUPPLY()")
add("wang_mintedBy", WANG, "mintedBy(address)", [U])
add("wang_mintOpen", WANG, "mintOpen()")
add("wang_totalSupply", WANG, "totalSupply()")
CPASS = "0x5877d2bb9f226cc3e438f4d656caeb27deafc576"
add("cpass_totalMinted", CPASS, "totalMinted()")
add("cpass_mintOpen", CPASS, "mintOpen()")
add("cpass_priceFor", CPASS, "priceFor(address)", [U])
add("cpass_mintCountOf", CPASS, "mintCountOf(address)", [U])
add("cpass_holdsAgentId", CPASS, "holdsAgentId(address)", [U])
add("cpass_balanceOf", CPASS, "balanceOf(address)", [U])
ZEPH = "0x00a9791be6317d6e3a6c60f75a706c870d882048"
add("zeph_totalMinted", ZEPH, "totalMinted()")
add("zeph_priceFor1", ZEPH, "priceFor(address,uint256)", [U, Q1])
add("zeph_mintedBy", ZEPH, "mintedBy(address)", [U])
add("zeph_mintOpen", ZEPH, "mintOpen()")
NOISE = "0xBA5352A3A05Ec637394810D791a412E78A349247"
add("noise_totalMinted", NOISE, "totalMinted()")
add("noise_remainingSupply", NOISE, "remainingSupply()")
add("noise_priceFor", NOISE, "priceFor(address)", [U])
add("noise_freeUsed", NOISE, "freeUsed(address)", [U])
B77D = "0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe"
add("b77d_totalMinted", B77D, "totalMinted()")
add("b77d_standardMinted", B77D, "standardMinted()")
add("b77d_legendaryMinted", B77D, "legendaryMinted()")
add("b77d_mintOpen", B77D, "mintOpen()")
add("b77d_freeCount", B77D, "freeCount()")
add("b77d_hasAgentId", B77D, "hasAgentId(address)", [U])
add("b77d_balanceOf", B77D, "balanceOf(address)", [U])
REOP = "0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9"
add("reop_totalSupply", REOP, "totalSupply()")
add("reop_freeClaimed", REOP, "freeClaimed()")
add("reop_FREE_SUPPLY", REOP, "FREE_SUPPLY()")
add("reop_mintOpen", REOP, "mintOpen()")
add("reop_mintedBy", REOP, "mintedBy(address)", [U])
add("reop_freeUsed", REOP, "freeUsed(address)", [U])
AZEN = "0x699b6397986cc6c444069efe692023b1253dc26d"
add("azen_totalSupply", AZEN, "totalSupply()")
add("azen_freeMintedPerWallet", AZEN, "freeMintedPerWallet(address)", [U])
add("azen_mintedPerWallet", AZEN, "mintedPerWallet(address)", [U])
add("azen_balanceOf", AZEN, "balanceOf(address)", [U])
PENGU = "0x5AEc03C90656743475810926B2B2bd443D5c26a4"
add("pengu_totalMinted", PENGU, "totalMinted()")
add("pengu_freeMinted", PENGU, "freeMinted()")
add("pengu_FREE_CAP", PENGU, "FREE_CAP()")
add("pengu_mintOpen", PENGU, "mintOpen()")
add("pengu_freeClaimed", PENGU, "freeClaimed(address)", [U])
add("pengu_mintsBy", PENGU, "mintsBy(address)", [U])
add("pengu_balanceOf", PENGU, "balanceOf(address)", [U])
WOOZ = "0xfF172b79d040faefA1Bf34B47151edc87130246E"
add("wooz_totalSnippets", WOOZ, "totalSnippets()")
add("wooz_currentCommit", WOOZ, "currentCommit()")
add("wooz_genesisOpen", WOOZ, "genesisOpen()")
AE77 = "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C"
AE07 = "0x07bD6DbbEf508ad83BA2C557ED979732488894A1"
for tag, a in [("ae77", AE77), ("ae07", AE07)]:
    add(tag + "_totalSupply", a, "totalSupply()")
    add(tag + "_freeMinted", a, "freeMinted()")
    add(tag + "_freeRemaining", a, "freeRemaining()")
    add(tag + "_FREE_POOL", a, "FREE_POOL()")
    add(tag + "_saleActive", a, "saleActive()")
NOVA_R = "0x38C1695eb72B7522c8d6452a4CE27122532A0d69"
add("novar_totalRemnants", NOVA_R, "totalRemnants()")
add("novar_currentCycle", NOVA_R, "currentCycle()")
add("novar_genesisOpen", NOVA_R, "genesisOpen()")
add("novar_priceFor", NOVA_R, "priceFor(address)", [U])
ANOVA = "0x43462d7f269fde4914b03e1e07067a61b62b9540"
add("anova_totalSupply", ANOVA, "totalSupply()")
add("anova_freeMintedPerWallet", ANOVA, "freeMintedPerWallet(address)", [U])
add("anova_mintedPerWallet", ANOVA, "mintedPerWallet(address)", [U])
add("anova_balanceOf", ANOVA, "balanceOf(address)", [U])
LUMEN = "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4"
add("lumen_totalSpecimens", LUMEN, "totalSpecimens()")
add("lumen_currentExperiment", LUMEN, "currentExperiment()")
add("lumen_genesisOpen", LUMEN, "genesisOpen()")
add("lumen_priceFor", LUMEN, "priceFor(address)", [U])
LEDG = "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d"
add("ledg_totalSupply", LEDG, "totalSupply()")
add("ledg_freeClaimed", LEDG, "freeClaimed()")
add("ledg_FREE_SUPPLY", LEDG, "FREE_SUPPLY()")
add("ledg_mintOpen", LEDG, "mintOpen()")
add("ledg_mintedBy", LEDG, "mintedBy(address)", [U])
add("ledg_freeUsed", LEDG, "freeUsed(address)", [U])
add("ledg_balanceOf", LEDG, "balanceOf(address)", [U])
MAMI = "0xfe36c6d7a1e352cd0822c6818269d190e8e63c13"
INKI = "0x5ae38f527340e1aaf4ea214f9778bdc2266e2bd7"
for tag, a in [("mami", MAMI), ("inki", INKI)]:
    add(tag + "_totalSupply", a, "totalSupply()")
    add(tag + "_costOf1", a, "costOf(address,uint256)", [U, Q1])
    add(tag + "_mintedBy", a, "mintedBy(address)", [U])
    add(tag + "_balanceOf", a, "balanceOf(address)", [U])
    add(tag + "_mintOpen", a, "mintOpen()")
HADE = "0x5aff123300685b6e08aa4396227baf44aabbd4ed"
add("hade_totalSupply", HADE, "totalSupply()")
add("hade_MAX_SUPPLY", HADE, "MAX_SUPPLY()")
add("hade_mintOpen", HADE, "mintOpen()")
add("hade_mintedBy", HADE, "mintedBy(address)", [U])
add("hade_balanceOf", HADE, "balanceOf(address)", [U])
SPARK = "0xd52fd117c4b47d03e4e16e778871f09faa5a024b"
add("spark_totalSupply", SPARK, "totalSupply()")
add("spark_totalMinted", SPARK, "totalMinted()")
add("spark_paused", SPARK, "paused()")
add("spark_mintedByWallet", SPARK, "mintedByWallet(address)", [U])
add("spark_balanceOf", SPARK, "balanceOf(address)", [U])
ORBIT = "0x7d5F7f323db3050AF92E9aa1584E883B3b24d680"
add("orbit_freeClaimed", ORBIT, "freeClaimed()")
add("orbit_totalSupply", ORBIT, "totalSupply()")
BRAVO = "0xd57a06f0c37e303704261080Fc884f7BE941331D"
add("bravo_freeClaimed", BRAVO, "freeClaimed()")
add("bravo_totalSupply", BRAVO, "totalSupply()")
BINAI = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
add("binai_launched", BINAI, "launched()")
add("binai_failed", BINAI, "failed()")
add("binai_isRefundPhase", BINAI, "isRefundPhase()")
add("binai_totalShares", BINAI, "totalShares()")
add("binai_tokenClaimed", BINAI, "tokenClaimed(address)", [U])

t0 = time.time()
try:
    block = race("eth_blockNumber", ["latest"])
    log["legs"]["reread_block"] = to_int(block)
except Exception as e:
    log["legs"]["reread_block"] = f"error {e}"[:120]
try:
    res = call_many([c for _, c in READS])
    vals = {}
    if isinstance(res, dict):
        res = [res.get(i) for i in range(len(READS))]
    for (label, _), r in zip(READS, res):
        vals[label] = to_int(r)
    log["legs"]["reread"] = {"ok": True, "n": len(READS), "elapsed_s": round(time.time() - t0, 1), "vals": vals}
except Exception as e:
    log["legs"]["reread"] = {"ok": False, "error": str(e)[:300]}

# record genuinely new contracts in hot-leg-seen.json
now = "2026-11-14T14:54:00+07:00"
added = {}
for a in new_all:
    key = a if a in seen else next((k for k in seen if k.lower() == a.lower()), a)
    if key not in seen and a.lower() not in seen_lower:
        sc = shape.get(a, {})
        seen[a] = {"first_seen_wib": now, "source": "sourcify-feed" if a in log["legs"]["feed"].get("new", []) else "boltbook",
                   "status": "checked-not-sale-shape" if not (sc.get("S1") or sc.get("S2")) else "NEW-SALE-SHAPE-NEEDS-TRIAGE",
                   "note": json.dumps(sc)[:400]}
        added[a] = seen[a]
if added:
    json.dump(seen, open(HF + "hot-leg-seen.json", "w"), indent=1)
log["legs"]["seen_added"] = list(added.keys())
json.dump(log, open(HF + f"hot-leg-run-{RUN}.json", "w"), indent=1)
print(json.dumps(log, indent=1)[:12000])
