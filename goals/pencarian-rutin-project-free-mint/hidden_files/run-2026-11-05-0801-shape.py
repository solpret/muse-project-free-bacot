import json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak
EPS=["https://bsc-dataseed.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc.publicnode.com"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def call(to,data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    for ep in EPS:
        try:
            req=urllib.request.Request(ep,data=p,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=10) as r: j=json.load(r)
            v=j.get("result"); return v if v and v!="0x" else None
        except Exception: continue
    return None
def iv(v):
    try: return int(v,16) if v else None
    except Exception: return None
def dec_str(v):
    try:
        b=bytes.fromhex(v[2:]); ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
    except Exception: return None
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u=USER[2:].lower().rjust(64,"0"); one="0"*63+"1"
feed=['0xc3834d0B19Fb787B59d6e4EF4e302e6F682Aa653', '0x24Ff4D5471A36E89aA3bC487EF1a435720C355eE', '0x88B2c13Be2Bf9FC7E333b02730C34613d4234DEf', '0x078FdeadC9BebE38cDA3703CeDb1Ea4319A57f2C', '0x62bb6C682Ac6a41ec96FF063aC0920f3bC21b4b7', '0xF7f4069eE0e5ff0dDC65894f6BDF40Fe6FffE842', '0x690429b9bf1DC310a2DFc0A24e0c9D2d46CaBFc0', '0x2d46bF45f5eCC12d84a30f502eBa855160971E0C', '0xB4D6De64abA94B66fE968b6521c977656548bc94', '0xD066Dcfc387974bA668D4C6AfaF412402B37A6Ba', '0xB3b55717Bac12585C30fE6B653E2C928B6BFCD89', '0xFe908513149782C364c6f912a7552Bf016603ab5', '0x6aB5568b45fa3b854a2e92BE8219AE91A5c09B95', '0x514B00308441a64A9a5Ba09f0681cE79d784E23E', '0x28e419746c87A0fFC8d94C8c407c77c8FFd77E5d', '0xE8AD8898294d4d0b769DaF7226ffC85c81E68d6f', '0x6d00e5cDd94377914Ae143131dB35E3622788466', '0x1989058Da9eb7F36E69779fCda0EA04578528570', '0x8D0feD5C69D0aF2d84e0dC3C1f995498656E37b0', '0x86C470486C8e5fA61E83578Da1B6FfB791a48e96']
def shape(a):
    o={}
    o['name']=dec_str(call(a,sel("name()"))); o['symbol']=dec_str(call(a,sel("symbol()")))
    o['decimals']=iv(call(a,sel("decimals()"))); o['totalSupply']=iv(call(a,sel("totalSupply()")))
    o['freeMinted']=iv(call(a,sel("freeMinted()"))); o['freeClaimed_total']=iv(call(a,sel("freeClaimed()")))
    o['FREE_SUPPLY']=iv(call(a,sel("FREE_SUPPLY()"))); o['FREE_SLOTS']=iv(call(a,sel("FREE_SLOTS()")))
    o['freeClaimed_user']=iv(call(a,sel("freeClaimed(address)")+u)); o['freeMinted_user']=iv(call(a,sel("freeMinted(address)")+u))
    o['quote_user1']=iv(call(a,sel("quote(address,uint256)")+u+one))
    o['agentRegistry']=call(a,sel("agentRegistry()")); o['registry']=call(a,sel("registry()"))
    o['freeSharesRemaining']=iv(call(a,sel("freeSharesRemaining()"))); o['freeAvailable']=iv(call(a,sel("freeAvailable()")))
    return o
out={}
with ThreadPoolExecutor(max_workers=20) as ex:
    for a,o in zip(feed, ex.map(shape, feed)): out[a]=o; print("SHAPE",a,o,flush=True)
json.dump(out,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0801-sourcify-shape.json","w"),indent=1)
# retry reread failures
retry={}
retry['NIULAI_phase']=iv(call("0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",sel("phase()")))
retry['DROID_totalMinted']=iv(call("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",sel("totalMinted()")))
retry['IMARS_freeMinted']=iv(call("0x64a3BaD89AbFFD6F30f086cE90CCB951D3Db432f",sel("freeMinted()")))
print("RETRY",retry)
json.dump(retry,open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0801-retry.json","w"),indent=1)
print("DONE")
