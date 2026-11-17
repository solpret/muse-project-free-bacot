import json, urllib.request, uuid
def audit(contract):
    body = json.dumps({"binanceChainId": "56", "contractAddress": contract, "requestId": str(uuid.uuid4())}).encode()
    req = urllib.request.Request("https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit",
        data=body, headers={"Content-Type": "application/json", "source": "agent"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())
for label, c in [("minter", "0x6288DFe86f22B53eEB6886aE2D78941de7483743"), ("tokenAGC", "0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6")]:
    res = audit(c)["data"]
    hits = []
    for it in res.get("riskItems", []):
        for d in it.get("details", []):
            if d.get("isHit"):
                hits.append((it.get("id"), d.get("title"), d.get("riskType")))
    print(f"{label}: hasResult={res.get('hasResult')} riskLevel={res.get('riskLevel')} riskAlert={res.get('riskAlert')} hits={hits}")
