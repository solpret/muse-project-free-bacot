#!/usr/bin/env python3
"""Minimal salvage 1819: leg1/2 from already-fetched local files (no network),
leg3 shape-check DEFERRED (Sourcify ABI egress stalled twice), leg4 RPC batch only.
Writes hot-leg-run-2026-11-18-1819.json + -reread.json. Does NOT update seen
(new feed contracts stay unseen so next run shape-checks them)."""
import json, re, sys, time
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124","0x8b47354e7b76b1970a0d06365c8244a810d37493"}
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def encode(sig, arg):
    d = "0x" + sel(sig)
    if arg == "user": d += enc_addr(USER)
    elif arg == "one": d += "%064x" % 1
    elif arg == "user1": d += enc_addr(USER) + "%064x" % 1
    return d
def qn_batch(calls, timeout=15):
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    payload = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]} for i,(to,data) in enumerate(calls)]
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally: conn.close()
    if status != 200: raise IOError(f"quicknode http {status}: {raw[:150]!r}")
    data = json.loads(raw.decode())
    by = {it["id"]: it for it in data if isinstance(it, dict)}
    out = []
    for i in range(len(calls)):
        it = by.get(i+1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try: out.append(int(it["result"], 16))
            except Exception: out.append(it["result"])
        elif "error" in it: out.append(f"err:{it['error']}")
        else: out.append(None)
    return out
seen = json.load(open(f"{HF}/hot-leg-seen.json")); seen_l = {k.lower() for k in seen}
out = {"run":"free-mint-hot-leg 2026-11-18 18:19 WIB","started_wib":now_wib,
 "transport":"Sourcify feed + Boltbook EN/ZH via direct curl (200, fetched 11:26-11:27 UTC); RPC via Quicknode CONNECT tunnel",
 "salvage_note":"Two full attempts (1819-run, 1819-salvage) hit the 280s/240s timeout in sequential leg3 Sourcify ABI fetches (egress stall; urlopen timeouts not bounding the stall). This minimal run skips leg3: new feed contracts are NOT added to seen, so the next run shape-checks them. Leg1/2 computed locally from the already-fetched files; leg4 RPC only."}
feed = json.load(open("/tmp/hotleg_sourcify.json"))
items = feed.get("results", [])
addrs = [(it.get("address"), it.get("verifiedAt")) for it in items if it.get("address")]
new1 = [(a,v) for a,v in addrs if a.lower() not in seen_l and a.lower() not in EXCLUDED]
out["leg1_sourcify"] = {"http":200,"total":len(addrs),"new":len(new1),"new_contracts":[a for a,_ in new1],
 "verified_window":[addrs[-1][1] if addrs else None, addrs[0][1] if addrs else None]}
def boltbook(lang, src):
    html = open(src, encoding="utf-8", errors="replace").read()
    a2 = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
    new = [a for a in a2 if a.lower() not in seen_l and a.lower() not in EXCLUDED and a.lower()!=REGISTRY.lower()]
    return {"bytes":len(html),"http_code":200,"addresses":len(a2),"new":len(new),"new_contracts":new,
            "free_kw":len(re.findall(r"free", html, re.I)),"zh_free_kw":len(re.findall("免费", html))}
for lang, src in (("en","/tmp/bb_en2.html"),("zh","/tmp/bb_zh.html")):
    try: out[f"leg2_boltbook_{lang}"] = boltbook(lang, src)
    except Exception as e: out[f"leg2_boltbook_{lang}"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
out["leg3_shape_check"] = "DEFERRED - Sourcify ABI egress stalled twice (full run 280s + salvage 240s timeouts); new contracts left out of seen for next run"
out["leg3_sale_shape"] = []
out["seen_added"] = []; out["seen_n"] = len(seen)
PLAN = [
 ("DGF CARD","0x01f9CA4ff95d49594cC8B6591022186dc5C1Bc72",[("totalMinted","totalMinted()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("BinanceAI","0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",[("launched","launched()",None),("failed","failed()",None),("tokenClaimed_user","tokenClaimed(address)","user")]),
 ("AlphaPulse V1","0xE09Ab25732b1e1FdA7ad4d551EEA0aAC65aD0711",[("totalSupply","totalSupply()",None),("mintOpen","mintOpen()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("FABE","0xFabE022a5943462fee1Bd221791945DA57510BE8",[("freeSharesRemaining","freeSharesRemaining()",None),("launched","launched()",None),("freeSharesClaimed_user","freeSharesClaimed(address)","user"),("totalShares","totalShares()",None)]),
 ("PUNNY","0xaFAE0Bf373ad87E88555afe1605111F66C99062C",[("freeMinted","freeMinted()",None),("FREE_SUPPLY","FREE_SUPPLY()",None),("totalMinted","totalMinted()",None),("hasClaimedFree_user","hasClaimedFree(address)","user")]),
 ("STOCK AGENT","0xba7068233da805bdebcc167be361c219002e6b7f",[("totalSupply","totalSupply()",None),("freeLeft","freeLeft()",None),("quote_user_1","quote(address,uint256)","user1"),("quoteFor_user_1","quoteFor(address,uint256)","user1"),("freeMintedByWallet_user","freeMintedByWallet(address)","user"),("balanceOf_user","balanceOf(address)","user")]),
]
calls=[]; meta=[]
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append((addr, encode(sig, arg))); meta.append((name, addr, label))
res=[]; errs=[]
for i in range(0, len(calls), 5):
    try: res += qn_batch(calls[i:i+5])
    except Exception as e:
        errs.append(f"calls {i}: {type(e).__name__}: {str(e)[:150]}"); res += [None]*len(calls[i:i+5])
reads={}
for (name, addr, label), val in zip(meta, res):
    reads.setdefault(name, {"address":addr,"views":{}})["views"][label]=val
try:
    entry = dynamic_credential_entry("custom.quicknode"); surrogate=str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=15)
    conn.request("POST", f"/{surrogate}/", body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode(), headers={"Content-Type":"application/json"})
    resp=conn.getresponse(); blk=json.loads(resp.read().decode()); conn.close()
    block=int(blk["result"],16)
except Exception as e: block=f"error: {str(e)[:120]}"
reread={"reads":reads,"errors":errs,"n_calls":len(calls),"elapsed_s":round(time.time()-T0,1),"block":block,"started_wib":now_wib}
json.dump(reread, open(f"{HF}/hot-leg-run-2026-11-18-1819-reread.json","w"), indent=1)
out["leg4_reread"]={"block":block,"reads":{k:v["views"] for k,v in reads.items()},"errors":errs}
prev={"DGF CARD totalMinted":1652,"BinanceAI launched()":0,"BinanceAI failed()":1,"AlphaPulse V1 totalSupply":34,"FABE freeSharesRemaining":2821,"PUNNY freeMinted":362,"PUNNY totalMinted":362,"STOCK AGENT totalSupply":776,"STOCK AGENT freeLeft":335}
cur={"DGF CARD totalMinted":reads["DGF CARD"]["views"].get("totalMinted"),"BinanceAI launched()":reads["BinanceAI"]["views"].get("launched"),"BinanceAI failed()":reads["BinanceAI"]["views"].get("failed"),"AlphaPulse V1 totalSupply":reads["AlphaPulse V1"]["views"].get("totalSupply"),"FABE freeSharesRemaining":reads["FABE"]["views"].get("freeSharesRemaining"),"PUNNY freeMinted":reads["PUNNY"]["views"].get("freeMinted"),"PUNNY totalMinted":reads["PUNNY"]["views"].get("totalMinted"),"STOCK AGENT totalSupply":reads["STOCK AGENT"]["views"].get("totalSupply"),"STOCK AGENT freeLeft":reads["STOCK AGENT"]["views"].get("freeLeft")}
out["leg4_changes"]={k:{"prev":prev[k],"now":cur[k]} for k in prev if prev[k]!=cur[k]}
pu=reads["PUNNY"]["views"]; st=reads["STOCK AGENT"]["views"]
punny_pct=(pu.get("freeMinted")/pu.get("FREE_SUPPLY")*100) if isinstance(pu.get("freeMinted"),int) and isinstance(pu.get("FREE_SUPPLY"),int) and pu.get("FREE_SUPPLY") else None
stock_free=(st.get("totalSupply")/1111*100) if isinstance(st.get("totalSupply"),int) else None
out["leg4_promotion_check"]={
 "PUNNY_free_pct":round(punny_pct,2) if punny_pct is not None else None,
 "PUNNY_note":"age VERIFIED <24h (mintStart 2026-11-17 20:32 WIB, closes 20:32 WIB today); website gate UNVERIFIED -> no promotion; pct must be >70% for strong lead.",
 "STOCK_free_pct_inferred":round(stock_free,2) if stock_free is not None else None,
 "STOCK_note":"age UNVERIFIED + website gate UNVERIFIED -> no promotion even if pct crossed 70%; inferred free% = totalSupply/1111.",
 "DGF_note":"age + free% still unverified; website verified but that alone is not a tier."}
out["leg4_note"]="No sellout, slot loss, age-exclusion, claim opening, or tier promotion unless leg4_changes shows a qualifying state change."
try:
    bridge=json.load(open(f"{HF}/scan-bridge.json")); contracts=bridge.get("contracts",{})
    snap=json.load(open(f"{HF}/onchain-snapshot.json")); snap_addrs=set()
    for coll in ("contracts","track_c"):
        for k,v in snap.get(coll,{}).items():
            if isinstance(v,dict):
                for f in ("address","sale","token","mint"):
                    if v.get(f): snap_addrs.add(str(v[f]).lower())
    for k,v in snap.get("pending_claims",{}).items():
        if isinstance(v,dict):
            for f in ("mint","token"):
                if v.get(f): snap_addrs.add(str(v[f]).lower())
    not_in=[a for a in contracts if a.lower() not in snap_addrs]
    disc=sum(1 for v in contracts.values() if isinstance(v,dict) and v.get("same_owner_discarded"))
    out["bridge"]={"total":len(contracts),"not_in_snapshot":len(not_in),"not_in_snapshot_list":not_in,"same_owner_discarded":disc,"note":"bridge contracts not in snapshot are not reported as new; no bridge promotion/change unless leg4 shows one."}
except Exception as e:
    out["bridge"]={"error":f"{type(e).__name__}: {str(e)[:150]}","note":"bridge skip - run continues"}
out["elapsed_s"]=round(time.time()-T0,1)
out["executions"]="none - no preview, no mint, no claim (read-only run)"
reportable=bool(out["leg3_sale_shape"]) or any((k in out["leg4_changes"] and out["leg4_changes"][k]["now"] is not None) for k in ("BinanceAI launched()","FABE freeSharesRemaining"))
out["result"]=("CHANGES FOUND - see leg3/leg4" if reportable else "SILENT - no new lead, candidate, pending claim, change, or blocked auto-mint/auto-claim.")
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-18-1819.json","w"), indent=1)
print(json.dumps(out, indent=1))
