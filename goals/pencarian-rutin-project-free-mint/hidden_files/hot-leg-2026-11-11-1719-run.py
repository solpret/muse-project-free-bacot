#!/usr/bin/env python3
"""Hot-leg run 2026-11-11 17:19 WIB. Feed (20 captured, window 10:10:15-10:22:54Z) + Boltbook EN/ZH fetched before script start (EN
45,276B / ZH 45,401B via ?lang=). Shape-check via curl (urllib
IncompleteRead on Sourcify ABI per run 1649 infra note). Leg 3b re-check
BA3C/FDD3/Mihao/Mihao2. Leg 4 prio re-read vs 1709 baseline. Read-only;
no preview/mint."""
import json, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-11-1719"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = "0" * 24 + USER[2:].lower()
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
AGENTID = "12411464190637771618140538948436718430879438309640658942350393382867700450815750101755948145101197728078227495339265465644916641821446368465628375122182145"
t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-11 17:19 WIB", "started_wib": "2026-11-11 17:19:38 WIB"}
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

# ---- Leg 1: feed already saved ----
feed = json.load(open(HF + f"hot-leg-{TAG}-feed.json"))
addrs = [x["address"] for x in feed["results"]]
new = [a for a in addrs if a.lower() not in seen_lower]
out["leg1_sourcify_feed"] = {"returned": len(addrs),
 "verified_range": [feed["results"][-1]["verifiedAt"], feed["results"][0]["verifiedAt"]],
 "new": new, "already_seen": len(addrs) - len(new)}

# ---- shape-check new contracts via curl ----
FREE_VIEWS = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
              "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted",
              "freeSharesLeft","freeRemaining"}
