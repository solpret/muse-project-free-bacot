#!/usr/bin/env python3
"""Main run 2026-11-06 08:01 WIB. Legs 1+2+5a + Track B + bridge (read-only).
Adapted from run-2026-11-06-0731-reread.py + hot-leg-2026-11-06-0809.py.
Adds the 6 newest early leads (FOD/NEBA/SHAY + trio 0701) to the re-read set.
Never writes the main snapshot (finalize step does that)."""
import json, urllib.request, urllib.error, subprocess, re, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-0901"
NOW = "2026-11-06T09:01:00+07:00"
T0 = time.time()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]
EXCLUDED = ["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"]
FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining",
                    "free_slots", "free_supply", "free_amount"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]
# CORRECTED gate: include underscore variants (0731 lesson: classify() missed AGENT_REGISTRY)
GATE_WORDS = ["agentid", "agent_id", "agentregistry", "agent_registry",
              "agentgate", "agent_gate", "hasagentid", "isagent"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data, timeout=5):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def block():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: return int(json.load(r)["result"], 16)
        except Exception: continue
    return None

NFT = {
 "HIVE Agents": ("0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132", ["totalSupply()", "totalMinted()", "freeQuota()", "remainingFree()", "mintedBy(address)", "costOf(address,uint256)", "balanceOf(address)", "agentGateOn()", "mintOpen()"]),
 "Mummyhive": ("0xf45fE22B3a9A748c59A7099e2E7B69f41216b1cd", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "Hashseers": ("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "Smeltbots": ("0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "Forklings": ("0xD7B3FD33e0b465B0e374906F60567D317b758FD8", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "costOf(address,uint256)", "mintsLeft(address)", "mintOpen()", "mintedBy(address)", "price()"]),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "PassAgentX": ("0x08b1A979Dd997492EEcc010fe986eA2e2925e620", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "SEAT-f11e": ("0xf11e9405b23ca0f53e6135162a85545d780a3737", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "StarAgent-7d39": ("0x7d390e37Ed41A359f276D8764ca15432704B99b7", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "WAGagent": ("0x06a6f51D30556f4262e38485C09556fE81e6A984", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "LuckyBox-d08e": ("0xd08ef372B52C29255fEd7004f59bF41571451894", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "mintedBy(address)", "freeUsed(address)", "canFreeMint(address)", "claimedFree(address)", "quote(address,uint256)"]),
 "SnailMail": ("0xb773e52fE45196c840F8e59c3B4bB944633Ae03a", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "costOf(address,uint256)", "mintsLeft(address)", "mintOpen()", "mintedBy(address)", "price()"]),
 "wheelz": ("0x5aCC0Ec4449Edb788f43803cDb1A11f1f6b7E64d", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "costOf(address,uint256)", "mintsLeft(address)", "mintOpen()", "mintedBy(address)", "price()"]),
 "Layerloom": ("0x1B72ceC52A74537b06F713FCebA0e491f53679aE", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Tumblebots": ("0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Mossminds": ("0x5b49B06a2E25FcE0BCa865Be70F3C62b6319367a", ["totalSupply()", "freeMinted()", "canFreeMint(address)", "claimedFree(address)", "balanceOf(address)"]),
 "Jolly": ("0xdc11764a5664e333c8d303eb465e89a1caadb85b", ["totalSupply()", "totalMinted()", "freeMinted()", "balanceOf(address)"]),
 "AgentGlyph": ("0x3ef2a97abf2e43182eacae323b82d2cac2132c6a", ["freeClaimed()", "totalSupply()", "FREE_SUPPLY()"]),
 "Pacture": ("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", ["freeClaimed(address)", "totalMinted()", "freeMinted()", "balanceOf(address)"]),
 "MILLION": ("0xD36B54fbd4c9fA99731b52907713c9e1983aD8a4", ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()", "agentRegistry()", "FREE_SUPPLY()", "balanceOf(address)"]),
 # New early leads run 0731 + trio 0701
 "FOD Agent": ("0xA3d24EE16b6b912192724598Da55C7909bBB97e8", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "mintedBy(address)", "balanceOf(address)", "costOf(address,uint256)", "spotsLeft()"]),
 "Nebula Ape Agent": ("0x79720611065DF9Fc810399DC1eeE870b3A8AD3fC", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "mintedBy(address)", "balanceOf(address)", "spotsLeft()", "MAX_SUPPLY()", "PRICE()", "quote(address,uint256)"]),
 "Shadow Yeti Agent": ("0xA193Ea677a39D4F04bB770555fe6954e0e00C02C", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "mintedBy(address)", "balanceOf(address)", "spotsLeft()", "MAX_SUPPLY()", "PRICE()", "quote(address,uint256)"]),
 "Silent Hydra Agent": ("0x56C7776351BaDf99D33A602026aAAD7Afc5E4dF4", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "mintedBy(address)", "balanceOf(address)", "spotsLeft()", "MAX_SUPPLY()", "PRICE()", "quote(address,uint256)"]),
 "Cipher Wraith Agent": ("0x50e9958a50B239f96fC64b9e1A06A3850D24063a", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "mintedBy(address)", "balanceOf(address)", "spotsLeft()", "MAX_SUPPLY()", "PRICE()", "quote(address,uint256)"]),
 "Umbra Lynx Agent": ("0x1062c963F5F11A5A55831B7e818E55b052B59947", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "mintedBy(address)", "balanceOf(address)", "spotsLeft()", "MAX_SUPPLY()", "PRICE()", "quote(address,uint256)"]),
 # New early leads run 0801 + Crack (sale-shape, age pending)
 "Data Synth": ("0x7Bd19ee3c72b4544787EbA0ebD655e1376FE3642", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "mintedBy(address)", "balanceOf(address)", "spotsLeft()", "MAX_SUPPLY()", "PRICE()", "quote(address,uint256)"]),
 "Zero Genesis": ("0x7807202FBE09f4AAC9ac312ed593ba16806F6b34", ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "mintedBy(address)", "balanceOf(address)", "spotsLeft()", "MAX_SUPPLY()", "PRICE()", "quote(address,uint256)"]),
 "Crack": ("0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09", ["totalSupply()", "totalMinted()", "publicRemaining()", "freeUsed(address)", "mintCost(address,uint256)", "mintOpen()", "hasAgentId(address)", "price()", "balanceOf(address)", "mintedBy(address)"]),
}

