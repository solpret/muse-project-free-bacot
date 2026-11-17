import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=6) as r: j=json.load(r)
            v=j.get("result")
            return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
tests=[("name()",""),("symbol()",""),("decimals()",""),("totalSupply()",""),("FREE_SUPPLY()",""),("FREE_SLOTS()",""),("FREE_AMOUNT()",""),("freeMinted()",""),("freeClaimed(address)",u),("freeClaimed()",""),("freeLeft(address)",u),("freeSharesRemaining()",""),("freeSharesClaimed()",""),("freeUsed(address)",u),("mintedBy(address)",u),("quote(address,uint256)",u+one),("registry()",""),("agentRegistry()",""),("contractURI()",""),("tokenURI(uint256)","0"*63+"1")]
addrs=['0xcBc9C217519d81303c4234750a68dBeC11867C51','0x507591b0657662575220b36361C7EBc4cD547Fd6','0xf211260D38dAB42734614352077791A1602346Ea','0x72b2e3d4D09A44A3C678Db3C8Ab09745082DA983','0xfBef0BC8a786D85EBB136D3Ff6BDdb14dDfdA74c','0xD9CC8C95dA13B0600DF1b3f6879A1892a0631392','0x1D4611A83FE8342Ab74C54D2D9C9D263Cc4cBb5B','0x79918BbA97Ba688103DC050B99C191831CCe213B','0xC5660C835EdE3AA94900aC842F59be6749374ACc','0x0dF71FF8CE792987b1f3F446c0cd6e09d4cC3313','0x3Fc6d0F17A79536e417C95624ee7cC5C2C78f785','0x605955F90e0D750E2c69a19FD9083F25c2cA8461','0xf23E21526093fd1246b32d4a666592A163916B6B','0x23F62961789385C162834FD2c70E42CCF3ca1BBf','0xc91355a8a20bf9C24fc5c98d7E7c2CC724D1fa40','0x8988b730a60e9fD05D6EAcc81F14EA8Cb029bB8a','0xD4dF49D311702Bf16d461265A9881001273b6174','0x88dDe91A7FA9Dd48e0954bB741bCe563Bd2Be807','0x0bE7062530D7f4e9005c4c21Ce4723d21a834C61','0x885C46C7638009Ea5EE000410C95c183B2abE34A']
def shape(a):
    out={}
    for name,arg in tests:
        v=call(a,sel(name)+arg)
        if v is not None:
            if name in ("registry()","agentRegistry()","contractURI()","tokenURI(uint256)"): out[name]=v
            elif name in ("name()","symbol()"):
                try: out[name]=bytes.fromhex(v[2:]).decode('utf-8','ignore').strip('\x00')
                except Exception: out[name]=v
            else: out[name]=iv(v)
    return out
res={}
with ThreadPoolExecutor(max_workers=15) as ex:
    for a,out in zip(addrs, ex.map(shape,addrs)):
        res[a]=out; print("SHAPE",a,out,flush=True)
json.dump(res,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/hot-leg-2026-11-04-2319-shape.json","w"),indent=1)
print("DONE")
