#!/usr/bin/env python3
"""Run 2026-11-08 20:31 WIB: track-C watchlist fresh re-read + Zorrie/Gloop/Skunk + binanceai.
Read-only; writes only its own output JSON. None = UNVERIFIED (revert/RPC artifact), never zero.
Per-item error tolerant raw batch (fast_rpc quirk: one revert kills whole batch)."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u256(n): return ("%064x" % n)
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def raw_batch(addr, calls_spec):
    """calls_spec: list of (key, data). Returns {key: int|None} or None on transport fail."""
    calls = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
              "params": [{"to": addr, "data": data}, "latest"]}
             for i, (_, data) in enumerate(calls_spec)]
    for ep in EPS:
        try:
            out = _fr_post(ep, calls, timeout=10, retries=0)
            if not isinstance(out, list) or len(out) != len(calls):
                continue
            res = {}
            for item, (key, _) in zip(out, calls_spec):
                if isinstance(item, dict) and "error" in item:
                    res[key] = None
                else:
                    res[key] = to_int(item.get("result")) if isinstance(item, dict) else None
            return res
        except Exception:
            continue
    return None

def noarg(sig): return (sig.split("(")[0], sel(sig))
def uarg(sig): return (sig.split("(")[0] + "_user", sel(sig) + enc_addr(USER))
def quote_user():
    return ("quote_user", sel("quote(address,uint256)") + enc_addr(USER) + enc_u256(1))

def call_quote_raw(addr):
    """quote(user,1) returns tuple; decode first two words separately."""
    data = sel("quote(address,uint256)") + enc_addr(USER) + enc_u256(1)
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=10, retries=0)
            if isinstance(out, dict) and "result" in out and out["result"] not in (None, "0x"):
                h = out["result"][2:]
                words = [int(h[i:i+64], 16) if len(h) >= i+64 else None for i in range(0, min(len(h), 128), 64)]
                return {"raw": out["result"], "word0": words[0] if words else None,
                        "word1": words[1] if len(words) > 1 else None}
            if isinstance(out, dict) and "error" in out:
                return {"raw": None, "word0": None, "word1": None, "error": str(out["error"])[:80]}
        except Exception as e:
            continue
    return {"raw": None, "word0": None, "word1": None}

TC_VIEWS = [noarg("totalSupply()"), noarg("freeMinted()"), noarg("freeSharesRemaining()"),
            noarg("totalFreeShares()"), noarg("totalShares()"), noarg("freeLeft()"),
            noarg("freeRemaining()"), noarg("totalFreeClaimed()"), noarg("FREE_SHARES()"),
            noarg("MAX_FREE()"), noarg("launched()"), noarg("mintOpen()"),
            noarg("phase()"), noarg("state()"), uarg("balanceOf(address)"),
            uarg("freeClaimed(address)"), uarg("freeUsed(address)"),
            uarg("freeSharesClaimedBy(address)"), uarg("freeLeft(address)"),
            noarg("freeClaimed()"), noarg("freeShares()")]

TC = {
    "AGENT MALTA": "0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0",
    "DeY": "0xDB062c12bF0a14227e7Fe896a988950b050B51C1",
    "FANBEIMAO-824d": "0x824d1e5c1395ed7543854fCd9e4da6D3F358De16",
    "NUSA": "0x7D08289E962f5aEc00d56D67322eb2FD056B687c",
    "NIULAI": "0x15e47c22df42D94Fa2f0aD078Fec5Bea6453d5cF",
    "OSK": "0xfe8919306a1e587c66bd913ffa6bf49e9aff6b37",
    "KillZero-K0-sale": "0x87ad9c1617ceb65f1b56f2ee06FE193F60aACF97",
    "DROID": "0xFcF6388DD3bcC674c095273aB479C7e54dd5E177",
    "960E-sale": "0x960E7e4126b97679053B8416fA59f13508be88bf",
    "Agentidbsc": "0x716BFaB3B7b0301D17Af0fF4c50a880C7721F39C",
    "CHTCI": "0x050a11c2bfcf881b546983a20550a0e409bf69da",
    "BoxBigem-3Ee9": "0x3Ee92296D663378D42521273aAA4779BDa8e25dD",
    "Pacture": "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9",
    "FABE": "0xFabE022a5943462fee1Bd221791945DA57510BE8",
    "Kiko9393": "0x34aE861Fbeb2aaA6071248F8a27AcE5f30aA7bBf",
}

out = {"started_wib": "2026-11-08 20:31 WIB", "track_c_watchlist": {}, "zgs": {}, "binanceai": {}}
for name, addr in TC.items():
    got = raw_batch(addr, TC_VIEWS)
    d = {"address": addr}
    if got is None:
        d["_batch_fail"] = True
        for k, _ in TC_VIEWS: d[k] = None
    else:
        d.update(got)
    d["quote_user_1"] = call_quote_raw(addr)
    out["track_c_watchlist"][name] = d
    print(f"TC {name} totalSupply={d.get('totalSupply')} freeMinted={d.get('freeMinted')} "
          f"freeSharesRemaining={d.get('freeSharesRemaining')} totalFreeShares={d.get('totalFreeShares')} "
          f"launched={d.get('launched')} mintOpen={d.get('mintOpen')} phase={d.get('phase')} state={d.get('state')} "
          f"bal_user={d.get('balanceOf_user')} freeClaimed_user={d.get('freeClaimed_user')} "
          f"freeUsed_user={d.get('freeUsed_user')} quote={d['quote_user_1'].get('word0')},{d['quote_user_1'].get('word1')}",
          flush=True)

# Zorrie / Gloop / Skunk Hollow
ZGS = {
    "Zorrie": ("0x47feee72353358a61618cE640265F9f406f88E47",
               [noarg("totalMinted()"), noarg("maxSupply()"), noarg("mintOpen()"),
                uarg("freeMintedPerWallet(address)"), uarg("balanceOf(address)")]),
    "Gloop": ("0x79d1821bC6E7576Aac4422BEAD0951A4adc7075a",
              [noarg("totalMinted()"), noarg("totalSupply()"), noarg("mintOpen()"),
               noarg("MINT_START()"), uarg("hasMinted(address)"), uarg("balanceOf(address)")]),
    "Skunk Hollow": ("0x88E4b613609af6C479F11D78e5a696d84B78993B",
                     [noarg("totalSkunksMinted()"), noarg("freeSkunksRemaining()"),
                      noarg("freeSkunksClaimed()"), noarg("freeWindowOpen()"),
                      noarg("FREE_SKUNKS_TOTAL()"), uarg("freeClaimedBy(address)"),
                      uarg("balanceOf(address)")]),
}
for name, (addr, views) in ZGS.items():
    got = raw_batch(addr, views)
    d = {"address": addr}
    if got is None:
        d["_batch_fail"] = True
        for k, _ in views: d[k] = None
    else:
        d.update(got)
    out["zgs"][name] = d
    print(f"ZGS {name} {d}", flush=True)

# binanceai track-B
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
b = raw_batch(MINT, [noarg("launched()"), noarg("failed()"), noarg("isRefundPhase()"),
                     noarg("totalShares()"), uarg("tokenClaimed(address)")])
tok = raw_batch(TOKEN, [uarg("balanceOf(address)"), noarg("totalSupply()")])
out["binanceai"] = {"mint": MINT, "token": TOKEN, "views": b, "tokenViews": tok}
print("BINANCEAI", b, tok, flush=True)

out["elapsed_s"] = round(time.time() - T0, 1)
with open(BASE + "/run-2026-11-08-2031-trackc-zgs-binanceai.json", "w") as f:
    json.dump(out, f, indent=1)
print(f"DONE in {out['elapsed_s']}s", flush=True)
