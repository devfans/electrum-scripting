import os
import sys
import warnings
import qrcode
import qrcode.image.svg

MIN_PYTHON_VERSION = "3.6.1"  # FIXME duplicated from setup.py
_min_python_version_tuple = tuple(map(int, (MIN_PYTHON_VERSION.split("."))))


if sys.version_info[:3] < _min_python_version_tuple:
    sys.exit("Error: Electrum requires Python version >= %s..." % MIN_PYTHON_VERSION)


def check_imports():
    # pure-python dependencies need to be imported here for pyinstaller
    try:
        import dns
        import pyaes
        import ecdsa
        import certifi
        import qrcode
        import qrcode.image.svg
        import google.protobuf
        import jsonrpclib
        import aiorpcx
    except ImportError as e:
        sys.exit(f"Error: {str(e)}. Try 'sudo python3 -m pip install <module-name>'")
    # the following imports are for pyinstaller
    from google.protobuf import descriptor
    from google.protobuf import message
    from google.protobuf import reflection
    from google.protobuf import descriptor_pb2
    from jsonrpclib import SimpleJSONRPCServer
    # make sure that certificates are here
    assert os.path.exists(certifi.where())

check_imports()

from electrum.logging import get_logger, configure_logging
from electrum import util
from electrum import constants
from electrum import SimpleConfig
from electrum.wallet import Wallet
from electrum.storage import WalletStorage, get_derivation_used_for_hw_device_encryption
from electrum.util import print_msg, print_stderr, json_encode, json_decode, UserCancelled, bfh
from electrum.util import InvalidPassword
from electrum.commands import get_parser, known_commands, Commands, config_variables
from electrum import daemon
from electrum import keystore
from electrum.transaction import Transaction
from electrum.bitcoin import base_encode

_logger = get_logger(__name__)


# get password routine
def prompt_password(prompt, confirm=True):
    import getpass
    password = getpass.getpass(prompt, stream=None)
    if password and confirm:
        password2 = getpass.getpass("Confirm: ")
        if password != password2:
            sys.exit("Error: Passwords do not match.")
    if not password:
        password = None
    return password


def init_daemon(config_options):
    config = SimpleConfig(config_options)
    storage = WalletStorage(config.get_wallet_path())
    if not storage.file_exists():
        print_msg("Error: Wallet file not found.")
        print_msg("Type 'electrum create' to create a new wallet, or provide a path to a wallet with the -w option")
        sys.exit(0)
    if storage.is_encrypted():
        if storage.is_encrypted_with_hw_device():
            plugins = init_plugins(config, 'cmdline')
            password = get_password_for_hw_device_encrypted_storage(plugins)
        elif config.get('password'):
            password = config.get('password')
        else:
            password = prompt_password('Password:', False)
            if not password:
                print_msg("Error: Password required")
                sys.exit(1)
    else:
        password = None
    config_options['password'] = password


def init_cmdline(config_options, server):
    config = SimpleConfig(config_options)
    cmdname = config.get('cmd')
    cmd = known_commands[cmdname]

    if cmdname == 'signtransaction' and config.get('privkey'):
        cmd.requires_wallet = False
        cmd.requires_password = False

    if cmdname in ['payto', 'paytomany'] and config.get('unsigned'):
        cmd.requires_password = False

    if cmdname in ['payto', 'paytomany'] and config.get('broadcast'):
        cmd.requires_network = True

    # instantiate wallet for command-line
    storage = WalletStorage(config.get_wallet_path())

    if cmd.requires_wallet and not storage.file_exists():
        print_msg("Error: Wallet file not found.")
        print_msg("Type 'electrum create' to create a new wallet, or provide a path to a wallet with the -w option")
        sys.exit(0)

    # important warning
    if cmd.name in ['getprivatekeys']:
        print_stderr("WARNING: ALL your private keys are secret.")
        print_stderr("Exposing a single private key can compromise your entire wallet!")
        print_stderr("In particular, DO NOT use 'redeem private key' services proposed by third parties.")

    # commands needing password
    if (cmd.requires_wallet and storage.is_encrypted() and server is None)\
       or (cmd.requires_password and (storage.is_encrypted() or storage.get('use_encryption'))):
        if storage.is_encrypted_with_hw_device():
            # this case is handled later in the control flow
            password = None
        elif config.get('password'):
            password = config.get('password')
        else:
            password = prompt_password('Password:', False)
            if not password:
                print_msg("Error: Password required")
                sys.exit(1)
    else:
        password = None

    config_options['password'] = config_options.get('password') or password

    if cmd.name == 'password':
        new_password = prompt_password('New password:')
        config_options['new_password'] = new_password


