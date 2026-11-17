#!/usr/bin/env python3
"""Hot-leg run 2026-11-08 10:54 WIB. Read-only except own hot-leg state files.
Legs: (1) Sourcify feed shape-check, (2) Boltbook EN+ZH, (3) n/a unless sale-shape,
(4) snapshot re-read (same 26 items as 1009), bridge complement check.
Target <2 min; a stalled leg is skipped, never waited on."""
import json, re, sys, time, urllib.request, concurrent.futures, subprocess, os
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1054"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EPS = ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()
log = {"run": "free-mint-hot-leg 2026-11-08 10:54:38 WIB"}

def get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

def curl(url, timeout=15):
    return subprocess.run(["curl","-sL","--max-time",str(timeout),url],
                          capture_output=True, text=True).stdout

# ---------- leg 1: Sourcify feed ----------
seen = json.load(open(BASE+"hot-leg-seen.json"))
seen_lower = {k.lower(): k for k in seen}
def is_seen(a): return a.lower() in seen_lower
feed_addrs = []
try:
    feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15))
    json.dump(feed, open(BASE+TAG+"-sourcify.json","w"), indent=1)
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    for e in results:
        a = e if isinstance(e, str) else (e.get("address") or (e.get("contract") or {}).get("address"))
        if a: feed_addrs.append(a)
    log["leg1_feed"] = {"n": len(feed_addrs), "addrs": feed_addrs}
except Exception as ex:
    log["leg1_feed"] = {"error": f"{type(ex).__name__}: {str(ex)[:160]}", "skipped": True}

