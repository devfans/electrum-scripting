#!/usr/bin/env python3
from electrum_scripting.wallet import WalletScripting as ws
ws.setup()

# cmd: listunspent
print('calling')
ws.call('listunspent')
