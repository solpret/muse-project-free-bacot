#!/usr/bin/env python3
"""Hot-leg run 2026-11-03 01:49 WIB. Read-only except own hot-leg state files."""
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

try:
    feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"))
    results = feed.get("results", feed) if isinstance(feed, dict) else feed
    addrs = []
    for e in results:
        if isinstance(e, str): a = e
        else: a = e.get("address") or (e.get("contract") or {}).get("address")
        if a: addrs.append(a)
    json.dump(feed, open(BASE+"hot-leg-2026-11-03-0149-sourcify.json","w"), indent=1)
    print("FEED_OK", len(addrs))
except Exception as ex:
    print("FEED_SKIPPED", f"{type(ex).__name__}: {str(ex)[:160]}")
    addrs = []
seen = json.load(open(BASE+"hot-leg-seen.json"))
new = [a for a in addrs if a not in seen and a not in EXCLUDED]
print("FEED_COUNT", len(addrs), "NEW", new)

def shape(addr):
    try:
        import subprocess as _sp
        _out = _sp.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"], capture_output=True, text=True).stdout
        meta = json.loads(_out)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","hasAgentId"})
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
json.dump(shapes, open(BASE+"hot-leg-2026-11-03-0149-sourcify-shape.json","w"), indent=1)
for s in shapes:
    print("SHAPE", json.dumps(s))
    if s.get("error") or not s.get("functions"):
        print("SHAPE_RETRY_NEXT_RUN", s["address"], s.get("error") or "empty-ABI-inconclusive")
        continue
    a = s["address"]
    if (s.get("S1") or s.get("S2")) and s.get("is_nft"):
        seen[a] = {"first_seen_wib":"2026-11-03T01:49:00+07:00","source":"sourcify-feed",
                   "status":"checked-not-track-c",
                   "note":"S1 literal pass BUT ERC-721 NFT (ownerOf/tokenURI), not a fungible share sale, so NOT a track-C lead. NFT early-lead stays with main job; never reported/previewed/minted."}
    elif s.get("S1") or s.get("S2"):
        seen[a] = {"first_seen_wib":"2026-11-03T01:49:00+07:00","source":"sourcify-feed",
                   "status":"sale-shape-pass","note":f"S1={s.get('S1')} S2={s.get('S2')} fns={s.get('functions')}"}
    else:
        seen[a] = {"first_seen_wib":"2026-11-03T01:49:00+07:00","source":"sourcify-feed",
                   "status":"checked-not-sale-shape",
                   "note":f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} err={s.get('error','')}"}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
print("SEEN_COUNT", len(seen))

for lang, fn in [("en","hot-leg-2026-11-03-0149-boltbook-en.html"),("zh","hot-leg-2026-11-03-0149-boltbook-zh.html")]:
    url = "https://boltbook.fun/" + ("?lang=zh" if lang=="zh" else "")
    try:
        html = get(url, timeout=12)
        open(BASE+fn,"w").write(html)
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        seen_lower = {k.lower(): k for k in seen}
        newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED and a.lower() != "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"]
        print("BOLTBOOK", lang, "bytes", len(html), "addrs", len(found), "new", newfound)
        for a in newfound:
            s = shape(a)
            print("BOLTBOOK_SHAPE", lang, json.dumps(s))
            if s.get("error") or not s.get("functions"):
                print("BOLTBOOK_SHAPE_RETRY_NEXT_RUN", a, s.get("error") or "empty-ABI-inconclusive")
                continue
            seen[a] = {"first_seen_wib":"2026-11-03T01:49:00+07:00","source":f"boltbook-{lang}",
                       "status":"checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft")) else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
                       "note":f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')} err={s.get('error','')}"}
        json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
    except Exception as ex:
        print("BOLTBOOK", lang, "URLLIB_FAILED", f"{type(ex).__name__}: {str(ex)[:120]}")
        try:
            import subprocess
            html = subprocess.run(["curl","-sL","--max-time","15",url], capture_output=True, text=True).stdout
            open(BASE+fn,"w").write(html)
            found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
            seen_lower = {k.lower(): k for k in seen}
            newfound = [a for a in found if a.lower() not in seen_lower and a not in EXCLUDED and a.lower() != "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"]
            print("BOLTBOOK_CURL", lang, "bytes", len(html), "addrs", len(found), "new", newfound)
            for a in newfound:
                s2 = shape(a)
                print("BOLTBOOK_SHAPE", lang, json.dumps(s2))
                if s2.get("error") or not s2.get("functions"):
                    print("BOLTBOOK_SHAPE_RETRY_NEXT_RUN", a, s2.get("error") or "empty-ABI-inconclusive"); continue
                seen[a] = {"first_seen_wib":"2026-11-03T01:49:00+07:00","source":f"boltbook-{lang}",
                           "status":"checked-not-track-c" if ((s2.get("S1") or s2.get("S2")) and s2.get("is_nft")) else ("sale-shape-pass" if (s2.get("S1") or s2.get("S2")) else "checked-not-sale-shape"),
                           "note":f"S1={s2.get('S1')} S2={s2.get('S2')} mint={s2.get('has_mint')} quote={s2.get('has_quote')} free={s2.get('free_views')} agent={s2.get('agent_ref')} token={s2.get('is_token')} err={s2.get('error','')}"}
            json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
        except Exception as ex2:
            print("BOLTBOOK", lang, "FAILED", f"{type(ex2).__name__}: {str(ex2)[:120]}")

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
  "Orbitmarshal":"0x74C2219fDCc10c303302592151c50965903aa7a9",
  "Crtdroid":"0xDe67dc24C9B37af22bC6C995cA99e86809b01286",
  "Fangcount":"0x75A2D4f6f158240CB5Fd4B4f866cEA85b143D165",
  "Vesperfang":"0x2a91b304eE74162007730CF1da24C1d8C137c627",
}
result = {"block": block()}

