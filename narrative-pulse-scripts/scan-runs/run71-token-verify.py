#!/usr/bin/env python3
"""Run 71: verify the NEW 27-wallet paid tokens (read-only eth_call + Ankr
topic-filtered Transfer logs + sent-tx aggregates). No preview/mint/sign/login."""
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
TOKENS = ["0xe51bf2d65277348d637aa2f5da0c469fcbe37777",
          "0xc2e1817850a53f79c86945aa693164d966e67777",
          "0x578532b4d613d63fafcf6e469ce5447cb8fa7777",
          "0xfff4f02e8dd452b24583440d5def001d34357777",
          "0xe4c99e2cd10284d549c040369a775ff7f3f47777",
          "0x25b466a9fff9292b863b2449facd9dc570b07777"]
OLD_MACHINE = {
    "CORLA 0x4a9c": "0x4a9c499574ea003846e81522d59aa4c27ca47777",
    "GrokBot 0xfcd0": "0xfcd04501ebaddcda73095a75e078a8e5292f7777",
    "ASI q1 0x7526": "0x7526782e635c2f4f9d63a7d4736194158d937777",
    "ASI q1 0x3e61": "0x3e612ed93b07239efc7db9da05ff07b7ad6f7777",
    "ASI q1 0x455e": "0x455e2e30de81c25ec7788d6c08431dbfc2b77777",
    "ASI q1 0x729a": "0x729a625d9649bbe2802d2cbb4d4ba6c1bb477777",
    "ASI q2 0xa77c": "0xa77c4d2a395dd4d7d51696edf5a9cc7f730b7777",
    "ASI q2 0xcf06": "0xcf060b7d5007a11bf71007f745df3e79b98c7777",
    "ASI q2 0xfd80": "0xfd800ac441efabb02d4059131a135b38d9c37777",
    "ASI q2 0x5c5a": "0x5c5aaafbc9ef01511eace8ab28a22808d2667777",
    "run66 0x19b7": "0x19b7fd3ae4234e4e632ff0b0f01f62a5340d7777",
    "run66 0x540d": "0x540df48115f469c4083ba7a6d03255ea5f6f7777",
    "run68 0xf3cc": "0xf3cc932cb9abd4351264ffd707b0c52fa2b57777",
    "run68 0xe7e2": "0xe7e2497b88e52bd9d96a56c3a792bb5bea227777",
    "run69 0x4d15": "0x4d15f82596c44040c17181d5670f36a5c9807777",
    "run70 0x4df7": "0x4df70606906311ea68dc75034a8ef45ffa547777",
    "run70 0xae06": "0xae060d25764a93b1e873ca6e1678bf38c8127777",
    "run70 0x2516": "0x25167807d55c4faf1b87990c268e1510bb057777",
    "run70 0x1247": "0x1247be8f13c178e663aa6971ee7d8847bb1a7777",
    "run70 0x8e0d": "0x8e0dacb670d5e2ba527b7b128ac2a395b03a7777",
}
tier = json.load(open(Path.home() / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
paid69 = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run71-paid.json"))
sent = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run71-sent.json"))
tx_by_hash = {}
for w, r in sent["results"].items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        tx_by_hash[t["hash"].lower()] = (w, t)

out = {}
for t in TOKENS:
    out[t] = {
        "name": read_str(t, "name()"),
        "symbol": read_str(t, "symbol()"),
        "decimals": read_uint(t, "decimals()"),
        "totalSupply": read_uint(t, "totalSupply()"),
        "owner": read_addr(t, "owner()"),
    }
    print(t, out[t], flush=True)

for t in TOKENS:
    try:
        data = ankr_mod.get_logs(t, FROM, TO, topics=[T_TRANSFER, None, sorted(tracked_padded)])
        logs = ((data.get("result") or {}).get("logs") or [])
        print(t, "ankr topic-filtered Transfer-to-tracked logs:", len(logs), flush=True)
        out[t]["tracked_transfer_log_count"] = len(logs)
        if logs:
            logs_sorted = sorted(logs, key=lambda l: (int(l.get("blockNumber","0x0"),16), int(l.get("logIndex","0x0"),16)))
            first = logs_sorted[0]
            ftx = first.get("transactionHash")
            print("  first:", ftx, "block", int(first.get("blockNumber","0x0"),16),
                  "from", first.get("topics")[1], "amount_raw", int(first.get("data","0x0"),16), flush=True)
            out[t]["first_tracked_transfer_tx"] = ftx
            out[t]["first_tracked_transfer_block"] = int(first.get("blockNumber","0x0"),16)
            out[t]["first_tracked_transfer_from"] = first.get("topics")[1]
            out[t]["first_tracked_transfer_amount_raw"] = int(first.get("data","0x0"),16)
            wtx = tx_by_hash.get((ftx or "").lower())
            if wtx:
                w, txd = wtx
                print("  first tx: wallet", w[:12], "value_wei", int(txd.get("value","0x0"),16),
                      "value_bnb", int(txd.get("value","0x0"),16)/1e18, "sel", txd.get("input_prefix"),
                      "time", txd.get("time_wib"), flush=True)
                out[t]["first_tx_wallet"] = w
                out[t]["first_tx_value_bnb"] = int(txd.get("value","0x0"),16)/1e18
                out[t]["first_tx_selector"] = txd.get("input_prefix")
                out[t]["first_tx_time_wib"] = txd.get("time_wib")
    except Exception as e:
        print(t, "ankr ERROR", e, flush=True)

for t in TOKENS:
    pair_padded = out[t].get("first_tracked_transfer_from")
    if not pair_padded or not pair_padded.startswith("0x"):
        continue
    pair = "0x" + pair_padded[-40:]
    t0 = read_addr(pair, "token0()")
    t1 = read_addr(pair, "token1()")
    print(t, "pair", pair, "token0", t0, "token1", t1, flush=True)
    out[t]["pair"] = pair
    out[t]["pair_token0"] = t0
    out[t]["pair_token1"] = t1

# old machine tokens: 0 wallets this run?
print("OLD MACHINE TOKENS this run:", flush=True)
for label, addr in OLD_MACHINE.items():
    print(f"  {label}: {len(paid69.get(addr.lower(), []))} wallets", flush=True)
    out.setdefault("old_machine_wallets", {})[label] = len(paid69.get(addr.lower(), []))

# 27-set aggregates over sent txs
MACHINE27 = set(paid69["0xe51bf2d65277348d637aa2f5da0c469fcbe37777"])  # a 27-wallet set of run 71 (five 27-tokens share it; 26-token is a subset - verified below)
print("machine27 set size:", len(MACHINE27), flush=True)
BUY = "0xb6f9de95"  # literal: swapExactETHForTokensSupportingFeeOnTransferTokens on PCS router (sel4 of the 3-arg form hashes to 0x79d836d2 - wrong, run-69 bug)
SELL = "0x791ac947"  # literal: swapExactTokensForETHSupportingFeeOnTransferTokens
APPR = sel4("approve(address,uint256)")
buys = sells = appr = deploys = 0
buy_value_wei = 0
for w, r in sent["results"].items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        if w.lower() not in MACHINE27: continue
        s = t.get("input_prefix")
        if s == BUY:
            buys += 1
            buy_value_wei += int(t.get("value","0x0"),16)
        elif s == SELL:
            sells += 1
        elif s == APPR:
            appr += 1
        if t.get("to") is None:
            deploys += 1
print(f"27-set window totals: buys={buys} buy_value_bnb={buy_value_wei/1e18:.4f} sells={sells} approves={appr} deployments={deploys}", flush=True)
out["machine27_window_totals"] = {"buys": buys, "buy_value_bnb": buy_value_wei/1e18,
                                   "sells": sells, "approves": appr, "deployments": deploys}
# which wallets deployed contracts this run
dep_wallets = {}
for w, r in sent["results"].items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        if t.get("to") is None:
            dep_wallets.setdefault(w, []).append(t["hash"])
print("deployment wallets:", {w[:12]: len(v) for w, v in dep_wallets.items()}, flush=True)
out["deployment_wallets"] = {w: len(v) for w, v in dep_wallets.items()}
out["deployment_hashes"] = dep_wallets

json.dump(out, open(Path.home() / "workspace/narrative-pulse/scan-runs/run71-token-verify.json", "w"), indent=1)
print("saved run71-token-verify.json", flush=True)
