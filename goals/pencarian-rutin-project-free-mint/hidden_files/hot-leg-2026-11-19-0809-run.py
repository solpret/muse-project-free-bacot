#!/usr/bin/env python3
"""hot-leg run 2026-11-19 08:09 WIB (same pattern as 2354 template; focus set carried from 0714 run (same ITEMS)).
Legs 1+2 (Sourcify feed + Boltbook EN/ZH), shape-check new contracts,
leg 3 on-chain verify for new S1/S2 contracts, bridge leg (read-only),
leg 4 reread focus set. Read-only except hot-leg-seen.json notes and this run's own outputs.
No preview/mint. No snapshot rewrite."""
import json, re, time, urllib.request, subprocess, base64
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
T0 = time.time()
from datetime import datetime, timezone, timedelta
NOW = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
RUN = "free-mint-hot-leg 2026-11-19 08:09 WIB"
out = {"run": RUN, "started_wib": NOW}

def fetch(url, timeout=15):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "hot-leg/1.0", url],
                       capture_output=True)
    if r.returncode == 0 and r.stdout:
        return r.stdout
    req = urllib.request.Request(url, headers={"User-Agent": "hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))

# --- Leg 1: Sourcify feed ---
try:
    raw = fetch("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=15)
    feed = json.loads(raw)
    items = feed if isinstance(feed, list) else feed.get("results", [])
    contracts = []
    va = []
    for c in items:
        if isinstance(c, dict) and c.get("address"):
            contracts.append(c["address"])
            if c.get("verifiedAt"): va.append(c["verifiedAt"])
    seen_l = {k.lower() for k in seen}
    new = [a for a in contracts if a.lower() not in seen_l and a.lower() != REGISTRY.lower()]
    out["sourcify_feed"] = {"total": len(contracts), "new": len(new), "new_contracts": new,
                            "top": contracts[0] if contracts else None,
                            "top_verifiedAt": max(va) if va else None,
                            "all": contracts, "fetch": "direct curl"}
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {e}"}
    new = []

# --- Leg 2: Boltbook EN + ZH ---
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    raw = fetch(url, timeout=20)
    open(BASE + f"hot-leg-2026-11-19-0809-boltbook-{lang}.html", "wb").write(raw)
    text = raw.decode("utf-8", errors="ignore")
    addrs = sorted(set(re.findall(r"0x[a-fA-F0-9]{40}", text)))
    low = text.lower()
    figs = re.findall(r"[^<>]{0,90}(?:1,?[0-9]{2,3}/1,?[0-9]{2,3}|minted|free)[^<>]{0,60}", text)[:8]
    return {"bytes": len(raw), "http_code": "200", "full_address_contracts": len(addrs),
            "addresses": addrs, "new": 0, "new_contracts": [],
            "free_kw": sum(low.count(k) for k in ("free share", "first share free", "1 free share", "free mint share")),
            "zh_free_kw": sum(text.count(k) for k in ("免费份额", "首个免费", "免费铸造", "免费mint")),
            "figures": figs}
bb = {}
for lang in ("en", "zh"):
    try: bb[lang] = boltbook(lang)
    except Exception as e: bb[lang] = {"error": f"{type(e).__name__}: {e}"}
out["boltbook_en"] = bb["en"]; out["boltbook_zh"] = bb["zh"]
bb_new = []
seen_l = {k.lower() for k in seen}
for lang in ("en", "zh"):
    for a in bb.get(lang, {}).get("addresses", []):
        if a.lower() not in seen_l and a.lower() not in [x.lower() for x in bb_new]:
            bb_new.append(a)
for lang in ("en", "zh"):
    if "new_contracts" in bb.get(lang, {}):
        bb[lang]["new"] = len([a for a in bb[lang]["addresses"] if a.lower() not in seen_l])
        bb[lang]["new_contracts"] = [a for a in bb[lang]["addresses"] if a.lower() not in seen_l]

# --- Shape-check new contracts ---
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted",
              "freeSharesClaimed", "freeMinted", "freeMintedTotal"]
def shape(addr):
    try:
        raw = fetch(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=15)
        d = json.loads(raw)
        abi = d.get("abi") or (d.get("stdJson", {}) or {}).get("abi") or []
        va2 = d.get("verifiedAt") or (d.get("stdJson", {}) or {}).get("verifiedAt")
    except Exception as e:
        return {"status": "shape-check-failed", "error": f"{type(e).__name__}: {e}"}
    names = [f.get("name", "").lower() for f in abi if isinstance(f, dict)]
    has_mint = any(n.startswith("mint") or n in ("claimfree", "claim", "mintfree") for n in names)
    has_quote = any("quote" in n or "price" in n or n.startswith("cost") for n in names)
    free = sorted(set(n for n in names if any(k.lower() in n for k in FREE_VIEWS)))
    agent = any("agent" in n or "registry" in n for n in names) or REGISTRY.lower() in json.dumps(abi).lower()
    tokenish = all(k in names for k in ("name", "symbol", "decimals", "totalsupply"))
    noarg_free = any(n in ("mintfree", "claimfree") for n in names)
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and noarg_free and bool(free) and agent
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free, "agent_ref": agent, "is_token": tokenish,
            "n_fns": len(abi), "status": "checked", "verifiedAt": va2}
EXCLUDED = ("0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493")
shape_res = {}
for a in (new + bb_new):
    if a.lower() in EXCLUDED:
        shape_res[a] = {"status": "excluded-example"}
        continue
    shape_res[a] = shape(a)
out["shape_check_targets"] = new + bb_new
out["shape_check"] = [dict({"address": a}, **shape_res[a]) for a in (new + bb_new)]
out["shape_hits"] = [a for a in (new + bb_new) if shape_res.get(a, {}).get("S1") or shape_res.get(a, {}).get("S2")]
out["seen_added"] = [a for a in (new + bb_new) if a.lower() not in seen_l]

# --- Leg 3: on-chain verify new S1/S2 contracts ---
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"): d += enc_u(int(a, 16))
        else: d += enc_u(int(a))
    return d
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def dec_str(hexs):
    try:
        b = bytes.fromhex(hexs[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", errors="ignore")
    except Exception: return None
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)

leg3 = {}
U = [USER]
snap_cache = None
for a in (new + bb_new):
    sh = shape_res.get(a, {})
    if not (sh.get("S1") or sh.get("S2")):
        continue
    views = [("freeClaimed", "freeClaimed()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
             ("FREE_PER_WALLET", "FREE_PER_WALLET()", []), ("freeLeft_user", "freeLeft(address)", U),
             ("freeUsed_user", "freeUsed(address)", U), ("freeFor_user1", "freeFor(address,uint256)", [USER, 1]),
             ("quote_user1", "quote(address,uint256)", [USER, 1]),
             ("AGENT_ID", "AGENT_ID()", []), ("agentIdRequired", "agentIdRequired()", []),
             ("mintOpen", "mintOpen()", []), ("totalSupply", "totalSupply()", []),
             ("name", "name()", []), ("symbol", "symbol()", []), ("contractURI", "contractURI()", [])]
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": a, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    got = None
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if isinstance(res, list) and len(res) == len(calls):
                got = (res, ep); break
        except Exception as e:
            print("  leg3 ep", ep, "exc", str(e)[:80], flush=True); continue
    if got is None:
        leg3[a] = {"error": "all RPC endpoints failed"}
        continue
    res, ep = got
    vals = {}
    for it, key in zip(res, meta):
        if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
            vals[key] = None
        else:
            r = it["result"]
            if key in ("name", "symbol", "contractURI"):
                vals[key] = dec_str(r)
            elif key == "AGENT_ID":
                vals[key] = "0x" + r[-40:] if len(r) >= 42 else r
            else:
                vals[key] = to_int(r[:66]) if len(r) >= 66 else r
    cu = vals.get("contractURI") or ""
    ext = None
    if cu.startswith("data:application/json;base64,"):
        try:
            ext = json.loads(base64.b64decode(cu.split(",", 1)[1]).decode("utf-8", errors="ignore"))
        except Exception as e:
            ext = {"decode_error": str(e)[:80]}
    elif cu.startswith("{"):
        try: ext = json.loads(cu)
        except Exception: ext = None
    vals["contractURI_json"] = ext
    if snap_cache is None:
        snap_cache = json.load(open(BASE + "onchain-snapshot.json"))
    in_snap = False
    for sec in ("contracts", "track_c"):
        for v in (snap_cache.get(sec) or {}).values():
            if isinstance(v, dict):
                for f in ("address", "sale", "contract", "token"):
                    if isinstance(v.get(f), str) and v[f].lower() == a.lower():
                        in_snap = True
    vals["in_main_snapshot"] = in_snap
    vals["rpc_ep"] = ep
    leg3[a] = vals
out["leg3"] = leg3

for a in (new + bb_new):
    if a.lower() not in seen_l:
        note = json.dumps(shape_res.get(a, {}))[:300]
        if a in leg3:
            note = json.dumps(leg3[a])[:400]
        seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed" if a in new else "boltbook",
                   "status": shape_res.get(a, {}).get("status", "checked"),
                   "note": note}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_n"] = len(seen)

# --- Bridge leg (read-only) ---
try:
    br = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = br.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    def _addr_vals(section, fields):
        o = set()
        for v in (snap.get(section) or {}).values():
            if isinstance(v, dict):
                for f in fields:
                    x = v.get(f)
                    if isinstance(x, str) and x.startswith("0x") and len(x) == 42:
                        o.add(x.lower())
        return o
    snap_addrs = (_addr_vals("contracts", ["address", "sale", "contract"])
                  | _addr_vals("track_c", ["sale", "address", "token", "contract"])
                  | _addr_vals("pending_claims", ["address", "sale", "mint"]))
    outside = []
    discarded = 0
    for addr, info in bcontracts.items():
        if info.get("same_owner_discarded"):
            discarded += 1
            continue
        if addr.lower() not in snap_addrs:
            outside.append(addr)
    out["bridge_scan"] = {"total": len(bcontracts), "not_in_snapshot": len(outside),
                          "not_in_snapshot_list": outside, "same_owner_discarded": discarded}
except Exception as e:
    out["bridge_scan"] = {"error": f"{type(e).__name__}: {e}"}

# --- Leg 4: reread focus set (25 items + bsccat + pepe) ---
V = lambda name, sig, args=None: (name, sig, args or [])
ITEMS = {
 "JADE": ("0x1b8894391a3dcfe7e248c321103265ab52e273e0",
    [V("cost_user_1","cost(address,uint256)",[USER,1]), V("freeClaimed","freeClaimed()"),
     V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()"),
     V("mintedBy_user","mintedBy(address)",U), V("balanceOf_user","balanceOf(address)",U)]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b",
    [V("freeMinted","freeMinted()"), V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "DRAGON": ("0xfc191b76041498b14dcae3c802af3389c74263e6",
    [V("freeMinted","freeMinted()"), V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",U)]),
 "Matrix": ("0x1F669b714337F3C2585072c53fdDD89581F928fF",
    [V("freeMinted","freeMinted()"), V("freeRemaining","freeRemaining()"), V("totalSupply","totalSupply()"),
     V("mintOpen","mintOpen()")]),
 "AGCLUB": ("0x67270bb351515abf3089ca5420456897363f5e75",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"), V("FREE_CAP","FREE_CAP()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "BNBG": ("0x1595013dfc8c6b3f4b172254bf09bdaf1421002b", [V("totalMinted","totalMinted()")]),
 "SPARKS": ("0xd52fd117c4b47d03e4e16e778871f09faa5a024b", [V("totalSupply","totalSupply()")]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
    [V("freeClaimed","freeClaimed()"), V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()"),
     V("freeUsed_user","freeUsed(address)",U), V("balanceOf_user","balanceOf(address)",U)]),
 "BoldLeonidas": ("0x84bcb8c16566e81ce902530c9da1e3de291f9941",
    [V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
    [V("totalSupply","totalSupply()"), V("freeMinted","freeMinted()"), V("mintOpen","mintOpen()")]),
 "CPASS": ("0x5877d2bb9f226cc3e438f4d656caeb27deafc576",
    [V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "REOPIR": ("0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",
    [V("freeClaimed","freeClaimed()"), V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()")]),
 "RAVE": ("0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"), V("mintOpen","mintOpen()")]),
 "MORFO": ("0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
    [V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()")]),
 "AgentNOVA": ("0x43462d7f269fde4914b03e1e07067a61b62b9540", [V("totalSupply","totalSupply()")]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [V("totalMinted","totalMinted()")]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()")]),
 "Kryntar": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe",
    [V("totalMinted","totalMinted()"), V("standardRemaining","standardRemaining()"),
     V("legendaryRemaining","legendaryRemaining()"), V("mintOpen","mintOpen()")]),
 "ONI": ("0x99d01eD93829DBB0EEc11F3a733388c789dA6caD",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()")]),
 "HAPPE": ("0x72c14121681F1133545947B0735563835CC07B67",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()")]),
 "PIXELFROGS": ("0x454054e55FA2D7Ba37df7F3ceA269696f19037dF",
    [V("totalSupply","totalSupply()"), V("freeMinted","freeMinted()"), V("freeLeft","freeLeft()"),
     V("mintOpen","mintOpen()"), V("freeClaimed_user","freeClaimed(address)",U)]),
 "Flare-bd6f": ("0xbd6ff7ed8fe96b79cb3cbf9dc32656ff7a98a599", [V("totalSupply","totalSupply()")]),
 "PunchCard": ("0x1d4ef0587dd3ff3875a141d4711c60bca40587c4",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"),
     V("paidMinted","paidMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("mintPriceFor_user_1","mintPriceFor(address,uint256)",[USER,1]),
     V("mintedCount_user","mintedCount(address)",U), V("balanceOf_user","balanceOf(address)",U)]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
    [V("freeSharesLeft","freeSharesLeft()"), V("openedAt","openedAt()"), V("freeClaimed","freeClaimed()"),
     V("freeBooked_user","freeBooked(address)",U)]),
 "STOCKAGENT": ("0xba7068233da805bdebcc167be361c219002e6b7f",
    [V("totalSupply","totalSupply()"), V("freeLeft","freeLeft()"), V("FREE_SUPPLY","FREE_SUPPLY()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("quote_user_1","quote(address,uint256)",[USER,1]),
     V("freeMintedByWallet_user","freeMintedByWallet(address)",U), V("balanceOf_user","balanceOf(address)",U)]),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f",
    [V("totalSupply","totalSupply()"), V("freeClaimed","freeClaimed()"), V("FREE_SUPPLY","FREE_SUPPLY()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U),
     V("mintedBy_user","mintedBy(address)",U)]),
 "ALIEN": ("0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb",
    [V("totalSupply","totalSupply()"), V("FREE_SUPPLY","FREE_SUPPLY()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("isFreePhase","isFreePhase()"), V("balanceOf_user","balanceOf(address)",U)]),
 "ARKT": ("0xf91b1ebbcb2b038107ed10b4cb163ed51ce39037",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("hasClaimed_user","hasClaimed(address)",U), V("balanceOf_user","balanceOf(address)",U)]),
 "AgentEcho": ("0xff2dac2389a6a9593209b6008d5ffa9e73aa19c2",
    [V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",U)]),
 "Kageveil": ("0xf79860f419be7b604d909e254785400d9edbd9d0",
    [V("normalMinted","normalMinted()"), V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "ADRAW": ("0xdc167f998341aa37d734de94db2108f0983bf2a7",
    [V("freeMinted","freeMinted()"), V("totalSupply","totalSupply()"), V("balanceOf_user","balanceOf(address)",U),
     V("hasClaimedFree_user","hasClaimedFree(address)",U)]),
 "Stromboat": ("0xC3CB4dF5256c8429Eab306E924BF6E3E6c72163d",
    [V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"), V("paidMinted","paidMinted()"),
     V("mintOpen","mintOpen()"), V("freeMintedBy_user","freeMintedBy(address)",U),
     V("balanceOf_user","balanceOf(address)",U)]),
 "ClafEye": ("0x1c759C4e075103b5B250DB5114B832b17B99C456",
    [V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",U), V("costFor_user_1","costFor(address,uint256)",[USER,1])]),
 "DGF": ("0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",U)]),
 "Hivebyte": ("0xaE9d85E78a609f185B4682d87Da12d13B03cf8d8",
    [V("totalSupply","totalSupply()"), V("freeClaimed","freeClaimed()"), V("FREE_SUPPLY","FREE_SUPPLY()"),
     V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "AgentPepe": ("0xA34C9D34b2Ee93b8059d0ED5302ae595c446423d",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "AlphaPulse": ("0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "THYRK": ("0x4d90ffc3075fb8897edff6d7c6269c906664a20e",
    [V("totalSupply","totalSupply()"), V("freeMinted","freeMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("balanceOf_user","balanceOf(address)",U)]),
 "E5F8": ("0xe5f8f8c424821908752332d527428258EcfC245b",
    [V("totalMinted","totalMinted()"), V("totalSupply","totalSupply()"), V("mintOpen","mintOpen()")]),
 "XCOPY": ("0x3fbec44c7c845374267b06033940abe45c63edfa",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"),
     V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "EIM": ("0x1fccfab61461c4b5c4d1b16580d12a7e32012baa",
    [V("totalMinted","totalMinted()"), V("MAX_SUPPLY","MAX_SUPPLY()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",U)]),
 "ARKTclaim": ("0x62a7AC33ca463331858693b8Aa05B16688bA29E0",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("balanceOf_user","balanceOf(address)",U)]),
 "Vitaliq": ("0xad0d78689d047bb9a32f5bf93438373a73da68ec",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()"),
     V("balanceOf_user","balanceOf(address)",U)]),
 "ARKT8334": ("0x8334C7d0e8aF217EEA5251A0A181e628971535e1",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("mintOpen","mintOpen()")]),
 "AgentMintPass": ("0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"),
     V("freeClaimed","freeClaimed()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "AGATE-Pass": ("0x5b63bd45e61a2e6540548c3509b598b6384206c5",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"),
     V("freeClaimed","freeClaimed()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "AgentDrop": ("0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9",
    [V("totalSupply","totalSupply()"), V("totalMinted","totalMinted()"), V("freeMinted","freeMinted()"),
     V("freeClaimed","freeClaimed()"), V("mintOpen","mintOpen()"), V("balanceOf_user","balanceOf(address)",U)]),
 "binanceai-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
    [V("launched","launched()"), V("failed","failed()"), V("isRefundPhase","isRefundPhase()"),
     V("totalShares","totalShares()"), V("tokenClaimed_user","tokenClaimed(address)",U)]),
}
BSCCAT = ("0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A",
    [V("totalMinted","totalMinted()"), V("soldShares","soldShares()"), V("freeMinted","freeMinted()"),
     V("freeClaimed","freeClaimed()"), V("freeSharesLeft","freeSharesLeft()"), V("FREE_SHARES","FREE_SHARES()"),
     V("FREE_SUPPLY","FREE_SUPPLY()"), V("totalShares","totalShares()"), V("totalSupply","totalSupply()"),
     V("mintOpen","mintOpen()"), V("opened","opened()"), V("poolOpen","poolOpen()"), V("isPoolOpen","isPoolOpen()"),
     V("launched","launched()"), V("hasMinted_user","hasMinted(address)",U),
     V("freeClaimed_user","freeClaimed(address)",U), V("freeUsed_user","freeUsed(address)",U),
     V("freeLeft_user","freeLeft(address)",U), V("mintedBy_user","mintedBy(address)",U),
     V("quote_user_1","quote(address,uint256)",[USER,1]), V("cost_user_1","cost(address,uint256)",[USER,1]),
     V("costOf_1","costOf(uint256)",[1]), V("bnbQuote_1","bnbQuote(uint256)",[1]),
     V("token","token()"), V("TOKEN","TOKEN()"), V("balanceOf_user","balanceOf(address)",U)])
PEPE = ("0x7E920e9e4Ad8E4497aEa7EB9bAF60Cd6c6C8D980",
    [V("freeMinted","freeMinted()"), V("soldShares","soldShares()"), V("FREE_SHARES","FREE_SHARES()"),
     V("opened","opened()"), V("costOf_1","costOf(uint256)",[1]), V("hasMinted_user","hasMinted(address)",U)])

def read_views(addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            o = {}
            for it, key in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    o[key] = None
                else:
                    r = it["result"]
                    if key in ("token", "TOKEN"):
                        o[key] = "0x" + r[-40:] if len(r) >= 42 else r
                    else:
                        o[key] = to_int(r[:66]) if len(r) >= 66 else r
            return o, ep
        except Exception:
            continue
    return None, None

def block_number():
    if time.time() - T0 > LEG4_DEADLINE:
        return None
    for ep in EPS:
        if time.time() - T0 > LEG4_DEADLINE:
            return None
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=10)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None

def chunked(items, n=4):
    items = list(items.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]

reads, ok, chunk_errors = {}, 0, []
LEG4_DEADLINE = 200  # seconds from T0; skip remaining chunks past this (RPC degraded last run)
for ci, ch in enumerate(chunked(ITEMS, 4)):
    if time.time() - T0 > LEG4_DEADLINE:
        print(f"chunk {ci+1} SKIPPED deadline ({time.time()-T0:.0f}s)", flush=True)
        chunk_errors.append([n for n, _ in ch] + ["deadline-skipped"])
        for n, _ in ch: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    calls, meta = [], []
    for name, (addr, views) in ch:
        for key, sig, args in views:
            calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
            meta.append((name, key))
    got = None
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=20)
            if isinstance(res, list) and len(res) == len(calls):
                got = (res, ep); break
        except Exception as e:
            print("  chunk ep", ep, "exc", str(e)[:100], flush=True); continue
    names = [n for n, _ in ch]
    if got is None:
        print(f"chunk {ci+1} FAIL {names}", flush=True)
        chunk_errors.append(names)
        for n in names: reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    res, ep = got
    o = {}
    for it, (name, key) in zip(res, meta):
        if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
            o.setdefault(name, {})[key] = None
        else:
            r = it["result"]
            o.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
    ok += sum(1 for n in names if o.get(n) is not None)
    for n in names: reads[n] = {"address": ITEMS[n][0], "views": o.get(n)}
    print(f"chunk {ci+1} OK via {ep} ({time.time()-T0:.0f}s) {names}", flush=True)
    time.sleep(1)

if time.time() - T0 > LEG4_DEADLINE:
    bsccat_views, bsccat_ep = None, "deadline-skipped"
    pepe_views, pepe_ep = None, "deadline-skipped"
else:
    bsccat_views, bsccat_ep = read_views(BSCCAT[0], BSCCAT[1])
    pepe_views, pepe_ep = read_views(PEPE[0], PEPE[1])
reread = {"started_wib": NOW, "reads": reads, "reads_ok": ok, "reads_total": len(ITEMS),
          "bsccat": {"address": BSCCAT[0], "views": bsccat_views},
          "pepe": pepe_views, "errors": chunk_errors,
          "n_calls": sum(len(v) for _, v in ITEMS.values()) + len(BSCCAT[1]) + len(PEPE[1]),
          "elapsed_s": round(time.time() - T0, 1), "block": None}
json.dump(reread, open(BASE + "hot-leg-run-2026-11-19-0809-reread.json", "w"), indent=1)
blk = block_number()
if blk is not None:
    reread["block"] = blk
    reread["elapsed_s"] = round(time.time() - T0, 1)
    json.dump(reread, open(BASE + "hot-leg-run-2026-11-19-0809-reread.json", "w"), indent=1)
out["leg4_reread_file"] = "hot-leg-run-2026-11-19-0809-reread.json"
out["leg4_rpc_note"] = "chunked direct JSON-RPC batches of 4 items (no fast_rpc race - it timed out + 429 on 0324 run); focus set 2309 + 11 items from main run 2301"
out["leg4_block"] = blk
out["leg4_chunk_errors"] = chunk_errors

# --- Diff vs 0649 reread ---
try:
    prev = json.load(open(BASE + "run-2026-11-19-0801-reread.json"))
    prev_reads = prev.get("reads", {})
    if not isinstance(prev_reads, dict): prev_reads = {}
    changes = []
    for name, item in reads.items():
        pv = (prev_reads.get(name) or {}).get("views") or {}
        cv = item.get("views") or {}
        diff = {}
        for k in set(list(pv.keys()) + list(cv.keys())):
            if pv.get(k) != cv.get(k):
                diff[k] = {"prev": pv.get(k), "now": cv.get(k)}
        if diff:
            changes.append({"item": name, "type": "value-change", "diff": diff})
    out["leg4_changes_vs_0801"] = changes
    pb = (prev.get("bsccat") or {}).get("views") or {}
    cb = bsccat_views or {}
    out["bsccat_changes_vs_0801"] = {k: {"prev": pb.get(k), "now": cb.get(k)}
                                     for k in set(list(pb.keys()) + list(cb.keys())) if pb.get(k) != cb.get(k)}
    pp = prev.get("pepe") or {}
    out["pepe_changes_vs_0801"] = {k: {"prev": pp.get(k), "now": (pepe_views or {}).get(k)}
                                   for k in set(list(pp.keys()) + list((pepe_views or {}).keys()))
                                   if pp.get(k) != (pepe_views or {}).get(k)}
except Exception as e:
    out["leg4_changes_vs_0801"] = {"error": f"{type(e).__name__}: {e}"}

# --- Threshold check (strong lead >70% + age <24h + slot open) ---
tc = {"notes": "Strong-lead bar >70% + age <24h + slot open. Age/website status per item must be judged from this run values + snapshot (see final run summary); bsccat website gate PASS carried from 0239 run (bsccat.com live read 02:17 WIB prints exact mint contract 0x9dd4C7D3276609892cF723a90A5AF3f8df40C79A twice; registry 0x60B9...022F printed) - site NOT re-read this run."}
try:
    pc = (reads.get("PunchCard") or {}).get("views") or {}
    if pc.get("freeMinted") is not None and pc.get("MAX_SUPPLY"):
        tc["PunchCard_free_pct"] = round(100 * pc["freeMinted"] / pc["MAX_SUPPLY"], 1)
    tc["PunchCard_totalSupply"] = pc.get("totalSupply")
    tc["PunchCard_slot"] = {"mintPriceFor_user_1": pc.get("mintPriceFor_user_1"),
                            "mintedCount_user": pc.get("mintedCount_user"),
                            "balanceOf_user": pc.get("balanceOf_user"),
                            "mintOpen": pc.get("mintOpen")}
    ag = (reads.get("AGCLUB") or {}).get("views") or {}
    if ag.get("freeMinted") is not None and ag.get("FREE_CAP"):
        tc["AGCLUB_free_pct"] = round(100 * ag["freeMinted"] / ag["FREE_CAP"], 1)
    mx = (reads.get("Matrix") or {}).get("views") or {}
    if mx.get("freeMinted") is not None and mx.get("freeRemaining") is not None:
        tc["Matrix_free_pct"] = round(100 * mx["freeMinted"] / (mx["freeMinted"] + mx["freeRemaining"]), 1)
    lg = (reads.get("Ledgera") or {}).get("views") or {}
    tc["Ledgera_freeClaimed"] = lg.get("freeClaimed")
    sa = (reads.get("STOCKAGENT") or {}).get("views") or {}
    if sa.get("freeLeft") is not None and sa.get("FREE_SUPPLY"):
        tc["STOCKAGENT_free_pct"] = round(100 * (sa["FREE_SUPPLY"] - sa["freeLeft"]) / sa["FREE_SUPPLY"], 1)
    tc["STOCKAGENT"] = {k: sa.get(k) for k in ("totalSupply","freeLeft","FREE_SUPPLY","mintOpen","quote_user_1","freeMintedByWallet_user","balanceOf_user")}
    lu = (reads.get("Lumenhold") or {}).get("views") or {}
    if lu.get("freeClaimed") is not None and lu.get("FREE_SUPPLY"):
        tc["Lumenhold_free_pct"] = round(100 * lu["freeClaimed"] / lu["FREE_SUPPLY"], 1)
    tc["Lumenhold"] = {k: lu.get(k) for k in ("totalSupply","freeClaimed","FREE_SUPPLY","mintOpen","balanceOf_user","mintedBy_user")}
    al = (reads.get("ALIEN") or {}).get("views") or {}
    if al.get("totalSupply") is not None and al.get("FREE_SUPPLY"):
        tc["ALIEN_free_pct"] = round(100 * al["totalSupply"] / al["FREE_SUPPLY"], 1)
    tc["ALIEN"] = {k: al.get(k) for k in ("totalSupply","FREE_SUPPLY","mintOpen","isFreePhase","balanceOf_user")}
    ar = (reads.get("ARKT") or {}).get("views") or {}
    tc["ARKT"] = {k: ar.get(k) for k in ("totalMinted","totalSupply","MAX_SUPPLY","mintOpen","hasClaimed_user","balanceOf_user")}
    ab = (reads.get("AgentBubble") or {}).get("views") or {}
    if ab.get("freeMinted") is not None and ab.get("MAX_SUPPLY"):
        tc["AgentBubble_free_pct"] = round(100 * ab["freeMinted"] / ab["MAX_SUPPLY"], 1)
    tc["AgentBubble"] = {k: ab.get(k) for k in ("freeMinted","totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user")}
    ae = (reads.get("AgentEcho") or {}).get("views") or {}
    tc["AgentEcho"] = {k: ae.get(k) for k in ("totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user")}
    kg = (reads.get("Kageveil") or {}).get("views") or {}
    tc["Kageveil"] = {k: kg.get(k) for k in ("normalMinted","totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user")}
    ad = (reads.get("ADRAW") or {}).get("views") or {}
    tc["ADRAW"] = {k: ad.get(k) for k in ("freeMinted","totalSupply","balanceOf_user","hasClaimedFree_user")}
    sb = (reads.get("Stromboat") or {}).get("views") or {}
    tc["Stromboat"] = {k: sb.get(k) for k in ("totalMinted","freeMinted","paidMinted","mintOpen","freeMintedBy_user","balanceOf_user")}
    ce = (reads.get("ClafEye") or {}).get("views") or {}
    tc["ClafEye"] = {k: ce.get(k) for k in ("totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user","costFor_user_1")}
    bn = (reads.get("binanceai-mint") or {}).get("views") or {}
    tc["binanceai_pending"] = {k: bn.get(k) for k in ("launched","failed","isRefundPhase","totalShares","tokenClaimed_user")}
    dg = (reads.get("DGF") or {}).get("views") or {}
    tc["DGF"] = {k: dg.get(k) for k in ("totalMinted","totalSupply","mintOpen","balanceOf_user")}
    hb = (reads.get("Hivebyte") or {}).get("views") or {}
    if hb.get("freeClaimed") is not None and hb.get("FREE_SUPPLY"):
        tc["Hivebyte_free_pct"] = round(100 * hb["freeClaimed"] / hb["FREE_SUPPLY"], 1)
    tc["Hivebyte"] = {k: hb.get(k) for k in ("totalSupply","freeClaimed","FREE_SUPPLY","MAX_SUPPLY","mintOpen","balanceOf_user")}
    ap = (reads.get("AgentPepe") or {}).get("views") or {}
    tc["AgentPepe"] = {k: ap.get(k) for k in ("totalMinted","totalSupply","MAX_SUPPLY","mintOpen","balanceOf_user")}
    alp = (reads.get("AlphaPulse") or {}).get("views") or {}
    tc["AlphaPulse"] = {k: alp.get(k) for k in ("totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user")}
    th = (reads.get("THYRK") or {}).get("views") or {}
    if th.get("freeMinted") is not None and th.get("MAX_SUPPLY"):
        tc["THYRK_free_pct"] = round(100 * th["freeMinted"] / th["MAX_SUPPLY"], 1)
    tc["THYRK"] = {k: th.get(k) for k in ("totalSupply","freeMinted","MAX_SUPPLY","balanceOf_user")}
    e5 = (reads.get("E5F8") or {}).get("views") or {}
    tc["E5F8"] = {k: e5.get(k) for k in ("totalMinted","totalSupply","mintOpen")}
    xc = (reads.get("XCOPY") or {}).get("views") or {}
    tc["XCOPY"] = {k: xc.get(k) for k in ("totalSupply","totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user")}
    ei = (reads.get("EIM") or {}).get("views") or {}
    tc["EIM"] = {k: ei.get(k) for k in ("totalMinted","MAX_SUPPLY","mintOpen","balanceOf_user")}
    ac = (reads.get("ARKTclaim") or {}).get("views") or {}
    tc["ARKTclaim"] = {k: ac.get(k) for k in ("totalSupply","totalMinted","balanceOf_user")}
    vi = (reads.get("Vitaliq") or {}).get("views") or {}
    tc["Vitaliq"] = {k: vi.get(k) for k in ("totalSupply","totalMinted","mintOpen","balanceOf_user")}
    a8 = (reads.get("ARKT8334") or {}).get("views") or {}
    tc["ARKT8334"] = {k: a8.get(k) for k in ("totalSupply","totalMinted","mintOpen")}
    pf = (reads.get("PIXELFROGS") or {}).get("views") or {}
    if pf.get("freeMinted") is not None and pf.get("freeLeft") is not None:
        tc["PIXELFROGS_free_pct"] = round(100 * pf["freeMinted"] / (pf["freeMinted"] + pf["freeLeft"]), 1)
    tc["AgentMintPass"] = {k: (reads.get("AgentMintPass") or {}).get("views", {}).get(k) for k in ("totalSupply","totalMinted","freeMinted","freeClaimed","mintOpen","balanceOf_user")}
    tc["AGATE-Pass"] = {k: (reads.get("AGATE-Pass") or {}).get("views", {}).get(k) for k in ("totalSupply","totalMinted","freeMinted","freeClaimed","mintOpen","balanceOf_user")}
    tc["AgentDrop"] = {k: (reads.get("AgentDrop") or {}).get("views", {}).get(k) for k in ("totalSupply","totalMinted","freeMinted","freeClaimed","mintOpen","balanceOf_user")}
except Exception as e:
    tc["error"] = f"{type(e).__name__}: {e}"
out["threshold_check"] = tc

# --- Poffzi FCFS process check ---
try:
    r = subprocess.run(["pgrep", "-af", "fcfs"], capture_output=True, text=True)
    out["poffzi_fcfs"] = r.stdout.strip() if r.stdout.strip() else "NO PROCESS FOUND"
except Exception as e:
    out["poffzi_fcfs"] = f"check error: {e}"

out["elapsed_s"] = round(time.time() - T0, 1)
out["executions"] = "none - no preview, no mint, no claim (this script is read-only)"
json.dump(out, open(BASE + "hot-leg-run-2026-11-19-0809.json", "w"), indent=1)
print("DONE ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - T0, 1))
