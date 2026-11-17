import json, urllib.request
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=6) as r: v=json.load(r)["result"]
            return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
addrs=["0x0d2CEc06cf73395404A9B87A5B23f4eE417ea90A","0x5DB4ea0Cb6E9B3109a09B9bBd5F35759167bEAeD","0xDE899991614529B2a63263809EFC4283EC682eE1","0xb0991558cbE0F31Bbfe6AeD9a39DaCe41aEA7f3B","0xbeB15f0d3472294B6A8C8D47CD05aE4AA57eE6B0","0x6ef09E4d535D8ec7897099789B35e3A4694d3541","0xc6A26eADD8f704A8851eeA7a14AeD1A39e1EFAd9","0x7483702c229151FBd80966Be1Df1aF67EeC426Ea","0xe71504018FF8260b43C98C64decB30E71ECf34eB","0xbE9d49e50E3D000c09262f4F5d99DB728Ad0A7F9","0x2014EDe1ba0094cf1788fEa32ACA2Aa606F8d908","0x784b551dA020A29416b54575Cde87A207A272DB3","0x4f63E878df8a8D5EAa99FD8BcEFA44f17b887777","0x7B1CC478deC30a14214a462e0e2f1DE1DC6A831a","0xfb60228E81F43d1fb8C255558a44669090ddF763","0xEAf930a21148e3B4456B5E8F24435F90f7C04905","0xC1CEbE1dE66Efdd0b415e5fbb5462469BB1b86ba","0xfc91976BE5B1f76A0513103c33e553d134Fc6De5","0x565417ea21019123B2d96DF25Ad941447EFb7777","0x39120A5a16F9f040e20b18465A3369b7D83ff38B"]
views=["totalSupply()","decimals()","freeClaimed()","FREE_SUPPLY()","freeMinted()","freeSharesRemaining()","agentRegistry()","freeLeft()"]
out={}
for a in addrs:
    out[a]={v: iv(call(a, sel(v))) for v in views}
    print(a, out[a])
json.dump(out, open("run-2026-11-04-0901-feedshape.json","w"), indent=1)
