#!/usr/bin/env python3
"""Hot-leg run 2026-11-11 13:59 WIB. Legs: (1) Sourcify feed + shape-check
(quote set widened: quoteFor/priceAt/getPrice per 1344 flag),
(2) Boltbook EN+ZH, (3) new sale-shape on-chain verify (only if any)
+ re-check of 1349 watchlist-only sale-shapes 0xBa3c / 0xFdD3,
(4) leg4 prio re-read via fast_rpc vs 1349 baseline. Read-only; no preview/mint.
Bridge: read scan-bridge.json read-only. Discards checked before any promotion."""
import json, re, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-1359"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = "0" * 24 + USER[2:].lower()
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
AGENTID = "12411464190637771618140538948436718430879438309640658942350393382867700450815750101755948145101197728078227495339265465644916641821446368465628375122182145"
t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-11 13:59 WIB", "started_wib": "2026-11-11 13:59:38 WIB"}

def get(url, timeout=12):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

seen = json.load(open(HF + "hot-leg-seen.json"))
seen_lower = {k.lower(): v for k, v in seen.items()}
try:
    disc = json.load(open(HF + "same-owner-discards.json"))
    disc_addrs = set()
    for d in disc:
        if isinstance(d, str): disc_addrs.add(d.lower())
        elif isinstance(d, dict):
            for k in ("address", "contract", "sale", "token"):
                if d.get(k): disc_addrs.add(str(d[k]).lower())
    out["discards_loaded"] = len(disc_addrs)
except Exception as e:
    disc_addrs = set(); out["discards_loaded"] = f"error: {e}"[:120]

# ---- Leg 1: Sourcify feed ----
feed = {"returned": 0, "new": [], "already_seen": 0, "error": None}
try:
    st, raw = get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 15)
    feed_json = json.loads(raw)
    with open(HF + f"hot-leg-{TAG}-feed.json", "w") as f:
        json.dump(feed_json, f)
    results = feed_json.get("results", [])
    feed["returned"] = len(results)
    feed["verified_range"] = (results[-1].get("verifiedAt"), results[0].get("verifiedAt")) if results else None
    for r in results:
        a = r.get("address", "")
        if a.lower() in seen_lower:
            feed["already_seen"] += 1
        else:
            feed["new"].append(a)
except Exception as e:
    feed["error"] = str(e)[:200]
out["leg1_sourcify_feed"] = feed

# ---- Leg 1b: shape-check new contracts ----
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted",
              "freeSharesLeft","freeRemaining"}
QUOTE_FNS = {"quote","cost","getCost","price","mintPrice","getQuote","quoteFor","priceAt","getPrice"}
shapes = {}
for addr in feed["new"]:
    if addr.lower() in EXCLUDED:
        shapes[addr] = {"excluded": True}; continue
    try:
        st, raw = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", 12)
        d = json.loads(raw)
        abi = d.get("abi") or d.get("stdJson", {}).get("abi") or []
        fns = [x.get("name","") for x in abi if x.get("type") == "function"]
        fnset = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in fnset)
        has_quote = bool(fnset & QUOTE_FNS)
        free_hits = sorted(fnset & FREE_VIEWS)
        has_token = bool(fnset >= {"name","symbol","decimals","totalSupply"})
        has_free_mint = "mintFree" in fnset
        has_free_slots = bool(fnset & {"FREE_SLOTS","FREE_SUPPLY","FREE_AMOUNT"})
        agent = bool(fnset & {"agentRegistry","AGENT_REGISTRY","agentIdOf","AgentGate"}) or REGISTRY.lower() in raw.decode("utf-8","ignore").lower()
        s1 = has_mint and has_quote and bool(free_hits) and agent
        s2 = has_token and has_free_mint and bool(free_hits) and has_free_slots and agent
        shapes[addr] = {"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
                        "free": free_hits, "agent": agent, "token": has_token, "fns": len(fns)}
    except Exception as e:
        shapes[addr] = {"error": str(e)[:150]}
out["leg1_shapes"] = shapes
with open(HF + f"hot-leg-{TAG}-shape.json", "w") as f:
    json.dump(shapes, f, indent=1)