def shape(addr):
    try:
        out = subprocess.run(["curl","-sL","--max-time","20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True).stdout
        meta = json.loads(out)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
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
        return {"address": addr, "abi_functions": sorted(names), "S1": s1, "S2": s2,
                "mint": has_mint, "quote": has_quote, "free": free_views, "agent": agent_ref, "token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

def record(addr, source, status, note):
    seen[addr] = {"first_seen_wib": "2026-11-08T10:54:00+07:00", "source": source,
                  "status": status, "note": note}
    seen_lower[addr.lower()] = addr

new1 = [a for a in feed_addrs if not is_seen(a) and a.lower() not in EXCLUDED]
excl1 = [a for a in feed_addrs if a.lower() in EXCLUDED]
shapes1 = []
if new1:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        shapes1 = list(ex.map(shape, new1))
    for s in shapes1:
        a = s["address"]
        if s.get("error") or not s.get("abi_functions"):
            continue  # retry next run; do not record
        if (s.get("S1") or s.get("S2")) and "ownerOf" in (s.get("abi_functions") or []):
            record(a, "sourcify-feed", "checked-not-track-c",
                   f"S1={s['S1']} S2={s['S2']} BUT ERC-721 NFT, not fungible share sale.")
        elif s.get("S1") or s.get("S2"):
            record(a, "sourcify-feed", "sale-shape-pass",
                   f"S1={s['S1']} S2={s['S2']} fns={s['abi_functions']}")
        else:
            record(a, "sourcify-feed", "checked-not-sale-shape",
                   f"S1={s['S1']} S2={s['S2']} mint={s['mint']} quote={s['quote']} free={s['free']} agent={s['agent']} token={s['token']}")
json.dump(shapes1, open(BASE+TAG+"-sourcify-shape.json","w"), indent=1)
log["leg1"] = {"new": new1, "new_excluded_rediscovered": excl1, "shapes": shapes1,
               "seen_total": len(seen)}

# ---------- leg 2: Boltbook EN + ZH ----------
snap = json.load(open(BASE+"onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address","sale","token"):
            if v.get(f): snap_addrs.add(v[f].lower())
KW_EN = ["free share","first share free","1 free share","free mint share"]
KW_ZH = ["免费份额","首个免费","免费铸造","免费mint"]
bolt = {}
for lang in ("en","zh"):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    html = ""
    rc = -1
    try:
        html = curl(url, timeout=15); rc = 0 if html else -1
    except Exception as ex:
        rc = -2
    open(BASE+TAG+f"-boltbook-{lang}.html","w").write(html)
    found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    kws = {}
    low = html.lower()
    for k in (KW_EN if lang=="en" else KW_ZH):
        kws[k] = low.count(k.lower())
    newfound = [a for a in found if not is_seen(a) and a.lower() not in EXCLUDED
                and a.lower() != REGISTRY]
    new_vs_snap = [a for a in newfound if a.lower() not in snap_addrs]
    sc = {}
    for a in new_vs_snap:
        try:
            code = batch([("eth_getCode", [a, "latest"])], endpoint=EPS[0], timeout=8)[0]
        except Exception:
            code = None
        if code == "0x":
            record(a, f"boltbook-{lang}", "checked-not-contract",
                   "eth_getCode 0x on bsc-dataseed — EOA/wallet address mentioned in a Boltbook post, not a contract; no sale shape, not a lead.")
            sc[a] = {"S1": False, "S2": False, "note": "EOA, not a contract"}
            continue
        s = shape(a)
        sc[a] = s
        if s.get("error") or not s.get("abi_functions"):
            continue  # Sourcify 404 / unavailable -> not verified, not sale-shape; retry next run
        if (s.get("S1") or s.get("S2")) and "ownerOf" in (s.get("abi_functions") or []):
            record(a, f"boltbook-{lang}", "checked-not-track-c",
                   f"S1={s['S1']} S2={s['S2']} BUT ERC-721 NFT, not fungible share sale.")
        elif s.get("S1") or s.get("S2"):
            record(a, f"boltbook-{lang}", "sale-shape-pass",
                   f"S1={s['S1']} S2={s['S2']} fns={s['abi_functions']}")
        else:
            record(a, f"boltbook-{lang}", "checked-not-sale-shape",
                   f"S1={s['S1']} S2={s['S2']} mint={s['mint']} quote={s['quote']} free={s['free']} agent={s['agent']} token={s['token']}")
    bolt[lang] = {"bytes": len(html), "rc": rc, "addrs": len(found), "keyword_hits": kws,
                  "new_vs_seen": newfound, "new_vs_snapshot": new_vs_snap,
                  "shape_check": {a: {"S1": s.get("S1"), "S2": s.get("S2"),
                                      "error": s.get("error"),
                                      "note": s.get("error") or f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')} token={s.get('token')}"}
                                  for a, s in sc.items()}}
    if lang == "en":
        bolt["en_addrs"] = len(found)
log["leg2_boltbook"] = bolt
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
log["seen_total_after"] = len(seen)

# ---------- leg 4: snapshot re-read (same 26 items as 1009) ----------
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    elif arg == "USER1": data += enc_addr(USER) + format(1, "064x")
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=8)
            return to_int(res[0])
        except Exception:
            continue
    return None

# (key, sig, arg) per item, mirroring 0939 reread.json fields
V = {
 "freeMinted": ("freeMinted()", ""), "FREE_CAP": ("FREE_CAP()", ""),
 "freeCount_user": ("freeCount(address)", "USER"), "mintOpen": ("mintOpen()", ""),
 "balanceOf_user": ("balanceOf(address)", "USER"), "totalSupply": ("totalSupply()", ""),
 "totalMinted": ("totalMinted()", ""), "FREE_SUPPLY": ("FREE_SUPPLY()", ""),
 "FREE_SHARES": ("FREE_SHARES()", ""), "finalized": ("finalized()", ""),
 "freeLeft": ("freeLeft()", ""), "freeClaimed": ("freeClaimed()", ""),
 "freeClaimed_user": ("freeClaimed(address)", "USER"),
 "freeLeft_user": ("freeLeft(address)", "USER"), "freeUsed_user": ("freeUsed(address)", "USER"),
 "freeFor_user1": ("freeFor(address,uint256)", "USER1"),
 "quote_user1": ("quote(address,uint256)", "USER1"),
 "priceFor_user": ("priceFor(address)", "USER"),
 "mintedBy_user": ("mintedBy(address)", "USER"), "freeUsed": ("freeUsed()", ""),
 "freeTakenBy_user": ("freeTakenBy(address)", "USER"), "mintActive": ("mintActive()", ""),
 "freeMintedTotal": ("freeMintedTotal()", ""), "freeMinted_user": ("freeMinted(address)", "USER"),
 "mintedCount_user": ("mintedCount(address)", "USER"), "totalMints": ("totalMints()", ""),
 "MAX_SUPPLY": ("MAX_SUPPLY()", ""), "FREE_QUOTA": ("FREE_QUOTA()", ""),
 "remainingFree": ("remainingFree()", ""), "phase": ("phase()", ""),
 "launched": ("launched()", ""), "sold": ("sold()", ""),
 "FREE_PER_WALLET": ("FREE_PER_WALLET()", ""),
}
ITEMS = {
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", ["freeMinted","FREE_CAP","freeCount_user","mintOpen","balanceOf_user"]),
 "WAR3": ("0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe", ["freeMinted","totalSupply","balanceOf_user"]),
 "HUNT PASS": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD", ["totalMinted","FREE_SUPPLY","freeMinted","balanceOf_user","mintedBy_user"]),
 "fab7-variant": ("0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72", ["freeMinted","FREE_SHARES","totalMinted","finalized"]),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", ["freeMinted","FREE_SUPPLY","freeClaimed_user"]),
 "LOCKSMITH": ("0x05e8738290be6639fD0f7236ebF444E5466D3164", ["totalMinted","freeMintedTotal","FREE_CAP","mintActive"]),
 "HOG ORBIT": ("0x7bc0b487febcbb1caa781148bf05a8cd72d02ec5", ["freeLeft","totalSupply","balanceOf_user"]),
 "AgentBook": ("0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0", ["FREE_QUOTA","remainingFree"]),
 "Night Bandits Club": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", ["freeUsed","freeTakenBy_user"]),
 "Ink Koi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", ["freeMinted","freeClaimed_user"]),
 "AURISLE": ("0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D", ["freeMinted","FREE_SUPPLY","freeClaimed_user"]),
 "CipherAgent": ("0x158b5e25015758a94703A27c152889451E5d52E5", ["totalMints","mintOpen","balanceOf_user"]),
 "MarsAgent": ("0x2231FdAe405c33dc4993f8C577c453802FF1AcE9", ["totalMints","mintOpen","balanceOf_user"]),
 "OnlyAI": ("0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba", ["totalSupply","balanceOf_user"]),
 "Gloops": ("0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE", ["totalMinted","mintOpen"]),
 "Saturnagent": ("0xef870a9b4a529373fb2e174b59ca7a66eb018074", ["freeClaimed","quote_user1"]),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f", ["freeClaimed","quote_user1"]),
 "Ninetailix": ("0x809215729bcbff2ef31dea5efd6c12a6b788ba9a", ["totalSupply","freeClaimed","FREE_SUPPLY","freeLeft_user","freeUsed_user","freeFor_user1","quote_user1","balanceOf_user","mintOpen"]),
 "REWARD": ("0xcfe5e4925a76a3aa11afa79e04c6fad3611cee40", ["freeMintedTotal","FREE_CAP","totalMinted","mintActive","freeMinted_user","mintedCount_user"]),
 "AgentSeat": ("0x3c1daedd9c9a4318e858229dd44608d3d5003d4b", ["totalSupply","MAX_SUPPLY","FREE_SUPPLY","priceFor_user","mintedBy_user","balanceOf_user"]),
 "Pumpkinfarm": ("0x77e38295603a06654a6ed3ed0849e6aa50749963", ["totalSupply","FREE_SUPPLY","freeClaimed","mintOpen","FREE_PER_WALLET","freeLeft_user","freeUsed_user","freeFor_user1","quote_user1","balanceOf_user"]),
 "Ghostling": ("0x6a4847cb5f658943222fbd23d2520049f824789d", ["freeClaimed","FREE_SUPPLY","freeLeft_user","freeUsed_user","mintedBy_user","balanceOf_user","freeFor_user1","quote_user1","mintOpen"]),
 "KAGENT": ("0xb34105002B19EF0ce43B59011fE848df5c8B174f", ["phase","launched","sold","freeClaimed","balanceOf_user"]),
 "Dafeiyu": ("0xD8DE64ACB25A87D98F1E170BF082a01427772511", ["totalSupply","FREE_SUPPLY","freeClaimed","freeMinted","mintOpen","balanceOf_user"]),
 "HokiKoi": ("0x74055b4Afe2d8c7347e8D4c0fc23e704405F7A36", ["freeMinted","FREE_CAP","mintOpen","balanceOf_user","freeCount_user"]),
 "Jinli Agents": ("0x0f45b52f80a3a42e56e66Cd8CFd1A65895c34496", ["freeClaimed","FREE_SUPPLY","totalSupply","mintOpen","balanceOf_user"]),
}
def do_item(name):
    addr, keys = ITEMS[name]
    out = {"address": addr}
    for k in keys:
        sig, arg = V[k]
        out[k] = single(addr, sig, arg)
    return name, out
try:
    blk = int(batch([("eth_blockNumber", [])], endpoint=EPS[0], timeout=8)[0], 16)
except Exception as ex:
    blk = None
    log["leg4_block_error"] = str(ex)[:120]
items = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for name, out in ex.map(do_item, ITEMS):
        items[name] = out
reread = {"block": blk, "items": items}
json.dump(reread, open(BASE+TAG+"-reread.json","w"), indent=1)
log["leg4"] = {"block": blk, "n": len(items)}

# diff vs 1019 reread
import glob as _glob
_prev_files = sorted([f for f in _glob.glob(BASE+"hot-leg-*-reread.json") if TAG not in f])
prev = json.load(open(_prev_files[-1])) if _prev_files else {"items": {}}
log["leg4_diff_prev_file"] = _prev_files[-1].split("/")[-1] if _prev_files else None
diffs = []
for name, cur in items.items():
    old = prev["items"].get(name, {})
    for k, v in cur.items():
        if k == "address": continue
        ov = old.get(k)
        if v != ov:
            diffs.append({"item": name, "field": k, "old": ov, "new": v})
log["leg4_diff_vs_prev"] = diffs

# ---------- leg 3b: PANDORA re-check (first mint seen at 1049, 32/5555 = 0.58%) ----------
# Early-lead detection stays with the main job's scan leg; this only re-reads
# whether a first mint has occurred since 1049 (would make launch age verifiable).
PANDORA = "0xdb8A4102C49a41cfAeD7673A3F155f19853Af5e8"
pandora = {"address": PANDORA}
for _k, _sig in {"totalMinted": "totalMinted()", "totalSupply": "totalSupply()",
                 "mintActive": "mintActive()", "publicRemaining": "publicRemaining()",
                 "freeUsed_user": "freeUsed(address)"}.items():
    _arg = "USER" if _k == "freeUsed_user" else ""
    pandora[_k] = single(PANDORA, _sig, _arg)
log["leg3b_pandora"] = pandora

# ---------- bridge complement leg ----------
bridge = json.load(open(BASE+"scan-bridge.json"))
bcontracts = bridge.get("contracts", {})
log["bridge"] = {"n_contracts": len(bcontracts),
                 "mtime": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(os.path.getmtime(BASE+"scan-bridge.json"))),
                 "note": "read-only; promotions only if a bridge contract already in snapshot newly meets a tier — none checked this run beyond count/mtime."}
# bridge contracts already in snapshot: check against snapshot addresses
snap_low = {a for a in snap_addrs}
bridge_in_snap = [a for a in bcontracts if a.lower() in snap_low]
log["bridge"]["in_snapshot"] = len(bridge_in_snap)

log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE+TAG+".log","w"), indent=1)
print(json.dumps(log, indent=1)[:6000])
print("ELAPSED", round(time.time()-t0, 1))
