import json, urllib.request, re, subprocess
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1614"
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG="60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def raw(to,data):
    tx={"to":to,"data":data}
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[tx,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=8) as r: out=json.load(r)
            if "error" in out: return {"error":str(out["error"])[:80]}
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return {"error":"rpc-fail"}
def call(to,sig,args=""): return raw(to,sel(sig)+args)
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=8) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None

# --- Leg 1: Sourcify feed + shape ---
feed=None
try:
    req=urllib.request.Request("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc",headers={"User-Agent":"curl"})
    with urllib.request.urlopen(req,timeout=20) as r: feed=json.load(r)
    json.dump(feed,open(f"{BASE}/run-{TS}-sourcify.json","w"),indent=1)
except Exception as e:
    feed={"error":str(e)}
addrs=[x["address"] for x in feed.get("results",[])] if isinstance(feed,dict) and "results" in feed else []
seen=json.load(open(f"{BASE}/hot-leg-seen.json"))
seen_l={k.lower():v for k,v in seen.items()}
new=[a for a in addrs if a.lower() not in seen_l]
excluded=["0x827e83e49bd7e15b67efa0e90fc25f17b8d96124","0x8b47354e7b76b1970a0d06365c8244a810d37493"]
new_not_excl=[a for a in new if a.lower() not in excluded]
print("FEED",len(addrs),"NEW",len(new),new)
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
    is_token=all(x in fns for x in ["name","symbol","decimals","totalSupply"])
    has_mintfree="mintFree" in fns
    s1=has_mint and has_quote and bool(free) and agent
    s2=is_token and has_mintfree and ("freeClaimed" in fns or "freeMinted" in fns) and ("FREE_SLOTS" in fns or "FREE_SUPPLY" in fns) and agent
    entry={"abi_functions":fns,"S1":s1,"S2":s2,"mint":has_mint,"quote":has_quote,"free":free,"agent":agent,"token":is_token}
    shape[a]=entry
    print("SHAPE",a,"S1",s1,"S2",s2,"mint",has_mint,"quote",has_quote,"free",free,"agent",agent,"token",is_token)
json.dump(shape,open(f"{BASE}/run-{TS}-sourcify-shape.json","w"),indent=1)

# --- Leg 2: Boltbook EN+ZH ---
bb={}
for lang,fn in [("en","hot-leg-1614-boltbook-en.html"),("zh","hot-leg-1614-boltbook-zh.html")]:
    url="https://boltbook.fun/" if lang=="en" else "https://boltbook.fun/?lang=zh"
    ok=False
    for attempt in range(2):
        try:
            r=subprocess.run(["curl","-sS","-L","--max-time","20","-A","Mozilla/5.0",url],capture_output=True,text=True,timeout=30)
            if r.returncode==0 and len(r.stdout)>10000:
                open(f"{BASE}/{fn}","w").write(r.stdout)
                bb[lang]={"bytes":len(r.stdout),"addrs":sorted(set(re.findall(r"0x[0-9a-fA-F]{40}",r.stdout))),"keywords":{k:(k in r.stdout) for k in (["free share","first share free","1 free share","free mint share"] if lang=="en" else ["免费份额","首个免费","免费铸造","免费mint"])}}
                ok=True; break
        except Exception as e: bb[lang]={"error":str(e)}
    if not ok and lang not in bb: bb[lang]={"error":"fetch-failed"}
    print("BOLTBOOK",lang,bb.get(lang))
json.dump(bb,open(f"{BASE}/run-{TS}-boltbook.json","w"),indent=1)

