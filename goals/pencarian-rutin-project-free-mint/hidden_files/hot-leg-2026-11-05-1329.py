import json, urllib.request, re, subprocess, os
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1329"
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data,frm=None):
    tx={"to":to,"data":data}
    if frm: tx["from"]=frm
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[tx,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:80]}
            return out["result"]
        except Exception: continue
    return {"error":"rpc-fail"}
def cint(v):
    if isinstance(v,dict): return v
    try: return int(v,16) if v and v!="0x" else 0
    except Exception: return v
def cstr(v):
    if isinstance(v,dict) or not v or v=="0x": return v
    try:
        h=v[2:]; ln=int(h[64:128],16); return bytes.fromhex(h[128:128+ln*2]).decode(errors="replace")
    except Exception: return v
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=10) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None

# --- Leg 1: Sourcify feed ---
feed=None
try:
    req=urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",headers={"User-Agent":"curl"})
    with urllib.request.urlopen(req,timeout=20) as r: feed=json.load(r)
    json.dump(feed,open(f"{BASE}/hot-leg-{TS}-sourcify.json","w"),indent=1)
except Exception as e:
    feed={"error":str(e)}
addrs=[x["address"] for x in feed.get("results",[])] if isinstance(feed,dict) and "results" in feed else []
seen=json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l={k.lower():v for k,v in seen.items()}
new=[a for a in addrs if a.lower() not in seen_l]
excluded=["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124","0x8b47354e7b76b1970a0d06365c8244a810d37493"]
new_not_excl=[a for a in new if a.lower() not in excluded]
print("FEED",len(addrs),"NEW",len(new),new)

