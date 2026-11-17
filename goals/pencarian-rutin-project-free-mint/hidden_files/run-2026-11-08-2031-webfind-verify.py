#!/usr/bin/env python3
"""Parent run 2031: verify 4 web-found contracts (Boltbook/Sourcify legs):
Saturnagent + 3 wave-4 lanes (ALL ACCESS / THE KEY / GOLDEN TICKET).
Reads owner (+same-owner-discards), free views, quote/slot user, first-mint walk.
Read-only; writes run-2026-11-08-2031-webfind-verify.json/.log."""
import sys, json, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _post as _fr_post
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u256(n): return "%064x" % n
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def call(addr, data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=10, retries=0)
            if isinstance(out, dict) and "result" in out: return out["result"]
            if isinstance(out, dict) and "error" in out: return None
        except Exception: continue
    return None
def dec_str(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64: return b.decode(errors="replace")
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def dec_addr(h):
    if not isinstance(h, str) or len(h) < 42: return None
    return "0x" + h[-40:]
def block_time_wib(blk):
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(blk), False]}, timeout=10, retries=0)
            if r and r.get("result"):
                ts = int(r["result"]["timestamp"], 16)
                return datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: continue
    return None
def head_block():
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber",
                              "params": []}, timeout=10, retries=0)
            return int(r["result"], 16)
        except Exception: continue
    return None

def first_mint(addr, head):
    earliest = None; total = 0; chunks = 0; empty_after = 0; CH = 20000; frm = head
    while frm > head - 384000:
        to = frm; frm = max(0, frm - CH + 1); chunks += 1
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "address": addr, "pageSize": 1000, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e:
            return {"error": str(e)[:200], "earliest_block": earliest, "logs": total, "chunks": chunks}
        logs = (body.get("result", {}) or {}).get("logs", []) if isinstance(body, dict) else []
        n4 = 0
        for lg in logs:
            if len(lg.get("topics", [])) == 4:
                blk = int(lg["blockNumber"], 16); total += 1; n4 += 1
                if earliest is None or blk < earliest: earliest = blk
        print(f"  chunk {frm}-{to}: {n4} mints, earliest {earliest}", flush=True)
        if earliest is not None and to < earliest:
            if n4 == 0:
                empty_after += 1
                if empty_after >= 3: break
            else:
                empty_after = 0
        time.sleep(1.0)
    return {"earliest_block": earliest, "logs": total, "chunks": chunks,
            "empty_chunks_after_earliest": empty_after, "walked_to_block": frm}

CANDS = {
    "Saturnagent": "0xef870a9b4a529373fb2e174b59ca7a66eb018074",
    "ALL ACCESS": "0xc3ce00677dad113f5d466d46c8c7b3a227855a5b",
    "THE KEY": "0xa4835228a47e8dcaa7ff44e2c9fd1c46c94b99da",
    "GOLDEN TICKET": "0x1de1a2bce14bbc230a21ec7b579a6591f43e1e4a",
}
discards = json.load(open(BASE + "/same-owner-discards.json"))
disc_owners = {str(d.get("owner", "")).lower() for d in discards if isinstance(d, dict)}
head = head_block()
print("HEAD", head, flush=True)
out = {"head": head, "started_wib": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M WIB")}
for name, addr in CANDS.items():
    print(f"== {name} {addr}", flush=True)
    r = {"address": addr}
    r["name"] = dec_str(call(addr, sel("name()")))
    r["symbol"] = dec_str(call(addr, sel("symbol()")))
    r["owner"] = dec_addr(call(addr, sel("owner()")))
    r["owner_in_discards"] = (r["owner"] or "").lower() in disc_owners if r["owner"] else None
    r["totalSupply"] = to_int(call(addr, sel("totalSupply()")))
    r["totalMinted"] = to_int(call(addr, sel("totalMinted()")))
    r["freeClaimed_noarg"] = to_int(call(addr, sel("freeClaimed()")))
    r["freeMinted"] = to_int(call(addr, sel("freeMinted()")))
    r["FREE_SUPPLY"] = to_int(call(addr, sel("FREE_SUPPLY()")))
    r["FREE_CAP"] = to_int(call(addr, sel("FREE_CAP()")))
    r["FREE_POOL"] = to_int(call(addr, sel("FREE_POOL()")))
    r["MAX_SUPPLY"] = to_int(call(addr, sel("MAX_SUPPLY()")))
    r["mintOpen"] = to_int(call(addr, sel("mintOpen()")))
    r["AGENT_ID"] = dec_addr(call(addr, sel("AGENT_ID()")))
    r["agentRegistry"] = dec_addr(call(addr, sel("agentRegistry()")))
    r["freeLeft_user"] = to_int(call(addr, sel("freeLeft(address)") + enc_addr(USER)))
    r["freeUsed_user"] = to_int(call(addr, sel("freeUsed(address)") + enc_addr(USER)))
    r["freeClaimed_user"] = to_int(call(addr, sel("freeClaimed(address)") + enc_addr(USER)))
    r["mintedBy_user"] = to_int(call(addr, sel("mintedBy(address)") + enc_addr(USER)))
    r["balanceOf_user"] = to_int(call(addr, sel("balanceOf(address)") + enc_addr(USER)))
    q = call(addr, sel("quote(address,uint256)") + enc_addr(USER) + enc_u256(1))
    r["quote_user_1_raw"] = q
    if q and len(q) >= 130:
        try: r["quote_user_1"] = [int(q[2+i*64:2+(i+1)*64], 16) for i in range((len(q)-2)//64)]
        except Exception: r["quote_user_1"] = None
    cu = dec_str(call(addr, sel("contractURI()")))
    r["contractURI_head"] = (cu or "")[:300] if cu else None
    print("  ", json.dumps({k: v for k, v in r.items() if k != "quote_user_1_raw"}, default=str)[:600], flush=True)
    if r["owner_in_discards"]:
        r["first_mint"] = {"skipped": "owner in same-owner-discards; age walk not needed"}
    else:
        fm = first_mint(addr, head)
        if fm.get("earliest_block"):
            fm["earliest_wib"] = block_time_wib(fm["earliest_block"])
        r["first_mint"] = fm
    out[name] = r
json.dump(out, open(BASE + "/run-2026-11-08-2031-webfind-verify.json", "w"), indent=1, default=str)
print("WROTE run-2026-11-08-2031-webfind-verify.json", flush=True)
