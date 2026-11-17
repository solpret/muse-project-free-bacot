#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 14:59 WIB. Legs 1+2+4 + bridge, single script,
hard per-leg deadlines (RPC/Sourcify degradation persists per 07:39 run).
Writes only its own run files + hot-leg-seen.json. Never touches main snapshot."""
import json, urllib.request, urllib.error, subprocess, re, time, sys
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-06-1459"
NOW = "2026-11-06T15:00:00+07:00"
T0 = time.time()
EXCLUDED = ["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"]
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed2.bnbchain.org"]

FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining",
                    "free_slots", "free_supply", "free_amount"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]

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

# ---------- Leg 1: Sourcify feed ----------
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
        out = subprocess.run(["curl", "-s", "--max-time", "15",
                              "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                             capture_output=True, text=True, timeout=20)
        feed = json.loads(out.stdout)
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
        a = r["address"]
        print(a, r["sourcify"], "S1=", r.get("S1"), "S2=", r.get("S2"),
              "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
              "free=", r.get("free_views"), "agent=", r.get("gate_fns"),
              "token=", r.get("token_fns"), flush=True)
    # on-chain probe for ABI-unavailable ones
    unavail = [r for r in shape_out if r["sourcify"].startswith("error")]
    probe = {}
    if unavail:
        def sel(s):
            k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
        SIGS = ["mintFree()", "freeClaimed()", "freeMinted()", "FREE_SLOTS()", "FREE_SUPPLY()",
                "freeSharesRemaining()", "freeLeft()", "agentRegistry()", "freeClaimed(address)",
                "quote(address,uint256)", "freeAvailable()"]
        pdl = time.time() + 20
        def probe_one(addr):
            hits = []
            for s in SIGS:
                if time.time() > pdl:
                    return {"address": addr, "probe": "deadline", "hits": hits}
                data = sel(s); got = False
                for rpc in RPCS:
                    if time.time() > pdl:
                        return {"address": addr, "probe": "deadline", "hits": hits}
                    try:
                        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                           "params": [{"to": addr, "data": data}, "latest"]}).encode()
                        req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
                        with urllib.request.urlopen(req, timeout=4) as rr:
                            out = json.load(rr)
                        if "error" in out:
                            continue
                        v = out.get("result")
                        if v and v != "0x":
                            got = True
                        break
                    except Exception:
                        continue
                if got:
                    hits.append(s)
            return {"address": addr, "probe": "done", "hits": hits}
        with ThreadPoolExecutor(max_workers=5) as ex:
            for res in ex.map(probe_one, [r["address"] for r in unavail]):
                probe[res["address"].lower()] = res
                print("PROBE", res["address"], res["probe"], "hits=", res["hits"], flush=True)
        json.dump(probe, open(f"{BASE}/run-{TS}-probe.json", "w"), indent=1)
        for r in shape_out:
            if r["sourcify"].startswith("error"):
                pr = probe.get(r["address"].lower(), {})
                r["probe"] = pr.get("probe"); r["probe_hits"] = pr.get("hits", [])
    # persist (fresh reload first)
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
            nft = bool(r.get("token_fns")) and ("ownerOf" in str(r.get("mint_fns")))
            seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                       "status": "sale-shape-new", "S1": r.get("S1"), "S2": r.get("S2")}
            sale_shapes.append(a)
        elif r["sourcify"].startswith("error"):
            hits = r.get("probe_hits", [])
            if hits:
                seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                           "status": "checked-not-sale-shape-probe",
                           "note": f"Sourcify verifiedAt {vat.get(a.lower())}. ABI fetch {r['sourcify']}; on-chain probe hits {hits} but S1/S2 not established; NOT a lead, never previewed/minted."}
            elif r.get("probe") == "deadline":
                seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                           "status": "checked-abi-unavailable",
                           "note": f"Sourcify verifiedAt {vat.get(a.lower())}. ABI fetch {r['sourcify']}; on-chain probe hit RPC deadline (degraded) - no sale-shape evidence; recorded, not a lead, never previewed/minted."}
            else:
                seen[a] = {"first_seen_wib": NOW, "source": "sourcify-feed",
                           "status": "checked-not-sale-shape-probe",
                           "note": f"Sourcify verifiedAt {vat.get(a.lower())}. ABI fetch {r['sourcify']}; on-chain probe: no sale-shape selector returns data. NOT a lead, never previewed/minted."}
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
print("LEG1 done in %.1fs" % (time.time() - T0), flush=True)

# ---------- Leg 2: Boltbook front page, boltbook.fun en+zh (Lemmy API returns
# a generic feed per run 08:54 note; direct front-page fetch is the correct source) ----------
bb_addrs = set()
bb_kw_hits = []
for lang, url in [("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")]:
    fn = f"{BASE}/boltbook-{TS}-{lang}.html"
    try:
        out = subprocess.run(["curl", "-s", "--max-time", "15", "-A", "Mozilla/5.0", url],
                             capture_output=True, text=True, timeout=20)
        html = out.stdout or ""
        open(fn, "w").write(html)
        print(f"BOLTBOOK {lang} bytes={len(html)}", flush=True)
        if not html:
            continue
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        kws = ["free share", "first share free", "1 free share", "free mint share",
               "free mint", "免费份额", "首个免费", "免费铸造", "免费mint"]
        for k in kws:
            for m in re.finditer(re.escape(k), text, re.IGNORECASE):
                s = max(0, m.start() - 120); e = min(len(text), m.end() + 160)
                bb_kw_hits.append((lang, k, text[s:e].strip()[:220]))
        for m in re.findall(r"0x[a-fA-F0-9]{40}", html):
            bb_addrs.add(m)
    except Exception as e:
        print(f"BOLTBOOK {lang} FAIL", repr(e), flush=True)
print("BOLTBOOK keyword hits:", len(bb_kw_hits), flush=True)
for h in bb_kw_hits[:12]:
    print("  KW", h, flush=True)
print("BOLTBOOK addresses:", sorted(bb_addrs), flush=True)
seen_l2 = {k.lower() for k in json.load(open(f"{BASE}/hot-leg-seen.json"))}
bb_new = [m for m in sorted(bb_addrs) if m.lower() not in seen_l2]
print("BOLTBOOK new (not in seen):", bb_new, flush=True)
if bb_new:
    dl2 = time.time() + 40
    bb_shape = []
    def bb_check(a):
        st, abi = fast_abi(a, dl2)
        r = {"address": a, "sourcify": st}
        if abi is not None:
            r.update(classify(abi))
        else:
            r["S1"] = False; r["S2"] = False
        return r
    with ThreadPoolExecutor(max_workers=5) as ex:
        bb_shape = list(ex.map(bb_check, bb_new))
    json.dump(bb_shape, open(f"{BASE}/run-{TS}-boltbook-shape.json", "w"), indent=1)
    seen = json.load(open(f"{BASE}/hot-leg-seen.json"))
    for r in bb_shape:
        a = r["address"]
        print(a, r["sourcify"], "S1=", r.get("S1"), "S2=", r.get("S2"),
              "mint=", r.get("mint_fns"), "quote=", r.get("quote_fns"),
              "free=", r.get("free_views"), "agent=", r.get("gate_fns"), flush=True)
        if a.lower() in EXCLUDED:
            seen[a] = {"first_seen_wib": NOW, "source": "boltbook", "status": "excluded"}
            continue
        if r.get("S1") or r.get("S2"):
            seen[a] = {"first_seen_wib": NOW, "source": "boltbook",
                       "status": "sale-shape-new", "S1": r.get("S1"), "S2": r.get("S2")}
            sale_shapes.append(a)
        else:
            seen[a] = {"first_seen_wib": NOW, "source": "boltbook",
                       "status": "checked-not-sale-shape",
                       "note": (f"Boltbook front page {TS}. S1={r.get('S1')} S2={r.get('S2')} "
                                f"mint={r.get('mint_fns')} quote={r.get('quote_fns')} "
                                f"free={r.get('free_views')} agent={r.get('gate_fns')}")}
    json.dump(seen, open(f"{BASE}/hot-leg-seen.json", "w"), indent=1)
    print("BOLTBOOK shape-checked", len(bb_shape), "SALE-SHAPES so far:", sale_shapes, flush=True)
print("LEG2 done in %.1fs" % (time.time() - T0), flush=True)

# ---------- Leg 4: targeted snapshot re-read (read-only) ----------
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
DL4 = time.time() + 50
def raw(to, data):
    for rpc in RPCS:
        if time.time() > DL4:
            return "deadline"
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
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

ITEMS = {
 "Forklings": ("0xD7B3FD33e0b465B0e374906F60567D317b758FD8",
   ["totalSupply()", "freeMinted()", "balanceOf(address)", "mintedBy(address)",
    "claimedFree(address)", "freeClaimed()"]),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90",
   ["totalSupply()", "freeMinted()", "freeClaimed()", "balanceOf(address)", "claimedFree(address)"]),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)", "claimedFree(address)"]),
 "Hashseers": ("0x7E634ED532a7b7b781262A0d4220ac3c3Ba6B688",
   ["totalSupply()", "freeMinted()", "balanceOf(address)", "claimedFree(address)"]),
 "Smeltbots": ("0xdC0004F3Efcc2aEA6052e138d3f1e680ca5D9b8e",
   ["totalSupply()", "freeMinted()", "balanceOf(address)", "claimedFree(address)"]),
 "PassAgentX": ("0x08b1A979Dd997492EEcc010fe986eA2e2925e620",
   ["totalSupply()", "totalMinted()", "freeMinted()", "balanceOf(address)", "freeUsed(address)"]),
 "MILLION": ("0xD36B54fbd4c9fA99731b52907713c9e1983aD8a4",
   ["totalSupply()", "totalMinted()", "freeMinted()", "balanceOf(address)"]),
 "AgentGlyph": ("0x3ef2a97abf2e43182eacae323b82d2cac2132c6a",
   ["freeClaimed()", "totalSupply()", "FREE_SUPPLY()"]),
 "KING Agent": ("0x2A2463d243E5c4dF850e48f350392AD23B494132",
   ["totalSupply()", "freeQuota()", "remainingFree()", "mintedBy(address)", "balanceOf(address)", "mintOpen()"]),
 "DROID": ("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
   ["opened()", "freeMinted()", "totalMinted()"]),
 "IMARS": ("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",
   ["opened()", "freeMinted()", "totalMinted()"]),
 "OSK": ("0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
   ["opened()", "totalMinted()"]),
 "Tacotron": ("0x05debe4445232205ae7e79d02cb5de5aa0641eff",
   ["totalSupply()", "freeClaimed()", "freeLeft(address)", "freeUsed(address)", "mintedBy(address)", "balanceOf(address)"]),
 "Candlix": ("0x263d87e3b4a284b6e4b0b80f7945b6095113ffe6",
   ["totalSupply()", "freeClaimed()", "freeLeft(address)", "freeUsed(address)", "mintedBy(address)", "balanceOf(address)"]),
 "DeY": ("0xDB062c12bF0a14227e7Fe896a988950b050B51C1",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "FANBEIMAO": ("0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "LuckyBox": ("0xd08ef372B52C29255fEd7004f59bF41571451894",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "NJAR": ("0x816458b734d17d59058762deaadd9b952bad6985",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "Predictagent": ("0x8fF4bd65584882324c44Ee794a23E7791820189b",
   ["totalSupply()", "freeClaimed()", "freeMinted()", "balanceOf(address)"]),
 "FABE": ("0xFabE022a5943462fee1Bd221791945DA57510BE8",
   ["freeSharesRemaining()", "freeSharesClaimed(address)", "launched()", "balanceOf(address)"]),
 "Agentidbsc": ("0x716BFaB3B7b0301D17Af0fF4c50a880C7721F39C",
   ["totalSupply()", "freeClaimed()", "freeAvailable()", "balanceOf(address)"]),
 "Crack-live": ("0xAeA1433dBD9e7edE0914d996C2Dad692E6e01e09",
   ["totalSupply()", "publicRemaining()", "mintOpen()", "mintCost(address,uint256)",
    "freeUsed(address)", "mintedBy(address)", "balanceOf(address)"]),
 "Neurolucha": ("0x56eBED63452Bb02B975ceE02949DA3C02466725b",
   ["totalSupply()", "freeMinted()", "balanceOf(address)", "claimedFree(address)",
    "canFreeMint(address)"]),
}
def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if sig.startswith("mintCost"):
            v = call(addr, sig, enc(USER) + "0" * 63 + "1"); key += "_user1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    print(name, d, flush=True)
    return name, d

blk = block()
print("BLOCK", blk, flush=True)
out = {"block": blk, "reread": {}}
with ThreadPoolExecutor(max_workers=10) as ex:
    for name, d in ex.map(read_item, list(ITEMS.items())):
        out["reread"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-reread-targeted.json", "w"), indent=1)
print("LEG4 done in %.1fs block %s" % (time.time() - T0, blk), flush=True)

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
              open(f"{BASE}/hot-leg-{TS}-bridge.json", "w"), indent=1)
except Exception as e:
    print("BRIDGE-ERROR", e, flush=True)
print("DONE total %.1fs" % (time.time() - T0), flush=True)
