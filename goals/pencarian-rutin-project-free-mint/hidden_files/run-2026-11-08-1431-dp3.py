import json, urllib.request, sys, base64
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
def enc_u(n): return format(n,'064x')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def single(addr, data):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=8, retries=0)
            if not isinstance(out,dict): continue
            if out.get("error"): return "ERR"
            r=out.get("result")
            if r is None: return None
            if r=="0x": return 0
            if r.startswith("0x") and len(r)<=66: return int(r,16)
            return r
        except Exception: continue
    return "ERR:all-fail"
def dec_str(r):
    if not isinstance(r,str) or not r.startswith("0x") or len(r)<130: return str(r)[:400]
    try:
        ln=int(r[66:130],16)
        b=bytes.fromhex(r[130:130+ln*2])
        return b.decode('utf-8','replace')
    except Exception as e: return f"decode-err {e}"
E='0xEB71a7cbF97e091beBE2175C48E350D1993a04c9'
print("EB71 mintOpen:", single(E, sel('mintOpen()')))
print("EB71 mintActive:", single(E, sel('mintActive()')))
print("EB71 contractURI:", dec_str(single(E, sel('contractURI()')))[:600])
print("EB71 MAX_FREE_SUPPLY:", single(E, sel('MAX_FREE_SUPPLY()')))
print("EB71 MAX_PAID_SUPPLY:", single(E, sel('MAX_PAID_SUPPLY()')))
print("EB71 MAX_MINTS_PER_WALLET:", single(E, sel('MAX_MINTS_PER_WALLET()')))
print("EB71 MAX_PER_WALLET:", single(E, sel('MAX_PER_WALLET()')))
# Dafeiyu ABI details
D='0xd8de64acb25a87d98f1e170bf082a01427772511'
url=f"https://sourcify.dev/server/v2/contract/56/{D}?fields=abi"
req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
d=json.load(urllib.request.urlopen(req, timeout=20))
for e in d.get("abi",[]):
    if e.get("type")=="function" and e.get("name") in ("freeAgentCount","freeAgent","priceFor","priceOf","poolOpened","openPool","remaining","isFreeEligible","isFreeAgent","mint"):
        print("Dafeiyu ABI",e.get("name"),"inputs:",[(i.get("type"),i.get("name")) for i in e.get("inputs",[])],"mutability:",e.get("stateMutability"))
print("Dafeiyu priceOf(1):", single(D, sel('priceOf(uint256)')+enc_u(1)))
print("Dafeiyu priceFor(1, user):", single(D, sel('priceFor(uint256,address)')+enc_u(1)+enc_addr(USER)))
print("Dafeiyu freeAgent(user):", single(D, sel('freeAgent(address)')+enc_addr(USER)))
# Undead contractURI decode (from deep log raw hex)
u_hex="0x00000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000121646174613a6170706c69636174696f6e2f6a736f6e3b6261736536342c65794a755957316c496a6f695657356b5a57466b4945354756484d694c434a6b5a584e6a636d6c7764476c7662694936496c56755a4756685a43424f526c527a4c6941314c4455314e5342776158686c6243427a6133567362484d6762323467516b35434c69424761584a7a644342746157353049475a795a57557549466736494768306448427a4f6938766543356a623230765657356b5a57466b546b5a5563794973496d563464475679626d46735833567962434936496d68306448427a4f6938766543356a623230765657356b5a57466b546b5a5563794973496e4e6c6247786c636c396d5a575666596d467a61584e6663473970626e527a496a6f784d444239"
s=dec_str(u_hex)
print("Undead contractURI decoded:", s[:500])
if s.startswith("data:application/json;base64,"):
    try:
        j=json.loads(base64.b64decode(s.split(",",1)[1]))
        print("Undead contractURI JSON keys:", list(j.keys()))
        print("Undead external_link/url:", j.get("external_link") or j.get("external_url"))
        print("Undead name/desc:", j.get("name"), str(j.get("description"))[:200])
    except Exception as e: print("Undead b64 decode err", e)