TC = {
 "OSK": "0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
 "NIULAI": "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",
 "KillZero-K0-sale": "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",
 "DROID": "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
 "IMARS": "0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
 "ASOC-43cE": "0x43cEef9313CB8c4ca3757bA841C44DF40A223205",
 "SENBAZURU-b215": "0xb21583A08581278BcF925351a99C61A4562C62f0",
 "FABE": "0xB44AC34F6089B7c5c99CBc1643E22838e67C9D4d",
 "QAGENT-2": "0xE3a4f3099a2136e0e66202A665815caB8FFA2704",
 "ShibAgent-R2": "0x016a148e728b8d61b2440ed311946ac06d4b5648",
 "DeY": "0xDB062c12bF0a14227e7Fe896a988950b050B51C1",
 "BoxBigem-3Ee9": "0x3Ee92296D663378D42521273aAA4779BDa8e25dD",
 "FANBEIMAO-824d": "0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",
 "Ikigai-Ihigi": "0x3611455bE1FC2c6987FE9d016971b7E40B341684",
 "Hongbao-HONGBAO": "0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97",
 "Nvagent-NVGT-28Fe": "0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2",
 "Soarm-SOARM": "0x4a02e3824b301a1bf6a8230e56b44b526174ca97",
 "SAFUAI": "0xbd6087fc30f2395344020cb190255c56cbc517bd",
}
TC_VIEWS = ["opened()", "launched()", "freeMinted()", "freeSharesRemaining()",
            "freeSharesClaimed(address)", "freeClaimed(address)", "hasFreeShare(address)",
            "totalMinted()", "sharesMinted()", "saleEnded()", "phase()"]

