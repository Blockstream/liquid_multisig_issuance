#!/usr/bin/env python3
from liquid_rpc_class import RPCHost
import json
import sys
from liquid_utils import connect, generate

if len (sys.argv) != 5 :
    print('Usage: python '+sys.argv[0]+' ASSET ASSETT_ADDRESS ASSET_AMOUNT ASSET_CHANGE_ADDRESS' )
    sys.exit (1)

asset = sys.argv[1]
address = sys.argv[2]
amount = float(sys.argv[3])
asset_change = sys.argv[4]

res = {}
host_1, host_2, host_3, host_4, host_5, host_6, host_7, host_8, host_9 = connect()

raw_tx = host_1.call('createrawtransaction', [], {address:amount}, 0, False, {address:asset})
bitcoin_change = host_1.call('getrawchangeaddress')
funded_raw_tx = host_1.call('fundrawtransaction', raw_tx, {'includeWatching':True, 'changeAddress':{'bitcoin':bitcoin_change,asset:asset_change}})
blinded_raw_tx = host_1.call('blindrawtransaction', funded_raw_tx['hex'])
signed_raw_tx = host_1.call('signrawtransactionwithwallet', blinded_raw_tx)
signed_raw_tx_2 = host_2.call('signrawtransactionwithwallet', signed_raw_tx['hex'])
signed_raw_tx_3 = host_3.call('signrawtransactionwithwallet', signed_raw_tx_2['hex'])
# if N>3 add other signers

test = host_1.call('testmempoolaccept', [signed_raw_tx_3['hex']])
res['testmempoolaccept'] = str(test)

if test[0]['allowed'] == True :
    tx = host_1.call('sendrawtransaction', signed_raw_tx_3['hex'])
    res['txid'] = tx
    generate()

print(json.dumps(res, indent=4, sort_keys=True))
