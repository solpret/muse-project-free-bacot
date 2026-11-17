#!/usr/bin/env python3
"""Run 85: full verification of the NEW 27-wallet paid token 0x2717... (SIZE ANOMALY:
typical buy ~0.23 BNB vs machine-token norm ~0.000114 BNB). Read-only eth_call +
Ankr topic-filtered logs + sent-tx aggregates + Sourcify grep. No preview/mint/sign/login."""
import json, sys, time, datetime, re, urllib.request
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

FROM, TO = 132041620, 132047945
TOKEN = "0x2717a156b86c3c8894bb2dea9a34c514e8fc7777"
OLD_MACHINE = {
    "CORLA 0x4a9c": "0x4a9c499574ea003846e81522d59aa4c27ca47777",
    "CORLA-97af": "0x97af0d7e9b5c1d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7",  # placeholder, replaced below if known
    "GrokBot 0xfcd0": "0xfcd04501ebaddcda73095a75e078a8e5292f7777",
    "run80 0x489e": "0x489e0000000000000000000000000000000000007777",
    "run81 0x7f7a": "0x7f7a0000000000000000000000000000000000007777",
    "run81 0x33f7": "0x33f70000000000000000000000000000000000007777",
    "run82 0xd468": "0xd4680000000000000000000000000000000000007777",
    "run82 0xa6e6": "0xa6e60000000000000000000000000000000000007777",
    "run82 0x887c": "0x887c0000000000000000000000000000000000007777",
}
# real old-machine addresses are read from run82-paid.json keys instead (see below)
tier = json.load(open(Path.home() / "workspace/narrative-pulse/tier-ab-watch-state.json"))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
uniq = []
for w in list(tier["wallets"].keys()) + feed:
    if w.lower() not in uniq: uniq.append(w.lower())
tracked_padded = {"0x" + "0" * 24 + w[2:] for w in uniq}
paid85 = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run85-paid.json"))
sent = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run85-sent.json"))
tx_by_hash = {}
for w, r in sent["results"].items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        tx_by_hash[t["hash"].lower()] = (w, t)

out = {}
out[TOKEN] = {
    "name": read_str(TOKEN, "name()"),
    "symbol": read_str(TOKEN, "symbol()"),
    "decimals": read_uint(TOKEN, "decimals()"),
    "totalSupply": read_uint(TOKEN, "totalSupply()"),
    "owner": read_addr(TOKEN, "owner()"),
}
print(TOKEN, out[TOKEN], flush=True)

# Ankr topic-filtered Transfer-to-tracked logs for the token
try:
    data = ankr_mod.get_logs(TOKEN, FROM, TO, topics=[T_TRANSFER, None, sorted(tracked_padded)])
    logs = ((data.get("result") or {}).get("logs") or [])
    print(TOKEN, "ankr topic-filtered Transfer-to-tracked logs:", len(logs), flush=True)
    out[TOKEN]["tracked_transfer_log_count"] = len(logs)
    if logs:
        ls = sorted(logs, key=lambda l: (int(l.get("blockNumber","0x0"),16), int(l.get("logIndex","0x0"),16)))
        first = ls[0]
        ftx = first.get("transactionHash")
        print("  first:", ftx, "block", int(first.get("blockNumber","0x0"),16),
              "from", first.get("topics")[1], "amount_raw", int(first.get("data","0x0"),16), flush=True)
        out[TOKEN]["first_tracked_transfer_tx"] = ftx
        out[TOKEN]["first_tracked_transfer_block"] = int(first.get("blockNumber","0x0"),16)
        out[TOKEN]["first_tracked_transfer_from"] = first.get("topics")[1]
        out[TOKEN]["first_tracked_transfer_amount_raw"] = int(first.get("data","0x0"),16)
        wtx = tx_by_hash.get((ftx or "").lower())
        if wtx:
            w, txd = wtx
            print("  first tx: wallet", w[:12], "value_bnb", int(txd.get("value","0x0"),16)/1e18, "sel", txd.get("input_prefix"), "time", txd.get("time_wib"), flush=True)
            out[TOKEN]["first_tx_wallet"] = w
            out[TOKEN]["first_tx_value_bnb"] = int(txd.get("value","0x0"),16)/1e18
            out[TOKEN]["first_tx_selector"] = txd.get("input_prefix")
            out[TOKEN]["first_tx_time_wib"] = txd.get("time_wib")
        pair = "0x" + first.get("topics")[1][-40:]
        t0 = read_addr(pair, "token0()")
        t1 = read_addr(pair, "token1()")
        print(TOKEN, "pair", pair, "token0", t0, "token1", t1, flush=True)
        out[TOKEN]["pair"] = pair
        out[TOKEN]["pair_token0"] = t0
        out[TOKEN]["pair_token1"] = t1
        # reserves
        rr = call(pair, sel4("getReserves()"))
        if isinstance(rr, str) and not rr.startswith("ERROR") and len(rr) >= 130:
            r0 = int(rr[2:66], 16); r1 = int(rr[66:130], 16)
            out[TOKEN]["pair_reserves_raw"] = [r0, r1]
            print("  reserves raw:", r0, r1, flush=True)
        else:
            out[TOKEN]["pair_reserves_raw"] = f"unreadable({str(rr)[:80]})"
            print("  reserves unreadable:", str(rr)[:80], flush=True)
