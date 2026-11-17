#!/usr/bin/env python3
"""Run 70: verify the single AFeng mint-pattern contract (read-only)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
from Crypto.Hash import keccak

def call(addr, data):
    try:
        return fast_rpc.race("eth_call", [{"to": addr, "data": data}, "latest"])
    except Exception as e:
        return f"ERROR:{e}"

def sel4(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def read_str(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR") or len(r) < 130:
        return f"unreadable({str(r)[:60]})"
    try:
        ln = int(r[130:194], 16)
        return bytes.fromhex(r[194:194 + ln * 2]).decode("utf-8", "replace")
    except Exception as e:
        return f"decode-error {e}"

def read_uint(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR"):
        return f"unreadable({str(r)[:60]})"
    try:
        return int(r, 16)
    except Exception:
        return f"raw:{r[:80]}"

def read_addr(addr, sig):
    r = call(addr, sel4(sig))
    if not isinstance(r, str) or r.startswith("ERROR"):
        return f"unreadable({str(r)[:60]})"
    try:
        return "0x" + r[-40:]
    except Exception:
        return f"raw:{r[:80]}"

C = "0x636fdfa9bc3db42c690c09e87b9017d05b36c743"
out = {
    "contract": C,
    "name": read_str(C, "name()"),
    "symbol": read_str(C, "symbol()"),
    "decimals": read_uint(C, "decimals()"),
    "totalSupply": read_uint(C, "totalSupply()"),
    "owner": read_addr(C, "owner()"),
}
print(json.dumps(out, indent=1))
json.dump(out, open("run70-afeng-verify.json", "w"), indent=1)
# compare with run-3 ETHBack tracker contract
C3 = "0x09bf84e67785974021222b72660b94d81e2901e6"
out3 = {"contract": C3, "name": read_str(C3, "name()"), "symbol": read_str(C3, "symbol()"),
        "decimals": read_uint(C3, "decimals()"), "totalSupply": read_uint(C3, "totalSupply()")}
print(json.dumps(out3, indent=1))
json.dump(out3, open("run70-afeng-verify-run3.json", "w"), indent=1)
