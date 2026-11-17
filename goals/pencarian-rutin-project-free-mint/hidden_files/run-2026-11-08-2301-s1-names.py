#!/usr/bin/env python3
"""Run 2301 web: read name()/symbol()/contractURI() for the 3 new SALE-S1 contracts
(2 fresh feed + Hexrotta) — method (H)/(J) gate evidence. Read-only eth_call.
Saves run-2026-11-08-2301-s1-names.json next to this script."""
import base64, json, pathlib, urllib.request
from Crypto.Hash import keccak

BASE = pathlib.Path.home() / "workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
EPS = ["https://bsc-dataseed.binance.org", "https://bsc-dataseed1.defibit.io",
       "https://bsc-dataseed2.bnbchain.org"]
ADDS = {
    "0xD743c793b23D1adE2099892B010d4F4530d44E0a": "feed-2301 S1 (verifiedAt 16:04:45Z)",
    "0x7F00b3Aa3A3e41dc145180C4ED8a24eE568eaED4": "feed-2301 S1 (verifiedAt 15:56:08Z)",
    "0x25256ee137d4b2b9d440431ae8fc8fd9770c50a9": "Hexrotta HEXRTA (Boltbook 23:21 WIB)",
}

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def eth_call(addr, data, ep):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]}).encode()
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("result")

def read(addr, sig):
    last = "empty result (all endpoints)"
    for ep in EPS:
        try:
            raw = eth_call(addr, sel(sig), ep)
            if raw not in (None, "0x", ""):
                return raw, ep
        except Exception as e:
            last = f"{type(e).__name__}: {e} ({ep})"
    return None, last

def decode_str(raw):
    # ABI-encoded string: offset(32) + len(32) + data
    try:
        b = bytes.fromhex(raw[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode("utf-8", "replace")
    except Exception as e:
        return f"<decode-error {e}>"

out = {"run": "2301", "contracts": {}}
for addr, src in ADDS.items():
    rec = {"source": src}
    raw, ep = read(addr, "name()")
    rec["name"] = decode_str(raw) if raw else None
    raw, ep = read(addr, "symbol()")
    rec["symbol"] = decode_str(raw) if raw else None
    raw, ep = read(addr, "contractURI()")
    if raw:
        uri = decode_str(raw)
        rec["contractURI_raw"] = uri[:600]
        try:
            if uri.startswith("data:application/json;base64,"):
                rec["contractURI_json"] = json.loads(
                    base64.b64decode(uri.split(",", 1)[1]).decode())
            elif uri.startswith("{"):
                rec["contractURI_json"] = json.loads(uri)
        except Exception as e:
            rec["contractURI_decode_error"] = str(e)
    else:
        rec["contractURI_raw"] = None
    out["contracts"][addr] = rec
    print(addr, "|", rec.get("name"), "|", rec.get("symbol"), "| contractURI:",
          (rec.get("contractURI_json") or {}).get("external_link") if rec.get("contractURI_json") else rec.get("contractURI_raw"))

json.dump(out, open(BASE / "run-2026-11-08-2301-s1-names.json", "w"), indent=1)
print("saved", BASE / "run-2026-11-08-2301-s1-names.json")
