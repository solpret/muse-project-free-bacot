#!/usr/bin/env python3
"""Parent deep-verify for BA 0xE3a382B8e577A58A5540420C11ABa287C62e49f4 (run 2231).
Read-only: retry None views + first-mint search via Ankr getLogs (address-filtered)."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from Crypto.Hash import keccak

BA = "0xE3a382B8e577A58A5540420C11ABa287C62e49f4"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
OUT = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-2231-ba-deep.json"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def raw(to, data):
    for rpc in ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
                "https://bsc-dataseed.binance.org/", "https://bsc-dataseed2.bnbchain.org/"]:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None

def as_int(v):
    if isinstance(v, str) and v.startswith("0x"):
        try: return int(v, 16)
        except Exception: return v
    return v

def dec_str(v):
    """Decode ABI string return (offset,len,bytes) to text or None."""
    if not isinstance(v, str) or not v.startswith("0x") or len(v) < 130: return None
    try:
        ln = int(v[66:130], 16)
        raw_b = bytes.fromhex(v[130:130 + ln * 2])
        return raw_b.decode("utf-8", "replace")
    except Exception:
        return None

res = {}
for sig in ["agentRegistry()", "AGENT_REGISTRY()", "PRICE()", "mintOpen()",
            "totalSupply()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
            "spotsLeft()", "MAX_PER_WALLET()", "MAX_FREE_PER_WALLET()"]:
    res[sig] = as_int(raw(BA, sel(sig)))
res["quote(user,1)"] = as_int(raw(BA, sel("quote(address,uint256)") + USER[2:].lower().rjust(64, "0") + format(1, "064x")))
res["freeClaimed(user)"] = as_int(raw(BA, sel("freeClaimed(address)") + USER[2:].lower().rjust(64, "0")))
res["mintedBy(user)"] = as_int(raw(BA, sel("mintedBy(address)") + USER[2:].lower().rjust(64, "0")))
res["freeUsed(user)"] = as_int(raw(BA, sel("freeUsed(address)") + USER[2:].lower().rjust(64, "0")))
res["canFreeMint(user)"] = as_int(raw(BA, sel("canFreeMint(address)") + USER[2:].lower().rjust(64, "0")))
res["contractURI"] = dec_str(raw(BA, sel("contractURI()")))
res["name"] = dec_str(raw(BA, sel("name()")))
res["symbol"] = dec_str(raw(BA, sel("symbol()")))
print(json.dumps(res, indent=1), flush=True)

# First-mint search: Ankr getLogs, address-filtered, Transfer from zero, chunked backwards.
def ankr_logs(from_b, to_b):
    params = {"blockchain": "bsc", "fromBlock": hex(from_b), "toBlock": hex(to_b),
              "address": BA.lower(),
              "topics": [TRANSFER, ZERO_TOPIC]}
    body = ankr_post("ankr_getLogs", params, timeout=30)
    logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
    return logs

first_block = None
hi = 131842544
lo = 131840908
# binary-ish search: walk back in 2000-block chunks from hi
cur_hi = hi
tries = 0
while cur_hi > 131830000 and tries < 8:
    cur_lo = max(cur_hi - 1999, 131830000)
    try:
        logs = ankr_logs(cur_lo, cur_hi)
    except Exception as e:
        print("ankr error", cur_lo, cur_hi, e, flush=True)
        res.setdefault("ankr_errors", []).append(str(e))
        break
    print("chunk", cur_lo, cur_hi, "logs:", len(logs), flush=True)
    if logs:
        first_block = min(int(l["blockNumber"], 16) for l in logs)
        res["first_mint_block_in_chunk"] = first_block
        res["first_mint_chunk"] = [cur_lo, cur_hi]
        res["mints_in_chunk"] = len(logs)
        break
    cur_hi = cur_lo - 1
    tries += 1
    time.sleep(1)

if first_block:
    # block timestamp via eth_getBlockByNumber
    for rpc in ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                               "params": [hex(first_block), False]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            ts = int(out["result"]["timestamp"], 16)
            res["first_mint_block"] = first_block
            res["first_mint_ts"] = ts
            import datetime
            res["first_mint_wib"] = datetime.datetime.fromtimestamp(
                ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
            print("first mint:", res["first_mint_wib"], "block", first_block, flush=True)
            break
        except Exception as e:
            continue
json.dump(res, open(OUT, "w"), indent=1)
print("WROTE", OUT, flush=True)
