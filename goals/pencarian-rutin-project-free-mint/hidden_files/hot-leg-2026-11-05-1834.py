#!/usr/bin/env python3
"""Hot-leg run 2026-11-05 18:34 WIB. Lean: threaded RPC (5s timeout, 2 RPCs),
Sourcify feed + shape-check, Boltbook EN/ZH (files already fetched this run),
bridge read-only, spotcheck re-read (read-only).
Writes only its own run files + hot-leg-seen.json. Never touches main snapshot."""
import json, urllib.request, time, subprocess, re
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-1834"
NOW = "2026-11-05 18:34 WIB"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def call_str(to, sig):
    v = raw(to, sel(sig))
    if not isinstance(v, str) or len(v) < 130: return None
    try:
        b = bytes.fromhex(v[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "ignore")
    except Exception:
        return None

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

# --- Leg 1: Sourcify feed + shape ---
feed = None
try:
    req = urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
                                 headers={"User-Agent": "curl"})
    with urllib.request.urlopen(req, timeout=20) as r: feed = json.load(r)
    json.dump(feed, open(f"{BASE}/hot-leg-{TS}-sourcify.json", "w"), indent=1)
except Exception as e:
    feed = {"error": str(e)}
    print("FEED-FAIL", str(e)[:80], flush=True)
addrs = [x["address"] for x in feed.get("results", [])] if isinstance(feed, dict) and "results" in feed else []
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower(): v for k, v in seen.items()}
new = [a for a in addrs if a.lower() not in seen_l]
excluded = ["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124", "0x8b47354e7b76b1970a0d06365c8244a810d37493"]
new_not_excl = [a for a in new if a.lower() not in excluded]
print("FEED", len(addrs), "NEW", len(new), new, flush=True)
FREE = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"]
shape = {}

def abi_of(a):
    for _ in range(2):
        try:
            req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",
                                         headers={"User-Agent": "curl"})
            with urllib.request.urlopen(req, timeout=15) as r: d = json.load(r)
            return d.get("abi") or d.get("stdJson", {}).get("abi") or []
        except Exception:
            continue
    try:
        out = subprocess.run(["curl", "-s", "--max-time", "15",
                              f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi"],
                             capture_output=True, text=True, timeout=20)
        d = json.loads(out.stdout)
        return d.get("abi") or d.get("stdJson", {}).get("abi") or []
    except Exception as e:
        return {"error": str(e)[:80]}

def shape_of(a):
    abi = abi_of(a)
    fns = sorted({f.get("name") for f in abi if isinstance(abi, list) and f.get("type") == "function" and f.get("name")}) if isinstance(abi, list) else []
    has_mint = any(n.startswith("mint") for n in fns)
    has_quote = "quote" in fns
    free = [f for f in fns if any(x in f for x in FREE)]
    agent = ("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns
             or (isinstance(abi, list) and REG in json.dumps(abi).lower()))
    is_token = all(x in fns for x in ["name", "symbol", "decimals", "totalSupply"])
    has_mintfree = "mintFree" in fns
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) \
        and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    return {"abi_functions": fns, "S1": s1, "S2": s2, "mint": has_mint,
            "quote": has_quote, "free": free, "agent": agent, "token": is_token}

for a in new_not_excl:
    sh = shape_of(a)
    shape[a] = sh
    print("SHAPE", a, "S1", sh["S1"], "S2", sh["S2"], "mint", sh["mint"], "quote", sh["quote"],
          "free", sh["free"], "agent", sh["agent"], "token", sh["token"], flush=True)
