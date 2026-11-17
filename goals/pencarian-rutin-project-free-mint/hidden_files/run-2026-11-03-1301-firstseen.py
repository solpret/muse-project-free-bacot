import sys, json, subprocess
sys.path.insert(0,"/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
sys.path.insert(0,"/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from onchain_nft_scan import rpc_call
from ankr import ankr_post
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return k.hexdigest()[:8]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; pad=USER[2:].rjust(64,'0')
def call(addr,sig,args=""):
    try:
        r=rpc_call("eth_call",[{"to":addr,"data":"0x"+sel(sig)+args},"latest"])
        if isinstance(r,str) and len(r)==66: return int(r,16)
        if isinstance(r,str) and len(r)==130: return "0x"+r[-40:]
        return r
    except Exception as e: return f"ERR:{type(e).__name__}"
TOP={"Drakogent":"0x87ca3c6704A08B56DC4e173315e948761EA2EB0C","Astragent":"0x3D8d32959F93d77B359d2c1674CB75Bb73306FA0","Orbitagent":"0x8E2831e922F9669A2203cb6B608dD7ccbc58299e"}
for name,addr in TOP.items():
    try:
        body=ankr_post("ankr_getLogs",{"blockchain":"bsc","fromBlock":hex(131300000),"toBlock":hex(131380258),"address":addr,"pageSize":1000,"decodeLogs":False},timeout=60)
        logs=body.get("result",{}).get("logs",[])
        earliest=min((int(l["blockNumber"],16) for l in logs),default=None)
        print(name,"pre-window logs(131300000-131380258):",len(logs),"earliest:",earliest,flush=True)
    except Exception as e: print(name,"ankr ERR",type(e).__name__,str(e)[:150],flush=True)
    vals={}
    for sig,args in [("totalSupply()",""),("freeClaimed()",""),("FREE_SUPPLY()",""),("mintOpen()",""),("mintedBy(address)",pad),("freeUsed(address)",pad),("balanceOf(address)",pad),("owner()",""),("quote(address,uint256)",pad+"0"*63+"1")]:
        vals[sig]=call(addr,sig,args)
    print(name,vals,flush=True)
REST=["0xB7Bb926572a1dC6de79f43a6c9B6d64bf4898829","0x2AB50B83a089E235BC1757fC689CcF0a609cf133","0xEFc3a126025C0888033726eD60F01c16860624A7","0x49E5a2f0E24152bC08a47D8DF24D3069f9e6e44A","0x5A11f1Ee9E48F88CDe418699F7C8aEbC7fc9F5bf","0x8E9dC38a2982Aeb747d2c7c8071D7c562d111875","0xD4b9E531B1FC43d031c4BB9b31c3BbcF944164D4","0xbc86C20aC9942d0Db0E96aeA373E8d64f4eB43ef","0xb951c29dB2E6c924dC5Cf193eDAC113376Ee34dD","0xB3b21Fa5429Baff99CBcb32ededB90b96b0AdCaD","0x5a75AA38f4E48c55af1b0f06F0B72C29B7A6E476","0xE3b1D32e43Ce8d658368e2CBFF95D57Ef39Be8a6"]
for addr in REST:
    try:
        raw=subprocess.run(["curl","-sL","--max-time","20",f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],capture_output=True,text=True).stdout
        d=json.loads(raw); abi=d.get('abi',[])
        fns=sorted({f['name'] for f in abi if f.get('type')=='function'})
        free=[f for f in fns if 'free' in f.lower() and not f.lower().startswith('freeze')]
        print(addr,"abi_fns",len(fns),"agent:",('AGENT_ID' in fns),"free:",free,"mint:",[f for f in fns if 'mint' in f.lower()],flush=True)
    except Exception as e: print(addr,"ABI ERR",type(e).__name__,str(e)[:120],flush=True)