def get_connected_hw_devices(plugins):
    supported_plugins = plugins.get_hardware_support()
    # scan devices
    devices = []
    devmgr = plugins.device_manager
    for splugin in supported_plugins:
        name, plugin = splugin.name, splugin.plugin
        if not plugin:
            e = splugin.exception
            _logger.error(f"{name}: error during plugin init: {repr(e)}")
            continue
        try:
            u = devmgr.unpaired_device_infos(None, plugin)
        except Exception as e:
            _logger.error(f'error getting device infos for {name}: {repr(e)}')
            continue
        devices += list(map(lambda x: (name, x), u))
    return devices


def get_password_for_hw_device_encrypted_storage(plugins):
    devices = get_connected_hw_devices(plugins)
    if len(devices) == 0:
        print_msg("Error: No connected hw device found. Cannot decrypt this wallet.")
        sys.exit(1)
    elif len(devices) > 1:
        print_msg("Warning: multiple hardware devices detected. "
                  "The first one will be used to decrypt the wallet.")
    # FIXME we use the "first" device, in case of multiple ones
    name, device_info = devices[0]
    plugin = plugins.get_plugin(name)
    derivation = get_derivation_used_for_hw_device_encryption()
    try:
        xpub = plugin.get_xpub(device_info.device.id_, derivation, 'standard', plugin.handler)
    except UserCancelled:
        sys.exit(0)
    password = keystore.Xpub.get_pubkey_from_xpub(xpub, ())
    return password


def run_offline_command(config, config_options, plugins):
    print(config)
    print(config_options)
    print(plugins)
    cmdname = config.get('cmd')
    cmd = known_commands[cmdname]
    print(cmd.__dict__)
    password = config_options.get('password')
    if cmd.requires_wallet:
        storage = WalletStorage(config.get_wallet_path())
        if storage.is_encrypted():
            if storage.is_encrypted_with_hw_device():
                password = get_password_for_hw_device_encrypted_storage(plugins)
                config_options['password'] = password
            storage.decrypt(password)
        wallet = Wallet(storage)
    else:
        wallet = None
    # check password
    if cmd.requires_password and wallet.has_password():
        try:
            wallet.check_password(password)
        except InvalidPassword:
            print_msg("Error: This password does not decode this wallet.")
            sys.exit(1)
    if cmd.requires_network:
        print_msg("Warning: running command offline")
    # arguments passed to function
    args = [config.get(x) for x in cmd.params]
    # decode json arguments
    if cmdname not in ('setconfig',):
        args = list(map(json_decode, args))
    # options
    kwargs = {}
    for x in cmd.options:
        kwargs[x] = (config_options.get(x) if x in ['password', 'new_password'] else config.get(x))
    cmd_runner = Commands(config, wallet, None)
    func = getattr(cmd_runner, cmd.name)
    result = func(*args, **kwargs)
    # save wallet
    if wallet:
        wallet.storage.write()
    return result


def init_plugins(config, gui_name):
    from electrum.plugin import Plugins
    return Plugins(config, gui_name)


class WalletScripting(object):
    # Default configurations, overwrite from setup or call
    config_options = {
        'verbosity': '',
        'verbosity_shortcuts': '',
        'portable': False,
        'testnet': False,
        'regtest': False,
        'simnet': False,
        'cwd': os.getcwd()
    }

    @classmethod
    def setup(cls, **kwargs):
        cls.config_options.update(kwargs)

    @classmethod
    def call(cls, command, *args, **kwargs):
        # command line
        config_options = {
            'cmd': command
        }
        config_options.update(cls.config_options)
        config_options.update(kwargs)

        # print(config_options)
        config = SimpleConfig(config_options)
        cmdname = config.get('cmd')

        server = daemon.get_server(config)
        init_cmdline(config_options, server)

        if server is not None:
            result = server.run_cmdline(config_options)
        else:
            cmd = known_commands[cmdname]
            if cmd.requires_network:
                print_msg("Daemon not running; try 'electrum daemon start'")
                sys.exit(1)
            else:
                plugins = init_plugins(config, 'cmdline')
                result = run_offline_command(config, config_options, plugins)

        return result

    @classmethod
    def qr(cls, tx, filename):
        if type(tx) == dict and 'hex' in tx:
            tx = tx['hex']
        tx = Transaction(tx)
        text = bfh(str(tx))
        text = base_encode(text, base=43)
        img = qrcode.make(text, image_factory=qrcode.image.svg.SvgPathImage)

        img.save(filename)
        print("QR Image saved as " + filename)




