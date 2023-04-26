from web3 import AsyncWeb3
from eth_typing import HexStr

from zksync2.shared.manage_contracts.abi import paymaster_flow_abi_default
from zksync2.shared.manage_contracts.contract_encoder_base import BaseContractEncoder


class AsyncPaymasterFlowEncoder(BaseContractEncoder):

    def __init__(self, web3: AsyncWeb3):
        super(AsyncPaymasterFlowEncoder, self).__init__(web3, abi=paymaster_flow_abi_default())

    def encode_approval_based(self, address: HexStr, min_allowance: int, inner_input: bytes) -> HexStr:
        return self.encode_method(fn_name="approvalBased", args=[address, min_allowance, inner_input])

    def encode_general(self, inputs: bytes) -> HexStr:
        return self.encode_method(fn_name="general", args=[inputs])
