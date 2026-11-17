#!/usr/bin/env python3
"""Hot-leg 0739: legs 1+2 (files fetched by background curl) + shape-check + bridge
+ MEMPL/BLOCK777 re-read + bounded leg-4 re-read. Read-only except hot-leg-seen.json."""
import json, re, subprocess, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0739"
T0 = time.time()
DEADLINE = 100
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MEMPL = "0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846"
B777 = "0x47529CF66091BeB0E8e0F78D5635e367473D52d5"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
FREE = ["freesharesremaining","freeclaimed","freefor","freeleft","freeused","freeavailable","freesharepoolexhausted","freesharesclaimed","freeminted","freemint","free_slots","free_supply","freeamount"]
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc-dataseed.binance.org",
        "https://bsc-dataseed1.defibit.io"]
WIB = timezone(timedelta(hours=7))
def now_wib():
    return datetime.now(WIB).isoformat(timespec="seconds")
NOW = now_wib()

def curl(url, timeout=25):
    p = subprocess.run(["curl","-s","-m",str(timeout),"-A","Mozilla/5.0",url],
                       capture_output=True, timeout=timeout+5)
    if p.returncode != 0 or not p.stdout: raise RuntimeError(f"curl rc={p.returncode}")
    return p.stdout

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def rpc_call(method, params, timeout=3):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    last = None
    for rpc in RPCS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    o = json.load(r)
                if "error" in o: return None
                return o.get("result")
            except Exception as e:
                last = f"err:{type(e).__name__}"; time.sleep(0.2)
    return last

def call(to, data, timeout=3):
    v = rpc_call("eth_call", [{"to":to,"data":data},"latest"], timeout)
    if v is None or v == "0x" or (isinstance(v,str) and v.startswith("err:")): return v
    try: return int(v, 16)
    except Exception: return v

def block_number():
    v = rpc_call("eth_blockNumber", [], 5)
    try: return int(v, 16)
    except Exception: return None

out = {"run": TS, "t0_wib": NOW}
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_lc = {k.lower(): k for k in seen}

# ---- Leg 1: Sourcify feed (file from background curl; fetch if absent) ----
try:
    feed = json.load(open(f"{BASE}/sourcify-feed-0739.json"))
    addrs1 = [r["address"] for r in feed.get("results", [])]
    out["leg1_source"] = "file"
except Exception as e:
    try:
        feed = json.loads(curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25))
        json.dump(feed, open(f"{BASE}/sourcify-feed-0739.json","w"), indent=1)
        addrs1 = [r["address"] for r in feed.get("results", [])]
        out["leg1_source"] = "refetch"
    except Exception as e2:
        feed = None; addrs1 = []; out["leg1_error"] = str(e2)
new1 = [a for a in addrs1 if a.lower() not in seen_lc and a.lower() != REG.lower() and a.lower() not in EXCLUDED]
out["leg1_feed"] = len(addrs1); out["leg1_new"] = new1
print("leg1 feed:", len(addrs1), "new:", new1, flush=True)

# ---- Leg 2: Boltbook EN+ZH (files from background curl) ----
addrs2 = []
for lang in ("en","zh"):
    try:
        html = open(f"{BASE}/boltbook-{lang}-0739.html", encoding="utf-8", errors="ignore").read()
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        print(f"leg2 {lang}: ok {len(html)} bytes, {len(found)} addrs", flush=True)
        addrs2 += found
    except Exception as e:
        print(f"leg2 {lang}: FAILED {e}", flush=True); out[f"leg2_{lang}_error"] = str(e)
addrs2 = sorted(set(addrs2))
new2 = [a for a in addrs2 if a.lower() not in seen_lc and a.lower() != REG.lower() and a.lower() not in EXCLUDED]
kw = ["免费份额","首个免费","免费铸造","免费mint","free share","first share free","1 free share","free mint share"]
kw_hits = {}
for lang in ("en","zh"):
    try:
        html = open(f"{BASE}/boltbook-{lang}-0739.html", encoding="utf-8", errors="ignore").read().lower()
        kw_hits[lang] = [k for k in kw if k.lower() in html]
    except Exception: kw_hits[lang] = "unreadable"
out["leg2_unique"] = len(addrs2); out["leg2_new"] = new2; out["leg2_kw"] = kw_hits
print("leg2 unique:", len(addrs2), "new:", new2, "kw:", kw_hits, flush=True)

