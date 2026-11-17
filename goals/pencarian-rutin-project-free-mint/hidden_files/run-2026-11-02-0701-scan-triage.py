import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return "0x"+a[2:].lower().rjust(64,"0")
def enc_uint(n): return "0x"+format(n,"064x")
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
        except Exception: pass
    return None
def iv(v): return int(v,16) if v else None
def words(v):
    if not v: return None
    b=bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32],"big") for i in range(0,len(b),32)]
CANDS=[
 ("GOAT","0xE7a548606eECB32a93B227411b6343B0399DC7C0",241),
 ("Fern Agent","0x066839014386926C7b90e5C7ACc7c9b5Ac1789eb",174),
 ("Jade Agent","0x19c0F31F85F19399b855ab91F0F4EdD15c8bE756",107),
 ("Voltibot","0x76A7babEbB9A6c0ED312690225FA1b64851dac0B",10),
 ("Dunora","0x443CF08bbD6cF3FC900f107949b8e8ad69392e1a",1),
 ("Thundra","0xdd97B0A6680c6cF4880ce1759185418888e5F48f",1),
 ("Cometra","0xb4ca267934Bd4bAb5993b303C90c3Be3A3b4718b",1),
 ("Tidalune","0x530695A8e3EB9a1253cAFC9239811F4ca88791f9",1),
 ("Iridawn","0x6912aD805cB3E0FDd6330F27347193E4EFC0742d",1),
 ("Glaciera","0x38850dA344c7674470943A9091dF1679F7E2A6D5",1),
 ("Trumpeto","0x13E2400414e18046B250269DAd7D1471B336273C",1),
 ("Sakurine","0x83eCA0CdacEdA13a6E7B033F6d6cf7bD96F07e72",1),
]
out={}
for name,C,wm in CANDS:
    r={"address":C,"window_mints":wm}
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{C}?fields=abi", headers={"User-Agent":"Mozilla/5.0"})
        d=json.load(urllib.request.urlopen(req, timeout=20)); abi=d.get("abi") or []
        r["abi_fns"]=[f["name"] for f in abi if f.get("type")=="function"]
        r["has_agent_fn"]=any("AGENT" in x.upper() or "REGISTRY" in x.upper() for x in r["abi_fns"])
    except Exception as e: r["abi_error"]=str(e)
    for fn in ["totalSupply()","totalMinted()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","AGENT_ID()","agentRegistry()","registry()","agentIdRegistry()"]:
        v=call(C,sel(fn))
        r[fn]=iv(v) if fn not in ("AGENT_ID()","agentRegistry()","registry()","agentIdRegistry()") else v
    r["mintedBy_user"]=iv(call(C,sel("mintedBy(address)")+enc_addr(USER)[2:]))
    r["freeUsed_user"]=iv(call(C,sel("freeUsed(address)")+enc_addr(USER)[2:]))
    r["balance_user"]=iv(call(C,sel("balanceOf(address)")+enc_addr(USER)[2:]))
    q=call(C,sel("quote(address,uint256)")+enc_addr(USER)[2:]+enc_uint(1)[2:]); r["quote_user_1"]=words(q)
    out[name]=r; print(name, json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0701-scan-triage-cand.json","w"), indent=1)
