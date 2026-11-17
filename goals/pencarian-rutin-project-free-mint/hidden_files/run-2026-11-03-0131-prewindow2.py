#!/usr/bin/env python3
import sys, json, datetime
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import get_logs
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"0"*64
out={}
for name,addr in [("Opera Agent","0x32ddd7d98bB711976cCfE19548Df52D0cdeC197c"),
                  ("Silk Agent","0xF888787f39dD5a5adCEC1b0d9833cF40a655c60e")]:
    all_logs=[]
    frm=131260000
    while frm<=131287525:
        to=min(frm+1999,131287525)
        try:
            res=get_logs(addr, frm, to, topics=[TRANSFER, ZERO])
            logs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
        except Exception as e:
            logs=[]; print(name, frm, to, "ERR", str(e)[:120])
        print(name, frm, to, "from-zero logs:", len(logs))
        all_logs.extend(logs)
        frm=to+1
    # window-range first mints
    try:
        res=get_logs(addr, 131287526, 131289525, topics=[TRANSFER, ZERO])
        wlogs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
    except Exception as e:
        wlogs=[]; print(name, "window ERR", str(e)[:120])
    print(name, "WINDOW from-zero logs:", len(wlogs))
    if wlogs:
        first=min(wlogs, key=lambda l: int(l["blockNumber"],16))
        blk=int(first["blockNumber"],16)
        print(name, "window first block:", blk, "tx:", first.get("transactionHash"))
        for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
            try:
                b=_single(ep,"eth_getBlockByNumber",[hex(blk),False],8,retries=0)
                ts=int(b["timestamp"],16)
                print(name, "window first WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat())
                break
            except Exception as e: print(" block err", str(e)[:100])
    if all_logs:
        first=min(all_logs, key=lambda l: int(l["blockNumber"],16))
        blk=int(first["blockNumber"],16)
        print(name, "PRE-WINDOW earliest block:", blk, "tx:", first.get("transactionHash"))
        for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
            try:
                b=_single(ep,"eth_getBlockByNumber",[hex(blk),False],8,retries=0)
                ts=int(b["timestamp"],16)
                print(name, "pre-window earliest WIB:", datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat())
                break
            except Exception as e: print(" block err", str(e)[:100])
    out[name]={"pre_window_count":len(all_logs),"window_count":len(wlogs)}
    json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0131-prewindow2.json","w"), indent=1)
print(json.dumps(out, indent=1))
