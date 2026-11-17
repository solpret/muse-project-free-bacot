#!/usr/bin/env python3
"""Run 1731 triage-2: single-call reads (avoid batch-revert artifacts).
Motor: PRICE/AGENT_FREE_CAP/X_FREE_CAP/agentFreeUsed/xFreeUsed/freeUsedByWallet/freeLeft.
Marbleworks: quote(user,1)/freeAvailable(user)/freeMinted/mintOpen/PRICE.
Osiris: hasFreeMinted(user)/freeMinted/mintOpen/owner.
ORDIagent: freeTaken()/freeClaimed()/sharesMinted().
0x13A1Ebc9: FREE_SUPPLY/freeRemaining/mintOpen/totalSupply + code registry bytes.
Read-only; writes run-2026-11-09-1731-triage2.json."""
import json, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
REG = "60b9262456de011f7d15a54CdD8c48bAaa8B022F".lower()
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def call(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]})
            if isinstance(res, dict):
                if "result" in res: return res["result"]
                if "error" in res: return {"error": str(res["error"])[:120]}
        except Exception as e:
            continue
    return None
def code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=25)
            if isinstance(r, dict) and r.get("result"): return r["result"]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None
def rd(addr, sig, *args):
    data = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x"): data += enc(a)
        else: data += str(int(a)).rjust(64, "0") if not isinstance(a, str) else a.rjust(64, "0")
    r = call(addr, data)
    if isinstance(r, dict): return r
    return to_int(r)
out = {"block": block(), "run": "2026-11-09-1731"}
MOTOR = "0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5"
out["motor"] = {v: rd(MOTOR, v) for v in
                ["PRICE()", "AGENT_FREE_CAP()", "X_FREE_CAP()", "agentFreeUsed()",
                 "xFreeUsed()", "freeLeft()", "totalSupply()", "paidMinted()", "mintOpen()"]}
out["motor"]["freeUsedByWallet_user"] = rd(MOTOR, "freeUsedByWallet(address)", USER)
out["motor"]["mintedBy_user"] = rd(MOTOR, "mintedBy(address)", USER)
print("MOTOR", json.dumps(out["motor"]), flush=True)
MARB = "0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0"
out["marbleworks"] = {"freeMinted": rd(MARB, "freeMinted()"), "FREE_SUPPLY": rd(MARB, "FREE_SUPPLY()"),
                      "mintOpen": rd(MARB, "mintOpen()"), "PRICE": rd(MARB, "price()"),
                      "totalSupply": rd(MARB, "totalSupply()"), "soldOut": rd(MARB, "soldOut()"),
                      "freeAvailable_user": rd(MARB, "freeAvailable(address)", USER),
                      "freeUsed_user": rd(MARB, "freeUsed(address)", USER)}
# quote(address,uint256) returns (freeShares?, cost?) - raw return kept
q = call(MARB, sel("quote(address,uint256)") + enc(USER) + "1".rjust(64, "0"))
out["marbleworks"]["quote_user_1_raw"] = q
print("MARBLEWORKS", json.dumps(out["marbleworks"]), flush=True)
OSI = "0xd6fcf9db58a559aafbbf9fd823f4f081e6701311"
out["osiris"] = {"freeMinted": rd(OSI, "freeMinted()"), "FREE_SUPPLY": rd(OSI, "FREE_SUPPLY()"),
                 "mintOpen": rd(OSI, "mintOpen()"), "owner": rd(OSI, "owner()"),
                 "hasFreeMinted_user": rd(OSI, "hasFreeMinted(address)", USER)}
print("OSIRIS", json.dumps(out["osiris"]), flush=True)
ORD = "0x7D10516D08f3bE98aaFD9Ac4169E6Cc30D6bCeB8"
out["ordiagent"] = {"freeTaken": rd(ORD, "freeTaken()"), "freeClaimed": rd(ORD, "freeClaimed()"),
                    "sharesMinted": rd(ORD, "sharesMinted()"), "FREE_SHARES": rd(ORD, "FREE_SHARES()")}
print("ORDIAGENT", json.dumps(out["ordiagent"]), flush=True)
NEW = "0x13A1Ebc988977f8AF0c2983027FF72f4D81BEF00"
c = code(NEW)
out["new_13A1"] = {"FREE_SUPPLY": rd(NEW, "FREE_SUPPLY()"), "freeRemaining": rd(NEW, "freeRemaining()"),
                   "mintOpen": rd(NEW, "mintOpen()"), "totalSupply": rd(NEW, "totalSupply()"),
                   "code_len": len(c) if c else None, "registry_bytes": (REG in c.lower()) if c else None}
print("NEW13A1", json.dumps(out["new_13A1"]), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-09-1731-triage2.json", "w"), indent=1)
print("TRIAGE2 DONE", flush=True)
