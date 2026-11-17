#!/usr/bin/env python3
"""Hot-leg run 2026-11-08 14:09 WIB — legs 1+2 only (Sourcify feed + Boltbook EN/ZH).
Read-only except own hot-leg state files. Lean; a stalled leg is skipped.
NOTE: BSC public RPC was degraded at 11:29–11:44 but recovered ~11:52 WIB per the 1144 run;
status re-probed this run. Ankr multichain exposes no eth_call/eth_blockNumber.
A 0x eth_getCode on degraded RPC is INCONCLUSIVE: never record checked-not-contract
from it; fall through to the Sourcify ABI shape-check instead."""
import json, re, sys, time, urllib.request, concurrent.futures, subprocess, os
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-1409"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EPS = ["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()
log = {"run": "free-mint-hot-leg 2026-11-08 14:09:38 WIB legs1-2"}

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
    try:
        feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15))
    except Exception:
        feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25))
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
        out = subprocess.run(["curl","-sL","--max-time","30",
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
    seen[addr] = {"first_seen_wib": "2026-11-08T14:09:00+07:00", "source": source,
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
        html = curl(url, timeout=15)
        if not html:
            html = curl(url, timeout=25)
        rc = 0 if html else -1
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
        # RPC degraded this run: a 0x code read is INCONCLUSIVE (11:34 run proved it
        # can be a flaky read). Fall through to the Sourcify ABI shape-check; only
        # record checked-not-contract when the ABI is ALSO empty (unverified) AND
        # the code read was 0x — handled below via shape() returning no functions.
        if code == "0x":
            s = shape(a)
            sc[a] = s
            if s.get("error") or not s.get("abi_functions"):
                continue  # unverified + flaky code read: leave unrecorded, retry next run
            if (s.get("S1") or s.get("S2")) and "ownerOf" in (s.get("abi_functions") or []):
                record(a, f"boltbook-{lang}", "checked-not-track-c",
                       f"S1={s['S1']} S2={s['S2']} BUT ERC-721 NFT, not fungible share sale. (code 0x on degraded RPC disregarded; ABI evidence used.)")
            elif s.get("S1") or s.get("S2"):
                record(a, f"boltbook-{lang}", "sale-shape-pass",
                       f"S1={s['S1']} S2={s['S2']} fns={s['abi_functions']} (code 0x on degraded RPC disregarded; ABI evidence used.)")
            else:
                record(a, f"boltbook-{lang}", "checked-not-sale-shape",
                       f"S1={s['S1']} S2={s['S2']} mint={s['mint']} quote={s['quote']} free={s['free']} agent={s['agent']} token={s['token']} (code 0x on degraded RPC disregarded; ABI evidence used.)")
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
log["leg2_boltbook"] = bolt
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
log["seen_total_after"] = len(seen)
log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE+TAG+"-legs12.log","w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time()-t0, 1))
