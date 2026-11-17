import json, urllib.request
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1431"
REG="0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
REG_HEX="60b9262456de011f7d15a54cdd8c48baaa8b022f"
scan=json.load(open(f"{BASE}/onchain-scan-{TS}.json"))
seen=json.load(open(f"{BASE}/onchain-scan-seen.json"))
snap=json.load(open(f"{BASE}/onchain-snapshot.json"))
seen_c={k.lower() for k in seen.get("contracts",{})}
seen_old={k.lower() for k in seen.get("known_older_leads",{})}
snap_addrs={v.get("address","").lower() for v in snap.get("contracts",{}).values()}
excluded=set()
_ex=snap.get("excluded")
if isinstance(_ex,dict):
    for v in _ex.values():
        excluded.add(v.get("address","").lower() if isinstance(v,dict) else str(v).lower())
elif isinstance(_ex,list):
    for v in _ex:
        excluded.add(v.get("address","").lower() if isinstance(v,dict) else str(v).lower())
print("SCAN window", scan.get("from_block"), "-", scan.get("to_block"), "head", scan.get("latest_block"), "ankr_calls", scan.get("ankr_calls"), "errors", scan.get("errors"))
print("nft contracts:", len(scan.get("contracts",[])), "erc20:", len(scan.get("erc20_mint_contracts_list",[])))
first=[]
for c in scan.get("contracts",[]):
    a=c["address"].lower()
    if a==REG.lower(): continue
    if a in seen_c or a in seen_old or a in snap_addrs or a in excluded: continue
    first.append(c)
print("FIRST-SEEN nft:", len(first))
for c in first: print("  ", c["address"], c.get("kind"), "mints", c.get("mint_count"), "minters", c.get("distinct_minters"), "first_block", c.get("first_block"))
json.dump(first, open(f"{BASE}/run-{TS}-scan-firstseen.json","w"), indent=1)

# --- agent-shape check via Sourcify ABI + bytecode registry bytes ---
def abi_of(a):
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi",headers={"User-Agent":"curl"})
        with urllib.request.urlopen(req,timeout=15) as r: d=json.load(r)
        return d.get("abi") or d.get("stdJson",{}).get("abi") or []
    except Exception as e: return {"error":str(e)[:80]}
def code_of(a):
    for rpc in ["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc.publicnode.com"]:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[a,"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as r: return json.load(r)["result"]
        except Exception: continue
    return ""
FREE_WORDS=["freeMinted","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeShare","FREE_SUPPLY","FREE_CAP","FREE_SLOTS","FREE_AMOUNT","freeMint","mintFree"]
shape={}
for c in first:
    a=c["address"]
    abi=abi_of(a)
    if isinstance(abi,dict): shape[a]={"sourcify":"unverified","abi_error":abi.get("error")}; print("SHAPE",a,"unverified"); continue
    fns=sorted({f.get("name") for f in abi if f.get("type")=="function" and f.get("name")})
    has_mint=any(n.startswith("mint") for n in fns)
    free=[f for f in fns if any(w in f for w in FREE_WORDS)]
    agent=("agentRegistry" in fns or "AGENT_ID" in fns or "AGENT_REGISTRY" in fns or "registry" in fns)
    code=code_of(a)
    reg_bytes=REG_HEX in (code or "").lower()
    agent_shaped=bool(agent or reg_bytes) and bool(has_mint and free)
    shape[a]={"sourcify":"verified","abi_functions":fns,"mint":has_mint,"free":free,"agent_fn":agent,"registry_bytes":reg_bytes,"agent_shaped":agent_shaped}
    print("SHAPE",a,"shaped" if agent_shaped else "not-shaped","mint",has_mint,"free",free,"agentFn",agent,"regBytes",reg_bytes)
json.dump(shape, open(f"{BASE}/run-{TS}-scan-shape.json","w"), indent=1)

# --- route 5c: ERC-20 backlog ---
checked=json.load(open(f"{BASE}/track-c-scan-checked.json")) if True else {}
try:
    checked=json.load(open(f"{BASE}/track-c-scan-checked.json"))
except Exception:
    checked={}
checked_l={k.lower() for k in checked}
erc=sorted(scan.get("erc20_mint_contracts_list",[]), key=lambda x:-x.get("mint_count",0))
cand=[e for e in erc if e.get("mint_count",0)>=10 and e["address"].lower() not in checked_l]
print("5c candidates mint>=10, unchecked:", len(cand), "of", len([e for e in erc if e.get('mint_count',0)>=10]))
json.dump(cand[:20], open(f"{BASE}/run-{TS}-erc20-new.json","w"), indent=1)
for e in cand[:20]: print("  5c", e["address"], "mints", e.get("mint_count"))
