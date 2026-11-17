#!/usr/bin/env python3
"""Run 0331 verify: Sourcify-feed contracts not in main snapshot/scan-seen with mint+free shape. Read-only."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v, 16) if v else None
def dec_str(v):
    if not v: return None
    b = bytes.fromhex(v[2:])
    if len(b) >= 64:
        ln = int.from_bytes(b[32:64], "big")
        if 0 < ln <= len(b) - 64: return b[64:64+ln].decode("utf-8", "replace")
    return None
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
def words(v):
    if not v: return None
    b = bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
def first_mints(C, head):
    logs = []; tok = None; pages = 0; err = None
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(131060000), "toBlock": hex(head), "pageSize": 1000, "decodeLogs": False,
                  "topics": ["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef", "0x" + "00" * 32], "address": C}
        if tok: params["pageToken"] = tok
        try: body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err = str(e)[:200]; break
        res = body.get("result", {}) if isinstance(body, dict) else {}
        got = [l for l in res.get("logs", []) if l.get("address", "").lower() == C.lower()]
        logs.extend(got); tok = res.get("nextPageToken"); pages += 1
        if not tok or pages >= 10: break
        time.sleep(1)
    out = {"count": len(logs), "err": err, "pages": pages}
    if logs:
        blks = sorted(int(l["blockNumber"], 16) for l in logs)
        minters = set(l.get("topics", [])[2] for l in logs if len(l.get("topics", [])) >= 3)
        out.update({"first_block": blks[0], "last_block": blks[-1], "distinct_minters": len(minters)})
        for ep in EPS:
            try:
                b = _single(ep, "eth_getBlockByNumber", [hex(blks[0]), False], 8, retries=0); out["first_ts"] = int(b["timestamp"], 16); break
            except Exception: pass
    return out
CANDS = ["0xE08289849427a82e336A64662bD951FcA4DE8d8E", "0x9f320879e96d493d7ed18a3c1025c0d7ADFDd11b",
         "0x4ec6086B7DEF22A0D95823BCB6e9ec8840B2d5C4", "0x21136e5ecBE886572b59a7e5B5D576fcE9534b89"]
head = blk()
result = {"head": head}
for C in CANDS:
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{C}?fields=abi", headers={"User-Agent": "free-mint-search/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r: meta = json.loads(r.read().decode())
        fns = sorted({e["name"] for e in meta.get("abi", []) if e.get("type") == "function"})
    except Exception as e:
        fns = []; result[C] = {"abi_error": f"{type(e).__name__}: {str(e)[:150]}"}
        print(C, "ABI FAIL", result[C]["abi_error"]); continue
    d = {"functions": fns, "head": head}
    d["name"] = dec_str(call(C, sel("name()")))
    d["symbol"] = dec_str(call(C, sel("symbol()")))
    for fn in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()"]:
        d[fn] = iv(call(C, sel(fn)))
    for fn in ["AGENT_ID()", "agentRegistry()", "registry()", "agentId()"]:
        d[fn] = call(C, sel(fn))
    d["mintedBy_user"] = iv(call(C, sel("mintedBy(address)") + enc_addr(USER)[2:]))
    d["freeUsed_user"] = iv(call(C, sel("freeUsed(address)") + enc_addr(USER)[2:]))
    d["balance_user"] = iv(call(C, sel("balanceOf(address)") + enc_addr(USER)[2:]))
    v = call(C, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    d["quote_user_1"] = words(v)
    d["first_mints"] = first_mints(C, head)
    result[C] = d
    print(C, d["name"], d["symbol"], "tot", d["totalSupply()"], "free", d["freeClaimed()"], "FSUP", d["FREE_SUPPLY()"], "AGENT_ID", d["AGENT_ID()"], "first", d["first_mints"])
print(json.dumps(result, indent=1))
json.dump(result, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0331-sourcify-verify.json", "w"), indent=1)