def read_item(args):
    name, addr, views = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if "address" in sig and "uint256" in sig:
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user_1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, d, flush=True)
    return name, d

# ---------- Leg 1: re-read ----------
jobs = []
for name, (addr, views) in NFT.items():
    jobs.append((name, addr, views))
for name, addr in TC.items():
    jobs.append((name, addr, TC_VIEWS))

blk = block()
print("BLOCK", blk, flush=True)
t0 = time.time()
out = {"block": blk, "reread": {}, "track_c": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_item, jobs):
        if name in NFT:
            out["reread"][name] = d
        else:
            out["track_c"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-reread-lean.json", "w"), indent=1)
print("LEG1 done in %.1fs block %s" % (time.time() - t0, blk), flush=True)

# ---------- Leg 2: Boltbook via Lemmy API ----------
try:
    req = urllib.request.Request(
        "https://boltbook.ai/api/v3/post/list?type_=All&sort=New&limit=50",
        headers={"User-Agent": "curl"})
    with urllib.request.urlopen(req, timeout=15) as r:
        bb = json.load(r)
    json.dump(bb, open(f"{BASE}/run-{TS}-boltbook-api.json", "w"), indent=1)
    posts = bb.get("posts", [])
    print("BOLTBOOK OK", len(posts), "newest",
          posts[0]["post"].get("published") if posts else None, flush=True)
    kws_en = ["free share", "first share free", "1 free share", "free mint share", "free mint"]
    kws_zh = ["免费份额", "首个免费", "免费铸造", "免费mint"]
    hits = []
    addr_re = re.compile(r"0x[a-fA-F0-9]{40}")
    addrs_found = set()
    for p in posts:
        post = p.get("post", {})
        text = ((post.get("name") or "") + " " + (post.get("body") or "")).lower()
        if any(k in text for k in kws_en + kws_zh):
            hits.append((post.get("id"), post.get("name"), post.get("ap_id")))
        for m in addr_re.findall(post.get("name", "") + " " + (post.get("body") or "")):
            addrs_found.add(m)
    print("BOLTBOOK keyword hits:", len(hits), hits, flush=True)
    print("BOLTBOOK addresses in 50 posts:", sorted(addrs_found), flush=True)
except Exception as e:
    print("BOLTBOOK FAIL", repr(e), flush=True)
print("LEG2 done in %.1fs" % (time.time() - T0), flush=True)

# ---------- Leg 5a: Sourcify feed + shape (corrected gate) ----------
def classify(abi):
    funcs = [it.get("name", "") for it in abi if isinstance(abi, list)
             and isinstance(it, dict) and it.get("type") == "function"]
    low = [f.lower() for f in funcs]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "mint", "claimfree")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "S1": s1, "S2": s2}

