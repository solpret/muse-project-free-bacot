#!/usr/bin/env python3
"""Run 0531 verify: two new Sourcify agent-shape contracts. Read-only."""
import json, sys, time
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
    out = {"count": len(logs), "err": err}
    if logs:
        blks = sorted(int(l["blockNumber"], 16) for l in logs)
        minters = set(l.get("topics", [])[2] for l in logs if len(l.get("topics", [])) >= 3)
        out.update({"first_block": blks[0], "last_block": blks[-1], "distinct_minters": len(minters)})
        for ep in EPS:
            try:
                b = _single(ep, "eth_getBlockByNumber", [hex(blks[0]), False], 8, retries=0); out["first_ts"] = int(b["timestamp"], 16); break
            except Exception: pass
    return out

head = blk(); print("head", head)
out = {"head": head}
# 0xD1D3: ERC721, mint+quote+freeClaimed/freeMinted+FREE_CAP+registry
C = "0xD1D3b730b154838b7B5F0c072dE7bA66FFBbe72b"
r = {"address": C, "name": dec_str(call(C, sel("name()"))), "symbol": dec_str(call(C, sel("symbol()")))}
for fn in ["totalMinted()", "totalSupply()", "freeClaimed()", "freeMinted()", "FREE_CAP()", "MAX_SUPPLY()", "freeOn()", "mintOpen()", "price()", "clanMinted()", "registry()"]:
    r[fn] = call(C, sel(fn)) if fn in ("registry()",) else iv(call(C, sel(fn)))
r["mintedBy_user"] = iv(call(C, sel("mintedBy(address)") + enc_addr(USER)[2:]))
r["balance_user"] = iv(call(C, sel("balanceOf(address)") + enc_addr(USER)[2:]))
r["walletInfo_user"] = words(call(C, sel("walletInfo(address)") + enc_addr(USER)[2:]))
v = call(C, sel("quote(uint256)") + enc_uint(1)[2:]); r["quote_1_words"] = words(v)
v = call(C, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:]); r["quote_user_1_words"] = words(v)
r["stats"] = words(call(C, sel("stats()")))
r["first_mints"] = first_mints(C, head)
out["D1D3"] = r; print("D1D3", json.dumps(r))
# 0x25F6: ERC721, mintFree no-arg + FREE_CAP + freeMinted + agentIdRegistry + mintStart/mintEnd
C = "0x25F6DF83D43496583BC7190f02E68A15C3E3bB25"
r = {"address": C, "name": dec_str(call(C, sel("name()"))), "symbol": dec_str(call(C, sel("symbol()")))}
for fn in ["totalMinted()", "totalSupply()", "freeMinted()", "FREE_CAP()", "PAID_CAP()", "MAX_SUPPLY()", "mintOpen()", "mintStart()", "mintEnd()", "PRICE()", "agentIdRegistry()", "paidMinted()", "inviteMinted()"]:
    r[fn] = call(C, sel(fn)) if fn in ("agentIdRegistry()",) else iv(call(C, sel(fn)))
r["balance_user"] = iv(call(C, sel("balanceOf(address)") + enc_addr(USER)[2:]))
r["minterAgentOf_user"] = call(C, sel("minterAgentOf(address)") + enc_addr(USER)[2:])
r["mintTypeOf_user"] = iv(call(C, sel("mintTypeOf(address)") + enc_addr(USER)[2:]))
r["first_mints"] = first_mints(C, head)
out["F25"] = r; print("F25", json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0531-verify.json", "w"), indent=1)
print(json.dumps(out, indent=1))
