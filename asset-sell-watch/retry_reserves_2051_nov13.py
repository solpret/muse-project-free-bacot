#!/usr/bin/env python3
import json, time
from pending_check_2051_nov13 import rpc_batch, sel, u256, call
from eth_abi import decode

PAIRS = {
 "YYDS": "0xD15c928B7b777CaC7d613FE840C6eC3dE8e4EdDA",
 "币安加油": "0xc939e2b49eea548c4539e45b4e355c2b2aa464d6",
 "JINMA": "0xaa91fd1b1fc70888f5df17784720b752472e99da",
 "LUCKY777": "0x81afde1cddf0d277580b8e524361e0a7ea2983c6",
}
out = {}
for attempt in range(3):
    calls = [("eth_call", [{"to": p, "data": "0x" + sel("getReserves()")}, "latest"]) for p in PAIRS.values()]
    res, err = rpc_batch(calls, timeout=15)
    out["attempt"] = attempt + 1
    out["error"] = err
    done = {}
    for (sym, p), rh in zip(PAIRS.items(), res):
        if rh:
            try:
                r0, r1, _ = decode(["uint112","uint112","uint32"], bytes.fromhex(rh[2:]))
                done[sym] = [str(r0), str(r1)]
            except Exception as ex:
                done[sym] = {"error": str(ex)}
    out["reserves"] = done
    if len(done) == len(PAIRS):
        break
    time.sleep(5)

# retry failed sale-state probes
checks = {}
for label, addr, sig in [
    ("CHEEMSA_tradingOpen", "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2", "tradingOpen()"),
    ("PACTURE_launched", "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", "launched()"),
    ("PACTURE_phase", "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", "phase()"),
]:
    try:
        h = call(addr, "0x" + sel(sig))
        checks[label] = u256(h) if h else None
    except Exception as ex:
        checks[label] = "error: " + str(ex)
out["sale_state_checks"] = checks
print(json.dumps(out, indent=1))
