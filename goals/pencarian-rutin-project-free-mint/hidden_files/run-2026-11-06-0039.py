#!/usr/bin/env python3
"""Hot-leg run 2026-11-06 00:39 WIB. Leg4 lean re-read (watch set) + Leg5 bridge read-only.
Writes only own run files + hot-leg-seen.json. Never touches main snapshot."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-0039"; NOW="2026-11-06 00:39 WIB"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
def raw(to,data):
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=5) as r: out=json.load(r)
            if "error" in out: return None
            v=out["result"]
            if not v or v=="0x": return None
            try: return int(v,16)
            except Exception: return v
        except Exception: continue
    return None
def call(to,sig,args=""): return raw(to,sel(sig)+args)
def block():
    for rpc in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
            req=urllib.request.Request(rpc,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=5) as r: return int(json.load(r)["result"],16)
        except Exception: continue
    return None
blk=block(); print("BLOCK",blk,flush=True)
WATCH_A=[("Mossminds","0x5b49b06a2e25fce0bca865be70f3c62b6319367a"),("Jolly","0xdc11764a5664e333c8d303eb465e89a1caadb85b"),
("Glyph","0x3ef2A97Abf2E43182eACAe323B82d2CAC2132C6A"),("Agent Frogs","0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31"),
("AgentLattice","0x5b9fe53468F1Aa4EDbe2b96a4387910D335e2eDB"),("Agent Goats","0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6"),
("Agent Owls","0x50B4bD215c409C975c940d5CF23B56D8F3ecfd3b")]
WATCH_C=[("Pacture","0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9"),("Ikigai","0x3611455bE1FC2c6987FE9d016971b7E40B341684"),
("Hongbao","0x834e5BC43Aa91bEbEB31B97eaFA1bCb2F4286d97"),("DeY","0xDB062c12bF0a14227e7Fe896a988950b050B51C1"),
("FANBEIMAO","0x824d1e5c1395ed7543854fCd9e4da6D3F358De16"),("LuckyBox","0xd08ef372B52C29255fEd7004f59bF41571451894"),
("NJAR","0x816458b734d17d59058762deaadd9b952bad6985"),("Predictagent","0x8fF4bd65584882324c44Ee794a23E7791820189b"),
("Nvagent","0x4951Eab992c6A68Ad86040Aa2df92D46C3c207B2"),("nVigent","0x28Fe0daD54dbfc84D29Cd48E88c27a82E76fF1c2")]
def read_a(item):
    name,a=item; d={"name":name,"address":a,"block":blk}
    d["totalSupply"]=call(a,"totalSupply()"); d["freeClaimed"]=call(a,"freeClaimed()")
    d["freeMinted"]=call(a,"freeMinted()"); d["FREE_SUPPLY"]=call(a,"FREE_SUPPLY()")
    d["mintOpen"]=call(a,"mintOpen()"); d["mintedBy_user"]=call(a,"mintedBy(address)",enc(USER))
    d["freeUsed_user"]=call(a,"freeUsed(address)",enc(USER)); d["freeLeft_user"]=call(a,"freeLeft(address)",enc(USER))
    d["quote_user_1"]=call(a,"quote(address,uint256)",enc(USER)+enc_uint(1))
    d["balanceOf_user"]=call(a,"balanceOf(address)",enc(USER))
    return d
def read_c(item):
    name,a=item; d={"name":name,"address":a,"block":blk}
    d["freeSharesRemaining"]=call(a,"freeSharesRemaining()"); d["freeClaimed_user"]=call(a,"freeClaimed(address)",enc(USER))
    d["freeLeft_user"]=call(a,"freeLeft(address)",enc(USER)); d["mintOpen"]=call(a,"mintOpen()")
    d["opened"]=call(a,"opened()"); d["launched"]=call(a,"launched()"); d["saleEnded"]=call(a,"saleEnded()")
    d["totalMinted"]=call(a,"totalMinted()"); d["freeMinted"]=call(a,"freeMinted()")
    d["quote_user_1"]=call(a,"quote(address,uint256)",enc(USER)+enc_uint(1))
    d["hasFreeShare_user"]=call(a,"hasFreeShare(address)",enc(USER))
    return d
out={}
with ThreadPoolExecutor(max_workers=8) as ex:
    for d in ex.map(read_a,WATCH_A):
        out[d["name"]]=d; print("REREAD-A",d,flush=True)
    for d in ex.map(read_c,WATCH_C):
        out[d["name"]]=d; print("REREAD-C",d,flush=True)
json.dump(out,open(f"{BASE}/run-{TS}-reread.json","w"),indent=1)
# --- Leg5 bridge read-only ---
try:
    br=json.load(open(f"{BASE}/scan-bridge.json")); cons=br.get("contracts",{})
    snap=json.load(open(f"{BASE}/onchain-snapshot.json")); snap_text=json.dumps(snap)
    not_in=[c for c in cons if c.lower() not in snap_text.lower()]
    discarded=[c for c,v in cons.items() if v.get("same_owner_discarded")]
    print("BRIDGE",len(cons),"discarded",len(discarded),"not_in_snapshot",len(not_in),flush=True)
    json.dump({"total":len(cons),"discarded":len(discarded),"not_in_snapshot":len(not_in),
               "not_in_snapshot_list":not_in},open(f"{BASE}/hot-leg-{TS}-bridge.json","w"),indent=1)
    pc=snap.get("pending_claims",{})
    print("PENDING_CLAIMS",pc,flush=True)
except Exception as e:
    print("BRIDGE-ERROR",e,flush=True)
print("DONE",flush=True)
