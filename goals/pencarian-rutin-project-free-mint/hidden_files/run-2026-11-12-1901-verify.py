#!/usr/bin/env python3
"""Verify for free-mint-search run 2026-11-12 19:01 WIB.
Priority re-reads (same 21 targets as run 1401) + the 5 new findings from
run 1401 with extra free/age deep-dive views + contractURI() string reads.
Read-only; writes run-2026-11-12-1901-verify.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            return {key: (None if (isinstance(it, dict) and "error" in it)
                          else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, key in zip(res, keys)}
        except Exception:
            continue
    return None

def raw_string(addr, sig):
    """eth_call returning a string/bytes; decode ABI string or raw bytes."""
    data = sel(sig)
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            r = res.get("result") if isinstance(res, dict) else None
            if not r or r == "0x":
                return None
            b = bytes.fromhex(r[2:])
            if len(b) >= 64:
                off = int.from_bytes(b[:32], "big")
                ln = int.from_bytes(b[32:64], "big")
                if 0 < ln < 10000 and off + 32 + ln <= len(b):
                    try:
                        return b[32 + off:32 + off + ln].decode("utf-8", errors="replace")
                    except Exception:
                        pass
            try:
                return b.decode("utf-8", errors="replace").strip("\x00")
            except Exception:
                return r[:200]
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

LEAN = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
        "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
        "freeUsed(address)", "mintedBy(address)", "freeMintedBy(address)", "freeLeft()",
        "freeAvailable(address)", "launched()", "freeSharesLeft()", "openedAt()",
        "freeSharesRemaining()", "mintStart()", "saleStart()", "saleEnd()", "PRICE()",
        "price()", "currentState()", "finalized()", "refunding()", "totalFreeMinted()",
        "FREE_SHARES()", "freeLeftFor(address)"]
OLIVER_EXTRA = ["START_TIME()", "startTime()", "mintOpensAt()", "freeRemaining()",
                "paidMinted()", "FREE_MAX()", "PAID_MAX()"]
FINDING_EXTRA = ["START_TIME()", "startTime()", "mintOpensAt()", "freeRemaining()",
                 "paidMinted()", "freeSupply()", "MAX_FREE()", "freeCap()",
                 "totalFreeSupply()", "agentFreeSupply()", "freeMax()",
                 "FREE_MINT_SUPPLY()", "agentFreeUsed()", "deadline()", "DEADLINE()",
                 "freeMintedBy(address)", "totalFreeMinted()"]

TARGETS = [
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"),
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459"),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA"),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0"),
    ("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F"),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f"),
    ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0"),
    ("LuckyCatch", "0xD405C90079c594DA2456F5b37B4158A12f1382e5"),
    ("BinanceLife", "0x4367b86F889014e6fD57fE812B86A581b913C645"),
    ("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("Kongtou-AirdropCnNFT", "0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"),
    ("0x7Eb9", "0x7Eb92041aa3037e39baA88154F279e3D9F85c593"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
    ("AgenticGangster", "0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3"),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("OLIVER AGENTS", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("AIRDROP", "0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9"),
    ("Cobalt Agent", "0x7ef49be2a9ade4fae0888f4065c8f122a146f6d0"),
    ("NAPPER", "0x3964BFc3354C0d18886dcAD52Abc55C689e6A1d4"),
    ("DACIT", "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd"),
    ("SYNERGYPASS", "0xb8a990e16fd66d398cc27d0c8bdb11524bc0dc8e"),
    ("DRAGON-0xad0d", "0xad0d8ac3d61fc8ab397b7136c69fcbf1281a4998"),
    ("AGENT COSMOS", "0x3Aeda314ec05BC22E3c26a543E16Df2B8cC8fe69"),
    ("AGENT ID card", "0x486d0947caa3d70c19e38f6c789489d39291e9e7"),
    ("RunicKey", "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"),
    ("Thor", "0x8aa9d6a09caf475593852e681b58b26dc94edd56"),
    ("Vexa", "0x6c17af4fac529e5679686e121a75e85b1063cd45"),
    ("ROBO", "0xf8b6867efa31bbd76e10d0bcefbdb22abc6b07fb"),
    ("Kitebots", "0x8B8e59c014eb3E229e043AE8F3B0D7E201d21DB0"),
    ("Dragon Agent", "0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6"),
]

block = get_block()
res = {"started_wib": "2026-11-12 19:01 WIB", "block": block, "reads": {}}
for name, addr in TARGETS:
    views = LEAN + (OLIVER_EXTRA if name == "OLIVER AGENTS" else [])
    if name in ("Cobalt Agent", "NAPPER", "DACIT", "SYNERGYPASS", "DRAGON-0xad0d", "AGENT COSMOS", "AGENT ID card", "RunicKey", "Thor", "Vexa", "ROBO"):
        views = LEAN + FINDING_EXTRA
    r = raw_batch(addr, views)
    e = {"address": addr, "views": r}
    if r:
        e["summary"] = {k: v for k, v in r.items() if v is not None}
    # contractURI string read (age/site pointer deep-dive) for the 5 findings + OLIVER
    if name in ("Cobalt Agent", "NAPPER", "DACIT", "SYNERGYPASS", "DRAGON-0xad0d", "OLIVER AGENTS", "AGENT COSMOS", "RunicKey", "Thor", "Vexa", "ROBO"):
        e["contractURI"] = raw_string(addr, "contractURI()")
    res["reads"][name] = e
    print(name, e.get("summary", "BATCH-FAIL"), "contractURI:", str(e.get("contractURI"))[:120] if e.get("contractURI") else None, flush=True)
res["elapsed_s"] = round(time.time() - t0, 1)
json.dump(res, open(BASE + "run-2026-11-12-1901-verify.json", "w"), indent=1)
print("BLOCK", block, "ELAPSED", res["elapsed_s"])