# ---- Leg 2: Boltbook EN + ZH ----
def boltbook(lang, fname):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "?lang=en")
    try:
        st, raw = get(url, 15)
        open(HF + fname, "wb").write(raw)
        txt = raw.decode("utf-8", "ignore")
        addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", txt)))
        new_addrs = [a for a in addrs if a.lower() not in seen_lower]
        return {"http": st, "bytes": len(raw), "addrs": len(addrs),
                "new_addrs": new_addrs,
                "kw_free_share": txt.lower().count("free share"),
                "kw_free_mint": txt.lower().count("free mint")}
    except Exception as e:
        try:
            import subprocess
            r = subprocess.run(["curl","-sS","-m","15","-A","Mozilla/5.0",url],
                               capture_output=True, timeout=20)
            raw = r.stdout
            open(HF + fname, "wb").write(raw)
            txt = raw.decode("utf-8", "ignore")
            addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", txt)))
            new_addrs = [a for a in addrs if a.lower() not in seen_lower]
            return {"http": 200, "bytes": len(raw), "retry": "curl-ok", "addrs": len(addrs),
                    "new_addrs": new_addrs,
                    "kw_free_share": txt.lower().count("free share"),
                    "kw_free_mint": txt.lower().count("free mint")}
        except Exception as e2:
            return {"error": str(e)[:120] + " | curl: " + str(e2)[:80]}
out["leg2_boltbook_en"] = boltbook("en", f"hot-leg-{TAG}-boltbook-en.html")
out["leg2_boltbook_zh"] = boltbook("zh", f"hot-leg-{TAG}-boltbook-zh.html")

# ---- Bridge (read-only) ----
try:
    br = json.load(open(HF + "scan-bridge.json"))
    baddrs = {k.lower() for k in br.get("contracts", {}).keys()}
    out["bridge"] = {"contracts": len(baddrs),
                     "new_feed_in_bridge": [a for a in feed["new"] if a.lower() in baddrs],
                     "new_boltbook_in_bridge": [a for a in out["leg2_boltbook_en"].get("new_addrs", []) + out["leg2_boltbook_zh"].get("new_addrs", []) if a.lower() in baddrs]}
except Exception as e:
    out["bridge"] = {"error": str(e)[:150]}

# ---- Leg 3/4 helpers ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def dec_uint(h):
    if not h or h == "0x" or len(h) < 66: return None
    try: return int(h[2:66], 16)
    except Exception: return None

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def batch_calls(calls_meta):
    res = {}
    for (name, label, kind), (method, params) in calls_meta:
        val = None; err = None
        for ep in EPS:
            try:
                val = _single(ep, method, params, 12, retries=0)
                break
            except Exception as e:
                err = str(e)[:120]
        if val is None:
            res.setdefault(name, {})[label] = {"error": err}
        else:
            res.setdefault(name, {})[label] = dec_uint(val)
    return res

# ---- Leg 3: verify new sale-shape contracts (S1/S2 pass only) ----
leg3 = {}
for addr, sh in shapes.items():
    if sh.get("S1") or sh.get("S2"):
        leg3[addr] = {"shape": sh, "note": "S1/S2 pass - on-chain verify needed"}
out["leg3_new_sale_shape"] = leg3

# ---- Leg 3b: re-check 1344 watchlist-only sale-shapes ----
recheck = []
# 0xBa3c: sale 0xBa3cCb10183688a601E5dea18a42bE4d584EE433
recheck.append(("BA3C", "opened", "opened()", "uint"))
recheck.append(("BA3C", "totalMinted", "totalMinted()", "uint"))
recheck.append(("BA3C", "freeMinted", "freeMinted()", "uint"))
recheck.append(("BA3C", "agentRegistry", "agentRegistry()", "uint"))
# 0xFdD3: free mint 0xFdD3Bc978349d528D935051AF39C8F04F77184D0
recheck.append(("FDD3", "freeMinted", "freeMinted()", "uint"))
recheck.append(("FDD3", "freeRemaining", "freeRemaining()", "uint"))
recheck.append(("FDD3", "paused", "paused()", "uint"))
recheck.append(("FDD3", "freeClaimed_user", "freeClaimed(address)", "user"))
ADDR3 = {"BA3C": "0xBa3cCb10183688a601E5dea18a42bE4d584EE433",
         "FDD3": "0xFdD3Bc978349d528D935051AF39C8F04F77184D0"}
calls3 = []
for name, label, sig, kind in recheck:
    arg = USER_PAD if kind == "user" else ""
    calls3.append(((name, label, kind), ("eth_call", [{"to": ADDR3[name], "data": sel(sig) + arg}, "latest"])))
out["leg3b_recheck"] = batch_calls(calls3)

