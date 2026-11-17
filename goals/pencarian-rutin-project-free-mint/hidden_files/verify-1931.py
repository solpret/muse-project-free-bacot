"""Leg 2 run 1931 on-chain verification (read-only).
Probes free-mint views + first-mint windows for Boltbook leg findings.
Uses bsc-dataseed eth_call (fast_rpc._single) and Ankr getLogs (ankr_post).
Ankr via proxy env (never set no_proxy for rpc.ankr.com).
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def rpc_call(method, params, timeout=12):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def call(addr, sig, args=""):
    try:
        o = rpc_call("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"])
        return o
    except Exception as e:
        return f"ERR:{type(e).__name__}:{str(e)[:120]}"

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_str(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 130:
        return None
    try:
        b = bytes.fromhex(out[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

USER_PAD = USER[2:].lower().rjust(64, "0")
ONE_PAD = "01".rjust(64, "0")

NOARG_UINT = ["totalSupply()", "freeLeft()", "freeClaimed()", "freeSupply()",
              "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "costOf()",
              "mintPrice()", "price()", "sharesSold()", "freeUsed()",
              "freeMinted()", "launched()", "freeSharePoolExhausted()"]
NOARG_STR = ["name()", "symbol()"]
USER_UINT = [("freeOf(address,uint256)", USER_PAD + ONE_PAD),
             ("mintedBy(address)", USER_PAD),
             ("freeMinted(address)", USER_PAD),
             ("freeClaimed(address)", USER_PAD),
             ("balanceOf(address)", USER_PAD),
             ("freeMintUsed(address)", USER_PAD),
             ("quote(address,uint256)", USER_PAD + ONE_PAD)]

TARGETS = {
    "BRAINROT": "0x3c7d328027ca0068e7cd8709d64d9161bc35de93",
    "HOPKIN": "0x2728c134D79D34A977d6D35D8A3014AbB5C97ed4",
    "GACHA": "0x7182f4230cbd53294366a344d13ddd041c4e734c",
    "HELM": "0xe0df49c281b8584f03ed21beac0e5002ec4a0599",
    "OMENS": "0xbd0e97f1a2b8b192382935a7b69c9514d75a479a",
    "TPET": "0x31975837d5c68eea0b66b5fd27de3506c2f109ba",
    "AGENTDRAGON": "0x2df7435f5bce0577bee213e13da68313c74d7d0b",
    "KZMB": "0xbd6e4c6def0065007bd163e4223ae4f3aa3b6f09",
    "HORUS": "0x794ad67a5590c7e5848e49181297f9cc7c6ce00e",
    "ONLYAI": "0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba",
    "TACOTRON": "0x05debe4445232205ae7e79d02cb5de5aa0641eff",
    "DINOBYTE": "0xd713ddfd37b8ff759afaeedaedad632d1985ed9c",
    "RAYGLIDE": "0xc4035e850f64d61adce8ecd774f1200d655e5f00",
    "HEROARENA": "0x5c46de8d0c5dfdf535558d363f492967cd5e146b",
    "NEKART": "0x3fc442342a5289d10773ae585c6cb3dc4a37254e",
    "LOOPMINT": "0x281c8b1c95ca989fde58998aa6f19d542ac99417",
    "LOOPTOKEN": "0x20d1f12ef71d5e07ea4fb7fc2d6a200b0eb71420",
    "TOKA": "0xaFEcb35096EF3A447460bF7A3B8b701f6d5468c7",
    "TOKB": "0x9791d92B63a566AC578e6070ee1F8546C8b2153B",
}

out = {}
try:
    head = rpc_call("eth_blockNumber", [])
    out["head_block"] = int(head, 16)
except Exception as e:
    out["head_block"] = f"ERR:{e}"

for name, addr in TARGETS.items():
    r = {"address": addr}
    for sig in NOARG_UINT:
        r[sig] = dec_uint(call(addr, sig))
    for sig in NOARG_STR:
        r[sig] = dec_str(call(addr, sig))
    for sig, args in USER_UINT:
        r[sig + "|user"] = dec_uint(call(addr, sig, args))
    # tokenURI(1) / contractURI() for BRAINROT only
    if name == "BRAINROT":
        r["tokenURI(1)"] = dec_str(call(addr, "tokenURI(uint256)", ONE_PAD))
        r["contractURI()"] = dec_str(call(addr, "contractURI()"))
    try:
        code = rpc_call("eth_getCode", [addr, "latest"])
        r["code_len"] = len(code) - 2 if isinstance(code, str) else None
    except Exception as e:
        r["code_len"] = f"ERR:{type(e).__name__}"
    out[name] = r
    print("probed", name, "totalSupply=", r.get("totalSupply()"), "freeLeft=", r.get("freeLeft()"), flush=True)

# Sourcify ABI presence + agentRegistry/free funcs for BRAINROT, HOPKIN, KZMB
def sourcify_abi(address, tries=2):
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
        except Exception:
            time.sleep(3)
    return ("error:retry-exhausted", None)

for name in ["BRAINROT", "HOPKIN", "KZMB"]:
    status, abi = sourcify_abi(TARGETS[name])
    info = {"sourcify": status}
    if isinstance(abi, list):
        fns = [i.get("name", "") for i in abi if i.get("type") == "function"]
        info["free_funcs"] = sorted(set(f for f in fns if "free" in f.lower()))
        info["mint_funcs"] = sorted(set(f for f in fns if "mint" in f.lower()))
        info["has_agentRegistry"] = any("agentregistr" in f.lower() for f in fns)
        info["has_agentgate"] = any("agentgate" in f.lower() for f in fns)
        info["fn_count"] = len(fns)
    out[name + "_sourcify"] = info
    print("sourcify", name, status, flush=True)

# First-mint windows via Ankr getLogs (Transfer from zero), chunked <=1000 blocks
def first_mint(addr, frm, to, label):
    earliest = None
    earliest_tx = None
    total = 0
    f = frm
    while f <= to:
        ct = min(f + 999, to)
        params = {"blockchain": "bsc", "fromBlock": hex(f), "toBlock": hex(ct),
                  "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC], "address": addr}
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
            logs = body.get("result", {}).get("logs", []) if isinstance(body, dict) else []
        except Exception as e:
            return {"label": label, "error": f"{f}-{ct}: {type(e).__name__}:{str(e)[:120]}",
                    "total": total, "earliest": earliest}
        total += len(logs)
        for l in logs:
            b = int(l["blockNumber"], 16)
            if earliest is None or b < earliest:
                earliest = b
                earliest_tx = l.get("transactionHash")
        f = ct + 1
        time.sleep(1.5)
    return {"label": label, "total": total, "earliest_block": earliest,
            "earliest_tx": earliest_tx}

head = out.get("head_block")
if isinstance(head, int):
    out["firstmint_BRAINROT"] = first_mint(TARGETS["BRAINROT"], 132195000, head, "brainrot")
    print("firstmint BRAINROT:", out["firstmint_BRAINROT"], flush=True)
    out["firstmint_HOPKIN"] = first_mint(TARGETS["HOPKIN"], 131387000, 131388000, "hopkin-firstseen-window")
    print("firstmint HOPKIN:", out["firstmint_HOPKIN"], flush=True)
    out["firstmint_GACHA"] = first_mint(TARGETS["GACHA"], 132181500, 132182500, "gacha-firstseen-window")
    out["firstmint_HELM"] = first_mint(TARGETS["HELM"], 132181500, 132182500, "helm-firstseen-window")
    out["firstmint_OMENS"] = first_mint(TARGETS["OMENS"], 132181500, 132182500, "omens-firstseen-window")
    print("firstmint lanes done", flush=True)
    # block timestamps via dataseed (NEVER Ankr raw getBlockByNumber - fake timestamps)
    for key in ["firstmint_BRAINROT", "firstmint_HOPKIN", "firstmint_GACHA",
                "firstmint_HELM", "firstmint_OMENS"]:
        b = out[key].get("earliest_block")
        if b:
            try:
                blk = rpc_call("eth_getBlockByNumber", [hex(b), False])
                out[key]["earliest_block_timestamp"] = int(blk["timestamp"], 16)
            except Exception as e:
                out[key]["earliest_block_timestamp"] = f"ERR:{type(e).__name__}"

json.dump(out, open("verify-1931.json", "w"), indent=1)
print("WROTE verify-1931.json")