# ---- Shape-check new ----
to_check = sorted(set([a.lower() for a in new1 + new2]))
shape = {}
for a in to_check:
    if time.time() - T0 > 55: shape[a] = {"error": "deadline-skip"}; continue
    abi = None; status = None
    for t in range(2):
        try:
            d = json.loads(curl(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 20))
            abi = d.get("abi") or []; status = "ok"; break
        except Exception as e:
            status = str(e); time.sleep(1)
    if abi is None:
        shape[a] = {"error": status}; continue
    fns = [f.get("name","") for f in abi if f.get("type")=="function"]
    src = json.dumps(abi).lower()
    mint = [f for f in fns if "mint" in f.lower()]
    quote = [f for f in fns if "quote" in f.lower() or "cost" in f.lower() or f.lower() in ("price","getprice")]
    free = [f for f in fns if any(k in f.lower() for k in FREE)]
    agent = [f for f in fns if "agent" in f.lower() or "registry" in f.lower()]
    token = [f for f in fns if f.lower() in ("name","symbol","decimals","totalsupply")]
    s1 = bool(mint) and bool(quote) and bool(free) and (REG.lower() in src or bool(agent))
    s2 = len(token)==4 and any("mintfree" in f.lower() for f in fns) and bool(free) and (REG.lower() in src or bool(agent))
    shape[a] = {"S1":s1,"S2":s2,"mint":mint,"quote":quote,"free":free,"agent":agent,"token":token,"n_fns":len(fns)}
    print(a,"S1",s1,"S2",s2,"mint",mint,"quote",quote,"free",free,"agent",agent, flush=True)
