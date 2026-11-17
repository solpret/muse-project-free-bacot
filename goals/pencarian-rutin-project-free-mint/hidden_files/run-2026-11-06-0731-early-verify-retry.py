import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-06-0731"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"00"*32
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed3.bnbchain.org/"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def ankr_logs(addr, frm, to):
    params={"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(to),"pageSize":1000,"decodeLogs":False,
            "topics":[TRANSFER, ZERO],"address":addr}
    body=ankr_post("ankr_getLogs", params, timeout=30)
    return body.get("result",{}).get("logs",[]) if isinstance(body,dict) else []
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def raw(to,data):
    for ep in EPS:
        try:
            out=_single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
            if not out or out=="0x": return None
            return int(out,16)
        except Exception: continue
    return None
def block_ts(blk):
    for ep in EPS:
        try:
            out=_single(ep,"eth_getBlockByNumber",[hex(blk),False],10,retries=0)
            return int(out["timestamp"],16) if out else None
        except Exception: continue
    return None
LEADS={
 "FOD Agent":("0xA3d24EE16b6b912192724598Da55C7909bBB97e8",131898649),
 "Unnamed-7972":("0x79720611065DF9Fc810399DC1eeE870b3A8AD3fC",131898146),
 "Unnamed-A193":("0xA193Ea677a39D4F04bB770555fe6954e0e00C02C",131899547),
}
out={}
for name,(addr,fb) in LEADS.items():
    earlier=0; failed=False; start=131880000
    while start < fb:
        end=min(start+1999, fb-1)
        try:
            logs=ankr_logs(addr, start, end)
            earlier+=len(logs)
        except Exception as e:
            print(name,"getLogs FAIL",start,end,repr(e),flush=True); failed=True; break
        start=end+1
        time.sleep(0.5)
    ts=block_ts(fb)
    import datetime
    wib=datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") if ts else None
    d={"address":addr,"first_block":fb,"earlier_mints_before_first_block":None if failed else earlier,
       "first_mint_verified":(not failed) and earlier==0,"first_mint_block_ts":ts,"first_mint_wib":wib}
    # state reads
    for sig in ["totalMinted()","totalSupply()","spotsLeft()","MAX_SUPPLY()","PRICE()","costOf(address,uint256)"]:
        args=enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001" if "costOf" in sig else (enc(USER) if "address" in sig else "")
        d[sig]=raw(addr, sel(sig)+args)
    d["mintedBy_user"]=raw(addr, sel("mintedBy(address)")+enc(USER))
    d["balanceOf_user"]=raw(addr, sel("balanceOf(address)")+enc(USER))
    d["quote_user_1"]=raw(addr, sel("quote(address,uint256)")+enc(USER)+"0000000000000000000000000000000000000000000000000000000000000001")
    out[name]=d
    print(name, json.dumps(d), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-early-verify-retry.json","w"), indent=1)
