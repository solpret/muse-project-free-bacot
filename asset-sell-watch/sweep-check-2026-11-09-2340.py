#!/usr/bin/env python3
"""Sweep-check 2026-11-09 ~23:40 WIB — saldo live semua token kandidat di wallet agent.
Read-only: balanceOf per token + BNB native + WBNB. Output JSON ke stdout."""
import json, urllib.request, sys

AGENT = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
ENDPOINTS = [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed1.bnbchain.org",
    "https://bsc-dataseed2.bnbchain.org",
    "https://bsc-dataseed3.bnbchain.org",
    "https://bsc-dataseed1.defibit.io",
]
TOKENS = [
    ("POA", "0x21bc810818d9c9c767ba73c543f67a989fb5a543", 18),
    ("BNBbaby", "0xd0079025a9bb66a7a1de991de2e4326faba35729", 18),
    ("PATCH", "0xBbA053567846842F95C060867a5C9eb6b3983c80", 18),
    ("QAGENT", "0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", 18),
    ("YYDS", "0xd23be069c3c3a7f631af52584a16a9e46bb41da1", 18),
    ("BIA", "0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", 18),
    ("PACTURE", "0x10b80088fDAf9363d83671BE66b64f231f9e92f6", 18),
    ("ORBITA", "0x19b8d7613A6C2E4168a6a0Bb97ca0c842035d709", 18),
    ("WW3", "0xf62628D99B28535ee593Ab5D6dFE7D914f5edca0", 18),
    ("POSTAGE", "0x6C310EABEdFD4eEd6148bf2C07241FB45a52FB42", 18),
    ("MALTA", "0x728095Ab0BD71636Db5DA4E2A6d7f5cc73729fc0", 18),
    ("JINMA", "0xe4517E6718b24D5725956ac7A90686592a7b1539", 18),
    ("Amber", "0x4008a353d3476884DC8Cd8Cd8Cd8fBf314970C8409FB22", 8),
    ("BNBS-OLD", "0x171F264F938D55D968AfC5d6B133C4157A61f05F", 18),
    ("MOTA", "0xfdd44c29af794249318930cebbf9cc3dfff9e4b1", 18),
    ("MWGL", "0x458ba0b810ff314b1d7d41a0f0f209706dcf949b", 18),
    ("STOCKMEMES", "0x8c36223b4f460521ca49d2ce43a1b60c8185ba80", 18),
    ("CAIBAO", "0x33d612C10b509aBD8723b7E0E11e1CFFB02f5a27", 18),
    ("WBNB", WBNB, 18),
]

def rpc(method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last_err = None
    for ep in ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=12) as r:
                res = json.loads(r.read().decode())
            if "result" in res:
                return res["result"]
            last_err = res.get("error", res)
        except Exception as e:
            last_err = str(e)
    return {"error": str(last_err)}

def balance_of(token):
    data = "0x70a08231" + "000000000000000000000000" + AGENT[2:].lower()
    return rpc("eth_call", [{"to": token, "data": data}, "latest"])

out = {"agent": AGENT, "balances": {}}
bnb = rpc("eth_getBalance", [AGENT, "latest"])
out["bnb_native_wei"] = bnb if isinstance(bnb, str) else bnb
for sym, addr, dec in TOKENS:
    r = balance_of(addr)
    if isinstance(r, str) and r.startswith("0x"):
        raw = int(r, 16)
        out["balances"][sym] = {"token": addr, "raw": str(raw), "human": raw / (10 ** dec), "decimals": dec}
    else:
        out["balances"][sym] = {"token": addr, "raw": None, "error": str(r)}
print(json.dumps(out, indent=1))