# ---- Leg 4: prio re-read ----
PRIO = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", [
    ("totalSupply","totalSupply()","uint"),("mintOpen","mintOpen()","uint"),
    ("agentFreeUsed","agentFreeUsed()","uint"),("freeLeft","freeLeft()","uint"),
    ("balanceOf_user","balanceOf(address)","user"),("agentFreeByWallet_user","agentFreeByWallet(address)","user")]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("totalMinted","totalMinted()","uint"),("freeMinted","freeMinted()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [
    ("totalSupply","totalSupply()","uint"),("agentFreeUsed","agentFreeUsed()","uint"),
    ("mintOpen","mintOpen()","uint"),("balanceOf_user","balanceOf(address)","user")]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [
    ("totalMinted","totalMinted()","uint"),("freeMinted","freeMinted()","uint"),
    ("FREE_SUPPLY","FREE_SUPPLY()","uint"),("mintOpen","mintOpen()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened","opened()","uint"),("totalFreeMinted","totalFreeMinted()","uint"),
    ("totalMinted","totalMinted()","uint")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("launched","launched()","uint"),("startTime","startTime()","uint"),
    ("freeClaimed_user","freeClaimed(address)","user")]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("FREE_SHARES","FREE_SHARES()","uint"),("freeClaimed_user","freeClaimed(address)","user")]),
 "CAP7": ("0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd", [
    ("freeMinted","freeMinted()","uint"),("sharesMinted","sharesMinted()","uint"),
    ("soldOut","soldOut()","uint"),("phase","phase()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("SALE_START","SALE_START()","uint"),("FREE_SHARES","FREE_SHARES()","uint"),
    ("freeSharesLeft","freeSharesLeft()","uint"),("openedAt","openedAt()","uint")]),
 "BotFighters": ("0x58a704d9e02FE11c0A61683AE7F606E4366F13eb", [
    ("FREE_CAP","FREE_CAP()","uint"),("freeMinted","freeMinted()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "BHTB": ("0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467", [
    ("freeRemaining","freeRemaining()","uint")]),
 "AgentGrid": ("0x651302C0043040D48EaAF85605E12F0549aD6D89", [
    ("freeUsed","freeUsed()","uint")]),
 "SUDOSAINTS": ("0x869d330bb48e7ab32da16745ef9a36a69d34f12f", [
    ("totalSupply","totalSupply()","uint"),("freeMinted","freeMinted()","uint"),
    ("mintActive","mintActive()","uint"),("freeUsed_user","freeUsed(address)","user"),
    ("balanceOf_user","balanceOf(address)","user")]),
}
calls4 = []
for name, (addr, specs) in PRIO.items():
    for label, sig, kind in specs:
        arg = USER_PAD if kind == "user" else ""
        calls4.append(((name, label, kind), ("eth_call", [{"to": addr, "data": sel(sig) + arg}, "latest"])))
calls4.append((("CAP7", "agentIdOf_user", "uint"), ("eth_call", [{"to": "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd", "data": sel("agentIdOf(address)") + USER_PAD}, "latest"])))
calls4.append((("CAP7", "freeClaimed_agentId", "uint"), ("eth_call", [{"to": "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd", "data": sel("freeClaimed(uint256)") + format(int(AGENTID), "064x")}, "latest"])))
calls4.append((("RigForge", "freeTaken_agentId", "uint"), ("eth_call", [{"to": "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", "data": sel("freeTaken(uint256)") + format(int(AGENTID), "064x")}, "latest"])))
calls4.append((("HEAD", "block", "uint"), ("eth_blockNumber", [])))
res4 = batch_calls(calls4)
head = res4.get("HEAD", {}).get("block")
out["leg4_block"] = head
out["leg4_values"] = {k: v for k, v in res4.items() if k != "HEAD"}
with open(HF + f"hot-leg-{TAG}-prio.json", "w") as f:
    json.dump({"block": head, "values": out["leg4_values"]}, f, indent=1)

# ---- update hot-leg-seen.json with newly seen (feed + boltbook) ----
now = "2026-11-11 13:59 WIB"
added = 0
for a in feed["new"]:
    if a not in seen and a.lower() not in seen_lower:
        seen[a] = {"first_seen": now, "source": "sourcify-feed-1359"}; added += 1
for a in out["leg2_boltbook_en"].get("new_addrs", []) + out["leg2_boltbook_zh"].get("new_addrs", []):
    if a not in seen and a.lower() not in seen_lower:
        seen[a] = {"first_seen": now, "source": "boltbook-1359"}; added += 1
if added:
    with open(HF + "hot-leg-seen.json", "w") as f:
        json.dump(seen, f, indent=1)
out["seen_added"] = added
out["elapsed_s"] = round(time.time() - t0, 1)
with open(HF + f"hot-leg-run-{TAG}.json", "w") as f:
    json.dump(out, f, indent=1)
print(json.dumps(out, indent=1))
