#!/usr/bin/env python3
"""Run 0831: WOJAGENT + HokiCat deep-check. Read-only.
WOJAGENT 0x62EC413381B74387b57F1E2734cdd2E5b96a57B7 (ERC20 share sale, mintFree).
HokiCat 0xdb51dcc2d8caf9942d9a975a2e68e023ab5e1fca (ERC721, S1-shaped, free cap unknown).
Writes run-2026-11-08-0831-woj-hokicat.json."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_NAME = "masgayut.ai"
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
        ln = int(r[66:130], 16)
        return bytes.fromhex(r[130:130+ln*2]).decode("utf-8", "replace")
    except Exception:
        return None

def abi(addr):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True, timeout=25)
        d = json.loads(r.stdout)
        return d.get("abi")
    except Exception as e:
        return None

out = {}
# ---- WOJAGENT ----
W = "0x62EC413381B74387b57F1E2734cdd2E5b96a57B7"
w = {"address": W}
w["name"] = raw_str(W, "name()"); w["symbol"] = raw_str(W, "symbol()")
w["decimals"] = view(W, "decimals()")
w["totalSupply"] = view(W, "totalSupply()")
w["totalShares"] = view(W, "totalShares()")
w["sharesMinted"] = view(W, "sharesMinted()")
w["freeShares"] = view(W, "freeShares()")
w["freeSharesClaimed"] = view(W, "freeSharesClaimed()")
w["freeClaimed"] = view(W, "freeClaimed()")
w["freeClaimed_user"] = view(W, "freeClaimed(address)", USER)
w["freeSharesClaimed_user"] = view(W, "freeSharesClaimed(address)", USER)
w["claimed_user"] = view(W, "claimed(address)", USER)
w["balanceOf_user"] = view(W, "balanceOf(address)", USER)
w["mintPaused"] = view(W, "mintPaused()")
w["FREE_SHARES"] = view(W, "FREE_SHARES()")
w["MAX_SHARES"] = view(W, "MAX_SHARES()")
w["TOKENS_PER_SHARE"] = view(W, "TOKENS_PER_SHARE()")
w["tokensPerShare"] = view(W, "tokensPerShare()")
w["pairAddress"] = None
abi_w = abi(W)
w["abi_fns"] = [f.get("name") for f in abi_w if f.get("type") == "function"] if abi_w else None
# mintFree signature: find it
if abi_w:
    for f in abi_w:
        if f.get("name") == "mintFree":
            w["mintFree_inputs"] = f.get("inputs")
        if f.get("name") in ("mintFree", "freeClaimed", "agentIdOf", "agentRegistry"):
            pass
print("WOJAGENT:", json.dumps({k: v for k, v in w.items() if k != "abi_fns"}, indent=0), flush=True)
print("WOJAGENT abi_fns:", w["abi_fns"], flush=True)
out["WOJAGENT"] = w

# ---- HokiCat ----
H = "0xdb51dcc2d8caf9942d9a975a2e68e023ab5e1fca"
h = {"address": H}
h["name"] = raw_str(H, "name()"); h["symbol"] = raw_str(H, "symbol()")
for sig in ["totalSupply()", "totalMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeClaimed()",
            "freeMinted()", "freeLeft()", "mintOpen()", "FREE_PER_WALLET()", "MAX_PER_WALLET()",
            "PRICE()", "freeSupply()", "maxSupply()", "freeCap()", "FREE_CAP()", "freeMintedBy(address)"]:
    key = sig.split("(")[0]
    if "(address)" in sig:
        h[key + "_user"] = view(H, sig, USER)
    else:
        h[key] = view(H, sig)
    time.sleep(0.05)
h["freeClaimed_user"] = view(H, "freeClaimed(address)", USER)
h["mintedBy_user"] = view(H, "mintedBy(address)", USER)
h["balanceOf_user"] = view(H, "balanceOf(address)", USER)
h["quote_user_1"] = view(H, "quote(address,uint256)", USER, 1)
h["quote_1"] = view(H, "quote(uint256)", 1)
h["contractURI"] = raw_str(H, "contractURI()")
abi_h = abi(H)
h["abi_fns"] = [f.get("name") for f in abi_h if f.get("type") == "function"] if abi_h else None
print("HOKICAT:", json.dumps({k: v for k, v in h.items() if k != "abi_fns"}, indent=0), flush=True)
print("HOKICAT abi_fns:", h["abi_fns"], flush=True)
out["HokiCat"] = h

# first-mint search for HokiCat + WOJAGENT (Transfer from zero, backward 1000-block windows)
def first_mint(addr, head, max_tries=30):
    to_b = head
    first_block = None
    tries = 0
    while to_b > 0 and tries < max_tries:
        from_b = max(0, to_b - 999)
        try:
            body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(from_b),
                "toBlock": hex(to_b), "pageSize": 1000, "decodeLogs": False,
                "topics": [TRANSFER, ZERO_TOPIC], "address": [addr]}, timeout=60)
            logs = body.get("result", {}).get("logs", [])
        except Exception as e:
            print(f"getLogs {addr[:10]} {from_b}-{to_b} FAILED: {e}", flush=True)
            return None, None
        print(f"firstmint {addr[:10]} window {from_b}-{to_b}: {len(logs)} logs", flush=True)
        if not logs:
            break
        first_block = min(int(l["blockNumber"], 16) for l in logs)
        to_b = first_block - 1
        tries += 1
    if first_block is None:
        return None, None
    ts = None
    for ep in EPS:
        try:
            res = batch([("eth_getBlockByNumber", [hex(first_block), False])], endpoint=ep, timeout=10)
            ts = int(res[0]["timestamp"], 16); break
        except Exception:
            continue
    return first_block, ts

head = None
for ep in EPS:
    try:
        res = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
        head = int(res[0], 16); break
    except Exception:
        continue
print("head:", head, flush=True)
for key, addr in (("WOJAGENT", W), ("HokiCat", H)):
    fb, ts = first_mint(addr, head)
    out[key]["firstMintBlock"] = fb
    out[key]["firstMintTimestamp"] = ts
    if ts:
        import datetime
        dt = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
        out[key]["firstMintWib"] = dt.strftime("%Y-%m-%d %H:%M:%S WIB")
    print(key, "firstMint:", fb, out[key].get("firstMintWib"), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-08-0831-woj-hokicat.json", "w"), indent=1)
print("WOJ-HOKICAT DONE", flush=True)
