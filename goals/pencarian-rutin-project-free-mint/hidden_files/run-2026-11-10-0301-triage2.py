#!/usr/bin/env python3
"""Triage2 run 0301 (2026-11-10): (a) Adventure Agent follow-up views
AGENT_ID_REGISTRY()/freeLeft()/factory()/MAX_FREE_PER_WALLET()/paidMinted()
+ name() retry; (b) track-C S1 lead 0x38491597 — ABI dump + sale views.
Read-only; never previews/mints. Writes run-2026-11-10-0301-triage2.json."""
import json, subprocess, time, urllib.request, urllib.error
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_call(addr, data):
    """Single eth_call returning raw hex result or None."""
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(r, dict) and "error" not in r and r.get("result"):
                return r["result"]
        except Exception:
            continue
    return None

def call_view(addr, sig, args=""):
    data = sel(sig) + args
    res = raw_call(addr, data)
    return to_int(res)

def call_addr(addr, sig):
    res = raw_call(addr, sel(sig))
    if res and len(res) >= 66:
        return "0x" + res[26:66]
    return None

def get_string(addr, sig):
    res = raw_call(addr, sel(sig))
    if not res or res == "0x":
        return None
    try:
        b = bytes.fromhex(res[2:])
        if len(b) >= 96:
            off = int.from_bytes(b[0:32], "big")
            ln = int.from_bytes(b[off:off+32], "big")
            return b[off+32:off+32+ln].decode("utf-8", "ignore")
    except Exception:
        return None
    return None

def sourcify_abi(address):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(3):
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
    return ("error", None)

out = {}

# (a) Adventure Agent follow-up
ADV = "0x7635ef16370ef490298649a188c9205d1d7fda67"
adv = {}
adv["AGENT_ID_REGISTRY"] = call_addr(ADV, "AGENT_ID_REGISTRY()")
adv["registry_is_official"] = (adv["AGENT_ID_REGISTRY"] or "").lower() == REGISTRY.lower()
adv["freeLeft"] = call_view(ADV, "freeLeft()")
adv["factory"] = call_addr(ADV, "factory()")
adv["MAX_FREE_PER_WALLET"] = call_view(ADV, "MAX_FREE_PER_WALLET()")
adv["MAX_PAID_PER_WALLET"] = call_view(ADV, "MAX_PAID_PER_WALLET()")
adv["paidMinted"] = call_view(ADV, "paidMinted()")
adv["boxMinted"] = call_view(ADV, "boxMinted()")
adv["totalMinted"] = call_view(ADV, "totalMinted()")
adv["freeMinted"] = call_view(ADV, "freeMinted()")
adv["name"] = get_string(ADV, "name()")
adv["advToken"] = call_addr(ADV, "advToken()")
adv["poolWallet"] = call_addr(ADV, "poolWallet()")
out["AdventureAgent_followup"] = adv
print("ADV followup:", json.dumps(adv), flush=True)

# (b) track-C S1 0x38491597
SALE = "0x3849159784aa47Fe76117103904204D9f5D153E7"
status, abi = sourcify_abi(SALE)
funcs = []
if isinstance(abi, list):
    funcs = sorted({f"{it.get('name','')}({','.join(i.get('type','') for i in it.get('inputs',[]))})"
                    for it in abi if it.get("type") == "function"})
sale = {"sourcify": status, "functions": funcs}
print("SALE funcs:", funcs, flush=True)
# candidate views (tolerate revert -> None)
sale["sharesMinted"] = call_view(SALE, "sharesMinted()")
sale["paidSharesMinted"] = call_view(SALE, "paidSharesMinted()")
sale["freeSharesClaimed"] = call_view(SALE, "freeSharesClaimed()")
sale["freeSharesRemaining"] = call_view(SALE, "freeSharesRemaining()")
sale["MAX_SHARES"] = call_view(SALE, "MAX_SHARES()")
sale["TOTAL_SHARES"] = call_view(SALE, "TOTAL_SHARES()")
sale["mintingOpen"] = call_view(SALE, "mintingOpen()")
sale["mintOpen"] = call_view(SALE, "mintOpen()")
sale["paused"] = call_view(SALE, "paused()")
sale["owner"] = call_addr(SALE, "owner()")
sale["token"] = call_addr(SALE, "token()")
sale["agentIdRegistry"] = call_addr(SALE, "agentIdRegistry()")
sale["hasAgentId_user"] = call_view(SALE, "hasAgentId(address)", enc(USER))
# quote(address,uint256) -> returns tuple; raw call, decode first two words
qres = raw_call(SALE, sel("quote(address,uint256)") + enc(USER) + "0" * 63 + "1")
if qres:
    try:
        b = bytes.fromhex(qres[2:])
        words = [int.from_bytes(b[i:i+32], "big") for i in range(0, min(len(b), 128), 32)]
        sale["quote_user_1_raw"] = words
    except Exception as e:
        sale["quote_user_1_raw"] = f"decode-err {e}"
else:
    # try quote(uint256)
    qres2 = raw_call(SALE, sel("quote(uint256)") + "0" * 63 + "1")
    if qres2:
        try:
            b = bytes.fromhex(qres2[2:])
            sale["quote_1_raw"] = [int.from_bytes(b[i:i+32], "big") for i in range(0, min(len(b), 128), 32)]
        except Exception as e:
            sale["quote_1_raw"] = f"decode-err {e}"
    else:
        sale["quote_user_1_raw"] = None
sale["name"] = get_string(SALE, "name()")
sale["symbol"] = get_string(SALE, "symbol()")
out["TrackC_0x38491597"] = sale
print("SALE views:", json.dumps({k: v for k, v in sale.items() if k != "functions"}), flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-10-0301-triage2.json", "w"), indent=1)
print(f"TRIAGE2 DONE in {time.time()-T0:.1f}s", flush=True)
