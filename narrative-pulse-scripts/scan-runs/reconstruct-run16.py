#!/usr/bin/env python3
"""Reconstruct run16 (window 131461916-131471150) after /tmp cleanup: sent pass all wallets + receipts.
Read-only. Outputs under workspace/narrative-pulse/scan-runs/ (persistent)."""
import sys, json, time, datetime
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
sys.path.insert(0, '/home/hatch/workspace/fast_exec')
from ankr import ankr_post
from fast_rpc import race, batch
FROM, TO = 131461916, 131471150
WIB = datetime.timezone(datetime.timedelta(hours=7))
def wib(ts): return datetime.datetime.fromtimestamp(ts, WIB).strftime('%Y-%m-%d %H:%M:%S WIB')
tier = json.load(open('/home/hatch/workspace/narrative-pulse/tier-ab-watch-state.json'))
feed = ["0x8e966a9f17beab1ea50039434c2a14ad9e09b8d6","0x2325f175975abdbcde555c79cc8e63381d28551b",
        "0xbf004bff64725914ee36d03b87d6965b0ced4903","0x6ba79dcc05a1056e19bf1021db4fca7be18b49e7",
        "0x892200223bdfb11d2506c5ab1cae9222ce253acc","0xda91cefe240175e6fab56271110427a4195ab71f"]
wallets = sorted(set(k.lower() for k in tier['wallets']) | set(w.lower() for w in feed))
print(f'WALLETS {len(wallets)} WINDOW {FROM}-{TO}', flush=True)
sent = {}
for w in wallets:
    token=None; inw=[]; ok=True; err=''
    try:
        for _ in range(25):
            params={"blockchain":"bsc","address":w,"pageSize":100}
            if token: params["pageToken"]=token
            res=ankr_post('ankr_getTransactionsByAddress', params)
            txs=res['result']['transactions']
            for t in txs:
                b=int(t['blockNumber'],16)
                if FROM<=b<=TO:
                    inw.append({'hash':t['hash'],'block':b,'to':(t.get('to') or '').lower(),
                                'value':t.get('value'),'status':t.get('status'),
                                'ts':int(t['timestamp'],16) if t.get('timestamp') else None,
                                'time_wib':wib(int(t['timestamp'],16)) if t.get('timestamp') else None,
                                'input_prefix':(t.get('input') or '')[:10]})
            token=res['result'].get('nextPageToken')
            if not txs or not token: break
    except Exception as e:
        ok=False; err=str(e)[:200]
    sent[w]={'ok':ok,'err':err,'in_window':inw}
    print(f'SENT {w[:8]} ok={ok} n={len(inw)}', flush=True)
json.dump({'from_block':FROM,'max_block':TO,'results':sent}, open('/home/hatch/workspace/narrative-pulse/scan-runs/run16-sent.json','w'), indent=1)
total=sum(len(v['in_window']) for v in sent.values())
print(f'SENT DONE total={total} failed={[w for w,v in sent.items() if not v["ok"]]}', flush=True)
APPROVE='0x095ea7b3'
cands=[]
for w,v in sent.items():
    for t in v['in_window']:
        if t['input_prefix']!=APPROVE: cands.append((w,t))
print(f'RECEIPT CANDIDATES {len(cands)}', flush=True)
tracked_padded=set('0x'+'0'*24+w[2:] for w in wallets)
ZERO='0x'+'0'*64
TSIG='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
TSIG_SINGLE='0xc3d58168c5ae7397731d9e3f1f0e6f497e7b40291dcb9a5b066a02f255a6d8e8f'
detail={}
for i in range(0,len(cands),6):
    chunk=cands[i:i+6]
    try:
        res=batch([('eth_getTransactionReceipt',[t['hash']]) for _,t in chunk])
    except Exception:
        res=[]
        for _,t in chunk:
            try: res.append(race('eth_getTransactionReceipt',[t['hash']]))
            except Exception: res.append(None)
            time.sleep(1)
    for (w,t),r in zip(chunk,res):
        if not r or r.get('status')!='0x1': continue
        events=[]
        for lg in r.get('logs',[]):
            topics=lg.get('topics',[])
            if len(topics)>=3 and topics[0].lower()==TSIG and topics[1].lower()==ZERO and topics[2].lower() in tracked_padded:
                events.append({'kind':'ERC721/20 Transfer','contract':lg['address'].lower(),'to':'0x'+topics[2][-40:],'token_id':int(topics[3],16) if len(topics)>3 else None})
            elif len(topics)>=4 and topics[0].lower()==TSIG_SINGLE and topics[2].lower()==ZERO and topics[3].lower() in tracked_padded:
                data=lg.get('data','0x'); tid=int(data[2:66],16) if len(data)>=66 else None
                events.append({'kind':'ERC1155 TransferSingle','contract':lg['address'].lower(),'to':'0x'+topics[3][-40:],'token_id':tid})
        if events:
            detail[t['hash']]={'wallet':w,'to':t['to'],'selector':t['input_prefix'],'value':t['value'],'time_wib':t['time_wib'],'receipt_status':'0x1','block':hex(t['block']),'events':events}
            print(f"MINT {t['hash']} wallet={w[:8]} time={t['time_wib']} events={events}", flush=True)
    time.sleep(4)
json.dump({'detail':detail}, open('/home/hatch/workspace/narrative-pulse/scan-runs/run16-detail.json','w'), indent=1)
print(f'RECEIPTS DONE mint_txs={len(detail)} mint_events={sum(len(v["events"]) for v in detail.values())}', flush=True)
