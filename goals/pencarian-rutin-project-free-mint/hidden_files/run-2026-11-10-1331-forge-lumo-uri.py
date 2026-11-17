#!/usr/bin/env python3
"""Run 1331 contractURI/tokenURI + Sourcify metadata for Forge Pass + LUMO (read-only)."""
import json, subprocess, urllib.request, base64
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def call(addr, data):
    for ep in EPS:
        try:
            r = post_rpc(ep, [{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}])
            if isinstance(r, list) and r and "result" in r[0]: return r[0]["result"]
        except Exception: continue
    return None
def dec_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        off = int.from_bytes(b[32:64], "big"); ln = int.from_bytes(b[64+off-32:64+off] if False else b[32+off:64+off], "big") if False else None
        # standard ABI string: offset(32) length(32) data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception as e:
        return f"<decode err {e}>"
for name, addr in [("Forge Pass","0x733358348e07c46332a01c76e2bf6ee5d40a6d89"),("LUMO","0x1e340592665889735c1f871aa13d038fa58bd09e")]:
    print("==", name)
    cu = call(addr, sel("contractURI()"))
    print(" contractURI:", dec_str(cu)[:500] if cu else None)
    # tokenURI(1) for Forge (token 1 exists), tokenURI(0)? LUMO token ids start 1; try 1
    tu = call(addr, sel("tokenURI(uint256)") + "0000000000000000000000000000000000000000000000000000000000000001")
    print(" tokenURI(1):", dec_str(tu)[:800] if tu else None)
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=metadata", headers={"User-Agent":"free-bacot/1331"})
        with urllib.request.urlopen(req, timeout=30) as r:
            meta = json.loads(r.read().decode())
        m = meta.get("metadata", {})
        print(" sourcify metadata keys:", list(m.keys()) if isinstance(m, dict) else type(m))
        print("  ", json.dumps(m, indent=1)[:1200])
    except Exception as e:
        print(" sourcify metadata ERROR:", e)
