import json, urllib.request, uuid
def audit(contract):
    body = json.dumps({"binanceChainId": "56", "contractAddress": contract, "requestId": str(uuid.uuid4())}).encode()
    req = urllib.request.Request("https://web3.binance.com/bapi/defi/v1/public/wallet-direct/security/token/audit",
        data=body, headers={"Content-Type": "application/json", "source": "agent"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())
for label, c in [("minter", "0x6288DFe86f22B53eEB6886aE2D78941de7483743"), ("tokenAGC", "0x63dea5aCdbE1F27c968907D08610A5f0A0284bA6")]:
    try:
        res = audit(c)
        print(f"--- {label} {c}")
        print(json.dumps(res, indent=2)[:3000])
    except Exception as e:
        print(f"--- {label} ERROR: {e}")
