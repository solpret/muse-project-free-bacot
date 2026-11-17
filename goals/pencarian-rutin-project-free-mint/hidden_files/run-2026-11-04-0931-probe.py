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
def dec(v):
    if not v: return None
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[64:96],'big'); return b[96:96+ln].decode(errors='ignore')
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0")
addrs={
 "BRIDGE_Monke":"0xd06518ea638cab567328ccd7b67e43a119c275e0","BRIDGE_Ore":"0x7b48474d25431dfad4337735a0a2e57b63573abb",
 "BRIDGE_ETHBack":"0x53ba295180ae4b730f9b2a031f77c1bcdb009509","BRIDGE_Ikigai":"0x76437a85b768bb5612e8a466e492d89d8ef634b1",
 "BRIDGE_Unver262":"0x775ee7b19c6aedc50598284f4da64c69f9ce69dd","BRIDGE_AGC":"0x63dea5acdbe1f27c968907d08610a5f0a0284ba6",
 "BRIDGE_Obscura":"0x44a6c3b3769d7526eabe1f5e631dbd35a7a7874c",
 "FEED_0":"0xB78c5A470ba8a37CD6F533485aCfFa4b9Cf14B59","FEED_1":"0x6B1BeB07D6cbd0A72cD904962AE6EaE261770A0f",
 "FEED_2":"0x4587aBb377E95d69b86a44d3eFf4BFeB430A7777","FEED_3":"0x7fBaE4001E8d85883B4781d114076f8179389C43",
 "FEED_4":"0xa6Ca72004777FE6452c98cd658734E58f85C5a90","FEED_5":"0xFA75C8314ef2f7a7d96B69d09919c62E716810af",
 "FEED_6":"0x1A93C0E0E922876166615D9cB33e682AEC8c650A","FEED_7":"0x90361581D9Df642dEF496d1f64376a93A4932aFC",
 "FEED_8":"0x53E7602E2CbAE677b3a4E56Fe7212e0E7D19A9be","FEED_9":"0xD047562bD12Eb459964551477903710A1d8E25eE",
 "FEED_10":"0xCE648e11906D793DF647f0851f1Eac08dB687777","FEED_11":"0x2017Ab674C69EBB1EAA8Eb05bcD7a72Edac01630",
 "FEED_12":"0x545A12090624C95fb96ef9a4cE9B60E58BE98ee9","FEED_13":"0xe0DEB1A792EeBD9cbA7Fd74B70A283Bfa2630771",
 "FEED_14":"0xb07ce968eea65375DF54dc68BF9f16BB92a0E636","FEED_15":"0x5574bA84eCb30e561747C74a988a3962044fD691",
 "FEED_16":"0xE6D3A485d82ac9BDbEF350c1158A568c5eFa371b","FEED_17":"0x3E25C4ceC8C43ADE9f0699a8E25C6734B315d31e",
 "FEED_18":"0xb489c398aaC594318bD8c6CDFa84A3656a6D2180","FEED_19":"0x3e2fE9F2a406D6Ef7270ebB563350b70d6857777",
 "FEED_20":"0xAEA9b066e3FC6F767BBb60f41C18E4239C6447E9","FEED_21":"0x731671b47236A2492bA673CdcD3d0351c61bCbc0",
 "FEED_22":"0x6E6a298c669A8a01B65FFAbFD74aEa52F39Df9bC","FEED_23":"0x8D1151Be37c1Be46740768F0b8443CA59433a95E",
 "FEED_24":"0xDF00Cb0086C88E0ae8a82F3F59c00dB5a28dAe0c","FEED_25":"0x0d2CEc06cf73395404A9B87A5B23f4eE417ea90A",
 "FEED_26":"0x5DB4ea0Cb6E9B3109a09B9bBd5F35759167bEAeD","FEED_27":"0xDE899991614529B2a63263809EFC4283EC682eE1",
 "FEED_28":"0xb0991558cbE0F31Bbfe6AeD9a39DaCe41aEA7f3B","FEED_29":"0xbeB15f0d3472294B6A8C8D47CD05aE4AA57eE6B0"}
out={}
for name,a in addrs.items():
    r={"name":dec(call(a,sel("name()"))),"symbol":dec(call(a,sel("symbol()"))),
       "totalSupply":iv(call(a,sel("totalSupply()"))),"freeClaimed":iv(call(a,sel("freeClaimed()"))),
       "FREE_SUPPLY":iv(call(a,sel("FREE_SUPPLY()"))),"freeMinted":iv(call(a,sel("freeMinted()"))),
       "totalFreeMinted":iv(call(a,sel("totalFreeMinted()"))),"freeSharesRemaining":iv(call(a,sel("freeSharesRemaining()"))),
       "agentRegistry":call(a,sel("agentRegistry()")),"balanceOf_user":iv(call(a,sel("balanceOf(address)")+u))}
    out[name]=r; print(name,a,r,flush=True)
json.dump(out,open("run-2026-11-04-0931-probe.json","w"),indent=1)
print("DONE")
