#!/usr/bin/env python3
"""Run 71: detail-verify the NEW 0x2325 mint-pattern contract 0x93bf08d2...
(read-only eth_call + Ankr topic-filtered Transfer logs + sent-tx aggregates).
No preview/mint/sign/login."""
import json, sys, time, datetime, re
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.ankr/bin"))
import fast_rpc
import ankr as ankr_mod
from Crypto.Hash import keccak

def topic(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()
T_TRANSFER = topic("Transfer(address,address,uint256)")
ZERO_PAD = "0x" + "0" * 64
jak = datetime.timezone(datetime.timedelta(hours=7))

def call(addr, data):
    try:
        return fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"])
    except Exception as e:
        return f"ERROR:{e}"

def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def read_str(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR") or len(r) < 130:
        return f"unreadable({str(r)[:60]})"
    try:
        ln = int(r[130:194], 16)
        raw = bytes.fromhex(r[194:194 + ln * 2])
        return raw.decode("utf-8", "replace")
    except Exception as e:
        return f"decode-error {e}"

def read_uint(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR"):
        return f"unreadable({str(r)[:60]})"
    try:
        return int(r, 16)
    except Exception:
        return f"raw:{r[:80]}"

def read_addr(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR"):
        return f"unreadable({str(r)[:60]})"
    try:
        return "0x" + r[-40:]
    except Exception:
        return f"raw:{r[:80]}"

FROM, TO = 131910706, 131926119
CTR = "0x93bf08d2936aefe0cd2ceba8f76cb566fdf9e1c9"
TX = "0xa20c70c177541d76b369f296640231bc45a578163aff03fcf8048e513d19db95"
WALLET = "0x2325f175975abdbcde555c79cc8e63381d28551b"

out = {
    "name": read_str(CTR, "name()"),
    "symbol": read_str(CTR, "symbol()"),
    "decimals": read_uint(CTR, "decimals()"),
    "totalSupply": read_uint(CTR, "totalSupply()"),
    "owner": read_addr(CTR, "owner()"),
}
print(CTR, out, flush=True)

# snapshot + bridge presence
snap = open(Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files/onchain-snapshot.json").read()
print("in_free_bacot_snapshot:", CTR.lower() in snap.lower(), flush=True)
bridge = json.load(open(Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files/scan-bridge.json"))
print("in_bridge:", CTR.lower() in bridge["contracts"], flush=True)

# topic-filtered Transfer logs to tracked wallets for this contract
tier = json.load(open(Path.home() / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
try:
    data = ankr_mod.get_logs(CTR, FROM, TO, topics=[T_TRANSFER, None, sorted(tracked_padded)])
    logs = ((data.get("result") or {}).get("logs") or [])
    print("ankr topic-filtered Transfer-to-tracked logs:", len(logs), flush=True)
    out["tracked_transfer_log_count"] = len(logs)
    for lg in sorted(logs, key=lambda l: (int(l.get("blockNumber","0x0"),16), int(l.get("logIndex","0x0"),16))):
        print("  log block", int(lg.get("blockNumber","0x0"),16), "tx", lg.get("transactionHash"),
              "from", lg.get("topics")[1], "to", lg.get("topics")[2],
              "amount_raw", int(lg.get("data","0x0"),16), flush=True)
    out["tracked_transfer_logs"] = [
        {"block": int(lg.get("blockNumber","0x0"),16), "tx": lg.get("transactionHash"),
         "from": lg.get("topics")[1], "to": lg.get("topics")[2],
         "amount_raw": int(lg.get("data","0x0"),16)} for lg in logs]
except Exception as e:
    print("ankr ERROR", e, flush=True)
    out["tracked_transfer_log_count"] = f"ERROR {e}"

# zero-from Transfer logs for this contract (any recipient)
try:
    data = ankr_mod.get_logs(CTR, FROM, TO, topics=[T_TRANSFER, ZERO_PAD, None])
    logs = ((data.get("result") or {}).get("logs") or [])
    print("ankr zero-from Transfer logs (any recipient):", len(logs), flush=True)
    out["zero_from_log_count"] = len(logs)
    recips = sorted({"0x" + (lg.get("topics")[2] or "")[-40:] for lg in logs if len(lg.get("topics") or []) >= 3})
    print("  recipients:", recips, flush=True)
    out["zero_from_recipients"] = recips
except Exception as e:
    print("ankr zero-from ERROR", e, flush=True)

# the finding tx itself
sent = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run71-sent.json"))
for w, r in sent["results"].items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        if t["hash"].lower() == TX.lower():
            print("finding tx:", w, "value_bnb", int(t["value"],16)/1e18, "sel", t["input_prefix"],
                  "block", t["block"], "time", t["time_wib"], flush=True)
            out["finding_tx"] = {"wallet": w, "value_bnb": int(t["value"],16)/1e18,
                                 "selector": t["input_prefix"], "block": t["block"], "time_wib": t["time_wib"]}
# all 0x2325 txs this window (context)
r2325 = sent["results"].get(WALLET, {})
print("0x2325 txs this window:", len(r2325.get("in_window", [])), flush=True)
for t in r2325.get("in_window", []):
    print("  ", t["hash"][:14], t["input_prefix"], "value_bnb", int(t["value"],16)/1e18, t["time_wib"], flush=True)

# AFeng repeat tracker txs (same contract as run 70) - amounts
rc = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run71-receipts.json"))
for h, v in rc.items():
    if v.get("mint_logs"):
        for ml in v["mint_logs"]:
            if ml["contract"].lower() == "0x636fdfa9bc3db42c690c09e87b9017d05b36c743":
                print("AFeng tracker mint:", h[:14], v["wallet"][:10], "value_bnb",
                      int(v["value"],16)/1e18, v["time_wib"], "amount_raw", int(ml["data"],16), flush=True)

json.dump(out, open(Path.home() / "workspace/narrative-pulse/scan-runs/run71-detail-93bf.json", "w"), indent=1)
print("saved run71-detail-93bf.json", flush=True)
