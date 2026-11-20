#!/usr/bin/env python3
"""CAP7 user slot + sale timing reads. freeClaimed takes agentId (uint256)."""
import json, sys, subprocess, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_u(n): return "%064x" % n
def batch_chunk(chunk, timeout=15):
    payload = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(chunk)]
    body = json.dumps(payload).encode()
    last = None
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                outp = json.loads(r.read().decode())
            if not isinstance(outp, list):
                raise IOError(f"non-list: {str(outp)[:150]}")
            res = []
            by_id = {it["id"]: it for it in outp if isinstance(it, dict)}
            for i in range(len(chunk)):
                it = by_id.get(i+1, {})
                if "result" in it and it["result"] not in (None, "0x"):
                    res.append(it["result"])
                else: res.append(None)
            return res, ep
        except Exception as e:
            last = e; continue
    raise IOError(f"batch failed: {last}")
# step 1: agentIdOf(user) + saleStart + phase + registry + constants
calls1 = [
    (ADDR, "0x" + sel("agentIdOf(address)") + enc_addr(USER)),
    (ADDR, "0x" + sel("saleStart()")),
    (ADDR, "0x" + sel("phase()")),
    (ADDR, "0x" + sel("registry()")),
    (ADDR, "0x" + sel("MAX_PAID_PER_ID()")),
    (ADDR, "0x" + sel("MAX_UNITS_PER_TX()")),
    (ADDR, "0x" + sel("PAID_SHARES()")),
    (ADDR, "0x" + sel("TOTAL_SHARES()")),
]
labels1 = ["agentIdOf_user","saleStart","phase","registry","MAX_PAID_PER_ID","MAX_UNITS_PER_TX","PAID_SHARES","TOTAL_SHARES"]
res1, ep = batch_chunk(calls1)
out = {"endpoint": ep}
def to_int(h):
    if h is None: return None
    try: return int(h, 16)
    except Exception: return h
vals = {}
for lab, v in zip(labels1, res1):
    vals[lab] = v
# agentIdOf returns (uint256, bool) = 64 bytes
aid_raw = vals["agentIdOf_user"]
agent_id, has_id = None, None
if aid_raw and len(aid_raw) >= 130:
    agent_id = int(aid_raw[2:66], 16)
    has_id = int(aid_raw[66:130], 16) == 1
out["agentIdOf_user_raw"] = aid_raw
out["agent_id"] = agent_id
out["has_agent_id"] = has_id
for lab in ["saleStart","phase","MAX_PAID_PER_ID","MAX_UNITS_PER_TX","PAID_SHARES","TOTAL_SHARES"]:
    out[lab] = to_int(vals[lab])
reg = vals["registry"]
out["registry"] = ("0x" + reg[-40:]) if reg else None
out["registry_is_agent_registry"] = (out["registry"] or "").lower() == REGISTRY.lower()
# step 2: freeClaimed(agentId) + paidById(agentId) + paidOf(user) + pot/trading
calls2 = []
labels2 = []
if agent_id is not None:
    calls2.append((ADDR, "0x" + sel("freeClaimed(uint256)") + enc_u(agent_id))); labels2.append("freeClaimed_agentId")
    calls2.append((ADDR, "0x" + sel("paidById(uint256)") + enc_u(agent_id))); labels2.append("paidById_agentId")
calls2 += [
    (ADDR, "0x" + sel("paidOf(address)") + enc_addr(USER)),
    (ADDR, "0x" + sel("potBnb()")),
    (ADDR, "0x" + sel("poolTokensTaken()")),
    (ADDR, "0x" + sel("tradingOpen()")),
    (ADDR, "0x" + sel("POOL_TOKENS()")),
    (ADDR, "0x" + sel("SALE_WINDOW()")),
    (ADDR, "0x" + sel("TOTAL_SUPPLY()")),
    (ADDR, "0x" + sel("TREASURY_BPS()")),
]
labels2 += ["paidOf_user","potBnb","poolTokensTaken","tradingOpen","POOL_TOKENS","SALE_WINDOW","TOTAL_SUPPLY","TREASURY_BPS"]
res2, ep2 = batch_chunk(calls2)
out["endpoint2"] = ep2
for lab, v in zip(labels2, res2):
    out[lab] = to_int(v)
# block
r = subprocess.run(["curl","-s","--max-time","15",ep,"-H","Content-Type: application/json",
    "-d", json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])],
    capture_output=True, timeout=20)
out["block"] = int(json.loads(r.stdout.decode())[0]["result"], 16)
# saleStart -> WIB
import datetime
ss = out.get("saleStart")
if isinstance(ss, int) and ss:
    out["saleStart_wib"] = datetime.datetime.fromtimestamp(ss, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    out["saleStart_age_hours_at_0931"] = round((datetime.datetime(2026,11,17,9,31, tzinfo=datetime.timezone(datetime.timedelta(hours=7))).timestamp() - ss)/3600, 2)
json.dump(out, open(f"{HF}/run-2026-11-17-0931-cap7-slot.json", "w"), indent=1)
print(json.dumps(out, indent=1))
