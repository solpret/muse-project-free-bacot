#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-15 00:14 WIB.
Legs (1) Sourcify feed, (2) Boltbook en+zh (curl), (3) shape-check new feed
contracts, (4) re-read snapshot focus set + GUARD 0xB8b7 (watchlist-only,
age-unverified at 19:24) via batch eth_call, bridge read-only.
Read-only except hot-leg-seen.json update + run outputs."""
import json, re, subprocess, time, urllib.request, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-0014"
NOW = time.strftime("%Y-%m-%dT%H:%M+07:00", time.gmtime(time.time()+7*3600))
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()
out = {"run": "free-mint-hot-leg " + NOW, "started_wib": NOW,
       "executed_wib": time.strftime("%Y-%m-%dT%H:%M+07:00", time.gmtime(time.time()+7*3600))}

def get(url, timeout=25, ua="free-mint-hot-leg/0014"):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def curl_get(url, timeout=25):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, timeout=timeout + 10)
    return r.stdout

# --- seen (case-insensitive index) ---
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_n_prev = len(seen)
seen_lower = {k.lower() for k in seen}

# --- (1) Sourcify feed ---
feed = None
try:
    raw = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25)
    feed = json.loads(raw.decode())
    json.dump(feed, open(BASE + "run-" + TAG + "-sourcify.json", "w"), indent=1)
    results = feed.get("results", [])
    feed_addrs = [r["address"] for r in results]
    new_feed = [a for a in feed_addrs if a.lower() not in seen_lower]
    out["sourcify_feed"] = {"total": len(results), "new": len(new_feed),
                            "new_contracts": new_feed,
                            "top": feed_addrs[0] if feed_addrs else None,
                            "top_verifiedAt": results[0].get("verifiedAt") if results else None}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
    feed_addrs, new_feed = [], []

# --- (2) Boltbook en + zh (curl) ---
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
for lang, fn in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    key = "boltbook_" + lang
    try:
        html = curl_get(fn, timeout=25).decode(errors="replace")
        open(BASE + "run-" + TAG + "-boltbook-" + lang + ".html", "w").write(html)
        addrs = sorted(set(ADDR_RE.findall(html)))
        newb = [a for a in addrs if a.lower() not in seen_lower]
        out[key] = {"bytes": len(html), "full_address_contracts": len(addrs), "new": len(newb),
                    "new_contracts": newb}
    except Exception as e:
        out[key] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- (3) shape-check new feed contracts ---
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=20).decode())
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in names
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "n_fns": len(names), "status": "checked"}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}

boltbook_new = []
for key in ("boltbook_en", "boltbook_zh"):
    for a in (out.get(key, {}) or {}).get("new_contracts", []):
        if a not in boltbook_new:
            boltbook_new.append(a)
# retry ONLY recent failures (first seen <24h ago), max 20/run: the 2214 run
# retried ALL 319 historic 404s and blew the <2-min target (236.6s).
_retry_all = [(a, v) for a, v in seen.items() if isinstance(v, dict) and v.get("status") == "shape-check-failed"]
from datetime import datetime as _dt, timedelta as _td
_now = _dt.strptime(NOW, "%Y-%m-%dT%H:%M+07:00")
def _recent(v):
    try: return (_now - _dt.strptime(v.get("first_seen_wib","")[:16], "%Y-%m-%dT%H:%M")) < _td(hours=24)
    except Exception: return False
retry = [a for a, v in _retry_all if _recent(v)][:20]
out["shape_retry_pool"] = len(_retry_all)
to_shape = list(dict.fromkeys(list(new_feed) + boltbook_new + retry))
out["shape_retry"] = retry
shapes = []
if to_shape:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        shapes = list(ex.map(shape, to_shape))
out["shape_check_targets"] = to_shape
va = {r["address"]: r.get("verifiedAt") for r in (feed.get("results", []) if isinstance(feed, dict) else [])}
for s in shapes:
    s["verifiedAt"] = va.get(s["address"])
out["shape_check"] = shapes
out["shape_hits"] = [s["address"] for s in shapes if s.get("S1") or s.get("S2")]

# --- bridge (read-only) ---
def collect_addrs(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and re.fullmatch(r"0x[0-9a-fA-F]{40}", k):
                acc.add(k.lower())
            collect_addrs(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect_addrs(v, acc)
    elif isinstance(obj, str) and re.fullmatch(r"0x[0-9a-fA-F]{40}", obj):
        acc.add(obj.lower())

try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    cons = bridge.get("contracts", {})
    snap = set()
    try:
        snapj = json.load(open(BASE + "onchain-snapshot.json"))
        collect_addrs(snapj, snap)
    except Exception as e:
        out["bridge_snapshot_error"] = str(e)[:150]
    not_in_snap = [a for a in cons if a.lower() not in snap]
    out["bridge"] = {"contracts": len(cons),
                     "same_owner_discarded": sum(1 for c in cons.values() if c.get("same_owner_discarded")),
                     "not_in_snapshot": len(not_in_snap),
                     "not_in_snapshot_list": not_in_snap[:10]}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- (4) re-read snapshot focus set + GUARD (batch eth_call) ---
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
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
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(r)

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
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
    ("mintedBy_user","mintedBy(address)",U),("hasAgentId_user","hasAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "LumenFindings": ("0x4158B701EaA30E8FaDBaA526F70780A38318c1C4", [
    ("totalSpecimens","totalSpecimens()",[]),("currentExperiment","currentExperiment()",[]),
    ("genesisOpen","genesisOpen()",[]),("genesisStart","genesisStart()",[]),
    ("priceFor_user","priceFor(address)",U),("holdsAgentId_user","holdsAgentId(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("mintsBy_user","mintsBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "CPASS": ("0x5877d2bb9f226cc3e438f4d656caeb27deafc576", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("priceFor_user","priceFor(address)",U),("mintCountOf_user","mintCountOf(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "ORBIT": ("0x7d5F7f323db3050AF92E9aa1584E883B3b24d680", [
    ("freeClaimed","freeClaimed()",[]),("FREE_MAX","FREE_MAX()",[]),
    ("claimOpen","claimOpen()",[]),("hasFreeClaimed_user","hasFreeClaimed(address)",U),
    ("totalSupply","totalSupply()",[])]),
 "SPEC": ("0x639329f5dc4317c44D9Fed961a1217ba845012F7", [
    ("totalSpecimens","totalSpecimens()",[]),("currentExperiment","currentExperiment()",[]),
    ("genesisOpen","genesisOpen()",[]),("genesisStart","genesisStart()",[])]),
 "TrashBandits": ("0x2d61347D9b48De99cBdF0D8D7a2DD73f5B15E90D", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "REOPIR": ("0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintedBy_user","mintedBy(address)",U),
    ("freeUsed_user","freeUsed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "FrieAgent-B751": ("0xb7517e3b31107695f2f8837fafc76999b956c871", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "FrieAgent-c64d": ("0xc64da7479c5abc8e6dfadeb4d17502ebcf9837e5", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "MAMI": ("0xfe36c6d7a1e352cd0822c6818269d190e8e63c13", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "INKI": ("0x5ae38f527340e1aaf4ea214f9778bdc2266e2bd7", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "HashcatDepot": ("0x5aff123300685b6e08aa4396227baf44aabbd4ed", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintsLeft","mintsLeft()",[]),("mintedBy_user","mintedBy(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "OTV": ("0xfab9c88d25e111edd68a2cca3e0f650863a5bf25", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("FREE_MINT_CAP","FREE_MINT_CAP()",[]),("freeMintsLeft","freeMintsLeft()",[]),
    ("PRICE","PRICE()",[]),("mintOpen","mintOpen()",[])]),
 "RAVE": ("0x7c40B78992d86EDfFB5553C74dB5EF427100bb95", [
    ("totalMinted","totalMinted()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("mintsBy_user","mintsBy(address)",U),
    ("holdsAgentId_user","holdsAgentId(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "HANAMI": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("freeSharesLeft","freeSharesLeft()",[]),("openedAt","openedAt()",[]),
    ("freeClaimed","freeClaimed()",[]),("freeBooked_user","freeBooked(address)",U)]),
 "PIXEL FROGS": ("0x454054e55FA2D7Ba37df7F3ceA269696f19037dF", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeLeft","freeLeft()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintStart","mintStart()",[]),("freeClaimed_user","freeClaimed(address)",U),
    ("balanceOf_user","balanceOf(address)",U)]),
 "GUARD": ("0xB8b7eF8D49981F8987Dfc271DCa50E24ce87AbEb", [
    ("totalMinted","totalMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("freeBlock","freeBlock()",[]),("maxSupply","maxSupply()",[]),
    ("mintOpenTimestamp","mintOpenTimestamp()",[]),("mintPaused","mintPaused()",[]),
    ("price","price()",[]),("freeUsed_user","freeUsed(address)",U),
    ("mintedBy_user","mintedBy(address)",U),("balanceOf_user","balanceOf(address)",U)]),
}

def chunked(items, n=3):
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
            o = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    o.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    o.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return o, ep
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
for ci, ch in enumerate(chunked(ITEMS, 3)):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"chunk {ci+1} FAIL {names}", flush=True)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"chunk {ci+1} OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(2)
blk = block_number()
reread = {"started_wib": NOW, "reads": reads, "reads_ok": ok,
          "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(reread, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)
out["reread"] = {"reads_ok": ok, "reads_total": len(ITEMS), "block": blk,
                 "elapsed_s": reread["elapsed_s"]}

# --- diff vs 23:34 re-read ---
try:
    prev = json.load(open(BASE + "run-2026-11-15-0009-reread.json"))
    prev_reads = prev.get("reads", {})
    changes = []
    for name, cur in reads.items():
        pv = (prev_reads.get(name) or {}).get("views") or {}
        cv = cur.get("views") or {}
        for k, v in cv.items():
            if pv.get(k) != v:
                changes.append({"contract": name, "view": k, "prev": pv.get(k), "now": v})
    out["reread_changes_vs_0009"] = changes
    out["reread_prev_block"] = prev.get("block")
except Exception as e:
    out["reread_diff_error"] = str(e)[:200]

# --- update seen with genuinely new contracts (feed + boltbook) ---
added = 0
for a in list(dict.fromkeys(list(new_feed) + boltbook_new)):
    if a.lower() not in seen_lower:
        st = "SALE-SHAPE" if any(s.get("address") == a and (s.get("S1") or s.get("S2")) for s in shapes) else "checked-not-sale-shape"
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed" if a in new_feed else "boltbook-en+zh", "status": st,
                   "note": str([s for s in shapes if s.get("address") == a])[:300]}
        seen_lower.add(a.lower()); added += 1
updated_retry = 0
for a in retry:
    s = [x for x in shapes if x.get("address") == a]
    if s:
        st = "SALE-SHAPE" if (s[0].get("S1") or s[0].get("S2")) else ("checked-not-sale-shape" if "error" not in s[0] else "shape-check-failed")
        seen[a] = {"first_seen_wib": seen[a].get("first_seen_wib", NOW), "source": seen[a].get("source", "sourcify-feed"),
                   "status": st, "note": str(s)[:300]}
        updated_retry += 1
out["seen_retry_updated"] = updated_retry
if added or updated_retry:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
out["seen_added"] = added
out["seen_n"] = len(seen)
out["seen_n_prev"] = seen_n_prev
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print(json.dumps(out, indent=1))