def fast_abi(addr, deadline):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    for i in range(2):
        if time.time() > deadline:
            return ("error:deadline", None)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                return ("verified", json.loads(resp.read().decode()).get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
        except Exception:
            time.sleep(1)
    return ("error:retry-exhausted", None)

feed = {"results": []}
try:
    req = urllib.request.Request(
        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",
        headers={"User-Agent": "curl"})
    with urllib.request.urlopen(req, timeout=15) as r:
        feed = json.load(r)
    print("FEED OK urllib", len(feed.get("results", [])), flush=True)
except Exception as e:
    print("FEED FAIL urllib", repr(e), flush=True)
    try:
        o = subprocess.run(["curl", "-s", "--max-time", "15",
                            "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                           capture_output=True, text=True, timeout=20)
        feed = json.loads(o.stdout)
        print("FEED OK via curl", len(feed.get("results", [])), flush=True)
    except Exception as e2:
        print("FEED FAIL curl", repr(e2), flush=True)
        feed = {"results": []}
json.dump(feed, open(f"{BASE}/run-{TS}-sourcify-feed.json", "w"), indent=1)
results = feed.get("results", [])
if results:
    print("FEED range", results[0].get("verifiedAt"), "->", results[-1].get("verifiedAt"), flush=True)
seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l = {k.lower() for k in seen}
addrs = [x["address"] for x in results]
new = [a for a in addrs if a.lower() not in seen_l]
print("FEED", len(addrs), "NEW", len(new), new, flush=True)
vat = {it["address"].lower(): it.get("verifiedAt") for it in results}
shape_out = []
sale_shapes = []
if new:
    dl = time.time() + 45
    def check(a):
        st, abi = fast_abi(a, dl)
        r = {"address": a, "verifiedAt": vat.get(a.lower()), "sourcify": st}
        if abi is not None:
            r.update(classify(abi))
        else:
            r["S1"] = False; r["S2"] = False
        return r
    with ThreadPoolExecutor(max_workers=6) as ex:
        shape_out = list(ex.map(check, new))
    for r in shape_out:
        print(r["address"], r["sourcify"], "S1=", r.get("S1"), "S2=", r.get("S2"),
              "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
              "free=", r.get("free_views"), "agent=", r.get("gate_fns"),
              "token=", r.get("token_fns"), flush=True)
    seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
    seen_l = {k.lower() for k in seen}
    for r in shape_out:
        a = r["address"]
        if a.lower() in seen_l:
            print("SKIP already in seen:", a, flush=True); continue
        if a.lower() in EXCLUDED:
            seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed", "status": "excluded"}
            print(a, "EXCLUDED", flush=True); continue
        if r.get("S1") or r.get("S2"):
            seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                       "status": "sale-shape-new", "S1": r.get("S1"), "S2": r.get("S2")}
            sale_shapes.append(a)
        elif r["sourcify"].startswith("error"):
            seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                       "status": "checked-abi-unavailable",
                       "note": f"Sourcify verifiedAt {vat.get(a.lower())}. ABI fetch {r['sourcify']}; no sale-shape evidence; recorded, not a lead."}
        else:
            seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                       "status": "checked-not-sale-shape",
                       "note": (f"Sourcify verifiedAt {vat.get(a.lower())}. "
                                f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint_fns')} "
                                f"quote={r.get('quote_fns')} free={r.get('free_views')} "
                                f"agent={r.get('gate_fns')} token={r.get('token_fns')}")}
    json.dump(shape_out, open(f"{BASE}/run-{TS}-sourcify-shape.json", "w"), indent=1)
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
    print("SEEN total", len(seen), "SALE-SHAPES", sale_shapes, flush=True)
print("LEG5a done in %.1fs" % (time.time() - T0), flush=True)

# ---------- Track B: binanceai.fun ----------
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
bai = {}
for sig in ["launched()", "failed()", "isRefundPhase()", "totalShares()"]:
    bai[sig] = raw(MINT, sel(sig), timeout=8)
bai["tokenClaimed(user)"] = raw(MINT, sel("tokenClaimed(address)") + enc(USER), timeout=8)
bai["tokenBalance(user)"] = raw(TOKEN, sel("balanceOf(address)") + enc(USER), timeout=8)
print("BINANCEAI", bai, flush=True)
json.dump(bai, open(f"{BASE}/run-{TS}-binanceai.json", "w"), indent=1)

# ---------- Bridge (read-only) ----------
try:
    br = json.load(open(f"{BASE}/scan-bridge.json"))
    cons = br.get("contracts", {})
    snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text = json.dumps(snap)
    not_in_snap = [c for c in cons if c.lower() not in snap_text.lower()]
    discarded = [c for c, v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE", len(cons), "discarded", len(discarded), "not_in_snapshot", len(not_in_snap), flush=True)
    json.dump({"total": len(cons), "discarded": len(discarded), "not_in_snapshot": len(not_in_snap),
               "not_in_snapshot_list": not_in_snap},
              open(f"{BASE}/run-{TS}-bridge.json", "w"), indent=1)
except Exception as e:
    print("BRIDGE-ERROR", e, flush=True)
print("DONE total %.1fs" % (time.time() - T0), flush=True)
