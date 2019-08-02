#!/usr/bin/env python3
from electrum_scripting.wallet import WalletScripting as ws
ws.setup()

# cmd: listunspent
ws.call('listunspent')

# cmd: paytomany
tx = ws.call('paytomany', unsigned=True, password='123321', outputs=[['bc1q9tguzkmqul768z9hxkeg8hd6yrrhexymwmykygwk4m6g4t8msheq3z0rxm', '0.001']])

# util: qr
ws.qr(tx['hex'], 'unsigned_tx.svg')

# cmd: signtransaction
tx_signed = ws.call('signtransaction', password='123321', tx=tx['hex'])
ws.qr(tx_signed['hex'], 'signed_tx.svg')
