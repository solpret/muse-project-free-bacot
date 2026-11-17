#!/usr/bin/env python3
"""Fresh Binance audit for HONGBAO (only executable-route candidate in the sweep).
Prints parsed audit: hasResult, riskLevel, riskAlert, RISK hits, CAUTION hits."""
import json, uuid, urllib.request

TOKEN = "0x44e9AeC5b828092A9eBC3070caCcd556BB21C725"
url = "https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit"
body = json.dumps({"binanceChainId": "56", "contractAddress": TOKEN,
                   "requestId": str(uuid.uuid4())}).encode()
req = urllib.request.Request(url, data=body,
    headers={"Content-Type": "application/json", "source": "agent",
             "User-Agent": "binance-web3/1.4 (Skill)"})
try:
    d = json.loads(urllib.request.urlopen(req, timeout=30).read())
except Exception as e:
    print(json.dumps({"error": str(e)}, indent=1))
    raise SystemExit(0)
data = d.get("data", {})
danger, caution = [], []
if data.get("riskAlert"):
    danger.append("riskAlert: %s" % data.get("riskAlert"))
for grp in (data.get("riskItems") or []):
    for det in (grp.get("details") or []):
        if det.get("isHit") and det.get("riskType") == "RISK":
            danger.append(det.get("title"))
        if det.get("isHit") and det.get("riskType") == "CAUTION":
            caution.append(det.get("title"))
print(json.dumps({
    "token": TOKEN,
    "hasResult": data.get("hasResult"),
    "riskLevel": data.get("riskLevel"),
    "riskAlert": data.get("riskAlert"),
    "danger_risk_hits": danger,
    "caution_hits": caution,
    "raw_keys": list(data.keys()),
}, indent=1))
