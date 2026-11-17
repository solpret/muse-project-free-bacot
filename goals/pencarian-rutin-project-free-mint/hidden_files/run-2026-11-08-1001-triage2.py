import json, sys, urllib.request, urllib.error, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch, _single as single
from Crypto.Hash import keccak
from ankr import ankr_post
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr, sig, arg=False, raw=False):
    data=sel(sig)+(enc(USER) if arg else "")
    for ep in EPS:
        try:
            r=single(ep, "eth_call", [{"to":addr,"data":data},"latest"], 8, retries=0)
            if r is None or r=="0x": return None
            if raw: return r
            return int(r,16)
        except Exception:
            continue
    return {"error":"all-eps-fail"}
def head_block():
    for ep in EPS:
        try: return int(batch([("eth_blockNumber",[])], endpoint=ep, timeout=10)[0],16)
        except Exception: pass
    return None
def block_ts(fb):
    for ep in EPS:
        try:
            b=batch([("eth_getBlockByNumber",[hex(fb), False])], endpoint=ep, timeout=10)
            ts=int(b[0]["timestamp"],16)
            return datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S")
        except Exception: pass
    return None
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
T721="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
T1155="0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
def logs(addr, frm, to, topics):
    body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":addr,"topics":topics})
    r=body.get("result",{})
    if isinstance(r,dict): return r.get("logs",[])
    return r if isinstance(r,list) else []
def first_mint(addr, head, topic, topic_name):
    # probe backwards until an EMPTY window; first log of last non-empty window is the true first mint
    cur_to=head; last=None; probes=0
    while cur_to>130000000 and probes<40:
        cur_from=max(130000000, cur_to-99999)
        try:
            ls=logs(addr, cur_from, cur_to, [topic, ZERO] if topic==T721 else [topic, None, ZERO])
        except Exception as e:
            return {"error":str(e)[:120],"probes":probes}
        probes+=1
        if ls:
            last={"first_block":int(ls[0]["blockNumber"],16),"first_time_wib":block_ts(int(ls[0]["blockNumber"],16)),"count_in_window":len(ls),"window":[cur_from,cur_to],"topic":topic_name}
            cur_to=cur_from-1
        else:
            break
    if last:
        last["probes"]=probes
        return last
    return {"first_block":None,"probes":probes}
def sourcify_abi(addr):
    url=f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d=json.load(r)
        abi=d.get("abi") or d.get("stdJson",{}).get("abi")
        if isinstance(abi,list):
            fns=[x.get("name","") for x in abi if x.get("type")=="function"]
            raw=json.dumps(abi).lower()
            return {"status":"verified","match":d.get("stdJson",{}).get("match") or d.get("match"),"verifiedAt":d.get("stdJson",{}).get("verifiedAt") or d.get("verifiedAt"),"fns":fns,"registry_in_abi":("60b9262456de011f7d15a54cdd8c48baaa8b022f" in raw) or ("agentregistry" in raw) or ("agent_id_registry" in raw)}
        return {"status":"no-abi","raw":str(d)[:200]}
    except urllib.error.HTTPError as e:
        return {"status":f"http-{e.code}"}
    except Exception as e:
        return {"status":"error","raw":str(e)[:150]}
TARGETS={
 "Zigzoo":"0x09ada5a12293c30d75b97c56e34967e8a4326a3c",
 "Chromeshade":"0x5ba7355fb4001efe5232eb0286e11fd81eee99a4",
 "Ninetailix":"0x809215729bcbff2ef31dea5efd6c12a6b788ba9a",
 "NovaAgent":"0xa6909af663637cd988e712efbc2e73f7076d9154",
}
head=head_block(); print("head:", head)
out={}
for name,addr in TARGETS.items():
    print("="*20, name, addr)
    d={"address":addr}
    for sig in ["AGENT_ID()","agentRegistry()","isAgent(address)","agentIdOf(address)"]:
        d[sig]=call(addr, sig, "(address)" in sig)
    d["supports721"]=call(addr,"supportsInterface(bytes4)",raw=False) if False else None
    d["sourcify"]=sourcify_abi(addr)
    print(" agent views:", {k:v for k,v in d.items() if k.startswith(("AGENT","agent","isAgent"))})
    print(" sourcify:", {k:(v if k!="fns" else f"{len(v)} fns: {v[:50]}") for k,v in d["sourcify"].items()})
    d["first_mint_721"]=first_mint(addr, head, T721, "Transfer")
    print(" first_mint_721:", d["first_mint_721"])
    if d["first_mint_721"].get("first_block") is None:
        d["first_mint_1155"]=first_mint(addr, head, T1155, "TransferSingle")
        print(" first_mint_1155:", d["first_mint_1155"])
    out[name]=d
json.dump(out, open("run-2026-11-08-1001-triage2.json","w"), indent=1)
print("WROTE run-2026-11-08-1001-triage2.json")
