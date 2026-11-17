#!/usr/bin/env python3
"""Probe new S1-positive Sourcify contract 0xF3A8A59F... (verified 07:31:19Z =
14:31:19 WIB) for run 2026-11-13 14:31. Read-only; one JSON-RPC batch.
Determines NFT vs share-sale shape, free pool, user slot, launch time."""
import json, subprocess, sys, importlib.util
_spec = importlib.util.spec_from_file_location(
    "verify1431",
    "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-13-1431-verify.py")
_verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_verify)
read_one, USER, AGENT_ID = _verify.read_one, _verify.USER, _verify.AGENT_ID
enc_addr, enc_u = _verify.enc_addr, _verify.enc_u
ADDR = "0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D"
VIEWS = [
    ("name", "name()"), ("symbol", "symbol()"), ("decimals", "decimals()"),
    ("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
    ("freeMinted", "freeMinted()"), ("freeRemaining", "freeRemaining()"),
    ("FREE_SUPPLY", "FREE_SUPPLY()"), ("FREE_PER_WALLET", "FREE_PER_WALLET()"),
    ("MAX_SUPPLY", "MAX_SUPPLY()"),
    ("saleStart", "saleStart()"), ("saleEnd", "saleEnd()"),
    ("mintStart", "mintStart()"), ("mintOpensAt", "mintOpensAt()"),
    ("saleOpen", "saleOpen()"), ("mintOpen", "mintOpen()"),
    ("isFreeOpen", "isFreeOpen()"),
    ("freeAvailable_user", "freeAvailable(address)", enc_addr(USER)),
    ("quote_user_1", "quote(address,uint256)", enc_addr(USER) + enc_u(1)),
    ("freeClaimed_user", "freeClaimed(address)", enc_addr(USER)),
    ("agentIdRegistry", "agentIdRegistry()"),
    ("owner", "owner()"),
    ("balanceOf_user", "balanceOf(address)", enc_addr(USER)),
]
r = read_one("F3A8", ADDR, VIEWS)
out = {"address": ADDR, "views": r.get("views", {}),
       "summary": {k: v for k, v in r.get("views", {}).items() if v is not None},
       "endpoint": r.get("endpoint"), "errors": r.get("errors")}
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-13-1431-newcontract.json", "w"), indent=1)
