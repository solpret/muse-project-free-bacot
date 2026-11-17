import sys, json
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import get_logs
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO="0x"+"0"*64
cands={
 "Cryptlichor":"0xb792Bf600DF37EB7638fb16434E813FC0c90C3C8",
 "Gondolux":"0xD37aF310F2Da74c8baBe301F2A8F8494f40e0C14",
 "Gachagent":"0xE23d1DC8F47f6a56F436d73c52862f40F26e9D39",
}
out={}
for name,addr in cands.items():
    all_logs=[]
    # pre-window walk 131270000..131283647 in <=2000-block chunks
    frm=131270000
    while frm<=131283647:
        to=min(frm+1999,131283647)
        try:
            res=get_logs(addr, frm, to, topics=[TRANSFER, ZERO])
            logs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
        except Exception as e:
            logs=[]; print(name, frm, to, "ERR", str(e)[:120])
        print(name, frm, to, "from-zero logs:", len(logs))
        all_logs.extend(logs)
        frm=to+1
    # also window-range first mints for reference
    try:
        res=get_logs(addr, 131283648, 131285647, topics=[TRANSFER, ZERO])
        wlogs=res.get("result",{}).get("logs",[]) if isinstance(res,dict) else []
    except Exception as e:
        wlogs=[]; print(name, "window ERR", str(e)[:120])
    print(name, "WINDOW from-zero logs:", len(wlogs))
    if wlogs:
        first=wlogs[0]
        print(name, "window first block:", int(first.get("blockNumber","0x0"),16), "tx:", first.get("transactionHash"), "ts:", first.get("timestamp"))
    out[name]={"pre_window_count":len(all_logs),
               "pre_window_first": (all_logs[0] if all_logs else None),
               "window_count":len(wlogs),
               "window_first": (wlogs[0] if wlogs else None)}
    # save raw first logs only to keep file small
    json.dump(out, open("run-2026-11-03-0101-prewindow.json","w"), indent=1)
print(json.dumps({k:{"pre":v["pre_window_count"],"win":v["window_count"]} for k,v in out.items()}, indent=1))
