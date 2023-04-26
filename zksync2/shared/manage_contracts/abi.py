import json
import importlib.resources as pkg_resources
from zksync2.shared.manage_contracts import contract_abi

zksync_abi_cache = {}


# todo: remove global cache var
def _zksync_abi(abi_file: str):
    global zksync_abi_cache

    abi_cache = zksync_abi_cache.get(abi_file)
    if abi_cache is None:
        with pkg_resources.path(contract_abi, abi_file) as p:
            with p.open(mode='r') as json_file:
                data = json.load(json_file)
                zksync_abi_cache[abi_file] = data['abi']
    return abi_cache


def zksync_abi_default():
    return _zksync_abi("IZkSync.json")


def contract_deployer_abi_default():
    return _zksync_abi("ContractDeployer.json")


def erc_20_abi_default():
    return _zksync_abi("IERC20.json")


def eth_token_abi_default():
    return _zksync_abi("IEthToken.json")


def l1_bridge_abi_default():
    return _zksync_abi("IL1Bridge.json")


def l2_bridge_abi_default():
    return _zksync_abi("IL2Bridge.json")


def nonce_holder_abi_default():
    return _zksync_abi("INonceHolder.json")


def paymaster_flow_abi_default():
    return _zksync_abi("IPaymasterFlow.json")
