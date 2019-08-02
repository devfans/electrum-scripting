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

```python
from electrum_scripting.wallet import WalletScripting as ws

# Call electrum command
ws.call('listunspent')

```


[pypi-image]: https://img.shields.io/pypi/v/electrum-scripting.svg
[pypi-url]: https://pypi.org/project/electrum-scripting/
[travis-image]: https://img.shields.io/travis/devfans/electrum-scripting/master.svg
[travis-url]: https://travis-ci.org/devfans/electrum-scripting

