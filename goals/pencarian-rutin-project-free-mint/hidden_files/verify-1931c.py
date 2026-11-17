"""Leg 2 run 1931 verification part 2 (read-only): remaining contracts
(no eth_getCode - dataseed stalls on it), Sourcify x3, Ankr first-mint windows,
block timestamps via dataseed."""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def rpc_call(method, params, timeout=8):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params}).encode()
    last = None
    for ep in EPS:
        req = urllib.request.Request(ep, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                d = json.loads(resp.read().decode())
            if "error" in d:
                return {"__rpc_error__": d["error"]}
            return d.get("result")
        except Exception as e:
            last = e
    return {"__transport_error__": f"{type(last).__name__}:{str(last)[:100]}"}

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def call(addr, sig, args=""):
    r = rpc_call("eth_call", [{"to": addr, "data": sel(sig) + args}, "latest"])
    if isinstance(r, dict):
        return "ERR:" + json.dumps(r)[:120]
    return r

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

VIEWS = {
    "DINOBYTE": ("0xd713ddfd37b8ff759afaeedaedad632d1985ed9c", [
        ("totalSupply", "totalSupply()", "", "uint")]),
    "RAYGLIDE": ("0xc4035e850f64d61adce8ecd774f1200d655e5f00", [
        ("totalSupply", "totalSupply()", "", "uint")]),
    "HEROARENA": ("0x5c46de8d0c5dfdf535558d363f492967cd5e146b", [
        ("totalSupply", "totalSupply()", "", "uint")]),
    "NEKART": ("0x3fc442342a5289d10773ae585c6cb3dc4a37254e", [
        ("totalSupply", "totalSupply()", "", "uint"),
        ("freeLeft", "freeLeft()", "", "uint")]),
    "LOOPMINT": ("0x281c8b1c95ca989fde58998aa6f19d542ac99417", [
        ("totalSupply", "totalSupply()", "", "uint"),
        ("name", "name()", "", "str")]),
    "LOOPTOKEN": ("0x20d1f12ef71d5e07ea4fb7fc2d6a200b0eb71420", [
        ("totalSupply", "totalSupply()", "", "uint"),
        ("name", "name()", "", "str"),
        ("symbol", "symbol()", "", "str")]),
    "TOKA": ("0xaFEcb35096EF3A447460bF7A3B8b701f6d5468c7", [
        ("totalSupply", "totalSupply()", "", "uint"),
        ("name", "name()", "", "str"),
        ("symbol", "symbol()", "", "str")]),
    "TOKB": ("0x9791d92B63a566AC578e6070ee1F8546C8b2153B", [
        ("totalSupply", "totalSupply()", "", "uint"),
        ("name", "name()", "", "str"),
        ("symbol", "symbol()", "", "str")]),
}

out = {}
head = rpc_call("eth_blockNumber", [])
out["head_block"] = int(head, 16) if isinstance(head, str) else head
print("head:", out["head_block"], flush=True)
for name, (addr, views) in VIEWS.items():
    r = {"address": addr}
    for label, sig, args, kind in views:
        raw = call(addr, sig, args)
        r[label] = dec_uint(raw) if kind == "uint" else dec_str(raw)
        if r[label] is None and isinstance(raw, str) and raw.startswith("ERR"):
            r[label] = raw
    out[name] = r
    print("probed", name, json.dumps(r), flush=True)

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

for name, addr in [("BRAINROT", "0x3c7d328027ca0068e7cd8709d64d9161bc35de93"),
                   ("HOPKIN", "0x2728c134D79D34A977d6D35D8A3014AbB5C97ed4"),
                   ("KZMB", "0xbd6e4c6def0065007bd163e4223ae4f3aa3b6f09")]:
    status, abi = sourcify_abi(addr)
    info = {"sourcify": status}
    if isinstance(abi, list):
        fns = [i.get("name", "") for i in abi if i.get("type") == "function"]
        info["free_funcs"] = sorted(set(f for f in fns if "free" in f.lower()))
        info["mint_funcs"] = sorted(set(f for f in fns if "mint" in f.lower()))
        info["has_agentRegistry"] = any("agentregistr" in f.lower() for f in fns)
        info["has_agentgate"] = any("agentgate" in f.lower() for f in fns)
        info["fn_count"] = len(fns)
    out[name + "_sourcify"] = info
    print("sourcify", name, json.dumps(info), flush=True)

def first_mint(addr, frm, to, label):
    earliest, earliest_tx, total = None, None, 0
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
                earliest, earliest_tx = b, l.get("transactionHash")
        f = ct + 1
        time.sleep(1.2)
    return {"label": label, "total": total, "earliest_block": earliest,
            "earliest_tx": earliest_tx}

head = out.get("head_block")
ADDRS = {"BRAINROT": "0x3c7d328027ca0068e7cd8709d64d9161bc35de93",
         "HOPKIN": "0x2728c134D79D34A977d6D35D8A3014AbB5C97ed4",
         "GACHA": "0x7182f4230cbd53294366a344d13ddd041c4e734c",
         "HELM": "0xe0df49c281b8584f03ed21beac0e5002ec4a0599",
         "OMENS": "0xbd0e97f1a2b8b192382935a7b69c9514d75a479a"}
if isinstance(head, int):
    out["firstmint_BRAINROT"] = first_mint(ADDRS["BRAINROT"], 132195000, head, "brainrot")
    print("firstmint BRAINROT:", out["firstmint_BRAINROT"], flush=True)
    out["firstmint_HOPKIN"] = first_mint(ADDRS["HOPKIN"], 131387000, 131388000, "hopkin-firstseen-window")
    print("firstmint HOPKIN:", out["firstmint_HOPKIN"], flush=True)
    for n in ["GACHA", "HELM", "OMENS"]:
        out["firstmint_" + n] = first_mint(ADDRS[n], 132181500, 132182500, n.lower() + "-firstseen-window")
        print("firstmint", n, ":", out["firstmint_" + n], flush=True)
    for key in ["firstmint_BRAINROT", "firstmint_HOPKIN", "firstmint_GACHA",
                "firstmint_HELM", "firstmint_OMENS"]:
        b = out[key].get("earliest_block")
        if b:
            blk = rpc_call("eth_getBlockByNumber", [hex(b), False])
            out[key]["earliest_block_timestamp"] = int(blk["timestamp"], 16) if isinstance(blk, dict) else blk
            print("timestamp", key, out[key]["earliest_block_timestamp"], flush=True)

json.dump(out, open("verify-1931b.json", "w"), indent=1)
print("WROTE verify-1931b.json")
