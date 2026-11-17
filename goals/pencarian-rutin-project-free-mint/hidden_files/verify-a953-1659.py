#!/usr/bin/env python3
"""Hot-leg 2026-11-16 16:59 WIB — leg 3 on-chain verify of new S1 contract
0xA9531f2C18E9398b50c13f1a108EbE7462927154. Read-only, single JSON-RPC batch."""
import json, subprocess
from Crypto.Hash import keccak

ADDR = "0xA9531f2C18E9398b50c13f1a108EbE7462927154"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")

def data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d

VIEWS = [
    ("name", "name()", []), ("symbol", "symbol()", []),
    ("FREE_SUPPLY", "FREE_SUPPLY()", []), ("freeMinted", "freeMinted()", []),
    ("freeRemaining", "freeRemaining()", []), ("isFreeOpen", "isFreeOpen()", []),
    ("saleOpen", "saleOpen()", []), ("saleStart", "saleStart()", []),
    ("saleEnd", "saleEnd()", []), ("SALE_END", "SALE_END()", []),
    ("FREE_PER_WALLET", "FREE_PER_WALLET()", []),
    ("freeAvailable_user", "freeAvailable(address)", [USER]),
    ("freeMintedBy_user", "freeMintedBy(address)", [USER]),
    ("mintedBy_user", "mintedBy(address)", [USER]),
    ("balanceOf_user", "balanceOf(address)", [USER]),
    ("costOf_user_1", "costOf(address,uint256)", [USER, 1]),
    ("quote_user_1_cost", "quote(address,uint256)", [USER, 1]),
    ("totalSupply", "totalSupply()", []), ("totalMinted", "totalMinted()", []),
    ("maxSupply", "maxSupply()", []), ("agentIdRegistry", "agentIdRegistry()", []),
    ("owner", "owner()", []), ("contractURI", "contractURI()", []),
    ("mintOpen", "mintOpen()", []), ("saleClosed", "saleClosed()", []),
]

def to_int(h):
    try: return int(h, 16)
    except Exception: return None

def dec_str(hexs):
    try:
        b = bytes.fromhex(hexs[2:])
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception as e:
        return f"<decode-fail {e}>"

calls = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
          "params": [{"to": ADDR, "data": data(sig, args)}, "latest"]}
         for i, (_, sig, args) in enumerate(VIEWS)]
blk_call = {"jsonrpc": "2.0", "id": 999, "method": "eth_blockNumber", "params": []}

out = {}
for ep in EPS:
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "30", "-X", "POST", ep,
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps(calls + [blk_call])],
                           capture_output=True, text=True, timeout=40)
        res = json.loads(r.stdout)
        if isinstance(res, list) and len(res) == len(calls) + 1:
            out["endpoint"] = ep
            out["block"] = to_int(res[-1].get("result", "0x0"))
            for (key, sig, args), it in zip(VIEWS, res):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    h = it["result"]
                    if key in ("name", "symbol", "contractURI"):
                        out[key] = dec_str(h)
                    elif key == "quote_user_1_cost":
                        out[key] = to_int(h[2:66]) if len(h) >= 66 else h
                    elif key in ("agentIdRegistry", "owner"):
                        out[key] = "0x" + h[-40:] if len(h) >= 42 else h
                    else:
                        out[key] = to_int(h[2:66]) if len(h) >= 66 else h
            break
        out.setdefault("errors", []).append(f"{ep}: bad shape {str(res)[:120]}")
    except Exception as e:
        out.setdefault("errors", []).append(f"{ep}: {str(e)[:120]}")

json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/verify-a953-1659.json", "w"), indent=1)
print(json.dumps(out, indent=1))
