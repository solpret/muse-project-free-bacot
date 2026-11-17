"""Follow-up checks run 1631: (a) AGMIN free-view revert nature + extra view names
+ Sourcify retry; (b) MYRA TRADE + AGMIN earlier-mint check before scan window.
Read-only."""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]

def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def raw_call(addr, data):
    """Direct urllib eth_call to see the raw JSON-RPC error (revert vs transport)."""
    import urllib.request, json as j
    body = j.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                    "params": [{"to": addr, "data": data}, "latest"]}).encode()
    last = None
    for ep in EPS:
        req = urllib.request.Request(ep, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return j.loads(resp.read().decode())
        except Exception as e:
            last = e
            time.sleep(2)
    return {"error": f"{type(last).__name__}: {str(last)[:200]}"}

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def sourcify_abi(address, tries=3):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
            time.sleep(3)
        except Exception as e:
            time.sleep(3)
    return ("error:retry-exhausted", None)

out = {}
AGMIN = "0x8670e99062ead2cE5402754aeDE769602FDf38b8"
MYRA = "0xEC234269297614ED73Db83103325cff68A40aE10"

# (a) raw revert check for AGMIN freeLeft()
r = raw_call(AGMIN, sel("freeLeft()"))
out["agmin_freeLeft_raw"] = r
r2 = raw_call(AGMIN, sel("freeCount()"))
out["agmin_freeCount_raw"] = r2
# extra view names via rpc_call
USER_PAD = USER[2:].lower().rjust(64, "0")
for sig, args in [("freeCount()", ""), ("canFreeMint(address)", USER_PAD),
                  ("freeMinted(address)", USER_PAD), ("mintPrice()", ""),
                  ("quoteMint(address,uint256)", USER_PAD + "01".rjust(64, "0"))]:
    try:
        o = rpc_call("eth_call", [{"to": AGMIN, "data": sel(sig) + args}, "latest"])
        out["agmin_" + sig] = dec_uint(o) if isinstance(o, str) else o
    except Exception as e:
        out["agmin_" + sig] = "error:" + type(e).__name__ + ":" + str(e)[:120]

# Sourcify retries
for addr, key in ((AGMIN, "agmin"), (MYRA, "myra")):
    status, abi = sourcify_abi(addr)
    free_funcs, mint_funcs = [], []
    if isinstance(abi, list):
        for item in abi:
            if item.get("type") != "function":
                continue
            nm = item.get("name", "")
            if "free" in nm.lower() and not nm.lower().startswith("freeze"):
                free_funcs.append(nm)
            if "mint" in nm.lower():
                mint_funcs.append(nm)
    out[key + "_sourcify_retry"] = status
    out[key + "_abi_free_funcs"] = sorted(set(free_funcs))
    out[key + "_abi_mint_funcs"] = sorted(set(mint_funcs))
    if isinstance(abi, list):
        out[key + "_abi_function_count"] = len([i for i in abi if i.get("type") == "function"])

# (b) earlier-mint check: Transfer-from-zero for each address, blocks 131780000..131794452
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
for addr, key in ((MYRA, "myra"), (AGMIN, "agmin")):
    total = 0
    earliest = None
    earliest_tx = None
    frm, to = 131780000, 131794452
    while frm <= to:
        chunk_to = min(frm + 1999, to)
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(chunk_to),
                  "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC], "address": addr}
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
            logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
            total += len(logs)
            for l in logs:
                b = int(l["blockNumber"], 16)
                if earliest is None or b < earliest:
                    earliest = b
                    earliest_tx = l.get("transactionHash")
        except Exception as e:
            out[key + "_earlier_mint_error"] = f"{frm}-{chunk_to}: {type(e).__name__}:{str(e)[:100]}"
            break
        frm = chunk_to + 1
        time.sleep(2.2)
    out[key + "_mints_before_131794453"] = total
    out[key + "_earliest_mint_block_before_window"] = earliest
    out[key + "_earliest_mint_tx_before_window"] = earliest_tx
    # did the contract exist at 131780000?
    try:
        code = rpc_call("eth_getCode", [addr, hex(131780000)])
        out[key + "_code_at_131780000_len"] = len(code) - 2 if isinstance(code, str) else None
    except Exception as e:
        out[key + "_code_at_131780000_len"] = "error:" + type(e).__name__

print(json.dumps(out, indent=1))
json.dump(out, open("run-2026-11-05-1631-followup.json", "w"), indent=1)
print("WROTE run-2026-11-05-1631-followup.json")