NEW5 = {
  "Wispuff":"0x693777E674fa13a8318821924296d52E90898191",
  "Neonhare":"0x553484EC13486cAec4cdB884B9953e381dd1d66B",
  "Mercubo":"0xa1bC72EcEC9f1F73Be9ED0c21b5cB880f42dA1A3",
  "Chimerito":"0x3203D93cE535c2ec88c99d1967324Fe556A4e8f6",
  "Servopaw":"0xAB23259Cac7D87d8cfE0ADaba80827d3e3AcC99F",
}
for n,a in NEW5.items():
    result[n] = collect(a, early_tests)
SEVARIS = "0x73085868F57C46E09C7b70AdFda6E6b806222Af0"
result["Sevaris"] = collect(SEVARIS, [("totalSupply()",""),("freeMinted()",""),("freeLeft()",""),("saleOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("hasAgentId(address)",enc_addr(USER)[2:])])

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
B749 = "0xb7496DAA943cc136a3f6c2C42147Bb1854A6B1F3"
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
UPONLY = "0x1ddBcbA032bc0D80A69B58D91C292aB83119cbc3"
result["UPONLY"] = collect(UPONLY, [("launched()",""),("startTime()",""),("deadline()",""),("soldFree()",""),("FREE_TOTAL()",""),("totalSold()",""),("soldPaid()","")])
# NEW sale-shape from 14:19 feed, not yet pool/slot-verified: 0x723BA73f3480628DD909798367fd47D763C8B5c8
S723 = "0x723BA73f3480628DD909798367fd47D763C8B5c8"
result["S723_token"] = collect(S723, [("token()",""),("pair()",""),("TOKENS_PER_SHARE()",""),("PRICE()",""),("MAX_FREE()",""),("MAX_SHARES()",""),("sharesMinted()",""),("freeMinted()",""),("paidShares()",""),("mintingOpen()",""),("poolOpen()",""),("openPool()","")])
# quote(uint256) with 0 and 1, and user slot views
def call2(to, data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0), None
        except Exception as e: err=f"{type(e).__name__}: {str(e)[:160]}"
    return None, err
def q(n):
    v,err=call2(S723, sel("quote(uint256)")+enc_uint(n)[2:])
    try: iv=int(v,16) if v else None
    except Exception: iv=None
    return {"int":iv,"raw":v,"error":err if v is None else None}
result["S723_quote"]={"quote0":q(0),"quote1":q(1)}
result["S723_user"] = collect(S723, [("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:]),("hasAgentId(address)",enc_addr(USER)[2:]),("paidBy(address)",enc_addr(USER)[2:])])
_tok_raw = (result["S723_token"].get("token()",{}) or {}).get("raw") or ""
_tok = "0x"+_tok_raw[-40:] if len(_tok_raw)>=42 else "0x0000000000000000000000000000000000000000"
result["S723_token_addr"] = _tok
result["S723_token_bal_USER"] = collect(_tok, [("balanceOf(address)", enc_addr(USER)[2:])])

# NEW snapshot items from main run 14:01 WIB (gate-blocked strong leads / track-C lead) — change detection only, no re-report of their blocked status
CYBER="0xD4D848F81216Ef2856fEe2cdFa529a1bB53c50C0"
AZET="0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37"
result["Cyberlynx"]=collect(CYBER, early_tests)
result["AZET"]=collect(AZET, early_tests+[("mintedByWallet(address)",enc_addr(USER)[2:])])
for n,a in {"Vampibo":"0x56fe33870a6f900969638d78d30b40d8377a9ae9","Neonpanda":"0xdc50866b4b76ae375344ba730c8c7c324797d38e","Jiayoutigo":"0xc2de0c87765685f88b9af69c288473411675a02c","Botowl":"0x6d872ade6f8ff1681a89989772aa5941574bff90","Venusia":"0xf621ed47bfce124069ea1d701522ad0c92bfe91d"}.items():
    result[n]=collect(a, early_tests)
Q2="0xE3a4f3099a2136e0e66202A665815caB8FFA2704"
result["QAGENT2"]=collect(Q2, [("sharesMinted()",""),("freeMinted()",""),("MAX_FREE()",""),("MAX_SHARES()",""),("mintingOpen()",""),("poolOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:])])
result["QAGENT2_token_bal_USER"]=collect("0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", [("balanceOf(address)", enc_addr(USER)[2:])])


for n,a in {"Jiayoupanda":"0x520ceb54367B729Dfa0b00E2a4541E6702D5a7E1","Hydralet":"0x429f23778562bc4be82c215ba12180e1ff297e8f","Gongxibao":"0xd8501c1ff155466854ba037a9ecf8031da290be7","Ghoulito":"0x0e13e8fd65452cd2b7238695a0a7dd9297383af9","Neonfawn":"0x2a93fafca568a6ee7d8213f9b31f41ed71d51f55","Nanobee":"0x4cd813ad6c3c2cc740d48f357d7e0f0e053449f1"}.items():
    result[n]=collect(a, early_tests)


WAG="0x5091F75CdFEf44883a5b24ff453322De8ef24aFd"
result["WAG"]=collect(WAG, [("sharesMinted()",""),("freeMinted()",""),("paidShares()",""),("MAX_FREE()",""),("mintingOpen()",""),("poolOpen()",""),("freeAvailable(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:]),("hasAgentId(address)",enc_addr(USER)[2:])])
result["WAG_token_bal_USER"]=collect("0xaa0c64f8394e5c4370f28148d0ce1825a00dee38", [("balanceOf(address)", enc_addr(USER)[2:])])


for n,a in {"Chihuolin":"0x656A1115BEd8E60748508C423e81FA85AA9c762F","Bandagrin":"0x6834a0b5d3bAb31A6d9A5505C2a9534daF46DbaF","Pyrevane":"0xFb8b2865727D7e7b8F8761cDC0cA0DE4E7f4e551","Spectrelle":"0xC2C955bf4FD212939cE70c86324659E6B416D742"}.items():
    result[n]=collect(a, early_tests)

json.dump(result, open(BASE+"hot-leg-2026-11-03-0149-reread.json","w"), indent=1)
print("REREAD block", result["block"])
for k,v in result.items():
    if k=="block": continue
    if isinstance(v, dict):
        print(k, {kk:(vv.get("int") if isinstance(vv, dict) else vv) for kk,vv in v.items()})
    else:
        print(k, v)

# EXTRA: main-run 17:31 strong/early leads (change detection only)
EXTRA = {
 "Griffito":"0x3a8b62d76900195Cb574315e01215c3b294ea402",
 "Niuniubo":"0x200aC8776A5351C29c4D854012ffC1794a7DfA79",
 "Witchibo":"0x30e2ED57e433671907d7AEB01a7E7514e17FD649",
 "Circuitfox":"0xD12B23694A910dBC74EF50aDBaC6aB4F6b34F55C",
 "MachineMuse":"0xED05274F0Fc42c53Fe2f02558f1afB5BeAd55A8d",
 "CopilotClub":"0x4EA51956dd8F4B3C04ffF36e0254Be1b04c051aF",
 "DelegateDAO":"0x9a1339B8Aaee25082e3e54aE09780905add63462",
 "Gourdwitch":"0x30405B8442Cf2F1C488F256A8DF12e1A2e22E581",
 "Glasscore":"0xe2826b507Da79a642aa1fce108Aa8dD11cE67e3f",
 "Neonpurrix":"0xd2136C5aF996D264414cbF981E7B1804ba80177C",
 "Gargrowl":"0x2BD4983c8f5E734D6E24d4Dba04F4C722a88F9DF",
}
extra = {}
for n,a in EXTRA.items():
    extra[n] = collect(a, early_tests)
extra["block"] = result["block"]
json.dump(extra, open(BASE+"hot-leg-2026-11-03-0149-reread-extra.json","w"), indent=1)
for k,v in extra.items():
    if k=="block": continue
    print("EXTRA", k, {kk:(vv.get("int") if isinstance(vv, dict) else vv) for kk,vv in v.items()})

# EXTRA2: snapshot 19:02 WIB additions (change detection only, already reported by main job)
EXTRA2 = {
 "Plutoko":"0xF5Cf199D08A7B9bFE5C1Fc44ef5eabdae4314A56",
 "Yydspanda":"0x9421429eF629db0175323b6F14804AE6b3528883",
 "Nexobyte":"0x7A75c1F85B2c047954E9B59e1a998F15091A9BC8",
 "Lumigeisha":"0x11aBA96f117b396A0EfCc919fa54FFcc8319E64d",
 "Stitchvolt":"0xAA911256Fa3Ca8F6Cff699FC6190905261350cF0",
 "Dragonito":"0x56E2604A33F1ccBc00376046a767cCE45B50F592",
 "Strawgrim":"0x96c17aB9D750aD979BBa894A234C31911289F669",
}
extra2 = {}
for n,a in EXTRA2.items():
    extra2[n] = collect(a, early_tests)
json.dump(extra2, open(BASE+"hot-leg-2026-11-03-0149-reread-extra2.json","w"), indent=1)
for k,v in extra2.items():
    print("EXTRA2", k, {kk:(vv.get("int") if isinstance(vv, dict) else vv) for kk,vv in v.items()})

# EXTRA3 (2024 run): near-threshold snapshot early leads not in the main NEAR list (>=38% at 20:03 snapshot) + ORBIT track-C gate-blocked lead (dropped from 2004/2009 rereads; pool was draining fast, 129 freeCardsRemaining at 19:54 verify)
EXTRA3 = {
 "TheWickedVault":"0x2760DB0Df38edA84Ce41710A95fBE1734C3F8F41",
 "Griffinko":"0xB5a083bd9E8E330085e8F459f13f080d4F8fE5B4",
 "Mummyrelic":"0xB330e582f45c0243e5Eb1B56958b56273f26a9eB",
 "Tangpinku":"0x33D66b461E55d6969ACfAe0C95dACf158F8d04B0",
 "Gearpixel":"0x9560703c474Ed34df8415Aa715991D15B9b3c47e",
 "Orbitty":"0xE08289849427a82e336A64662bD951FcA4DE8d8E",
 "Sphinxel":"0x4ec6086B7DEF22A0D95823BCB6e9ec8840B2d5C4",
 "Skelebop":"0xaB5183443e2B82333A4b173e55bb38cCe7c46b01",
 "Ravenhex":"0xB44050254A25dAA8077C14BbB20d0a595e6CECE",
 "Ghostbloom":"0xd987945d1df5FcD111155bF9C494fAAde3f91E3e",
}
extra3 = {}
for n,a in EXTRA3.items():
    extra3[n] = collect(a, early_tests)
extra3["ORBIT"] = collect("0x6e0c18185f584781592fa972ff2b7566c5532e12", [("totalCards()",""),("cardsSold()",""),("freeCardsRemaining()",""),("freeGiven()",""),("gateOn()",""),("paused()",""),("freeClaimed(address)",enc_addr(USER)[2:]),("quotaLeft(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:])])
extra3["ORBIT_token_bal_USER"] = collect("0xc09eea8ecc744e0adf299c849ccc9fb897a545d8", [("balanceOf(address)", enc_addr(USER)[2:])])
json.dump(extra3, open(BASE+"hot-leg-2026-11-03-0149-reread-extra3.json","w"), indent=1)
for k,v in extra3.items():
    print("EXTRA3", k, {kk:(vv.get("int") if isinstance(vv, dict) else vv) for kk,vv in v.items()})

# VARIANT re-check 21:04 WIB (change detection only, never preview/mint)
VAR = {}
VAR["Ec77"] = collect("0xEc77268Fbb7e8b62D1dE8b913440d301c7B8CF55", [("opened()",""),("openedTime()",""),("FREE_CAP()",""),("freeMinted()",""),("paidShares()",""),("firstMintTime()",""),("freeUsedByAgent(address)",enc_addr(USER)[2:])])
def qcost(n):
    v,err=call2("0xEc77268Fbb7e8b62D1dE8b913440d301c7B8CF55", sel("quoteCost(uint256)")+enc_uint(n)[2:])
    try: iv=int(v,16) if v else None
    except Exception: iv=None
    return {"int":iv,"raw":v,"error":err if v is None else None}
VAR["Ec77_quoteCost"]={"quoteCost1":qcost(1)}
VAR["Var4071"] = collect("0x4071F04A71B7C4E157C87631eAF4aaa827522E0f", [("opened()",""),("openedTime()",""),("saleStart()",""),("totalMinted()",""),("totalPaid()","")])
VAR["Var1044"] = collect("0x1044efcAF34F01E26C758460F087E9C74dD9bc29", [("opened()",""),("openedTime()",""),("totalMinted()",""),("totalPaid()","")])
def costof(n):
    v,err=call2("0x1044efcAF34F01E26C758460F087E9C74dD9bc29", sel("costOf(uint256)")+enc_uint(n)[2:])
    try: iv=int(v,16) if v else None
    except Exception: iv=None
    return {"int":iv,"raw":v,"error":err if v is None else None}
VAR["Var1044_costOf"]={"costOf1":costof(1)}
VAR["VarBD6B"] = collect("0xBD6BE040625fF3eB2CD0407F730935e16aa883Ba", [("totalShares()",""),("poolCreated()",""),("pair()",""),("freeMinted()","")])
json.dump(VAR, open(BASE+"hot-leg-2026-11-03-0149-reread-variant.json","w"), indent=1)
for k,v in VAR.items():
    print("VARIANT", k, {kk:(vv.get("int") if isinstance(vv, dict) else vv) for kk,vv in v.items()} if isinstance(v,dict) else v)

# IHIGI prelaunch re-check 23:54 (opens 23:30 WIB per prior run; quote was 0.001 BNB = not free)
IHIGI = {}
IHIGI["Ihigi"] = collect("0x3611455bE1FC2c6987FE9d016971b7E40B341684", [("poolOpened()",""),("phase()",""),("freeMinted()",""),("FREE_CAP()",""),("startTime()",""),("totalMinted()",""),("mintedBy(address)",enc_addr(USER)[2:]),("freeClaimed(address)",enc_addr(USER)[2:])])
def _qih(n):
    v,err=call2("0x3611455bE1FC2c6987FE9d016971b7E40B341684", sel("quote(uint256)")+enc_uint(n)[2:])
    try: iv=int(v,16) if v else None
    except Exception: iv=None
    return {"int":iv,"raw":v,"error":err if v is None else None}
IHIGI["Ihigi_quote"]={"quote1":_qih(1)}
json.dump(IHIGI, open(BASE+"hot-leg-2026-11-03-0149-reread-ihigi.json","w"), indent=1)
for k,v in IHIGI.items():
    print("IHIGI", k, {kk:(vv.get("int") if isinstance(vv, dict) else vv) for kk,vv in v.items()} if isinstance(v,dict) else v)

# NVAGENT GROUP re-check (change detection only; 0x7Eb3 watchlist-age-unverified-gate-failed, 0x4951 gate-blocked 23:59, nVigent open)
NV = {}
def _qnv(to, n):
    v,err=call2(to, sel("quote(uint256)")+enc_uint(n)[2:])
    try: iv=int(v,16) if v else None
    except Exception: iv=None
    return {"int":iv,"raw":v,"error":err if v is None else None}
for _n,_a in {"Nvagent7Eb3":"0x7Eb3a26F895d4D1b8FcD38A67E9689cB2693661f","Nvagent4951":"0x4951Eab992c6A68Ad86040Aa2df92D46C3c207B2","nVigent":"0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2"}.items():
    NV[_n]=collect(_a, [("mintOpen()",""),("totalMints()",""),("totalSupply()",""),("freeLeft(address)",enc_addr(USER)[2:]),("mintedBy(address)",enc_addr(USER)[2:]),("balanceOf(address)",enc_addr(USER)[2:])])
    NV[_n+"_quote"]={"quote1":_qnv(_a,1)}
json.dump(NV, open(BASE+"hot-leg-2026-11-03-0149-reread-nvagent.json","w"), indent=1)
for k,v in NV.items():
    print("NVAGENT", k, {kk:(vv.get("int") if isinstance(vv, dict) else vv) for kk,vv in v.items()} if isinstance(v,dict) else v)
