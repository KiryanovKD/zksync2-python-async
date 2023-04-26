from eth_utils import to_checksum_address, is_address
from eth_utils.curried import apply_formatter_to_array

from eth_utils.curried import apply_formatter_at_index
from web3.module import Module
from web3._utils.formatters import integer_to_hex
from web3._utils.method_formatters import (
    ABI_REQUEST_FORMATTERS,
    METHOD_NORMALIZERS,
    PYTHONIC_REQUEST_FORMATTERS,
    combine_formatters,
    apply_formatter_if,
    apply_formatters_to_dict,
    apply_list_to_array_formatter,
    to_hex_if_integer, PYTHONIC_RESULT_FORMATTERS, FILTER_RESULT_FORMATTERS,
    apply_module_to_formatters, is_not_null, to_ascii_if_bytes
)

from web3.types import RPCEndpoint

from zksync2.shared.module.response_types import ZksAccountBalances
from zksync2.shared.core.types import BridgeAddresses, ZksMessageProof, Token, Fee
from zksync2.shared.module.request_types import *
from eth_utils import remove_0x_prefix
from eth_utils.toolz import compose
from typing import Any, Callable, List, Union, Dict

from zksync2.shared.module.rpc_endpoints import eth_estimate_gas_rpc, zks_estimate_fee_rpc, zks_get_confirmed_tokens_rpc, \
    zks_get_bridge_contracts_rpc, zks_get_all_account_balances_rpc, zks_get_l2_to_l1_log_proof_prc, \
    zks_get_l2_to_l1_msg_proof_prc


def bytes_to_list(v: bytes) -> List[int]:
    return [int(e) for e in v]


def meta_formatter(eip712: EIP712Meta) -> dict:
    ret = {
        "gasPerPubdata": integer_to_hex(eip712.gas_per_pub_data)
    }
    if eip712.custom_signature is not None:
        ret["customSignature"] = eip712.custom_signature.hex()

    factory_formatter = apply_formatter_to_array(bytes_to_list)
    if eip712.factory_deps is not None:
        ret["factoryDeps"] = factory_formatter(eip712.factory_deps)

    pp_params = eip712.paymaster_params
    if pp_params is not None:
        paymaster_input = bytes_to_list(pp_params.paymaster_input)
        ret["paymasterParams"] = {
            "paymaster": pp_params.paymaster,
            "paymasterInput": paymaster_input
        }
    return ret


ZKS_TRANSACTION_PARAMS_FORMATTERS = {
    'data': to_ascii_if_bytes,
    'from': apply_formatter_if(is_address, to_checksum_address),
    'gas': to_hex_if_integer,
    'gasPrice': to_hex_if_integer,
    'maxPriorityFeePerGas': to_hex_if_integer,
    'nonce': to_hex_if_integer,
    'to': apply_formatter_if(is_not_null, to_checksum_address),
    'value': to_hex_if_integer,
    'chainId': to_hex_if_integer,
    'transactionType': to_hex_if_integer,
    'eip712Meta': meta_formatter,
}

zks_transaction_request_formatter = apply_formatters_to_dict(ZKS_TRANSACTION_PARAMS_FORMATTERS)

ZKSYNC_REQUEST_FORMATTERS: [RPCEndpoint, Callable[..., Any]] = {
    eth_estimate_gas_rpc: apply_formatter_at_index(zks_transaction_request_formatter, 0),
    zks_estimate_fee_rpc: apply_formatter_at_index(zks_transaction_request_formatter, 0),
}


def to_token(t: dict) -> Token:
    return Token(l1_address=to_checksum_address(t["l1Address"]),
                 l2_address=to_checksum_address(t["l2Address"]),
                 symbol=t["symbol"],
                 decimals=t["decimals"])


def to_bridge_address(t: dict) -> BridgeAddresses:
    return BridgeAddresses(
        erc20_l1_default_bridge=HexStr(to_checksum_address(t["l1Erc20DefaultBridge"])),
        erc20_l2_default_bridge=HexStr(to_checksum_address(t["l2Erc20DefaultBridge"]))
    )


def to_zks_account_balances(t: dict) -> ZksAccountBalances:
    result = dict()
    for k, v in t.items():
        result[k] = int(v, 16)
    return result


def to_fee(v: dict) -> Fee:
    gas_limit = int(remove_0x_prefix(v['gas_limit']), 16)
    max_fee_per_gas = int(remove_0x_prefix(v['max_fee_per_gas']), 16)
    max_priority_fee_per_gas = int(remove_0x_prefix(v['max_priority_fee_per_gas']), 16)
    gas_per_pubdata_limit = int(remove_0x_prefix(v['gas_per_pubdata_limit']), 16)
    return Fee(gas_limit=gas_limit,
               max_fee_per_gas=max_fee_per_gas,
               max_priority_fee_per_gas=max_priority_fee_per_gas,
               gas_per_pubdata_limit=gas_per_pubdata_limit)


def to_msg_proof(v: dict) -> ZksMessageProof:
    return ZksMessageProof(id=v['id'],
                           proof=v['proof'],
                           root=v['root'])


ZKSYNC_RESULT_FORMATTERS: Dict[RPCEndpoint, Callable[..., Any]] = {
    zks_get_confirmed_tokens_rpc: apply_list_to_array_formatter(to_token),
    zks_get_bridge_contracts_rpc: to_bridge_address,
    zks_get_all_account_balances_rpc: to_zks_account_balances,
    zks_estimate_fee_rpc: to_fee,
    zks_get_l2_to_l1_log_proof_prc: to_msg_proof,
    zks_get_l2_to_l1_msg_proof_prc: to_msg_proof
}


def zksync_get_request_formatters(
        method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]]
) -> Dict[str, Callable[..., Any]]:
    request_formatter_maps = (
        ZKSYNC_REQUEST_FORMATTERS,
        ABI_REQUEST_FORMATTERS,
        METHOD_NORMALIZERS,
        PYTHONIC_REQUEST_FORMATTERS,
    )
    formatters = combine_formatters(request_formatter_maps, method_name)
    return compose(*formatters)


def zksync_get_result_formatters(
        method_name: Union[RPCEndpoint, Callable[..., RPCEndpoint]],
        module: "Module",
) -> Dict[str, Callable[..., Any]]:
    # formatters = combine_formatters((PYTHONIC_RESULT_FORMATTERS,), method_name)
    # formatters_requiring_module = combine_formatters(
    #     (FILTER_RESULT_FORMATTERS,), method_name
    # )
    # partial_formatters = apply_module_to_formatters(
    #     formatters_requiring_module, module, method_name
    # )
    # return compose(*partial_formatters, *formatters)

    formatters = combine_formatters(
        (ZKSYNC_RESULT_FORMATTERS,
         PYTHONIC_RESULT_FORMATTERS),
        method_name
    )
    formatters_requiring_module = combine_formatters(
        (FILTER_RESULT_FORMATTERS,),
        method_name
    )

    partial_formatters = apply_module_to_formatters(
        formatters_requiring_module,
        module,
        method_name
    )
    return compose(*partial_formatters, *formatters)
