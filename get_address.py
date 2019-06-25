#!/usr/bin/env python3
from liquid_rpc_class import RPCHost
import json
import sys
from liquid_utils import connect

if len (sys.argv) != 2 :
    print('Usage: python '+sys.argv[0]+' LABEL' )
    sys.exit (1)

label = sys.argv[1]

res = {}
host_1, host_2, host_3 = connect()

res['address'] = host_3.call('getnewaddress', label)

print(json.dumps(res, indent=4, sort_keys=True))