QUOTE_FNS = {"quote","cost","getCost","price","mintPrice","getQuote","quoteFor","priceAt","getPrice"}
def shape_of(addr):
    p = subprocess.run(["curl","-sS","-m","15","-A","Mozilla/5.0",
        f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
        capture_output=True, text=True)
    if p.returncode != 0 or not p.stdout.strip():
        raise RuntimeError(f"curl rc={p.returncode} err={p.stderr[:100]}")
    d = json.loads(p.stdout)
    abi = d.get("abi") or d.get("stdJson", {}).get("abi") or []
    fns = [x.get("name","") for x in abi if x.get("type") == "function"]
    fnset = set(fns)
    has_mint = any(n.lower().startswith("mint") for n in fnset)
    has_quote = bool(fnset & QUOTE_FNS)
    free_hits = sorted(fnset & FREE_VIEWS)
    has_token = all(n in fnset for n in ("name","symbol","decimals","totalSupply"))
    has_free_mint = "mintFree" in fnset
    has_free_slots = bool(fnset & {"FREE_SLOTS","FREE_SUPPLY","FREE_AMOUNT"})
    agent = bool(fnset & {"agentRegistry","AGENT_REGISTRY","agentIdOf","AgentGate"}) or REGISTRY.lower() in json.dumps(d).lower()
    s1 = has_mint and has_quote and bool(free_hits) and agent
    s2 = has_token and has_free_mint and bool(free_hits) and has_free_slots and agent
    return {"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free_hits, "agent": agent, "token": has_token, "fns": len(fns)}
shapes = {}
for a in new:
    try:
        shapes[a] = shape_of(a)
    except Exception as e:
        shapes[a] = {"error": str(e)[:150]}
out["leg1_shapes"] = shapes
json.dump(shapes, open(HF + f"hot-leg-{TAG}-shape.json", "w"), indent=1)

# ---- Leg 2: Boltbook files already saved ----
def bb(fname):
    txt = open(HF + fname, encoding="utf-8", errors="ignore").read()
    addrs2 = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", txt)))
    return {"bytes": len(txt), "addrs": len(addrs2),
            "new_addrs": [a for a in addrs2 if a.lower() not in seen_lower],
            "kw_free_share": txt.lower().count("free share"),
            "kw_free_mint": txt.lower().count("free mint"),
            "kw_zh_free_share": txt.count("免费份额"),
            "kw_zh_free_mint": txt.count("免费铸造") + txt.count("免费mint")}
out["leg2_boltbook_en"] = bb(f"hot-leg-{TAG}-boltbook-en.html")
out["leg2_boltbook_zh"] = bb(f"hot-leg-{TAG}-boltbook-zh.html")

# ---- Bridge (read-only) ----
try:
    br = json.load(open(HF + "scan-bridge.json"))
    baddrs = {k.lower() for k in br.get("contracts", {}).keys()}
    out["bridge"] = {"contracts": len(baddrs),
                     "new_feed_in_bridge": [a for a in new if a.lower() in baddrs],
                     "new_boltbook_in_bridge": [a for a in out["leg2_boltbook_en"].get("new_addrs", []) + out["leg2_boltbook_zh"].get("new_addrs", []) if a.lower() in baddrs]}
except Exception as e:
    out["bridge"] = {"error": str(e)[:150]}

# ---- RPC helpers ----
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

# ---- Leg 3: new sale-shape? ----
out["leg3_new_sale_shape"] = {a: s for a, s in shapes.items() if s.get("S1") or s.get("S2")}

# ---- Leg 3b ----
recheck = [("BA3C","opened","opened()","uint"),("BA3C","totalMinted","totalMinted()","uint"),
 ("BA3C","freeMinted","freeMinted()","uint"),("BA3C","agentRegistry","agentRegistry()","uint"),
 ("FDD3","freeMinted","freeMinted()","uint"),("FDD3","freeRemaining","freeRemaining()","uint"),
 ("FDD3","paused","paused()","uint"),("FDD3","freeClaimed_user","freeClaimed(address)","user"),
 ("MIHAO","opened","opened()","uint"),("MIHAO","freeMinted","freeMinted()","uint"),
 ("MIHAO","totalMinted","totalMinted()","uint"),
 ("MIHAO2","freeMinted","freeMinted()","uint"),("MIHAO2","totalMinted","totalMinted()","uint"),
 ("MIHAO2","FREE_SHARES","FREE_SHARES()","uint"),("MIHAO2","freePhaseActive","freePhaseActive()","uint"),
 ("MIHAO2","opened","opened()","uint")]
ADDR3 = {"BA3C": "0xBa3cCb10183688a601E5dea18a42bE4d584EE433",
         "FDD3": "0xFdD3Bc978349d528D935051AF39C8F04F77184D0",
         "MIHAO": "0x1f82539520a8b3d4eB7C3145f7E1EaFe4B52c4e1",
         "MIHAO2": "0x34eA49e9BC199418f121366BdBEa8fDbab10c26b"}
calls3 = []
for name, label, sig, kind in recheck:
    arg = USER_PAD if kind == "user" else ""
    calls3.append(((name, label, kind), ("eth_call", [{"to": ADDR3[name], "data": sel(sig) + arg}, "latest"])))
out["leg3b_recheck"] = batch_calls(calls3)

# ---- Leg 4: prio re-read (same set as 1649) ----
PRIO = {
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("totalMinted","totalMinted()","uint"),("freeMinted","freeMinted()","uint"),
    ("hasFreeMinted_user","hasFreeMinted(address)","user"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "HANAMI": ("0x8A742EcE2a8C1dCc5dE792A062dbEe9C00A74640", [
    ("totalSupply","totalSupply()","uint"),("freeMinted","freeMinted()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [
    ("totalSupply","totalSupply()","uint"),("agentFreeUsed","agentFreeUsed()","uint"),
    ("mintOpen","mintOpen()","uint"),("balanceOf_user","balanceOf(address)","user"),
    ("FREE_SUPPLY","FREE_SUPPLY()","uint"),("MAX_SUPPLY","MAX_SUPPLY()","uint"),
    ("freeSupply","freeSupply()","uint"),("FREE_CAP","FREE_CAP()","uint")]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [
    ("totalMinted","totalMinted()","uint"),("freeMinted","freeMinted()","uint"),
    ("FREE_SUPPLY","FREE_SUPPLY()","uint"),("mintOpen","mintOpen()","uint"),
    ("freeAvailable_user","freeAvailable(address)","user"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened","opened()","uint"),("totalFreeMinted","totalFreeMinted()","uint"),
    ("totalMinted","totalMinted()","uint")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("launched","launched()","uint"),("startTime","startTime()","uint"),
    ("freeClaimed_user","freeClaimed(address)","user")]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("FREE_SHARES","FREE_SHARES()","uint"),("freeClaimed_user","freeClaimed(address)","user")]),
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
 "binanceai": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()","uint")]),
}
calls4 = []
for name, (addr, specs) in PRIO.items():
    for label, sig, kind in specs:
        arg = USER_PAD if kind == "user" else ""
        calls4.append(((name, label, kind), ("eth_call", [{"to": addr, "data": sel(sig) + arg}, "latest"])))
calls4.append((("RigForge", "freeTaken_agentId", "uint"), ("eth_call", [{"to": "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", "data": sel("freeTaken(uint256)") + format(int(AGENTID), "064x")}, "latest"])))
calls4.append((("HEAD", "block", "uint"), ("eth_blockNumber", [])))
res4 = batch_calls(calls4)
out["leg4_read_wib"] = time.strftime("%Y-%m-%d %H:%M:%S WIB", time.localtime(time.time() + 7*3600))
out["leg4_block"] = res4.get("HEAD", {}).get("block")
out["leg4_values"] = {k: v for k, v in res4.items() if k != "HEAD"}
json.dump({"block": out["leg4_block"], "values": out["leg4_values"]}, open(HF + f"hot-leg-{TAG}-prio.json", "w"), indent=1)

# ---- update seen for new feed + boltbook new ----
added = 0
for a, s in shapes.items():
    if "error" not in s:
        seen[a] = {"first_seen": "2026-11-11 17:19 WIB", "source": "sourcify-feed-1719",
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')} token={s.get('token')}",
                   "status": "checked-not-sale-shape" if not (s.get("S1") or s.get("S2")) else "sale-shape-1714"}
        added += 1
for a in out["leg2_boltbook_en"].get("new_addrs", []) + out["leg2_boltbook_zh"].get("new_addrs", []):
    if a not in seen and a.lower() not in seen_lower:
        seen[a] = {"first_seen": "2026-11-11 17:19 WIB", "source": "boltbook-1719"}; added += 1
if added:
    json.dump(seen, open(HF + "hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = added
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(HF + f"hot-leg-run-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
