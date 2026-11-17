#!/usr/bin/env python3
"""Run 0831: verify Cabinette 0xa8543350e5accacc780c9613bfa2fb9b52d3858e (Boltbook post sDxwv9fvElCh).
Read-only. Writes run-2026-11-08-0831-cabinette.json. Single-call batches (batch reverts if one view reverts).
First-mint search via Ankr getLogs chunked <=1000 blocks, backward from head; block timestamp via dataseed.
"""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0831"
ADDR = "0xa8543350e5accacc780c9613bfa2fb9b52d3858e"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def single(addr, data, timeout=10):
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)
            return res[0]
        except Exception:
            continue
    return None

def view(addr, sig, arg=None, arg2=None):
    data = sel(sig)
    if arg is not None:
        data += enc(arg) if isinstance(arg, str) and arg.startswith("0x") else enc_uint(arg)
    if arg2 is not None:
        data += enc_uint(arg2)
    return to_int(single(addr, data))

def raw_str(addr, sig):
    r = single(addr, sel(sig))
    if r is None: return None
    try:
        # abi-encoded string: offset(32) + len(32) + data
        ln = int(r[66:130], 16)
        return bytes.fromhex(r[130:130+ln*2]).decode("utf-8", "replace")
    except Exception:
        return None

def addr_view(addr, sig):
    r = single(addr, sel(sig))
    if r is None: return None
    try: return "0x" + r[-40:]
    except Exception: return None

out = {"address": ADDR, "name": raw_str(ADDR, "name()"), "symbol": raw_str(ADDR, "symbol()")}
print("name:", out["name"], "symbol:", out["symbol"], flush=True)
for sig in ["totalSupply()", "totalMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeClaimed()",
            "freeMinted()", "freeLeft()", "mintOpen()", "FREE_PER_WALLET()", "MAX_PER_WALLET()",
            "PRICE()", "freeSupply()", "maxSupply()"]:
    out[sig.split("(")[0]] = view(ADDR, sig)
    print(sig, "=", out[sig.split("(")[0]], flush=True)
    time.sleep(0.1)
out["freeClaimed_user"] = view(ADDR, "freeClaimed(address)", USER)
out["freeFor_user"] = view(ADDR, "freeFor(address)", USER)
out["freeMintedBy_user"] = view(ADDR, "freeMintedBy(address)", USER)
out["mintedBy_user"] = view(ADDR, "mintedBy(address)", USER)
out["balanceOf_user"] = view(ADDR, "balanceOf(address)", USER)
out["quote_user_1"] = view(ADDR, "quote(address,uint256)", USER, 1)
out["quote_1"] = view(ADDR, "quote(uint256)", 1)
out["owner"] = addr_view(ADDR, "owner()")
out["agentRegistry"] = addr_view(ADDR, "agentRegistry()")
out["AGENT_REGISTRY"] = addr_view(ADDR, "AGENT_REGISTRY()")
out["contractURI"] = raw_str(ADDR, "contractURI()")
print("user views:", {k: out[k] for k in ("freeClaimed_user","freeFor_user","freeMintedBy_user","mintedBy_user","balanceOf_user","quote_user_1","quote_1")}, flush=True)
print("owner:", out["owner"], "agentRegistry:", out["agentRegistry"], "AGENT_REGISTRY:", out["AGENT_REGISTRY"], flush=True)
print("contractURI:", out["contractURI"], flush=True)
# ERC-721 / ERC-1155 interface check
def supports(iface):
    data = sel("supportsInterface(bytes4)") + iface[2:].ljust(64, "0")
    r = single(ADDR, data)
    return r is not None and int(r, 16) == 1
out["isERC721"] = supports("0x80ac58cd")
out["isERC1155"] = supports("0xd9b67a26")
print("ERC721:", out["isERC721"], "ERC1155:", out["isERC1155"], flush=True)
out["tokenURI_1"] = raw_str(ADDR, "tokenURI(uint256)") if False else None
# tokenURI needs arg; do it manually
r = single(ADDR, sel("tokenURI(uint256)") + enc_uint(1))
if r:
    try:
        ln = int(r[66:130], 16)
        out["tokenURI_1"] = bytes.fromhex(r[130:130+ln*2]).decode("utf-8", "replace")
    except Exception as e:
        out["tokenURI_1"] = f"decode-fail {e}"
print("tokenURI(1):", out["tokenURI_1"], flush=True)

# head
head = None
for ep in EPS:
    try:
        res = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
        head = int(res[0], 16); break
    except Exception:
        continue
out["head"] = head
print("head:", head, flush=True)

# first-mint search: backward 1000-block windows from head until a window with no mints
def getlogs(from_b, to_b):
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(from_b),
        "toBlock": hex(to_b), "pageSize": 1000, "decodeLogs": False,
        "topics": [TRANSFER, ZERO_TOPIC],
        "address": [ADDR]}, timeout=60)
    return body.get("result", {}).get("logs", [])

first_block = None
first_logs = []
to_b = head
tries = 0
while to_b > 0 and tries < 40:
    from_b = max(0, to_b - 999)
    try:
        logs = getlogs(from_b, to_b)
    except Exception as e:
        print(f"getLogs {from_b}-{to_b} FAILED: {e}", flush=True)
        break
    print(f"window {from_b}-{to_b}: {len(logs)} mint logs", flush=True)
    if not logs:
        break
    first_logs = logs
    first_block = min(int(l["blockNumber"], 16) for l in logs)
    to_b = first_block - 1
    tries += 1
    if len(logs) >= 1000:
        print("WARNING: window returned exactly 1000 logs - may be truncated", flush=True)
out["firstMintBlock"] = first_block
out["firstMintLogsInWindow"] = len(first_logs)
if first_block:
    # block timestamp via dataseed (Ankr timestamps are FAKE)
    ts = None
    for ep in EPS:
        try:
            res = batch([("eth_getBlockByNumber", [hex(first_block), False])], endpoint=ep, timeout=10)
            ts = int(res[0]["timestamp"], 16); break
        except Exception:
            continue
    out["firstMintTimestamp"] = ts
    if ts:
        import datetime
        dt = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
        out["firstMintWib"] = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
    print("firstMintBlock:", first_block, "ts:", ts, "wib:", out.get("firstMintWib"), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-cabinette.json", "w"), indent=1)
print("CABINETTE-VERIFY DONE", flush=True)
