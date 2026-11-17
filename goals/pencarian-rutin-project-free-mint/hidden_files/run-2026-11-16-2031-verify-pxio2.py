#!/usr/bin/env python3
"""PXIO round 2: quote/canMint/pricing + site pointers. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
ADDR = "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def call(data):
    payload = {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]}
    out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
    try: return json.loads(out).get("result")
    except Exception: return None
def u(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def s_decode(r):
    if not r or len(r) < 130: return r
    try:
        off = int(r[2:66],16); ln = int(r[66:130],16)
        return bytes.fromhex(r[130:130+ln*2]).decode(errors="replace")
    except Exception: return r
tests = [
    ("quote(user,1)", sel("quote(address,uint256)") + enc_addr(USER) + enc_u(1)),
    ("quote(user,2)", sel("quote(address,uint256)") + enc_addr(USER) + enc_u(2)),
    ("canMint(user)", sel("canMint(address)") + enc_addr(USER)),
    ("mintableBy(user)", sel("mintableBy(address)") + enc_addr(USER)),
    ("hasAgentId(user)", sel("hasAgentId(address)") + enc_addr(USER)),
    ("unitPrice(1)", sel("unitPrice(uint256)") + enc_u(1)),
    ("unitPrice(2)", sel("unitPrice(uint256)") + enc_u(2)),
    ("PRICE_2_TO_10", sel("PRICE_2_TO_10()")),
    ("PRICE_11_TO_20", sel("PRICE_11_TO_20()")),
    ("PRICE_21_TO_30", sel("PRICE_21_TO_30()")),
    ("MAX_PER_WALLET", sel("MAX_PER_WALLET()")),
    ("contractURI()", sel("contractURI()")),
    ("externalUrl()", sel("externalUrl()")),
    ("xUrl()", sel("xUrl()")),
]
res = {}
for name, data in tests:
    r = call(data)
    if name in ("contractURI()","externalUrl()","xUrl()"):
        # may be base64 json or plain string; try decode
        v = s_decode(r)
        res[name] = v
        print(name, "->", str(v)[:300], flush=True)
    else:
        # quote may return tuple (price, ...) - show raw
        res[name] = r
        print(name, "->", r, flush=True)
json.dump(res, open("run-2026-11-16-2031-verify-pxio2.json","w"), indent=1)
print("DONE")
