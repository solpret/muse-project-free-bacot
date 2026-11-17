#!/usr/bin/env python3
"""Run 86: LIGHT verification of the TWO new high-wallet paid tokens
0x2bfb... (27 wallets) and 0xc459... (26 wallets) — machine-token fast-path
check: name/symbol empty? decimals/totalSupply? buy-size stats vs class norm?
No free-mint path already established by receipts pass (0 mint logs).
Read-only eth_call + Ankr topic-filtered logs. No preview/mint/sign/login."""
import json, sys, time, datetime
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
        return bytes.fromhex(r[194:194 + ln * 2]).decode("utf-8", "replace")
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

FROM, TO = 132054228, 132061861
TOKENS = ["0x889a76e4d48169d0398828a36c57b64298577777",
          "0x42491efdffe0aea61799d12b79cfe6ad2a977777"]
tier = json.load(open(Path.home() / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
sent = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run87-sent.json"))
tx_by_hash = {}
for w, r in sent["results"].items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        tx_by_hash[t["hash"].lower()] = (w, t)
part = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run87-receipts-partial.json"))
paid86 = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run87-paid.json"))

out = {}
for TOKEN in TOKENS:
    e = {
        "name": read_str(TOKEN, "name()"),
        "symbol": read_str(TOKEN, "symbol()"),
        "decimals": read_uint(TOKEN, "decimals()"),
        "totalSupply": read_uint(TOKEN, "totalSupply()"),
        "owner": read_addr(TOKEN, "owner()"),
        "wallets": len(paid86.get(TOKEN, [])),
    }
    print(TOKEN, e, flush=True)
    try:
        data = ankr_mod.get_logs(TOKEN, FROM, TO, topics=[T_TRANSFER, None, sorted(tracked_padded)])
        logs = ((data.get("result") or {}).get("logs") or [])
        e["tracked_transfer_log_count"] = len(logs)
        print(f"  ankr topic-filtered Transfer-to-tracked logs: {len(logs)}", flush=True)
        if logs:
            ls = sorted(logs, key=lambda l: (int(l.get("blockNumber","0x0"),16), int(l.get("logIndex","0x0"),16)))
            first = ls[0]
            ftx = first.get("transactionHash")
            e["first_tracked_transfer_tx"] = ftx
            e["first_tracked_transfer_block"] = int(first.get("blockNumber","0x0"),16)
            e["first_tracked_transfer_from"] = first.get("topics")[1]
            e["first_tracked_transfer_amount_raw"] = int(first.get("data","0x0"),16)
            wtx = tx_by_hash.get((ftx or "").lower())
            if wtx:
                w, txd = wtx
                e["first_tx_wallet"] = w
                e["first_tx_value_bnb"] = int(txd.get("value","0x0"),16)/1e18
                e["first_tx_selector"] = txd.get("input_prefix")
                e["first_tx_time_wib"] = txd.get("time_wib")
                print(f"  first: {ftx[:14]} block {e['first_tracked_transfer_block']} from-pair {first.get('topics')[1][:12]} wallet {w[:12]} value {e['first_tx_value_bnb']} sel {txd.get('input_prefix')} time {txd.get('time_wib')}", flush=True)
            pair = "0x" + first.get("topics")[1][-40:]
            t0 = read_addr(pair, "token0()")
            t1 = read_addr(pair, "token1()")
            e["pair"] = pair; e["pair_token0"] = t0; e["pair_token1"] = t1
            print(f"  pair {pair} token0 {t0} token1 {t1}", flush=True)
            rr = call(pair, sel4("getReserves()"))
            if isinstance(rr, str) and not rr.startswith("ERROR") and len(rr) >= 130:
                r0 = int(rr[2:66], 16); r1 = int(rr[66:130], 16)
                e["pair_reserves_raw"] = [r0, r1]
                print(f"  reserves raw: {r0} {r1}", flush=True)
            else:
                e["pair_reserves_raw"] = f"unreadable({str(rr)[:80]})"
    except Exception as ex:
        print(f"  ankr ERROR {ex}", flush=True)
        e["ankr_error"] = str(ex)[:200]
    vals, sells = [], 0
    for h, rec in part.items():
        if not isinstance(rec, dict): continue
        for lg in rec.get("logs") or []:
            t = lg.get("topics") or []
            if not t or t[0] != T_TRANSFER or len(t) < 3: continue
            if (lg.get("address") or "").lower() != TOKEN: continue
            if t[2] in tracked_padded:
                st = tx_by_hash.get(h.lower())
                if st: vals.append(int(st[1].get("value","0x0"),16)/1e18)
            elif t[1] in tracked_padded:
                sells += 1
    vs = sorted(vals); n = len(vs)
    e["buy_tx_count"] = n
    e["buy_value_bnb_total"] = round(sum(vals), 6)
    e["buy_value_bnb_min"] = vs[0] if n else None
    e["buy_value_bnb_median"] = vs[n//2] if n else None
    e["buy_value_bnb_max"] = vs[-1] if n else None
    e["sell_transfer_count_from_tracked"] = sells
    print(f"  buys: n={n} total={sum(vals):.4f} min={vs[0] if n else None} median={vs[n//2] if n else None} max={vs[-1] if n else None} sells_from_tracked={sells}", flush=True)
    out[TOKEN] = e
    time.sleep(1)

# old machine tokens this run
state = json.load(open(Path.home() / "workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"))
old = {}
for mt in state.get("machine_tokens", []):
    a = mt.get("contract", "")
    old[f"machine {a[:6]}"] = len(paid86.get(a.lower(), []))
old["GrokBot 0xfcd0"] = len(paid86.get("0xfcd04501ebaddcda73095a75e078a8e5292f7777", []))
old["CORLA 0x4a9c"] = len(paid86.get("0x4a9c499574ea003846e81522d59aa4c27ca47777", []))
print("OLD MACHINE TOKENS this run:", old, flush=True)
out["old_machine_wallets"] = old
json.dump(out, open(Path.home() / "workspace/narrative-pulse/scan-runs/run87-token-verify.json", "w"), indent=1)
print("saved run87-token-verify.json", flush=True)