except Exception as e:
    print(TOKEN, "ankr ERROR", e, flush=True)
    out[TOKEN]["ankr_error"] = str(e)[:200]

# buy-size stats for this token from partial receipts (Transfer of token -> tracked wallet)
part = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run85-receipts-partial.json"))
vals = []
sells = 0
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
vals_sorted = sorted(vals)
n = len(vals)
out[TOKEN]["buy_tx_count"] = n
out[TOKEN]["buy_value_bnb_total"] = round(sum(vals), 6)
out[TOKEN]["buy_value_bnb_min"] = vals_sorted[0] if n else None
out[TOKEN]["buy_value_bnb_median"] = vals_sorted[n//2] if n else None
out[TOKEN]["buy_value_bnb_max"] = vals_sorted[-1] if n else None
out[TOKEN]["buy_value_bnb_mode"] = max(set(vals), key=vals.count) if n else None
out[TOKEN]["sell_transfer_count_from_tracked"] = sells
print(f"buys of token: n={n} total={sum(vals):.4f} BNB min={vals_sorted[0] if n else None} median={vals_sorted[n//2] if n else None} max={vals_sorted[-1] if n else None} sells_from_tracked={sells}", flush=True)

# old machine tokens: wallets this run (from run85-paid.json + run82 paid for addresses)
old = {}
for label, addr in OLD_MACHINE.items():
    if "00000000000000000000000000000000000000" in addr: continue
    old[label] = len(paid85.get(addr.lower(), []))
# run80/81/82 token addresses from state machine_tokens
state = json.load(open(Path.home() / "workspace/narrative-pulse/tracked-wallet-mint-scan-state.json"))
for mt in state.get("machine_tokens", []):
    a = mt.get("contract", "")
    old[f"machine {a[:6]}"] = len(paid85.get(a.lower(), []))
print("OLD MACHINE TOKENS this run:", old, flush=True)
out["old_machine_wallets"] = old

# 27-set identity: overlap of this token's wallets with run82 tokens' wallets
MACHINE27 = set(paid85[TOKEN])
print("machine27 set size:", len(MACHINE27), flush=True)
try:
    paid82 = json.load(open(Path.home() / "workspace/narrative-pulse/scan-runs/run82-paid.json"))
    prev = set()
    for k in ["0xd4680000000000000000000000000000000000007777"]:
        pass
    # run82 paid keys are full addresses; take the union of all 27-wallet tokens from run82
    for k, v in paid82.items():
        if len(v) >= 20: prev |= set(v)
    print("overlap with run82 >=20-wallet token sets:", len(MACHINE27 & prev), "of", len(MACHINE27), flush=True)
    out["overlap_run82_big_sets"] = len(MACHINE27 & prev)
except Exception as e:
    print("overlap check error:", e, flush=True)

BUY = sel4("swapExactETHForTokensSupportingFeeOnTransferTokens(address[],address,uint256)")
SELL = sel4("swapExactTokensForETHSupportingFeeOnTransferTokens(uint256,uint256,address[],address,uint256)")
APPR = sel4("approve(address,uint256)")
buys = sells_n = appr = deploys = 0
buy_value_wei = 0
for w, r in sent["results"].items():
    if not r.get("ok"): continue
    for t in r["in_window"]:
        if w.lower() not in MACHINE27: continue
        s = t.get("input_prefix")
        if s == BUY:
            buys += 1; buy_value_wei += int(t.get("value","0x0"),16)
        elif s == SELL:
            sells_n += 1
        elif s == APPR:
            appr += 1
        if t.get("to") is None:
            deploys += 1
print(f"27-set window totals: buys={buys} buy_value_bnb={buy_value_wei/1e18:.4f} sells={sells_n} approves={appr} deployments={deploys}", flush=True)
out["machine27_window_totals"] = {"buys": buys, "buy_value_bnb": buy_value_wei/1e18, "sells": sells_n, "approves": appr, "deployments": deploys}

# Sourcify grep (same pattern as pointer scripts)
entry = {}
for fields in ("sources", "abi"):
    url = f"https://sourcify.dev/server/v2/contract/56/{TOKEN}?fields={fields}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Muse-scan/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode(errors="replace")
        urls = sorted(set(re.findall(r'https?://[A-Za-z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+', body)))
        fns = sorted(set(re.findall(r'\b(?:website|siteURL|siteUrl|domain|external(?:_url|Url|Link)?)\b', body)))
        entry[f"sourcify_{fields}"] = {"http_status": resp.status, "body_len": len(body), "urls_found": urls[:30], "site_fn_words": fns}
    except Exception as e:
        entry[f"sourcify_{fields}"] = {"error": str(e)[:300]}
    time.sleep(2)
print("sourcify:", json.dumps(entry)[:1500], flush=True)
out[TOKEN]["sourcify"] = entry

json.dump(out, open(Path.home() / "workspace/narrative-pulse/scan-runs/run85-token-verify.json", "w"), indent=1)
print("saved run85-token-verify.json", flush=True)
