#!/usr/bin/env python3
"""Hot-leg run 2026-11-02 13:04 WIB. Read-only except own hot-leg state files."""
import json, urllib.request, concurrent.futures, re, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124","0x8b47354E7b76B1970a0D06365c8244a810d37493"}

def get(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent":"hot-leg/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
results = feed.get("results", feed) if isinstance(feed, dict) else feed
addrs = []
for e in results:
    if isinstance(e, str): a = e
    else: a = e.get("address") or (e.get("contract") or {}).get("address")
    if a: addrs.append(a)
json.dump(feed, open(BASE+"hot-leg-2026-11-02-1304-sourcify.json","w"), indent=1)
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
        return {"address": addr, "functions": sorted(names), "S1": s1, "S2": s2, "is_nft": bool(names & {"ownerOf","tokenURI"}),
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
    shapes = list(ex.map(shape, new))
json.dump(shapes, open(BASE+"hot-leg-2026-11-02-1304-sourcify-shape.json","w"), indent=1)
for s in shapes:
    print("SHAPE", json.dumps(s))
    a = s["address"]
    if (s.get("S1") or s.get("S2")) and s.get("is_nft"):
        seen[a] = {"first_seen_wib":"2026-11-02T13:04:00+07:00","source":"sourcify-feed",
                   "status":"checked-not-track-c",
                   "note":"S1 literal pass BUT ERC-721 NFT (ownerOf/tokenURI), not a fungible share sale, so NOT a track-C lead. NFT early-lead stays with main job; never reported/previewed/minted."}
    elif s.get("S1") or s.get("S2"):
        seen[a] = {"first_seen_wib":"2026-11-02T13:04:00+07:00","source":"sourcify-feed",
                   "status":"sale-shape-pass","note":f"S1={s.get('S1')} S2={s.get('S2')} fns={s.get('functions')}"}
    else:
        seen[a] = {"first_seen_wib":"2026-11-02T13:04:00+07:00","source":"sourcify-feed",
                   "status":"checked-not-sale-shape",
                   "note":f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} err={s.get('error','')}"}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
print("SEEN_COUNT", len(seen))

for lang, fn in [("en","hot-leg-2026-11-02-1304-boltbook-en.html"),("zh","hot-leg-2026-11-02-1304-boltbook-zh.html")]:
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
            seen[a] = {"first_seen_wib":"2026-11-02T13:04:00+07:00","source":f"boltbook-{lang}",
                       "status":"checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft")) else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                       "note":f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} err={s.get('error','')}"}
        json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
    except Exception as ex:
        print("BOLTBOOK", lang, "FAILED", f"{type(ex).__name__}: {str(ex)[:120]}")

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
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

early_tests = [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeUsed(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:])]
NEAR = {
  "Malabao":"0x2C215262635E66c798c5a1Ba4411fA9F06852bDD",
  "NightshadeClub":"0x2C027F14d36a080E5e058CF39407EAc2503B90Cc",
  "Nightsable":"0xc4f2797f050835daf3d24c1764eca60ac4168f21",
  "Kitsunaru":"0x96838f487f3551db0a25a401ab221843b72b715e",
  "GrimHarvest":"0xC43Fc6F38629c39642C8E0EDEB7F647866321699",
  "Nimaluo":"0xd531f1b8b56882c48ab5fe9be8c4855a54c90f26",
  "Gourdwick":"0x0ae19c56570d1d8b7878c309c13847a737738ead",
  "Krakenbo":"0x46c1815082ccf1273e3c07548ef2004046Bb7Fc0",
  "Mothwraith":"0x11fa2C4b71EcE40f242992a08C4ACC6C23c99Ca0",
  "Junepup":"0x7Fbedd1E2EF6e4765e8F72b2668E9f4A964600f7",
  "Medusine":"0x8E878C801b9F37cc0Cb6FF3C4597Af8FC057988b",
  "Orbitmarshal":"0x74C2214fDCc10c303302592151c50965903aa7a9",
  "Crtdroid":"0xDe67dc24C9B37af22bC6C995cA99e86809b01286",
  "Fangcount":"0x75A2D4f6f158240CB5Fd4B4f866cEA85b143D165",
  "Vesperfang":"0x2a91b304eE74162007730CF1da24C1d8C137c627",
}
result = {"block": block()}
for n,a in NEAR.items():
    result[n] = collect(a, early_tests)
# track-B pending + track-C watchlist + FABE + PrelaunchSale
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
POLLEN = "0x3E9B4F58e2bC9b064F002cF89531e12FC5CfA00f"
POLLEN_TOK = "0x2d91628eeed28f5442C8903cfF8bB85bCf38FF9B"
result["TrackB_MINT"] = collect(MINT, [("launched()",""),("tokenClaimed(address)",enc_addr(USER)[2:]),("totalShares()",""),("isRefundPhase()",""),("failed()","")])
result["TrackB_TOKEN_bal_USER"] = collect(TOKEN, [("balanceOf(address)", enc_addr(USER)[2:])])
result["Pollen_MINT"] = collect(POLLEN, [("launched()",""),("phase()",""),("pollenAgents()",""),("paidSold()","")])
result["Pollen_TOKEN_bal_USER"] = collect(POLLEN_TOK, [("balanceOf(address)", enc_addr(USER)[2:])])
QAG = "0x93eAbc3f8496A304eb0CDC3F1AD00CCCdb877877"
NIUBI = "0x094DA228770A141bB2aCaE22608A08D66a8f789a"
DROID = "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177"
B749 = "0xb7496DAA943cc136a3f6c2C42147Bb1849A6B1F3"
PREL = "0x9807a084dcCfFed3F9e530Ab08635ae08c35BF14"
FABES = "0xFabE022a5943462fee1Bd221791945DA57510BE8"
FABET = "0xB44AC34F6089B7c5c99CBc1643E22838e67C9D4d"
result["QAGENT"] = collect(QAG, [("sharesMinted()",""),("freeMinted()",""),("paidShares()",""),("MAX_FREE()",""),("mintingOpen()",""),("poolOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:])])
result["NIUBI"] = collect(NIUBI, [("sharesMinted()",""),("freeMinted()",""),("MAX_FREE()",""),("mintingOpen()",""),("poolOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:])])
result["DROID"] = collect(DROID, [("FREE_SHARES()",""),("freeMinted()",""),("paused()",""),("freeUsed(address)",enc_addr(USER)[2:])])
result["B749"] = collect(B749, [("totalCards()",""),("cardsSold()",""),("freeCardsRemaining()",""),("freeGiven()",""),("gateOn()",""),("paused()",""),("freeClaimed(address)",enc_addr(USER)[2:]),("quotaLeft(address)",enc_addr(USER)[2:])])
result["PrelaunchSale"] = collect(PREL, [("launched()",""),("soldFree()",""),("FREE_TOTAL()",""),("totalSold()",""),("soldPaid()","")])
result["FABE_sale"] = collect(FABES, [("freeSharesRemaining()",""),("FREE_SHARES()",""),("totalShares()","")])
result["FABE_token_bal_USER"] = collect(FABET, [("balanceOf(address)", enc_addr(USER)[2:])])
json.dump(result, open(BASE+"hot-leg-2026-11-02-1304-reread.json","w"), indent=1)
print("REREAD block", result["block"])
for k,v in result.items():
    if k=="block": continue
    print(k, {kk:vv.get("int") for kk,vv in v.items()})
