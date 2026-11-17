#!/usr/bin/env python3
"""Hot-leg 0554: RPC view probe for 20 new Sourcify feed contracts (read-only)."""
import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=8) as r: v=json.load(r)["result"]
            if v and v!="0x":
                # address-returning views: last 20 bytes if 32-byte word
                return v
            return None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
views=["totalSupply()","decimals()","freeClaimed()","freeMinted()","FREE_SUPPLY()","FREE_SLOTS()","mintOpen()","poolOpen()","freeSharesRemaining()","freeAvailable()"]
feed=["0x3c1d49451791eE8bE33FD766A879b4A79B9a06e5","0xC61B5c2c2399edAda510E4AB6782FBCAF892365E","0x05fE99a07be8455C907aD29B263094366a20503E","0x929CBBe57771d60B051916E95D415fFb20A15112","0x962250573775E920f5969d0613A4a1AA2Bc56677","0x25C833848b0c4fAEd5A1f2634743183989B16A66","0x31e79835D370D042a5c45c743f95e63E63Ed8356","0x2725aaa76033E609d2a71078beDD7c340AE2e8d2","0xE1eF6f4AcBfe2d257C135b644FA4bFdd498536e7","0x1C499b9Dd65E3cbfc854E52A5d7208e36F802083","0x10Bcfe1D7DC1416067caF371Eaf9A0Bf4B0a49eE","0xf768E56D779263235Ad235C5Cc0F729779406cc7","0xFFe8ED361Ce18E9fa7C418C39272E1d9186cfdda","0x602c42F4a82Ddb60cde5B35c609163B615D797b2","0x654461557A3CA8397EA21BA04A06a65bEC03b4Ba","0x662e144aFEF030E6e24236337c72FA3a53C15793","0x7555E67B932c4c8c7cb593B311D84E3eBcbc9CCc","0x3CCaDFFaFeb1F7fD24Ec7ab183B1D3A1E39fa73C","0xbC8CF31dd2E2f501587df0cfbA703E7298DB100e","0xB2DD7a694eb8F85b92074Cf8070E615a4E84766C"]
def probe(a):
    out={}
    for v in views: out[v]=iv(call(a,sel(v)))
    # agentRegistry address view
    raw=call(a,sel("agentRegistry()"))
    out["agentRegistry()"]=("0x"+raw[-40:]) if raw and len(raw)>=42 else None
    raw2=call(a,sel("registry()"))
    out["registry()"]=("0x"+raw2[-40:]) if raw2 and len(raw2)>=42 else None
    return a,out
res={}
with ThreadPoolExecutor(max_workers=10) as ex:
    for a,out in ex.map(probe,feed): res[a]=out; print(a,out)
json.dump(res,open("hot-leg-2026-11-04-0554-sourcify-shape.json","w"),indent=1)
