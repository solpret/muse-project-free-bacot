#!/usr/bin/env python3
"""Hot-leg run 2026-11-02 04:09 WIB. Read-only except own hot-leg state files."""
import json, urllib.request, concurrent.futures, re, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}

def get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent":"hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

# --- Leg 1: Sourcify feed ---
feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
results = feed.get("results", feed) if isinstance(feed, dict) else feed
addrs = []
for e in results:
    if isinstance(e, str): a = e
    else: a = e.get("address") or (e.get("contract") or {}).get("address")
    if a: addrs.append(a)
json.dump(feed, open(BASE+"hot-leg-2026-11-02-0414-sourcify.json","w"), indent=1)
seen = json.load(open(BASE+"hot-leg-seen.json"))
new = [a for a in addrs if a not in seen and a not in EXCLUDED]
print("FEED_COUNT", len(addrs), "NEW", new)

def shape(addr):
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"))
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID","agentIdOf","hasAgentId"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "functions": sorted(names), "S1": s1, "S2": s2,
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    shapes = list(ex.map(shape, new))
json.dump(shapes, open(BASE+"hot-leg-2026-11-02-0414-sourcify-shape.json","w"), indent=1)
for s in shapes:
    print("SHAPE", json.dumps(s))
    a = s["address"]
    if s.get("S1") or s.get("S2"):
        seen[a] = {"first_seen_wib":"2026-11-02T04:14:00+07:00","source":"sourcify-feed",
                   "status":"sale-shape-pass","note":f"S1={s.get('S1')} S2={s.get('S2')} fns={s.get('functions')}"}
    else:
        seen[a] = {"first_seen_wib":"2026-11-02T04:14:00+07:00","source":"sourcify-feed",
                   "status":"checked-not-sale-shape",
                   "note":f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} err={s.get('error','')}"}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
print("SEEN_COUNT", len(seen))

