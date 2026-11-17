#!/usr/bin/env python3
"""Hot-leg 19:54 part 2: track-C dedicated views + Cyberlynx/AZET + ORBIT age logs. Read-only."""
import json, sys, urllib.request, concurrent.futures
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
U = enc_addr(USER)[2:]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def collect(to, tests):
    out = {}
    for name, arg in tests:
        v, err = call(to, sel(name) + arg)
        try: iv = int(v, 16) if v else None
        except Exception: iv = None
        out[name] = iv
    return out
def decode_str(to, fn):
    v, err = call(to, sel(fn))
    if not v or len(v) < 138: return None
    try:
        ln = int(v[66:130], 16)
        return bytes.fromhex(v[130:130 + ln * 2]).decode(errors="replace")
    except Exception: return None
early = [("totalSupply()", ""), ("freeClaimed()", ""), ("FREE_SUPPLY()", ""),
         ("mintedBy(address)", U), ("freeUsed(address)", U), ("balanceOf(address)", U)]
out = {}
out["Cyberlynx"] = collect("0xD4D848F81216Ef2856fEe2cdFa529a1bB53c50C0", early)
out["AZET"] = collect("0xFF8BfeF2c0d16BDa6E8667812bCa35Ecb42A1a37", early)
out["QAGENT"] = collect("0x93eAbc3f8496A304eb0CDC3F1AD00CCCdb877877",
    [("sharesMinted()", ""), ("freeMinted()", ""), ("paidShares()", ""), ("MAX_FREE()", ""),
     ("mintingOpen()", ""), ("poolOpen()", ""), ("freeAvailable(address)", U),
     ("freeClaimed(address)", U), ("mintedBy(address)", U)])
out["NIUBI"] = collect("0x094DA228770A141bB2aCaE22608A08D66a8f789a",
    [("sharesMinted()", ""), ("freeMinted()", ""), ("MAX_FREE()", ""), ("mintingOpen()", ""),
     ("poolOpen()", ""), ("freeAvailable(address)", U), ("freeClaimed(address)", U), ("mintedBy(address)", U)])
out["DROID"] = collect("0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
    [("FREE_SHARES()", ""), ("freeMinted()", ""), ("paused()", ""), ("freeUsed(address)", U)])
out["WAG"] = collect("0x5091F75CdFEf44883a5b24ff453322De8ef24aFd",
    [("sharesMinted()", ""), ("freeMinted()", ""), ("paidShares()", ""), ("MAX_FREE()", ""),
     ("mintingOpen()", ""), ("poolOpen()", ""), ("freeAvailable(address)", U),
     ("freeClaimed(address)", U), ("mintedBy(address)", U), ("hasAgentId(address)", U)])
out["S723"] = collect("0x723BA73f3480628DD909798367fd47D763C8B5c8",
    [("sharesMinted()", ""), ("freeMinted()", ""), ("paidShares()", ""), ("MAX_FREE()", ""),
     ("mintingOpen()", ""), ("poolOpen()", ""), ("freeAvailable(address)", U),
     ("freeClaimed(address)", U), ("mintedBy(address)", U), ("hasAgentId(address)", U)])
out["S723_quote1"] = collect("0x723BA73f3480628DD909798367fd47D763C8B5c8", [("quote(uint256)", enc_uint(1)[2:])])
out["FABE_sale"] = collect("0xFabE022a5943462fee1Bd221791945DA57510BE8",
    [("freeSharesRemaining()", ""), ("FREE_SHARES()", ""), ("totalShares()", "")])
out["PrelaunchSale"] = collect("0x9807a084dcCfFed3F9e530Ab08635ae08c35BF14",
    [("launched()", ""), ("soldFree()", ""), ("FREE_TOTAL()", ""), ("totalSold()", ""), ("soldPaid()", "")])
out["UPONLY"] = collect("0x1ddBcbA032bc0D80A69B58D91C292aB83119cbc3",
    [("launched()", ""), ("soldFree()", ""), ("FREE_TOTAL()", ""), ("totalSold()", ""), ("soldPaid()", "")])
out["Sevaris"] = collect("0x73085868F57C46E09C7b70AdFda6E6b806222Af0",
    [("totalSupply()", ""), ("freeMinted()", ""), ("freeLeft()", ""), ("saleOpen()", ""),
     ("freeAvailable(address)", U), ("freeClaimed(address)", U), ("hasAgentId(address)", U)])
out["E45B_token_name"] = decode_str("0x99487232829ac745b5be20c1d215f255335812ef", "name()")
out["E45B_token_symbol"] = decode_str("0x99487232829ac745b5be20c1d215f255335812ef", "symbol()")
out["ORBIT_token_name"] = decode_str("0xc09eea8ecc744e0adf299c849ccc9fb897a545d8", "name()")
out["ORBIT_token_symbol"] = decode_str("0xc09eea8ecc744e0adf299c849ccc9fb897a545d8", "symbol()")
# Age logs: first Transfer from ORBIT sale on ORBIT token, and first Transfer from e45b sale on its token
def rpc(ep, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())["result"]
def first_transfer(token, frm, label):
    try:
        blk = int(rpc(EPS[0], "eth_blockNumber", []), 16)
        frm_block = hex(max(0, blk - 70000))
        sig = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
        pad = "0x" + frm[2:].lower().rjust(64, "0")
        logs = rpc(EPS[0], "eth_getLogs", [{"address": token, "fromBlock": frm_block, "toBlock": "latest",
                                            "topics": [sig, pad]}])
        if not logs:
            return {"label": label, "found": False, "block_range": [frm_block, hex(blk)], "note": "no Transfer from sale in last 70000 blocks"}
        first = min(logs, key=lambda l: int(l["blockNumber"], 16))
        b = rpc(EPS[0], "eth_getBlockByNumber", [first["blockNumber"], False])
        return {"label": label, "found": True, "block": int(first["blockNumber"], 16),
                "timestamp": int(b["timestamp"], 16), "tx": first["transactionHash"], "count_in_window": len(logs)}
    except Exception as e:
        return {"label": label, "error": f"{type(e).__name__}: {str(e)[:160]}"}
out["ORBIT_first_share_transfer"] = first_transfer("0xc09eea8ecc744e0adf299c849ccc9fb897a545d8",
    "0x6e0c18185f584781592fa972ff2b7566c5532e12", "ORBIT")
out["E45B_first_share_transfer"] = first_transfer("0x99487232829ac745b5be20c1d215f255335812ef",
    "0xe45b4a6755e29EaDbc3fF90CB15207F56B7B43B1", "E45B")
json.dump(out, open(BASE + "hot-leg-2026-11-02-1954-trackc.json", "w"), indent=1)
for k, v in out.items(): print(k, v)