out["shape"] = shape
for a, s in shape.items():
    if "error" in s: continue
    if a not in seen_lc:
        seen[a] = {"first_seen_wib": NOW,
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={bool(s.get('mint'))} quote={bool(s.get('quote'))} free={s.get('free')} agent={bool(s.get('agent'))} token={s.get('token')}",
                   "source": "hot-leg-0739",
                   "status": "sale-shape" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json","w"), indent=1)
out["seen_total"] = len(seen)

# ---- Bridge (read-only) ----
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    contracts = bridge.get("contracts", {})
    snap_text = open(f"{BASE}/onchain-snapshot.json", encoding="utf-8", errors="ignore").read().lower()
    disc = [a for a,v in contracts.items() if v.get("same_owner_discarded")]
    in_snap = [a for a in contracts if a.lower() in snap_text]
    not_in = [a for a in contracts if a.lower() not in snap_text]
    out["bridge"] = {"total": len(contracts), "same_owner_discarded": len(disc),
                     "in_snapshot_by_text": len(in_snap), "not_in_snapshot": len(not_in)}
    print("bridge:", out["bridge"], flush=True)
except Exception as e:
    out["bridge_error"] = str(e); print("bridge FAILED:", e, flush=True)

# ---- MEMPL + B777 re-read ----
blk = block_number()
out["leg4_block"] = blk
print("block:", blk, flush=True)
USER_PAD = "0x" + "0"*24 + USER[2:].lower()
mempl_state = {}
for sig in ["totalMints()","mintOpen()","FREE_PER_WALLET()","MAX_MINTS()"]:
    mempl_state[sig.split("(")[0]] = call(MEMPL, sel(sig))
mempl_state["freeLeft_user"] = call(MEMPL, sel("freeLeft(address)") + USER_PAD[2:])
mempl_state["quote_user_1"] = call(MEMPL, sel("quote(address,uint256)") + USER_PAD[2:] + format(1, "064x"))
mempl_state["mintedBy_user"] = call(MEMPL, sel("mintedBy(address)") + USER_PAD[2:])
mempl_state["balanceOf_user"] = call(MEMPL, sel("balanceOf(address)") + USER_PAD[2:])
out["mempl_state"] = mempl_state
print("mempl state:", mempl_state, flush=True)
b777_state = {}
for sig in ["totalMints()","MAX_MINTS()","mintOpen()","FREE_PER_WALLET()","MAX_PER_WALLET()"]:
    b777_state[sig.split("(")[0]] = call(B777, sel(sig))
b777_state["freeLeft_user"] = call(B777, sel("freeLeft(address)") + USER_PAD[2:])
b777_state["quote_user_1"] = call(B777, sel("quote(address,uint256)") + USER_PAD[2:] + format(1, "064x"))
b777_state["mintedBy_user"] = call(B777, sel("mintedBy(address)") + USER_PAD[2:])
b777_state["balanceOf_user"] = call(B777, sel("balanceOf(address)") + USER_PAD[2:])
out["b777_state"] = b777_state
print("b777 state:", b777_state, flush=True)

# ---- Leg 4: bounded re-read of live snapshot items ----
ITEMS = {
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132", ["totalMinted()","remainingFree()","freeQuota()","mintOpen()"]),
 "MERGEBORN": ("0x348455be18b700cae8aa425bd84e456e47f16e8b", ["freeMinted()","FREE_CAP()","totalSupply()","freeClaimed()"]),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1", ["totalSupply()","freeMinted()","FREE_SLOTS()","freeClaimed()"]),
 "FANBEIMAO-824d": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16", ["totalSupply()","freeClaimed()","freeSharesRemaining()","freeAvailable()"]),
 "LuckyBox-LUCK": ("0xd08ef372B52C29255fEd7004f59bF41571451894", ["totalSupply()","freeMinted()","FREE_SUPPLY()","freeClaimed()"]),
 "NJAR": ("0x816458b734d17d59058762deaadd9b952bad6985", ["totalSupply()","freeClaimed()","freeSharesRemaining()","freeAvailable()"]),
 "Predictagent-PRDICT": ("0x8fF4bd65584882324c44Ee794a23E7791820189b", ["totalSupply()","freeMinted()","FREE_SLOTS()","freeClaimed()"]),
 "CLEPSYDRA": ("0x9e2738B3DD3773c6c71cA24Fbc92660B501C0B6b", ["totalSupply()","freeMinted()","FREE_SLOTS()","freeClaimed()"]),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", ["totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()"]),
 "ChimpAgent": ("0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689", ["totalSupply()","totalMints()","MAX_MINTS()","mintOpen()","freeClaimed()"]),
 "Pacture": ("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", ["totalSupply()","freeClaimed()","freeMinted()","FREE_SHARES()","freeSharesRemaining()"]),
 "960E-sale": ("0x960E7e4126b97679053B8416fA59f13508be88bf", ["freeMinted()","FREE_CAP()","freeClaimed()","totalShares()"]),
 "Agentidbsc": ("0x716BFaB3B7b0301D17Af0fF4c50a880C7721F39C", ["totalMints()","mintOpen()","freeLeft()","mintedBy()"]),
 "BelieveBNB": ("0x2d15595d2e6EfB1c1EBf938Cd7Fd0f57d11C6b86", ["totalSupply()","freeMinted()","FREE_SHARES()","freeClaimed()"]),
 "Pubzz-9f10": ("0x9f10c0D8b8E5eFB8706243b1E9336A19E924CCeF", ["totalSupply()","freeMinted()","FREE_CAP()","freeClaimed()"]),
 "Tampesta": ("0x6aA51bd62C0c6B0bA206e25952F4063a7e0CCE79", ["totalSupply()","freeMinted()","FREE_SUPPLY()","freeClaimed()"]),
}
def read_one(args):
    name, (addr, views) = args
    d = {}
    for sig in views:
        if time.time() - T0 > DEADLINE:
            d[sig.split("(")[0]] = "deadline"; continue
        try: d[sig.split("(")[0]] = call(addr, sel(sig))
        except Exception as e: d[sig.split("(")[0]] = f"err:{type(e).__name__}"
    if time.time() - T0 <= DEADLINE:
        try: d["freeClaimed_user"] = call(addr, sel("freeClaimed(address)") + USER_PAD[2:])
        except Exception as e: d["freeClaimed_user"] = f"err:{type(e).__name__}"
    return name, d
reread = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(read_one, it): it[0] for it in ITEMS.items()}
    for f in as_completed(futs):
        try:
            n, d = f.result(); reread[n] = d
        except Exception as e:
            reread[futs[f]] = {"error": str(e)}
out["leg4"] = reread
for n, d in reread.items(): print(n, d, flush=True)
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/hot-leg-{TS}.json","w"), indent=1)
print("DONE duration", out["duration_s"], flush=True)
