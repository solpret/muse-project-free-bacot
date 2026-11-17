import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from Crypto.Hash import keccak
from ankr import ankr_post
ADDR="0x1a904Da7ebBE7708D79d52DB594A73EbB7d2875B"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc.publicnode.com/","https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","mintPrice()","balanceOf(address)","freeClaimed(address)","owner()","name()","symbol()","AGENT_ID()","agentRegistry()","isFree()","FREE_HASH()"]
calls=[]; keys=[]
for sig in VIEWS:
    base=sig.split("(")[0]
    if "(address)" in sig:
        calls.append(("eth_call",[{"to":ADDR,"data":sel(sig)+enc(USER)},"latest"])); keys.append(base+"_user")
    else:
        calls.append(("eth_call",[{"to":ADDR,"data":sel(sig)},"latest"])); keys.append(base)
out={}
for ep in EPS:
    try:
        res=batch(calls, endpoint=ep, timeout=10)
        out={k:to_int(v) for k,v in zip(keys,res)}
        print("endpoint ok:", ep); break
    except Exception as e:
        print("endpoint fail:", ep, str(e)[:100])
# name/symbol are strings - decode raw
for ep in EPS:
    try:
        res=batch([("eth_call",[{"to":ADDR,"data":sel("name()")},"latest"]),("eth_call",[{"to":ADDR,"data":sel("symbol()")},"latest"]),("eth_call",[{"to":ADDR,"data":sel("owner()")},"latest"])], endpoint=ep, timeout=10)
        def dec(h):
            try:
                b=bytes.fromhex(h[2:])
                ln=int.from_bytes(b[64:96],"big")
                return b[96:96+ln].decode()
            except Exception: return None
        out["name_str"]=dec(res[0]); out["symbol_str"]=dec(res[1])
        out["owner_raw"]=res[2]
        print("name/symbol/owner ok:", ep); break
    except Exception as e:
        print("name fail:", ep, str(e)[:100])
print(json.dumps(out, indent=1, default=str))
# first mint: chunked ankr getLogs Transfer from 0x0, from block 132300000
ZERO="0x0000000000000000000000000000000000000000000000000000000000000000"
topic0="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def logs(frm,to):
    body=ankr_post("ankr_getLogs", {"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"address":ADDR,"topics":[topic0, ZERO]})
    r=body.get("result",{})
    if isinstance(r,dict): return r.get("logs",[])
    return r if isinstance(r,list) else []
all_logs=[]
frm=132300000
head=None
for ep in EPS:
    try:
        head=int(batch([("eth_blockNumber",[])], endpoint=ep, timeout=10)[0],16); break
    except Exception: pass
print("head:", head)
cur=frm
while cur<=head:
    nxt=min(cur+999, head)
    try:
        ls=logs(cur,nxt)
        if ls:
            all_logs.extend(ls)
            print(f"logs {cur}-{nxt}: {len(ls)}")
    except Exception as e:
        print(f"logs {cur}-{nxt} FAIL:", str(e)[:120])
    cur=nxt+1
print("total first-mint logs from 132300000:", len(all_logs))
if all_logs:
    first=all_logs[0]
    fb=int(first["blockNumber"],16)
    print("first mint block:", fb, "tx:", first.get("transactionHash"))
    # block timestamp via fast_rpc
    for ep in EPS:
        try:
            b=batch([("eth_getBlockByNumber",[hex(fb), False])], endpoint=ep, timeout=10)
            ts=int(b[0]["timestamp"],16)
            import datetime
            print("first mint time WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S"))
            break
        except Exception as e:
            print("block ts fail:", ep, str(e)[:80])
json.dump({"views":out,"first_mint_logs":len(all_logs),"first_block": (int(all_logs[0]["blockNumber"],16) if all_logs else None),"head":head}, open("run-2026-11-08-0931-oink1a90.json","w"), indent=1)
