#!/usr/bin/env python3
"""Discovery leg run 2026-11-08 12:01 WIB (free-mint-search).
READ-ONLY. Never writes snapshot/seen/scan-bridge. Own outputs only:
run-2026-11-08-1201-discovery.json + -summary.txt.
Routes: 2 Boltbook EN+ZH, 5a Sourcify feed, on-chain verify of genuinely new contracts.
"""
import json, re, sys, time, urllib.request, concurrent.futures, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "run-2026-11-08-1201-discovery"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EPS = ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()
out = {"run": "free-mint-search 2026-11-08 12:01 WIB discovery (routes 2, 5a + on-chain verify)",
       "generated_wib": "2026-11-08 ~12:2x WIB", "routes": {}}

def get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-discovery/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

def curl(url, timeout=20):
    return subprocess.run(["curl","-sL","--max-time",str(timeout),url],
                          capture_output=True, text=True).stdout

# known sets (read-only)
snap = json.load(open(BASE+"onchain-snapshot.json"))
snap_addrs = set()
snap_by_addr = {}
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address","sale","token"):
            if v.get(f):
                snap_addrs.add(v[f].lower()); snap_by_addr[v[f].lower()] = v
seen = json.load(open(BASE+"onchain-scan-seen.json"))["contracts"]
seen_lower = {k.lower() for k in seen}
try:
    hl = json.load(open(BASE+"hot-leg-seen.json"))
    hl_lower = {k.lower() for k in hl}
except Exception:
    hl_lower = set()
def known(a):
    return a.lower() in snap_addrs or a.lower() in seen_lower or a.lower() in hl_lower

# ---------- shape() via Sourcify ----------
def shape(addr):
    try:
        try:
            raw = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        except Exception:
            raw = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=25)
        d = json.loads(raw)
        abi = d.get("abi") or (d.get("contract") or {}).get("abi") or []
        if not abi and isinstance(d, dict) and d.get("stdJson"):
            abi = d["stdJson"].get("output",{}).get("contracts",{})
        fns = {}
        for e in (abi if isinstance(abi, list) else []):
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names) or bool(names & {"claimFreeShare","claimFree","claim"})
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","REGISTRY","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","AGENT_REGISTRY","hasAgentId"})
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        nft_shaped = bool(names & {"ownerOf","tokenURI"}) and has_mint
        return {"address": addr, "verified": True, "abi_functions": sorted(names), "S1": s1, "S2": s2,
                "mint": has_mint, "quote": has_quote, "free": free_views, "agent": agent_ref,
                "token": is_token, "nft_shaped": nft_shaped}
    except Exception as ex:
        return {"address": addr, "verified": False, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

# ---------- route 5a: Sourcify feed ----------
feed_addrs = []
try:
    feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15))
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    for e in results:
        a = e if isinstance(e, str) else (e.get("address") or (e.get("contract") or {}).get("address"))
        if a: feed_addrs.append(a)
    out["routes"]["5a_sourcify"] = {"n": len(feed_addrs), "addrs": feed_addrs, "error": None}
except Exception as ex:
    out["routes"]["5a_sourcify"] = {"n": 0, "addrs": [], "error": f"{type(ex).__name__}: {str(ex)[:160]}"}

new5a = [a for a in feed_addrs if not known(a) and a.lower() not in EXCLUDED and a.lower() != REGISTRY]
excl5a = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes5a = []
if new5a:
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        shapes5a = list(ex.map(shape, new5a))
out["routes"]["5a_sourcify"]["new_vs_known"] = new5a
out["routes"]["5a_sourcify"]["excluded_rediscovered"] = excl5a
out["routes"]["5a_sourcify"]["shapes"] = shapes5a

# ---------- route 2: Boltbook EN + ZH ----------
KW_EN = ["free share","first share free","1 free share","free mint share"]
KW_ZH = ["免费份额","首个免费","免费铸造","免费mint"]
bolt = {}
for lang in ("en","zh"):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    html = ""
    try:
        html = curl(url, timeout=20)
        if not html: html = curl(url, timeout=30)
    except Exception as ex:
        bolt[lang] = {"error": f"{type(ex).__name__}: {str(ex)[:120]}"}
        continue
    open(BASE+TAG+f"-boltbook-{lang}.html","w").write(html)
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    low = html.lower()
    kws = {k: low.count(k.lower()) for k in (KW_EN if lang=="en" else KW_ZH)}
    newfound = [a for a in found if not known(a) and a.lower() not in EXCLUDED and a.lower() != REGISTRY]
    new_vs_snap = [a for a in newfound if a.lower() not in snap_addrs]
    sc = {}
    for a in new_vs_snap:
        sc[a] = shape(a)
    bolt[lang] = {"bytes": len(html), "addrs_found": len(found), "keyword_hits": kws,
                  "new_vs_known": newfound, "new_vs_snapshot": new_vs_snap,
                  "shape_check": sc}
out["routes"]["2_boltbook"] = bolt

