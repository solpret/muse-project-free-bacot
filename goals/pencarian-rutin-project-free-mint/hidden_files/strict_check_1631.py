"""STRICT agent-shape check for first-seen contracts, run 2026-11-05 1631.
Read-only. Uses same RPC helpers as onchain_nft_scan.py (Ankr module import
for getLogs, dataseeds for eth_call/eth_getCode, Sourcify for ABI).
Agent-shaped ONLY if: registry bytes in eth_getCode (DIRECT) AND a free-mint
function / free-supply constant / free view that ACTUALLY RESPONDS.
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from eth_hash.auto import keccak

REGISTRY_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ZERO = "0x0000000000000000000000000000000000000000"
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

def call(addr, sig, args_hex=""):
    data = sel(sig) + args_hex
    out = rpc_call("eth_call", [{"to": addr, "data": data}, "latest"])
    return out

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_bool(out):
    v = dec_uint(out)
    return None if v is None else bool(v)

def dec_str(out):
    if not isinstance(out, str) or not out.startswith("0x"):
        return None
    try:
        raw = bytes.fromhex(out[2:])
    except Exception:
        return None
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64 + ln].decode("utf-8", "replace")
        except Exception:
            pass
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None

def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode())
            return ("verified", data.get("abi"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return ("not_verified", None)
        return (f"http_{e.code}", None)
    except Exception as e:
        return (f"error:{type(e).__name__}", None)

def ankr_logs(from_block, to_block, topics, address=None):
    params = {"blockchain": "bsc", "fromBlock": hex(from_block),
              "toBlock": hex(to_block), "pageSize": 1000, "decodeLogs": False,
              "topics": topics}
    if address:
        params["address"] = address
    body = ankr_post("ankr_getLogs", params, timeout=30)
    result = body.get("result", {}) if isinstance(body, dict) else {}
    return result.get("logs", [])

TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
TS_SINGLE = "0xc3d58168c5ae7397731d063d5bbf3d657854427343f4c083240f7aacaa2d0f62"
ZERO_TOPIC = "0x" + "00" * 32

FIRST_SEEN = [
    ("0x8670e99062ead2cE5402754aeDE769602FDf38b8", "ERC721", 7, 7, 131795711),
    ("0x201698e3CC6E64278686844B43FCe502d46DCe40", "ERC721", 1, 1, 131795438),
    ("0xEC234269297614ED73Db83103325cff68A40aE10", "ERC721", 1, 1, 131796453),
    ("0x7DB8cA2ee362C0bBC96818d714E0F5B5267274a9", "ERC1155", 1, 1, 131795444),
]

USER_PAD = USER[2:].lower().rjust(64, "0")
NOARG_VIEWS = ["totalSupply()", "MAX_SUPPLY()", "FREE_SUPPLY()", "FREE_PER_WALLET()",
               "freeLeft()", "freeRemaining()", "freeMinted()", "freeClaimed()",
               "freeSupply()", "freeUsed()", "mintOpen()", "freeOpen()",
               "totalMinted()", "maxSupply()", "MAX_MINT_PER_WALLET()"]
ADDR_VIEWS = ["balanceOf(address)", "freeClaimed(address)", "freeFor(address)",
              "mintedBy(address)", "freeMintedBy(address)", "freeMinted(address)"]
STR_VIEWS = ["name()", "symbol()", "contractURI()", "tokenURI(uint256)"]

results = []
for addr, kind, mints, minters, first_block in FIRST_SEEN:
    r = {"address": addr, "kind": kind, "scan_mint_count": mints,
         "scan_distinct_minters": minters, "scan_first_block": first_block}
    # 1. eth_getCode DIRECT
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        r["code_len"] = len(code) - 2 if isinstance(code, str) else None
        r["registry_bytes_direct"] = (REGISTRY_BYTES in code[2:].lower()) if isinstance(code, str) else None
    except Exception as e:
        r["registry_bytes_direct"] = None
        r["code_error"] = str(e)
    # 2. Sourcify retry
    status, abi = sourcify_abi(addr)
    r["sourcify"] = status
    free_funcs, mint_funcs, all_funcs = [], [], []
    if isinstance(abi, list):
        for item in abi:
            if item.get("type") != "function":
                continue
            nm = item.get("name", "")
            all_funcs.append(nm)
            if "free" in nm.lower() and not nm.lower().startswith("freeze"):
                free_funcs.append(nm)
            if "mint" in nm.lower():
                mint_funcs.append(nm)
    r["abi_free_funcs"] = sorted(set(free_funcs))
    r["abi_mint_funcs"] = sorted(set(mint_funcs))
    r["abi_function_count"] = len(all_funcs)
    # 3. Actually call free views (no-arg uint/bool)
    views = {}
    for sig in NOARG_VIEWS:
        try:
            out = call(addr, sig)
            v = dec_uint(out)
            views[sig] = v if v is not None else ("raw:" + str(out)[:40] if isinstance(out, str) else "noresp")
        except Exception as e:
            views[sig] = "error:" + type(e).__name__
    for sig in ADDR_VIEWS:
        try:
            out = call(addr, sig, USER_PAD)
            v = dec_uint(out)
            views[sig + "[user]"] = v if v is not None else ("raw:" + str(out)[:40] if isinstance(out, str) else "noresp")
        except Exception as e:
            views[sig + "[user]"] = "error:" + type(e).__name__
    r["views"] = views
    # 4. owner()
    try:
        out = call(addr, "owner()")
        r["owner"] = ("0x" + out[-40:]) if isinstance(out, str) and len(out) >= 42 else out
    except Exception as e:
        r["owner"] = "error:" + type(e).__name__
    # 5. name/symbol direct
    for sig, key in (("name()", "name"), ("symbol()", "symbol")):
        try:
            r[key] = dec_str(call(addr, sig))
        except Exception:
            r[key] = None
    # STRICT verdict
    responding_free = [k for k, v in views.items()
                       if isinstance(v, int) and ("free" in k.lower() or "FREE" in k)]
    r["responding_free_views"] = responding_free
    r["agent_shaped_strict"] = bool(r.get("registry_bytes_direct")) and bool(responding_free)
    results.append(r)
    print(json.dumps(r, indent=1))
    time.sleep(1)

# 6. First-mint verification for STRICT agent-shaped only
for r in results:
    if not r["agent_shaped_strict"]:
        continue
    addr = r["address"]
    fb = r["scan_first_block"]
    lo = max(0, fb - 2000)
    try:
        logs = ankr_logs(lo, fb + 50, [TRANSFER, ZERO_TOPIC], address=addr)
        # first Transfer from zero = mint
        if logs:
            first = min(logs, key=lambda l: (int(l["blockNumber"], 16), int(l.get("logIndex", "0x0"), 16)))
            r["first_mint_block"] = int(first["blockNumber"], 16)
            r["first_mint_tx"] = first.get("transactionHash")
            blk = rpc_call("eth_getBlockByNumber", [hex(int(first["blockNumber"], 16)), False])
            r["first_mint_timestamp"] = int(blk["timestamp"], 16) if blk else None
        else:
            r["first_mint_block"] = None
    except Exception as e:
        r["first_mint_error"] = str(e)

json.dump({"run": "2026-11-05-1631", "results": results},
          open("run-2026-11-05-1631-scan-firstseen.json", "w"), indent=1)
print("WROTE run-2026-11-05-1631-scan-firstseen.json")