# --- Leg 2: Boltbook direct fetch en + zh ---
for lang, fn in [("en","hot-leg-2026-11-02-0414-boltbook-en.html"),("zh","hot-leg-2026-11-02-0414-boltbook-zh.html")]:
    url = "https://boltbook.fun/" + ("?lang=zh" if lang=="zh" else "")
    try:
        html = get(url, timeout=12)
        open(BASE+fn,"w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen_lower = {k.lower(): k for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED]
        print("BOLTBOOK", lang, "bytes", len(html), "addrs", len(found), "new", newfound)
        for a in newfound:
            s = shape(a)
            print("BOLTBOOK_SHAPE", lang, json.dumps(s))
            seen[a] = {"first_seen_wib":"2026-11-02T04:14:00+07:00","source":f"boltbook-{lang}",
                       "status":"sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
                       "note":f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} err={s.get('error','')}"}
        json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
    except Exception as ex:
        print("BOLTBOOK", lang, "FAILED", f"{type(ex).__name__}: {str(ex)[:120]}")

# --- Leg 4: snapshot re-read (same contract set as 23:44 run) ---
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
HIVE = "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77"
BUB = "0xc205F8c74733D914776D66cBc4Cf10BF701D96Aa"
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
PAIR = "0x903ACC22B9BABCD427bfb9AF2C27a27a5aC7c698"
POLLEN = "0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f"
POLLEN_TOK = "0x2d91628eeed28f5442C8903cfF8bB85bCf38FF9B"
BABY = "0xbb7ed59ca41ea03cf20084a8c9de94244b7b2637"
QILIN = "0xbb77f247e6b57f4dcd09c5900b2ffc4250b6b88f"
DOG = "0xA74bEF84304D8838db798faE96fb873dd46fB4C1"
EARLY = {"Zapcourier":"0x672c1dF4F7121DaCBD3504995441C47d2fAbCdDC","Mothwraith":"0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0","Cryonyx":"0x787b522d48084A83b8B1b0C206aA4A12B1FD1cc2","Cathodex":"0x0AC5591d1B980C7bE16861d722E59E21E2624868","Malabao":"0x2C215262635E66c798c5a1Ba4411fA9F06852bDD"}
def call(to, data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:160]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        val, err = call(to, sel(name)+arg)
        try: iv = int(val,16) if val else None
        except Exception: iv = None
        out[name] = {"int": iv, "raw": val, "error": err if val is None else None}
    return out
def block():
    for ep in EPS:
        try: return int(_single(ep,"eth_blockNumber",[],8,retries=0),16)
        except Exception: pass
    return None
hive_tests = [("totalSupply()",""),("START_TIME()",""),("FREE_SUPPLY()",""),("FREE_PER_WALLET()",""),("totalPaid()",""),("freeMintedBy(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:]),("quote(uint256)",enc_uint(1)[2:]),("currentPrice()","")]
bub_tests = [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("MAX_SUPPLY()",""),("mintOpen()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeUsed(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:])]
tb_tests = [("launched()",""),("tokenClaimed(address)",enc_addr(USER)[2:]),("totalShares()",""),("isRefundPhase()",""),("failed()",""),("FREE_SHARES()","")]
pollen_tests = [("launched()",""),("phase()",""),("startAt()",""),("endAt()",""),("pollenAgents()",""),("pollenSlice()",""),("paidSold()",""),("PAID_SHARES()","")]
baby_tests = [("sharesMinted()",""),("freeMinted()",""),("paidShares()",""),("MAX_SHARES()",""),("mintingOpen()",""),("poolOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:]),("quote(uint256)",enc_uint(1)[2:])]
dog_tests = [("sharesMinted()",""),("FREE_SHARES()",""),("MAX_SHARES()",""),("deadline()",""),("saleFailed()","")]
early_tests = [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeUsed(address)",enc_addr(USER)[2:])]
qilin_tests = [("totalCards()",""),("cardsSold()",""),("cardsRemaining()",""),("freeCardCap()",""),("freeCardsRemaining()",""),("freeGiven()",""),("gateOn()",""),("paused()",""),("freeClaimed(address)",enc_addr(USER)[2:]),("quotaLeft(address)",enc_addr(USER)[2:])]
result = {"block": block(),
  "HIVE": collect(HIVE, hive_tests),
  "Bubblebruin": collect(BUB, bub_tests),
  "TrackB_MINT": collect(MINT, tb_tests),
  "TrackB_TOKEN_bal_MINT": collect(TOKEN, [("balanceOf(address)", enc_addr(MINT)[2:])]),
  "TrackB_TOKEN_bal_USER": collect(TOKEN, [("balanceOf(address)", enc_addr(USER)[2:])]),
  "Pollen_MINT": collect(POLLEN, pollen_tests),
  "Pollen_TOKEN_bal_USER": collect(POLLEN_TOK, [("balanceOf(address)", enc_addr(USER)[2:])]),
  "BNBbaby": collect(BABY, baby_tests),
  "QILIN": collect(QILIN, qilin_tests)}
result["DOG"] = collect(DOG, dog_tests)
for _n,_a in EARLY.items():
    result["EARLY_"+_n] = collect(_a, early_tests)

BNBPIG = "0xfd3d4e0d7a81534addd11f96fdd8008f942097f9"
SAMBA = "0xe15e68C9198ee0A5780fba96016e1780204aF3B4"
NIUBI = "0x094DA228770A141bB2aCaE22608A08D66a8f789a"
pig_tests = [("sharesMinted()",""),("freeMinted()",""),("paidShares()",""),("MAX_FREE()",""),("mintingOpen()",""),("poolOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:])]
samba_tests = [("totalCards()",""),("cardsSold()",""),("freeCardCap()",""),("freeCardsRemaining()",""),("gateOn()",""),("paused()",""),("freeClaimed(address)",enc_addr(USER)[2:]),("quotaLeft(address)",enc_addr(USER)[2:])]
niubi_tests = [("sharesMinted()",""),("freeMinted()",""),("MAX_FREE()",""),("MAX_SHARES()",""),("mintingOpen()",""),("poolOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:])]
result["BNBPIG"] = collect(BNBPIG, pig_tests)
result["SAMBARIO"] = collect(SAMBA, samba_tests)
result["NIUBI_094D"] = collect(NIUBI, niubi_tests)
json.dump(result, open(BASE+"hot-leg-2026-11-02-0414-reread.json","w"), indent=1)

print("REREAD", json.dumps(result, indent=1)[:6000])

# --- Extra re-read: RuninAI / LingYuanGou / a7Be / JUBAO / ZCMAO / JINLONG ---
RUNIN = "0xfB50746BCc9D585AEb49cd410Fa0100b657ce9e6"
ZERO = "0xc180b8bffdd65531f4bae6ac7586cfb192164a9b"
A7 = "0xa7Bef74f9327daacEe49fEa9Db9C34253900936A"
JUB = "0x1ed3BF35e4DA25b1289C27ddbD82f0A38DDCee8b"
ZCM = "0x8362e6a5F38427d8d719EA47f08890784F6023DC"
JIN = "0x2Df4Ef534cbBe1a8F647e24D0f8C75ECe74D8288"
extra_result = {"block": block(),
  "RuninAI": collect(RUNIN, [("freeClaimed()",""),("freeShares()",""),("phase()",""),("sold()",""),("launched()","")]),
  "LingYuanGou": collect(ZERO, [("soldFree()",""),("FREE_TOTAL()",""),("totalSold()","")]),
  "a7Be": collect(A7, [("sharesMinted()",""),("freeSharesMinted()",""),("FREE_SHARES()",""),("saleFailed()","")]),
  "JUBAO": collect(JUB, [("freeClaimed()",""),("FREE_SHARES()","")]),
  "ZCMAO": collect(ZCM, [("freeClaimed()",""),("FREE_SHARES()","")]),
  "JINLONG": collect(JIN, [("freeClaimed()",""),("FREE_SHARES()","")])}
json.dump(extra_result, open(BASE+"hot-leg-2026-11-02-0414-reread-extra.json","w"), indent=1)
print("EXTRA", json.dumps(extra_result))

# --- Extra2: snapshot-only track-C leads JINLI / BIAO / 兕 ---
JINLI = "0xd7a2567929da32cab052cf287522cd6e3d3ecfa2"
BIAO = "0x16469C174cd827A5e21f4bf3eE3711f2bB42e275"
SI = "0x071f76c1868039e2f042Dca1890EcB0364D8494a"
extra2 = {"block": block(),
  "JINLI": collect(JINLI, [("freeClaimed()",""),("FREE_SHARES()",""),("PAID_SHARES()",""),("phase()",""),("sold()",""),("launched()",""),("startedAt()","")]),
  "BIAO": collect(BIAO, [("freeClaimed()",""),("FREE_SHARES()",""),("MAX_PAID()",""),("phase()",""),("sold()",""),("totalPaidBNB()",""),("PRICE()",""),("launched()",""),("startedAt()","")]),
  "SI": collect(SI, [("FREE_POOL()",""),("soldFree()",""),("soldPaid()",""),("TOTAL_CAP()",""),("currentPrice()",""),("startTime()","")])}
json.dump(extra2, open(BASE+"hot-leg-2026-11-02-0414-reread-extra2.json","w"), indent=1)
print("EXTRA2", json.dumps(extra2))
