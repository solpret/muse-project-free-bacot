#!/usr/bin/env python3
"""Hot-leg 0714: legs 1+2+bridge+leg4 (parallel RPC) + MEMPL first-mint retry via
public Blockscout logs API then small-chunk eth_getLogs. Read-only except hot-leg-seen.json."""
import json, re, subprocess, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-0714"
T0 = time.time()
DEADLINE = 100
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MEMPL = "0xd3bE54Ae65F837d0646709fFBc2A5eFB0b034846"
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

# ---- Leg 1: Sourcify feed ----
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_lc = {k.lower(): k for k in seen}
try:
    feed = json.loads(curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 25))
    json.dump(feed, open(f"{BASE}/hot-leg-{TS}-feed.json","w"), indent=1)
    addrs1 = [r["address"] for r in feed.get("results", [])]
except Exception as e:
    feed = None; addrs1 = []; out["leg1_error"] = str(e)
new1 = [a for a in addrs1 if a.lower() not in seen_lc and a.lower() != REG.lower() and a.lower() not in EXCLUDED]
out["leg1_feed"] = len(addrs1); out["leg1_new"] = new1
print("leg1 feed:", len(addrs1), "new:", new1, flush=True)

# ---- Leg 2: Boltbook EN+ZH ----
addrs2 = []
for lang, url in [("en","https://boltbook.fun/?lang=en"),("zh","https://boltbook.fun/?lang=zh")]:
    try:
        html = curl(url, 25).decode("utf-8","ignore")
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        print(f"leg2 {lang}: ok {len(html)} bytes, {len(found)} addrs", flush=True)
        addrs2 += found
        open(f"{BASE}/hot-leg-{TS}-boltbook-{lang}.html","w").write(html)
    except Exception as e:
        print(f"leg2 {lang}: FAILED {e}", flush=True); out[f"leg2_{lang}_error"] = str(e)
addrs2 = sorted(set(addrs2))
new2 = [a for a in addrs2 if a.lower() not in seen_lc and a.lower() != REG.lower() and a.lower() not in EXCLUDED]
kw = ["免费份额","首个免费","免费铸造","免费mint","free share","first share free","1 free share","free mint share"]
kw_hits = {}
for lang in ("en","zh"):
    try:
        html = open(f"{BASE}/hot-leg-{TS}-boltbook-{lang}.html", encoding="utf-8", errors="ignore").read().lower()
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
                   "source": "hot-leg-0714",
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
                     "in_snapshot_by_text": len(in_snap), "not_in_snapshot": len(not_in),
                     "not_in_snapshot_list": not_in}
    print("bridge:", out["bridge"], flush=True)
except Exception as e:
    out["bridge_error"] = str(e); print("bridge FAILED:", e, flush=True)

# ---- MEMPL: pool/slot re-read + first-mint retry ----
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

# first-mint: (a) public Blockscout logs API, Minted event
minted_topic = "0x" + keccak.new(digest_bits=256, data=b"Minted(address,uint256,uint256,uint256,string)").hexdigest()
transfer_topic = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
ZERO_PAD = "0x" + "0"*64
first_mint = {"method": None, "block": None, "timestamp": None, "errors": []}
if blk:
    try:
        url = ("https://bsc.blockscout.com/api?module=logs&action=getLogs"
               f"&fromBlock={blk-20000}&toBlock={blk}&address={MEMPL}&topic0={minted_topic}")
        d = json.loads(curl(url, 25))
        logs = d.get("result", []) if isinstance(d, dict) else []
        if isinstance(logs, list) and logs:
            first = min(logs, key=lambda l: int(l.get("blockNumber","0x0"), 16))
            first_mint["method"] = "blockscout-public-minted"
            first_mint["block"] = int(first["blockNumber"], 16)
            first_mint["timestamp"] = int(first.get("timeStamp", "0"), 16) if first.get("timeStamp") else None
            first_mint["n_logs"] = len(logs)
        else:
            first_mint["errors"].append(f"blockscout-public: {str(d)[:200]}")
    except Exception as e:
        first_mint["errors"].append(f"blockscout-public: {e}")
    # (b) eth_getLogs Minted, 2k-block chunks walking back from latest, max 10 chunks
    if not first_mint["block"]:
        for i in range(10):
            hi = blk - i*2000
            lo = hi - 1999
            v = rpc_call("eth_getLogs", [{"fromBlock": hex(lo), "toBlock": hex(hi),
                                          "address": MEMPL, "topics": [minted_topic]}], 8)
            if isinstance(v, list) and v:
                first = min(v, key=lambda l: int(l.get("blockNumber","0x0"), 16))
                fb = int(first["blockNumber"], 16)
                bt = rpc_call("eth_getBlockByNumber", [hex(fb), False], 5)
                ts = int(bt["timestamp"], 16) if isinstance(bt, dict) and bt.get("timestamp") else None
                first_mint["method"] = "eth_getLogs-minted"
                first_mint["block"] = fb; first_mint["timestamp"] = ts
                first_mint["chunk"] = f"{lo}-{hi}"
                break
            elif isinstance(v, str):
                first_mint["errors"].append(f"eth_getLogs {lo}-{hi}: {v}")
            else:
                first_mint["errors"].append(f"eth_getLogs {lo}-{hi}: empty/None")
            if time.time() - T0 > DEADLINE: break
if first_mint["timestamp"]:
    dt = datetime.fromtimestamp(first_mint["timestamp"], WIB)
    first_mint["time_wib"] = dt.isoformat(timespec="seconds")
    age_h = (datetime.now(WIB) - dt).total_seconds()/3600
    first_mint["age_hours"] = round(age_h, 2)
    first_mint["age_le_48h"] = age_h <= 48
out["mempl_first_mint"] = first_mint
print("mempl first-mint:", first_mint, flush=True)

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
 "Orchidia": ("0x09bcdd97186f6f37521bd1b281d329e48ac54b89", ["totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()"]),
 "DigitalBomb-C3f8": ("0xC3f847430D660e5AAbE8D4b2B5792d6Fcbb171F9", ["totalSupply()","freeClaimed()","freeMinted()","FREE_SUPPLY()"]),
 "ChimpAgent": ("0x57D41Ff4895A19f518a0Ec3A2Fa56284a85f5689", ["totalSupply()","totalMints()","MAX_MINTS()","mintOpen()","freeClaimed()"]),
 "Block777-B777": ("0x47529CF66091BeB0E8e0F78D5635e367473D52d5", ["totalMints()","MAX_MINTS()","mintOpen()","FREE_PER_WALLET()","MAX_PER_WALLET()"]),
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
try:
    b777 = "0x47529CF66091BeB0E8e0F78D5635e367473D52d5"
    reread.setdefault("Block777-B777", {})
    reread["Block777-B777"]["freeLeft_user"] = call(b777, sel("freeLeft(address)") + USER_PAD[2:])
    reread["Block777-B777"]["quote_user_1"] = call(b777, sel("quote(address,uint256)") + USER_PAD[2:] + format(1, "064x"))
    reread["Block777-B777"]["mintedBy_user"] = call(b777, sel("mintedBy(address)") + USER_PAD[2:])
    reread["Block777-B777"]["balanceOf_user"] = call(b777, sel("balanceOf(address)") + USER_PAD[2:])
except Exception as e:
    out["leg4_b777_user_error"] = str(e)
out["leg4"] = reread
for n, d in reread.items(): print(n, d, flush=True)
out["duration_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{BASE}/hot-leg-{TS}.json","w"), indent=1)
print("DONE duration", out["duration_s"], flush=True)
