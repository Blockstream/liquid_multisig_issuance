from liquid_rpc_class import RPCHost
import time

network = 'regtest'

def connect():
    if network == 'regtest':
        serverURL_1 = 'http://username:password@127.0.0.1:18888/wallet/wallet_1.dat'
        serverURL_2 = 'http://username:password@127.0.0.1:18888/wallet/wallet_2.dat'
        serverURL_3 = 'http://username:password@127.0.0.1:18888/wallet/wallet_3.dat'
    else:
        serverURL_1 = 'http://username:password@127.0.0.1:7041/wallet/wallet_1.dat'
        serverURL_2 = 'http://username:password@127.0.0.1:7041/wallet/wallet_2.dat'
        serverURL_3 = 'http://username:password@127.0.0.1:7041/wallet/wallet_3.dat'

    host_1 = RPCHost(serverURL_1)
    host_2 = RPCHost(serverURL_2)
    host_3 = RPCHost(serverURL_3)

    return(host_1, host_2, host_3)

def generate():
    time.sleep(5)
    if network == 'regtest':
        serverURL = 'http://username:password@127.0.0.1:18888/wallet/wallet.dat'
        host = RPCHost(serverURL)
        address = host.call('getnewaddress')
        return(host.call('generatetoaddress', 1, address))
    else:
        return(0)
