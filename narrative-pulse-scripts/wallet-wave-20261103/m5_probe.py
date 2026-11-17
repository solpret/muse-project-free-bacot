#!/usr/bin/env python3
"""Method 5 probe: V2 factory PairCreated trick + V2 Mint topic decode.
READ-ONLY. All selectors/topics computed programmatically (keccak), never typed."""
import json, sys
sys.path.insert(0, '/home/hatch/workspace/custom-connectors/custom.ankr/bin')
import ankr
from Crypto.Hash import keccak

def k(s):
    return '0x' + keccak.new(digest_bits=256, data=s.encode()).hexdigest()

def pad(a):
    return '0x' + a[2:].lower().rjust(64, '0')

V2_FACTORY = '0xca143ce32fe78f1f7019d7d551a6402fc5350c73'
PAIR_CREATED = k('PairCreated(address,address,address,uint256)')
MINT_V2 = k('Mint(address,address,uint256,uint256)')
MINT_V3 = k('Mint(address,address,int24,int24,uint128,uint256,uint256)')
print('PairCreated:', PAIR_CREATED)
print('Mint V2:', MINT_V2)
print('Mint V3:', MINT_V3)

# AKE: token + pool from m1_coins.json
coins = json.load(open('/home/hatch/workspace/narrative-pulse/wallet-wave-20261103/m1_coins.json'))
ake = [c for c in coins if c['name'] == 'AKE'][0]
token, pool = ake['token'], ake['pool']
print('AKE token', token, 'pool', pool, 'first_buy', ake['verify']['first_buy_block'])

# PairCreated with token as token0, then as token1
for pos in (1, 2):
    topics = [PAIR_CREATED, None, None]
    topics[pos] = pad(token)
    r = ankr.get_logs(V2_FACTORY, 0, 'latest', topics=topics)
    logs = r.get('result', {}).get('logs', []) if isinstance(r, dict) else []
    print(f'token as token{pos}: {len(logs)} logs')
    for lg in logs[:30]:
        data = lg.get('data', '')
        # PairCreated non-indexed params: (pair address, uint256) = first 32 bytes pair
        pair_in_data = '0x' + data[26:66] if len(data) >= 66 else data
        print('  block', lg.get('blockNumber'), 'pair_in_data', pair_in_data,
              'MATCH' if pair_in_data.lower() == pool.lower() else '')

# V2 Mint on AKE pair around first buy (window 2M blocks back)
fb = ake['verify']['first_buy_block']
for name, topic in (('V2 Mint', MINT_V2), ('V3 Mint', MINT_V3)):
    r = ankr.get_logs(pool, fb - 2000000, fb, topics=[topic])
    logs = r.get('result', {}).get('logs', []) if isinstance(r, dict) else []
    print(f'{name} on AKE pair [{fb-2000000},{fb}]: {len(logs)} logs')
    for lg in logs[:3] + logs[-3:]:
        t = lg.get('topics', [])
        print('  block', lg.get('blockNumber'), 't1', t[1][-40:] if len(t) > 1 else '?',
              't2', t[2][-40:] if len(t) > 2 else '?', 'tx', lg.get('transactionHash'))
# No-topic sample: all logs on the pair in a small window around first buy
r = ankr.get_logs(pool, fb - 1000, fb + 1000)
logs = r.get('result', {}).get('logs', []) if isinstance(r, dict) else []
print(f'ALL logs on AKE pair [{fb-1000},{fb+1000}]: {len(logs)} logs')
for lg in logs[:10]:
    print('  block', lg.get('blockNumber'), 'topic0', (lg.get('topics') or ['?'])[0][:18])
