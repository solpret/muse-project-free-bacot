#!/usr/bin/env python3
"""Verify PXIO Miners 0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab (Boltbook new lead run 2031). Read-only."""
import json, subprocess, urllib.request
ADDR = "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def call(to, data):
    payload = {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}
    out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
    try: return json.loads(out).get("result")
    except Exception: return None
def u(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
VIEWS = ["name()","symbol()","totalSupply()","totalMinted()","freeMinted()","freeClaimed()","FREE_SUPPLY()","FREE_MAX()","FREE_CAP()","MAX_SUPPLY()","mintOpen()","saleOpen()","mintPrice()","priceFor(address)","freeLeft()","freeSupply()","mintStart()","START_TIME()","startTime()","saleStart()","owner()","freeMintedBy(address)","mintedBy(address)","balanceOf(address)"]
res = {}
for v in VIEWS:
    sig = v
    args = []
    if "(address)" in v: args = [USER]
    data = sel(sig)
    for a in args: data += enc_addr(a)
    r = call(ADDR, data)
    if v in ("name()","symbol()"):
        if r and len(r) > 130:
            try:
                off = int(r[2:66],16); ln = int(r[66:130],16)
                res[v] = bytes.fromhex(r[130:130+ln*2]).decode(errors="replace")
            except Exception: res[v] = r
        else: res[v] = r
    else:
        res[v] = u(r) if r else None
    print(v, "->", res[v], flush=True)
# bytecode registry check
payload = {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[ADDR,"latest"]}
out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
code = json.loads(out).get("result","") or ""
print("code_len:", len(code), "registry_bytes:", "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code.lower())
# block number
payload = {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}
out = subprocess.run(["curl","-sL","--max-time","30","-X","POST",EP,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True, timeout=40).stdout
print("head:", int(json.loads(out)["result"],16))
# Sourcify
try:
    with urllib.request.urlopen(f"https://sourcify.dev/server/v2/contract/56/{ADDR}", timeout=30) as r:
        d = json.load(r)
    print("sourcify:", d.get("match"), d.get("verifiedAt"))
except Exception as e:
    print("sourcify: 404/unverified", str(e)[:80])
json.dump(res, open("run-2026-11-16-2031-verify-pxio.json","w"), indent=1)
print("DONE")