json.dump(shape, open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json", "w"), indent=1)
for a in new:
    if a.lower() in excluded:
        seen[a] = {"first_seen": NOW, "status": "excluded"}
    else:
        sh = shape.get(a, {})
        st = "checked-not-sale-shape"
        nt = "S1=%s S2=%s mint=%s quote=%s free=%s agent=%s token=%s" % (
            sh.get("S1"), sh.get("S2"), sh.get("mint"), sh.get("quote"),
            sh.get("free"), sh.get("agent"), sh.get("token"))
        if sh.get("S1") or sh.get("S2"):
            st = "sale-shape-NEEDS-VERIFY"; nt = "SALE SHAPE " + nt
        seen[a] = {"first_seen": NOW, "status": st, "note": nt, "source": "sourcify-feed"}
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("SEEN-UPDATED", len(new), flush=True)

# --- Leg 1b: extra on-chain verify for the two "spots" contracts (mint+quote+registry,
# spotsLeft pool view, not in enumerated free list -> strict S1 False, verify free-ness anyway) ---
SPOTS = ["0xA3a006A1bD6dfB4e9cD3F595dd318a7f3FD750E8", "0xf2c03cF7D3cfEEbFac7F79916CD32969CED10cb0"]
verify = {}
for a in SPOTS:
    d = {}
    d["name"] = call_str(a, "name()")
    d["symbol"] = call_str(a, "symbol()")
    d["WEBSITE"] = call_str(a, "WEBSITE()")
    d["TWITTER"] = call_str(a, "TWITTER()")
    d["spotsLeft"] = call(a, "spotsLeft()")
    d["totalSpotsMinted"] = call(a, "totalSpotsMinted()")
    d["totalMinted"] = call(a, "totalMinted()")
    d["MAX_SPOTS"] = call(a, "MAX_SPOTS()")
    d["MAX_SUPPLY"] = call(a, "MAX_SUPPLY()")
    d["PRICE"] = call(a, "PRICE()")
    d["quote_user_1"] = call(a, "quote(address,uint256)", enc(USER) + enc_uint(1))
    d["mintedBy_user"] = call(a, "mintedBy(address)", enc(USER))
    d["balanceOf_user"] = call(a, "balanceOf(address)", enc(USER))
    d["totalSupply"] = call(a, "totalSupply()")
    verify[a] = d
    print("VERIFY-SPOTS", a, d, flush=True)
json.dump(verify, open(f"{BASE}/hot-leg-{TS}-spots-verify.json", "w"), indent=1)

# --- Leg 2: Boltbook front page EN + ZH (files fetched this run via curl) ---
bb_new = []
for lang in ["en", "zh"]:
    fn = f"{BASE}/hot-leg-1834-boltbook-{lang}.html"
    try:
        html = open(fn).read()
        addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", html)))
        kw = {k: html.lower().count(k) for k in ["free share", "first share free", "free mint",
             "\u514d\u8d39\u4efd\u989d", "\u9996\u4e2a\u514d\u8d39", "\u514d\u8d39\u94f8\u9020", "\u514d\u8d39mint"]}
        fresh = [a for a in addrs if a.lower() not in {k.lower() for k in seen}]
        print("BOLTBOOK", lang, len(html), "bytes,", len(addrs), "addrs, new-vs-seen:", fresh, kw, flush=True)
        bb_new.extend(fresh)
    except Exception as e:
        print("BOLTBOOK-ERROR", lang, e, flush=True)
bb_new = sorted(set(bb_new))
bb_shape = {}
for a in bb_new:
    sh = shape_of(a)
    bb_shape[a] = sh
    print("BOLTBOOK-SHAPE", a, "S1", sh["S1"], "S2", sh["S2"], "mint", sh["mint"], "quote", sh["quote"],
          "free", sh["free"], "agent", sh["agent"], "token", sh["token"], flush=True)
    seen[a] = {"first_seen": NOW, "status": "sale-shape-NEEDS-VERIFY" if (sh["S1"] or sh["S2"]) else "checked-not-sale-shape",
               "note": "S1=%s S2=%s mint=%s quote=%s free=%s agent=%s token=%s" % (
                   sh["S1"], sh["S2"], sh["mint"], sh["quote"], sh["free"], sh["agent"], sh["token"]),
               "source": "boltbook-frontpage"}
json.dump(bb_shape, open(f"{BASE}/hot-leg-{TS}-boltbook-shape.json", "w"), indent=1)
json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
print("BOLTBOOK-SEEN-UPDATED", len(bb_new), flush=True)

# --- Leg 3: Bridge (read-only) ---
try:
    br = json.load(open(f"{BASE}/scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text = json.dumps(snap)
    not_in_snap = [c for c in cons if c.lower() not in snap_text.lower()]
    discarded = [c for c, v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE", len(cons), "discarded", len(discarded), "not_in_snapshot", len(not_in_snap), flush=True)
    json.dump({"total": len(cons), "discarded": len(discarded), "not_in_snapshot": len(not_in_snap),
               "not_in_snapshot_list": not_in_snap}, open(f"{BASE}/hot-leg-{TS}-bridge.json", "w"), indent=1)
except Exception as e:
    print("BRIDGE-ERROR", e, flush=True)

# --- Leg 4: spotcheck re-read (read-only) ---
NFTS = [
 ("Cachejack", "0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5"),
 ("Layerloom", "0x1B72ceC52A74537b06F713FCebA0e491f53679aE"),
 ("Tumblebots", "0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17"),
 ("Forklings", "0xD7B3FD33e0b465B0e374906F60567D317b758FD8"),
 ("StarAgent", "0x7d390e37Ed41A359f276D8764ca15432704B99b7"),
 ("RigOrb", "0x72D977237f7b3931A08434cEBD0D3814fE13539e"),
 ("HACKED", "0xCD355D1191Ce9849B3A935C821A66d9DF37cFE77"),
 ("AgentCoffee", "0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010"),
 ("Driftnauts", "0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b"),
 ("AgentMiner", "0x8670e99062ead2cE5402754aeDE769602FDf38b8"),
 ("AFROG", "0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31"),
 ("RACKRUSH", "0x5e42db19a22f5c858dc72df6352495ffff9abb62"),
 ("LuckyBox", "0xd08ef372B52C29255fEd7004f59bF41571451894"),
]

def read_nft(item):
    name, addr = item
    d = {"address": addr}
    d["totalSupply"] = call(addr, "totalSupply()")
    d["freeMinted"] = call(addr, "freeMinted()")
    d["freeClaimed"] = call(addr, "freeClaimed()")
    d["claimedFree_user"] = call(addr, "claimedFree(address)", enc(USER))
    d["canFreeMint_user"] = call(addr, "canFreeMint(address)", enc(USER))
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    if name == "AgentMiner":
        d["freeFor_user_1"] = call(addr, "freeFor(address,uint256)", enc(USER) + enc_uint(1))
        d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
        d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
    if name == "AFROG":
        d["FREE_SUPPLY"] = call(addr, "FREE_SUPPLY()")
    if name == "RACKRUSH":
        d["FREE_CAP"] = call(addr, "FREE_CAP()")
        d["MAX_SUPPLY"] = call(addr, "MAX_SUPPLY()")
    if name == "LuckyBox":
        d["freeLeft_user"] = call(addr, "freeLeft(address)", enc(USER))
        d["freeUsed_user"] = call(addr, "freeUsed(address)", enc(USER))
        d["freeFor_user_1"] = call(addr, "freeFor(address,uint256)", enc(USER) + enc_uint(1))
        d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
        d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
        d["mintOpen"] = call(addr, "mintOpen()")
    if name == "RigOrb":
        d["priceFor_user_1"] = call(addr, "priceFor(address,uint256)", enc(USER) + enc_uint(1))
    if name == "HACKED":
        d["freeDone_user"] = call(addr, "freeDone(address)", enc(USER))
    print(name, d, flush=True)
    return name, d

TC = [
 ("WAGA", "0x06a6f51D30556f4262e38485C09556fE81e6A984"),
 ("SENBAZURU", "0xb21583A08581278BcF925351a99C61A4562C62f0"),
 ("IMARS", "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"),
 ("NIULAI", "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF"),
 ("ASOC", "0x43cEef9313CB8c4ca3757bA841C44DF40A223205"),
]

def read_tc(item):
    key, sale = item
    d = {"sale": sale}
    if key == "WAGA":
        d["totalMints"] = call(sale, "totalMints()")
        d["quote_user_1"] = call(sale, "quote(address,uint256)", enc(USER) + enc_uint(1))
        d["mintOpen"] = call(sale, "mintOpen()")
    if key == "SENBAZURU":
        d["freeClaimed"] = call(sale, "freeClaimed()")
        d["paidSold"] = call(sale, "paidSold()")
        d["hasFreeShare_user"] = call(sale, "hasFreeShare(address)", enc(USER))
    if key == "IMARS":
        d["opened"] = call(sale, "opened()")
        d["freeMinted"] = call(sale, "freeMinted()")
        d["totalMinted"] = call(sale, "totalMinted()")
    if key == "NIULAI":
        d["phase"] = call(sale, "phase()")
        d["launched"] = call(sale, "launched()")
        d["freeClaimed"] = call(sale, "freeClaimed()")
        d["freeShares"] = call(sale, "freeShares()")
    if key == "ASOC":
        d["freeUsed"] = call(sale, "freeUsed()")
        d["paidSold"] = call(sale, "paidSold()")
    print("TC", key, d, flush=True)
    return key, d

blk = block()
print("BLOCK", blk, flush=True)
out = {"block": blk, "spotcheck": {}, "track_c": {}}
t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    for name, d in ex.map(read_nft, NFTS):
        out["spotcheck"][name] = d
        json.dump(out, open(f"{BASE}/hot-leg-{TS}-spotcheck.json", "w"), indent=1)
    for key, d in ex.map(read_tc, TC):
        out["track_c"][key] = d
        json.dump(out, open(f"{BASE}/hot-leg-{TS}-spotcheck.json", "w"), indent=1)
print("DONE in %.1fs, block %s" % (time.time() - t0, blk), flush=True)
json.dump(out, open(f"{BASE}/hot-leg-{TS}-spotcheck.json", "w"), indent=1)