# ---------- on-chain verify genuinely new contracts ----------
# Candidates: any address new vs snapshot from routes 2/5a with a verified ABI shape
# (agent-shaped NFT or sale shape). Unverified (empty ABI) -> retry next run, no verify.
verify_addrs = []
for s in shapes5a:
    if s.get("verified") and (s.get("S1") or s.get("S2") or s.get("nft_shaped")):
        verify_addrs.append(s["address"])
for lang in ("en","zh"):
    for a, s in (bolt.get(lang,{}).get("shape_check") or {}).items():
        if s.get("verified") and (s.get("S1") or s.get("S2") or s.get("nft_shaped")) and a not in verify_addrs:
            verify_addrs.append(a)

def enc(fn, *args):
    # minimal ABI encoding for common view fns
    import hashlib
    try:
        from eth_utils import keccak
        sel = keccak(text=fn)[:4].hex()
    except Exception:
        import sha3
        sel = sha3.keccak_256(fn.encode()).hexdigest()[:8]
    data = "0x" + sel
    for a in args:
        if isinstance(a, str) and a.startswith("0x"):
            data += a[2:].rjust(64, "0")
        else:
            data += format(int(a), "064x")
    return data

VIEWS = [
    ("totalSupply", "totalSupply()", []),
    ("totalMinted", "totalMinted()", []),
    ("freeClaimed", "freeClaimed()", []),
    ("freeLeft", "freeLeft()", []),
    ("freeSupply", "freeSupply()", []),
    ("FREE_SUPPLY", "FREE_SUPPLY()", []),
    ("MAX_SUPPLY", "MAX_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []),
    ("name", "name()", []),
    ("symbol", "symbol()", []),
    ("AGENT_ID", "AGENT_ID()", []),
    ("agentRegistry", "agentRegistry()", []),
    ("freeClaimed_user", "freeClaimed(address)", [USER]),
    ("freeUsed_user", "freeUsed(address)", [USER]),
    ("mintedBy_user", "mintedBy(address)", [USER]),
    ("balanceOf_user", "balanceOf(address)", [USER]),
]
verified = {}
for addr in verify_addrs:
    calls = []
    for label, sig, args in VIEWS:
        calls.append(("eth_call", [{"to": addr, "data": enc(sig, *args)}, "latest"]))
    res = None
    for ep in EPS:
        try:
            res = batch(calls, endpoint=ep, timeout=15)
            break
        except Exception:
            continue
    entry = {"address": addr, "rpc_ok": res is not None}
    if res:
        for (label, sig, args), r in zip(VIEWS, res):
            if r is None: entry[label] = None; continue
            try:
                v = int(r, 16)
                entry[label] = v
            except Exception:
                # string return (name/symbol) or address
                try:
                    raw = bytes.fromhex(r[2:])
                    if label in ("name","symbol"):
                        # abi string: offset+len+data
                        ln = int.from_bytes(raw[32:64], "big")
                        entry[label] = raw[64:64+ln].decode(errors="replace")
                    elif label in ("AGENT_ID","agentRegistry"):
                        entry[label] = "0x" + raw[-20:].hex()
                    else:
                        entry[label] = r
                except Exception:
                    entry[label] = r
    verified[addr] = entry
out["onchain_verify"] = verified

# ---------- tiering ----------
tiers = []
for addr, v in verified.items():
    sh = None
    for s in shapes5a:
        if s["address"].lower() == addr.lower(): sh = s
    if sh is None:
        for lang in ("en","zh"):
            sc = bolt.get(lang,{}).get("shape_check") or {}
            for a, s in sc.items():
                if a.lower() == addr.lower(): sh = s
    agent_ok = bool(sh and sh.get("agent")) or (v.get("AGENT_ID") or "").lower() == REGISTRY or (v.get("agentRegistry") or "").lower() == REGISTRY
    free_total = v.get("FREE_SUPPLY") or v.get("freeSupply")
    free_claimed = v.get("freeClaimed")
    free_pct = None
    if free_total and free_claimed is not None:
        free_pct = round(100.0 * free_claimed / free_total, 2)
    total = v.get("totalSupply") if v.get("totalSupply") is not None else v.get("totalMinted")
    tiers.append({"address": addr, "name": v.get("name"), "symbol": v.get("symbol"),
                  "agent_shaped": agent_ok, "S1": bool(sh and sh.get("S1")), "S2": bool(sh and sh.get("S2")),
                  "nft_shaped": bool(sh and sh.get("nft_shaped")),
                  "totalSupply": total, "freeClaimed": free_claimed, "free_total": free_total,
                  "free_pct": free_pct, "mintOpen": v.get("mintOpen"),
                  "user_free_used": v.get("freeUsed_user"), "user_mintedBy": v.get("mintedBy_user"),
                  "user_balance": v.get("balanceOf_user"),
                  "tier": "UNVERIFIED-AGE" if not agent_ok else ("EARLY-candidate" if agent_ok and total is not None else "watchlist-only"),
                  "note": "age unverified (no project-stated launch time read this run); first-mint corroboration not run for discovery leg — parent re-read decides tier."})
out["tiering"] = tiers
out["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(out, open(BASE+TAG+".json","w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
print("ELAPSED", round(time.time()-t0, 1))
