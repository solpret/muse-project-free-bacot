#!/usr/bin/env python3
"""Run 0201 verify: Sourcify-feed agent-shaped contracts. Read-only."""
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
AGENTID = "0x934122e8fc4fe823a60d9dde4b2b716dd6bdcff35db0ad4ec90f97a1b0b7d310"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
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
NFTS = {
 "SourcifyNFT-a233": "0xa233C45f881A6982647b63c61D7a5f9a3F90C5f4",
 "SourcifyNFT-8E87": "0x8E878C801b9F37cc0Cb6FF3C4597Af8FC057988b",
 "SourcifyNFT-EbAd": "0xEbAdb5Be9692b0BF25E8A5F3351C35DdC58f195d",
 "SourcifyNFT-B330": "0xB330e582f45c0243e5Eb1B56958b56273f26a9eB",
 "SourcifyNFT-B440": "0xB44050254A25dAA8077C14BbB20d0a595e6CECE2",
 "SourcifyNFT-74C2": "0x74C2214fDCc10c303302592151c50965903aa7a9",
 "SourcifyNFT-7f22": "0x7f22e7cf2D2F85Ca6eb62Bf0B55f0B9229FF150F",
 "SourcifyNFT-011F": "0x011F1aeaF230A5E8dee20168654644DA4DE3C4B5",
}
for nm, C in NFTS.items():
    r = {"address": C, "name": dec_str(call(C, sel("name()"))), "symbol": dec_str(call(C, sel("symbol()")))}
    for fn in ["totalSupply()", "totalMinted()", "freeClaimed()", "freeLeft()", "freePerWallet()", "FREE_SUPPLY()", "FREE_PER_WALLET()", "MAX_SUPPLY()", "MAX_PER_WALLET()", "mintOpen()", "PRICE()"]:
        r[fn] = iv(call(C, sel(fn)))
    r["AGENT_ID"] = call(C, sel("AGENT_ID()"))
    r["agentRegistry"] = call(C, sel("agentRegistry()"))
    r["agentIdRegistry"] = call(C, sel("agentIdRegistry()"))
    r["mintedBy_user"] = iv(call(C, sel("mintedBy(address)") + enc_addr(USER)[2:]))
    r["freeUsed_user"] = iv(call(C, sel("freeUsed(address)") + enc_addr(USER)[2:]))
    r["freeFor_user"] = iv(call(C, sel("freeFor(address)") + enc_addr(USER)[2:]))
    r["balance_user"] = iv(call(C, sel("balanceOf(address)") + enc_addr(USER)[2:]))
    v = call(C, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:]); r["quote_user_1_words"] = words(v)
    r["costFor1"] = iv(call(C, sel("costFor(uint256)") + enc_uint(1)[2:]))
    r["currentPrice"] = iv(call(C, sel("currentPrice()")))
    r["first_mints"] = first_mints(C, head)
    out[nm] = r; print(nm, json.dumps(r))
# Track-C variant 1646
C = "0x16469C174cd827A5e21f4bf3eE3711f2bB42e275"
r = {"address": C, "name": dec_str(call(C, sel("name()"))), "symbol": dec_str(call(C, sel("symbol()"))), "decimals": iv(call(C, sel("decimals()")))}
for fn in ["totalSupply()", "freeClaimed()", "FREE_SHARES()", "MAX_PAID()", "phase()", "startedAt()", "sold()", "launched()", "pair()", "POOL_TOKENS()", "TOKENS_PER_SHARE()", "PRICE()", "totalPaidBNB()", "deadline()"]:
    r[fn] = iv(call(C, sel(fn)))
r["REGISTRY"] = call(C, sel("REGISTRY()"))
r["registry_addr"] = call(C, sel("REGISTRY()"))
r["balance_user"] = iv(call(C, sel("balanceOf(address)") + enc_addr(USER)[2:]))
r["freeClaimedById_agentId"] = words(call(C, sel("freeClaimedById(bytes32)") + AGENTID[2:]))
r["paidSharesById_agentId"] = words(call(C, sel("paidSharesById(bytes32)") + AGENTID[2:]))
r["remainingQuota_agentId"] = words(call(C, sel("remainingQuota(bytes32)") + AGENTID[2:])) if False else None
# registry agentIdOf check
for sig in ["agentIdOf(address)", "getAgentId(address)", "agentOf(address)"]:
    r["registry_" + sig] = call(REGISTRY, sel(sig) + enc_addr(USER)[2:])
r["first_mints"] = first_mints(C, head)
out["TrackC-1646"] = r; print("TrackC-1646", json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0201-verify.json", "w"), indent=1)