# --- Leg 3: Bridge (read-only) ---
try:
    br=json.load(open(f"{BASE}/scan-bridge.json"))
    cons=br.get("contracts",{})
    snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
    snap_text=json.dumps(snap)
    not_in_snap=[c for c in cons if c.lower() not in snap_text.lower()]
    discarded=[c for c,v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE",len(cons),"discarded",len(discarded),"not_in_snapshot_text",len(not_in_snap))
    json.dump({"total":len(cons),"discarded":len(discarded),"not_in_snapshot":len(not_in_snap),"not_in_snapshot_list":not_in_snap},open(f"{BASE}/run-{TS}-bridge.json","w"),indent=1)
except Exception as e:
    print("BRIDGE-ERROR",e)

# --- Leg 4: spotcheck re-read (read-only) ---
res={"block":block()}
CJ="0x18042D2E0bFd11fc2cc8ee1E59a6601e530C3dF5"
LL="0x1B72ceC52A74537b06F713FCebA0e491f53679aE"
TB="0x02f10432EAf9CbF72e1aC9b9208af601aADd6b17"
AM="0x8670e99062ead2cE5402754aeDE769602FDf38b8"
WAGA="0x06a6f51D30556f4262e38485C09556fE81e6A984"
SEN="0xb21583A08581278BcF925351a99C61A4562C62f0"
AFROG="0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31"
RK="0x5e42db19a22f5c858dc72df6352495ffff9abb62"
IMARS="0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f"
NIULAI="0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF"
AGF="0x53A3D78FF23d9c9cb14Ae8B2fd168A44391b2010"
DRFT="0x6a926234D3767F2EEb3DB12c1B4C9e2912C5589b"
LUCK="0xd08ef372B52C29255fEd7004f59bF41571451894"
for name,addr in [("Cachejack",CJ),("Layerloom",LL),("Tumblebots",TB)]:
    res[name]={"totalSupply()":call(addr,"totalSupply()"),"freeMinted()":call(addr,"freeMinted()"),"claimedFree(user)":call(addr,"claimedFree(address)",enc(USER)),"canFreeMint(user)":call(addr,"canFreeMint(address)",enc(USER))}
res["AgentMiner"]={"totalSupply()":call(AM,"totalSupply()"),"freeFor(user,1)":call(AM,"freeFor(address,uint256)",enc(USER)+enc_uint(1)),"quote(user,1)":call(AM,"quote(address,uint256)",enc(USER)+enc_uint(1)),"mintedBy(user)":call(AM,"mintedBy(address)",enc(USER))}
res["WAGA"]={"totalMints()":call(WAGA,"totalMints()"),"quote(user,1)":call(WAGA,"quote(address,uint256)",enc(USER)+enc_uint(1)),"mintOpen()":call(WAGA,"mintOpen()")}
res["SENBAZURU"]={"freeClaimed()":call(SEN,"freeClaimed()"),"paidSold()":call(SEN,"paidSold()"),"hasFreeShare(user)":call(SEN,"hasFreeShare(address)",enc(USER))}
res["AFROG"]={"totalSupply()":call(AFROG,"totalSupply()"),"freeClaimed()":call(AFROG,"freeClaimed()"),"FREE_SUPPLY()":call(AFROG,"FREE_SUPPLY()")}
res["RACKRUSH"]={"totalSupply()":call(RK,"totalSupply()"),"freeMinted()":call(RK,"freeMinted()"),"claimedFree(user)":call(RK,"claimedFree(address)",enc(USER)),"FREE_CAP()":call(RK,"FREE_CAP()"),"MAX_SUPPLY()":call(RK,"MAX_SUPPLY()")}
res["IMARS"]={"opened()":call(IMARS,"opened()"),"freeMinted()":call(IMARS,"freeMinted()"),"totalMinted()":call(IMARS,"totalMinted()")}
res["NIULAI"]={"phase()":call(NIULAI,"phase()"),"launched()":call(NIULAI,"launched()"),"freeClaimed()":call(NIULAI,"freeClaimed()"),"freeShares()":call(NIULAI,"freeShares()")}
res["LuckyBox"]={"totalSupply()":call(LUCK,"totalSupply()"),"freeLeft(user)":call(LUCK,"freeLeft(address)",enc(USER)),"freeUsed(user)":call(LUCK,"freeUsed(address)",enc(USER)),"freeFor(user,1)":call(LUCK,"freeFor(address,uint256)",enc(USER)+enc_uint(1)),"quote(user,1)":call(LUCK,"quote(address,uint256)",enc(USER)+enc_uint(1)),"mintedBy(user)":call(LUCK,"mintedBy(address)",enc(USER)),"mintOpen()":call(LUCK,"mintOpen()")}
for name,addr in [("AgentCoffee",AGF),("Driftnauts",DRFT)]:
    res[name]={"totalSupply()":call(addr,"totalSupply()"),"freeMinted()":call(addr,"freeMinted()"),"claimedFree(user)":call(addr,"claimedFree(address)",enc(USER)),"canFreeMint(user)":call(addr,"canFreeMint(address)",enc(USER))}
print(json.dumps(res,indent=1))
json.dump(res,open(f"{BASE}/run-{TS}-spotcheck.json","w"),indent=1)
print("DONE")
