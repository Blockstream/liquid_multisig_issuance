#!/usr/bin/env python3
from liquid_rpc_class import RPCHost
import wallycore as wally
import json
import sys
import struct
from liquid_utils import connect, generate

# FIXME: contract information (all required for asset registry)
issuer_pubkey = ''
name = 'asset name'
ticker = 'XYZ'
precision = 0
domain = 'domain.com'
version = 0 # don't change

# Is issuance blind?
blind = False

feerate = 0.00003000

if len (sys.argv) != 5 :
    print('Usage: python '+sys.argv[0]+' ASSET_AMOUNT ASSET_ADDRESS REISSUANCE_TOKEN_AMOUNT REISSUANCE_TOKEN_ADDRESS' )
    sys.exit(1)

amount = round(float(sys.argv[1]), 8)
asset_address = sys.argv[2]
reissuance_amount = round(float(sys.argv[3]), 8)
reissuance_token_address = sys.argv[4]

res = {}
host_1, host_2, host_3 = connect()

# Create base transaction
base = host_1.call('createrawtransaction', [], [{'data':'00'}])
funded = host_1.call('fundrawtransaction', base, {'feeRate':feerate})

# Calculate prevout
decoded = host_1.call('decoderawtransaction', funded['hex'])
prev_tx = decoded['vin'][0]['txid']
prev_vout = decoded['vin'][0]['vout']
res['prev_tx'] = '{}:{}'.format(prev_tx, prev_vout)

# Create the contact and calculate the asset id (Needed for asset registry!)
contract = json.dumps({'name': name, 'ticker': ticker, 'precision': precision, 'entity': {'domain': domain}, 'issuer_pubkey': issuer_pubkey, 'version': version}, separators=(',',':'), sort_keys=True)
contract_hash = wally.hex_from_bytes(wally.sha256(contract.encode('ascii')))
a = wally.hex_from_bytes(wally.hex_to_bytes(prev_tx)[::-1])+wally.hex_from_bytes(struct.pack('<L', int(prev_vout)))
a = wally.hex_from_bytes(wally.sha256d(wally.hex_to_bytes(a)))
b = a + contract_hash
merkle = wally.hex_from_bytes(wally.sha256_midstate(wally.hex_to_bytes(b)))
c = merkle + '0000000000000000000000000000000000000000000000000000000000000000'
merkle = wally.hex_from_bytes(wally.sha256_midstate(wally.hex_to_bytes(c))[::-1])
res['asset_id'] = merkle
res['contract'] = contract
res['contract_hash'] = contract_hash

# Create the rawissuance transaction
contract_hash_rev = wally.hex_from_bytes(wally.hex_to_bytes(contract_hash)[::-1])
rawissue = host_1.call('rawissueasset', funded['hex'], [{'asset_amount':amount, 'asset_address':asset_address, 'token_amount':reissuance_amount, 'token_address':reissuance_token_address, 'blind':blind, 'contract_hash':contract_hash_rev}])

# Blind the transaction
blind = host_1.call('blindrawtransaction', rawissue[0]['hex'], True, [], False)

# Sign transaction
signed = host_1.call('signrawtransactionwithwallet', blind)
decoded = host_1.call('decoderawtransaction', signed['hex'])
res['decoded_raw_transaction'] = decoded
res['raw_transaction'] = signed['hex']

# Test transaction
test = host_1.call('testmempoolaccept', [signed['hex']])
res['testmempoolaccept'] = str(test)

if test[0]['allowed'] is True:
    txid = host_1.call('sendrawtransaction', signed['hex'])
    res['txid'] = txid
    generate()

    # Import issuance blinding key in the second signer
    issuanceblindingkey = host_1.call('dumpissuanceblindingkey', txid, 0)
    host_2.call('importissuanceblindingkey', txid, 0, issuanceblindingkey)
    res['issuanceblindingkey'] = issuanceblindingkey

print(json.dumps(res, indent=4, sort_keys=True))
