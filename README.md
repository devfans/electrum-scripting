# electrum-scripting
Scripting interface wrapper for electrum wallet

[![PYPI Version][pypi-image]][pypi-url]
[![Build Status][travis-image]][travis-url]


## Setup

You would need to setup electrum wallet first and start the daemon if required.

Sample setup
```
# Download from https://electrum.org/#download
sudo apt-get install python3-pyqt5
wget https://download.electrum.org/3.3.8/Electrum-3.3.8.tar.gz
tar -xvf Electrum-3.3.8.tar.gz
cd Electrum-3.3.8
python3 -m pip install .[fast]

# Start deamon
./run_electrum daemon start
./run_electrum daemon load_wallet
```

Install electrum scripting
```
python3 -m pip install electrum-scripting
```

## Get Started

```

> from electrum_scripting.wallet import WalletScripting as ws

# Call electrum command
> unspents = ws.call('listunspent')
[{'address': 'bc1q9tguzkmqul768z9hxkeg8hd6yrrhexymwmykygwk4m6g4t8msheq3z0rxm', 'value': '0.00258', 'prevout_n': 1, 'prevout_hash': '18810325792ff18d52fa65f1724d13750a584bfec8f44a4670f7baecac6d1510', 'height': 587939, 'coinbase': False}]

> tx = ws.call('paytomany', unsigned=True, password="password", outputs=[['address1', 'amount1']])
{'hex': '45505446ff000200000000010110156dacecbaf770464af4c8fe4b580a75134d72f165fa528df12f79250381180100000000fdffffff02a0860100000000002200202ad1c15b60e7fda388b735b283ddba20c77c989b76c96221d6aef48aacfb85f2164d020000000000220020ab8433b505b64af499a5561951404ad86c7ae93b894febc457acf6420fce75a6feffffffffd0ef0300000000000000050001ff01ff01fffd0201534c53ff02aa7ed301638c8c3b80000001cb70696dad3ba23bc1899b72be25bf489eb954fb61e5f7037bad5ed00366f37f036317daa8d96ef7023909f3551853df43a40999505bd846d377f04f5b523e2def000000004c53ff02aa7ed3015c8338c880000001657348468a9482ae1bc5090b8823e8628e6fbaf0673d98777eec1407b5ed43ee0272c445a9a82c43c69eb091b26f3872bcb46449387392bee44a1b4b7951d7ec85000000004c53ff02aa7ed301bc696fad8000000152b96b078f8ee0f02603dc6852ad00cc1a9083ddc0901499cb36da1732d79b570222b0d8e6260969dfc02f8090c875c865a75da175c02b5dc054f6d2ae9f0d78100000000053ae7ef90800', 'complete': False, 'final': False}

# Other utils
> ws.qr(tx, 'unsigned_tx.png')

```


[pypi-image]: https://img.shields.io/pypi/v/electrum-scripting.svg
[pypi-url]: https://pypi.org/project/electrum-scripting/
[travis-image]: https://img.shields.io/travis/devfans/electrum-scripting/master.svg
[travis-url]: https://travis-ci.org/devfans/electrum-scripting