# --- Shape-check new only ---
FREE=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed"]
shape={}
def abi_of(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or []
    except Exception as e: return {"error":str(e)[:80]}
for a in new_not_excl:
    abi=abi_of(a)
    fns=sorted({f.get("name") for f in abi if isinstance(abi,list) and f.get("type")=="function" and f.get("name")}) if isinstance(abi,list) else []
    has_mint=any(n.startswith("mint") for n in fns)
    has_quote="quote" in fns
    free=[f for f in fns if any(x in f for x in FREE)]
    agent=("agentRegistry" in fns or "AGENT_REGISTRY" in fns or "registry" in fns or (isinstance(abi,list) and REG in json.dumps(abi).lower()))
    is_token=("name" in fns and "symbol" in fns and "decimals" in fns and "totalSupply" in fns)
    has_mintfree="mintFree" in fns
    s1=has_mint and has_quote and bool(free) and agent
    s2=is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    entry={"abi_functions":fns,"S1":s1,"S2":s2,"mint":has_mint,"quote":has_quote,"free":free,"agent":agent,"token":is_token}
    # quick on-chain name/symbol/totalSupply + quote if S1/S2-ish
    if s1 or s2 or (has_mint and has_quote and bool(free)):
        for fn in ["name()","symbol()","totalSupply()"]:
            v=raw(a,sel(fn)); entry[fn]=cstr(v) if fn in ("name()","symbol()") else cint(v)
        if s1:
            qd=sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
            entry["quote(user,1)"]=cint(raw(a,qd))
    shape[a]=entry
    print("SHAPE",a,entry.get("S1"),entry.get("S2"),entry.get("free"),entry.get("agent"))
json.dump(shape,open(f"{BASE}/hot-leg-{TS}-sourcify-shape.json","w"),indent=1)

# --- WAGA recheck (gate-blocked lead 13:04) ---
WAGA="0x06a6f51D30556f4262e38485C09556fE81e6A984"
w={}
for fn,frm in [("totalMints()",None),("freeLeft(address)",USER),("mintedBy(address)",USER),("mintOpen()",None)]:
    v=raw(WAGA,sel(fn)+(enc(frm) if frm else "")); w[fn]=cint(v)
qd=sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001"
w["quote(user,1)"]=cint(raw(WAGA,qd))
print("WAGA",w)
json.dump({"waga":w,"shape":shape},open(f"{BASE}/hot-leg-{TS}-waga.json","w"),indent=1)

# --- Leg 2: Boltbook EN+ZH ---
bb={}
for lang,fn in [("en","hot-leg-1329-boltbook-en.html"),("zh","hot-leg-1329-boltbook-zh.html")]:
    url="https://boltbook.fun/" if lang=="en" else "https://boltbook.fun/?lang=zh"
    ok=False
    for attempt in range(2):
        try:
            r=subprocess.run(["curl","-sS","-L","--max-time","20","-A","Mozilla/5.0",url],capture_output=True,text=True,timeout=30)
            if r.returncode==0 and len(r.stdout)>10000:
                open(f"{BASE}/{fn}","w").write(r.stdout); bb[lang]={"bytes":len(r.stdout),"addrs":sorted(set(re.findall(r"0x[0-9a-fA-F]{40}",r.stdout))),"keywords":{k:(k in r.stdout) for k in (["free share","first share free","1 free share","free mint share"] if lang=="en" else ["免费份额","首个免费","免费铸造","免费mint"])}}
                ok=True; break
        except Exception as e: bb[lang]={"error":str(e)}
    if not ok and lang not in bb: bb[lang]={"error":"fetch-failed"}
    print("BOLTBOOK",lang,bb.get(lang))
json.dump(bb,open(f"{BASE}/hot-leg-{TS}-boltbook.json","w"),indent=1)

# --- Leg 4: reread snapshot (same set as 1309.py) ---
jobs={}
def add(k,addr,fn,frm=None): jobs[k]=(addr,sel(fn),frm)
STAR="0x7d390e37ed41a359f276d8764ca15432704b99b7"
add("STAR_totalSupply",STAR,"totalSupply()"); add("STAR_balance_user",STAR,"balanceOf(address)",USER); add("STAR_freeClaimed_user",STAR,"freeClaimed(address)",USER)
PACT="0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9"
add("PACT_sharesMinted",PACT,"sharesMinted()"); add("PACT_freeMinted",PACT,"freeMinted()"); add("PACT_paidShares",PACT,"paidShares()"); add("PACT_freeClaimed_user",PACT,"freeClaimed(address)",USER)
M="0x7a38395ad7317594a8eb6c658f3f073a693dfaab"
add("MEOW_totalSupply",M,"totalSupply()"); add("MEOW_balance_user",M,"balanceOf(address)",USER); add("MEOW_launched",M,"launched()")
add("OSK_opened","0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37","opened()"); add("OSK_totalMinted","0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37","totalMinted()")
add("NIULAI_launched","0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF","launched()"); add("NIULAI_phase","0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF","phase()")
add("KillZero_launched","0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97","launched()")
add("DROID_opened","0xFcF6388DD3bcC674c095273aB479C7e54dd5E177","opened()"); add("DROID_freeMinted","0xFcF6388DD3bcC674c095273aB479C7e54dd5E177","freeMinted()"); add("DROID_totalMinted","0xFcF6388DD3bcC674c095273aB479C7e54dd5E177","totalMinted()")
add("IMARS_opened","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f","opened()"); add("IMARS_freeMinted","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f","freeMinted()"); add("IMARS_totalMinted","0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f","totalMinted()")
add("ASOC_freeClaimed_user","0x43cEef9313CB8c4ca3757bA841C44DF40A223205","freeClaimed(address)",USER); add("ASOC_saleEnded","0x43cEef9313CB8c4ca3757bA841C44DF40A223205","saleEnded()")
def run(item):
    k,(a,s,frm)=item
    v=raw(a, s+enc(frm) if frm else s, frm=frm)
    return k,(cint(v) if not isinstance(v,dict) else v)
blk=block()
with ThreadPoolExecutor(max_workers=12) as ex:
    res=dict(ex.map(run, jobs.items()))
out={"block":blk,"values":res}
print("REREAD block",blk,res)
json.dump(out,open(f"{BASE}/hot-leg-{TS}-reread.json","w"),indent=1)

# --- Bridge (read-only) ---
try:
    br=json.load(open(f"{BASE}/scan-bridge.json"))
    cons=br.get("contracts",{})
    snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text=json.dumps(snap)
    not_in_snap=[c for c in cons if c.lower() not in snap_text.lower()]
    discarded=[c for c,v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE",len(cons),"discarded",len(discarded),"not_in_snapshot_text",len(not_in_snap))
    json.dump({"total":len(cons),"discarded":len(discarded),"not_in_snapshot":len(not_in_snap),"not_in_snapshot_list":not_in_snap},open(f"{BASE}/hot-leg-{TS}-bridge.json","w"),indent=1)
except Exception as e:
    print("BRIDGE-ERROR",e)
