#!/usr/bin/env python3
"""DAGENT website + first-mint walk-back probe (read-only).
- baseURI() + tokenURI(1) via fast_rpc race, direct-curl fallback.
- Ankr getLogs walk-back: Transfer logs for the contract over
  132425000-132435149 (before observed first mint 132435150); any
  Transfer from 0x0 there would disprove first-mint-at-132435150.
Writes backfill-triage-132433882-132436704-walkback.json.
"""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6"
ANKR = "/home/hatch/workspace/custom-connectors/custom.ankr/bin/ankr.py"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_uint(n):
    return format(int(n), "064x")

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def eth_call_race(data):
    try:
        r = race("eth_call", [{"to": ADDR, "data": data}, "latest"])
        if isinstance(r, dict) and "error" in r:
            return {"error": str(r["error"])[:200]}
        return {"result": r}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:200]}"}

def eth_call_curl(data):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": ADDR, "data": data}, "latest"]})
    for url in ["https://bsc-dataseed.binance.org/",
                "https://bsc-dataseed1.bnbchain.org/"]:
        try:
            r = subprocess.run(["curl", "-s", "-m", "20", "-X", "POST",
                                "-H", "Content-Type: application/json",
                                "-d", payload, url],
                               capture_output=True, text=True, timeout=30)
            d = json.loads(r.stdout)
            if "result" in d:
                return {"via": url, "result": d["result"]}
        except Exception:
            continue
    return {"error": "direct-curl failed"}

def call_str(sig, args=None):
    data = "0x" + sel(sig)
    for a in (args or []):
        data += enc_uint(a)
    r = eth_call_race(data)
    if "error" in r:
        r2 = eth_call_curl(data)
        if "result" in r2:
            return {"fn": sig, "value": dec_str(r2["result"]), "via": "direct-curl"}
        return {"fn": sig, "error": r["error"], "curl_error": r2.get("error")}
    return {"fn": sig, "value": dec_str(r["result"]), "via": "race"}

def ankr_logs(frm, to):
    try:
        r = subprocess.run(["python3", ANKR, "logs", ADDR, str(frm), str(to)],
                           capture_output=True, text=True, timeout=120)
        out = r.stdout.strip()
        try:
            d = json.loads(out)
        except Exception:
            return {"from": frm, "to": to, "error": f"non-json rc={r.returncode}: {out[:300]}"}
        return {"from": frm, "to": to, "raw": d}
    except Exception as e:
        return {"from": frm, "to": to, "error": f"{type(e).__name__}: {e}"}

def main():
    out = {"address": ADDR, "observed_first_block": 132435150}
    out["baseURI"] = call_str("baseURI()")
    out["tokenURI(1)"] = call_str("tokenURI(uint256)", [1])
    # walk-back: any Transfer (mint = from 0x0) before 132435150?
    zero = "0x0000000000000000000000000000000000000000000000000000000000000000"
    transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    total_mint_logs = 0
    ranges = []
    for frm, to in [(132425000, 132430000), (132430001, 132435149)]:
        res = ankr_logs(frm, to)
        logs = []
        if "raw" in res:
            raw = res["raw"]
            if isinstance(raw, dict):
                logs = raw.get("logs", raw.get("result", []))
            elif isinstance(raw, list):
                logs = raw
        mint_logs = [l for l in logs if isinstance(l, dict)
                     and str(l.get("topics", [""])[0]).lower() == transfer_topic
                     and len(l.get("topics", [])) > 1
                     and str(l["topics"][1]).lower() == zero]
        total_mint_logs += len(mint_logs)
        ranges.append({"from": frm, "to": to, "logs_returned": len(logs),
                       "mint_from_zero": len(mint_logs),
                       "error": res.get("error")})
    out["walkback_ranges"] = ranges
    out["walkback_mint_before_first_block"] = total_mint_logs
    out["first_mint_confirmed"] = (total_mint_logs == 0)
    json.dump(out, open(f"{BASE}/backfill-triage-132433882-132436704-walkback.json", "w"), indent=1)
    print(json.dumps(out, indent=1)[:3000])
    print("WROTE backfill-triage-132433882-132436704-walkback.json")

if __name__ == "__main__":
    main()
