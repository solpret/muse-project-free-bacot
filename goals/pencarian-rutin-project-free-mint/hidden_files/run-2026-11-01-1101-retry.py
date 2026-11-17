#!/usr/bin/env python3
"""Retry failed 11:01 reads with direct _single calls, sequential across Binance dataseeds, no breaker/race."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
SEL = "0x18160ddd"
names = {
 "Agent Periodic Lab": "0xfE5Ab5ce9b1D86a55d70E7D0573a14D559029C18",
 "AgentPad Pass": "0xf66fbea12f23D9928D9032bb258Fbc25203957A0",
 "Alibaba & The 70 Thieves": "0xA2F2ffCA66D324af5ED58e5c98c9D6f544b13303",
 "BANKS / Pixel Vaults": "0xaCe6E160FFA40C0d27F92e9349EEdbb1fA2BE0B5",
 "Brushborn": "0x5d43566e40E2e6D396EC10224363E5cAcFc40Cf0",
 "CIOW Citizens": "0xa81b3DcD5c181C0E2E1603e49487ca4ACc814974",
 "Chocho Agent": "0x34fc2a5cff16969e814d6d5e8ed13dcb00f0f943",
 "CyberRonin": "0x6a943b12a0377b165f7923eb5c49d3e4c2966d50",
 "Lodepass": "0x31b074C8e77e44F29df285F19d4fc76E6D927d01",
 "MARS PLOTS": "0xbc2c4a71791fb86d14a2a859b0253aa3bbaeb34c",
 "Synth Ape Syndicate": "0x68869D4EDc15Ec2FBA0eaCfe1486caf9d0C37572",
 "UMBRA Agents": "0x9C0309dC71F89d7f4F0b55d934213C28F10C9e23",
 "URBANOVA Agentic Pass": "0x4a800D4775F1c0aCAF8124422127CB7Fe3D5b959",
}
out = {}
for name, addr in names.items():
    val = None; err = None
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": addr, "data": SEL}, "latest"], 8, retries=0)
            val = int(r, 16) if isinstance(r, str) and r.startswith("0x") else None
            break
        except Exception as e:
            err = f"{ep}: {type(e).__name__}"
    out[name] = {"address": addr, "totalSupply": val, "error": err if val is None else None}
print(json.dumps(out, indent=1))
