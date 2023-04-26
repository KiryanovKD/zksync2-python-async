from abc import ABC

from hexbytes import HexBytes
from web3 import Web3
from web3._utils.threads import Timeout
from web3.exceptions import TransactionNotFound, TimeExhausted

from web3.eth import Eth
from web3.types import _Hash32, TxReceipt

from zksync2.shared.module.response_types import ZksEstimateFee, ZksMainContract, ZksTokens, ZksTokenPrice, \
    ZksL1ChainId, ZksAccountBalances, ZksBridgeAddresses, ZksTransactionTrace, ZksSetContractDebugInfoResult
from zksync2.shared.core import Limit, From, ContractSourceDebugInfo, \
    BridgeAddresses, TokenAddress, ZksMessageProof, Fee, Token
from zksync2.synchronous.manage_contracts.zksync_contract import ZkSyncContract
from zksync2.shared.module.request_types import *
from eth_typing import Address
from web3.method import Method, default_root_munger
from typing import Callable, List

from zksync2.shared.module.formatters import zksync_get_request_formatters, zksync_get_result_formatters

from zksync2.shared.module.rpc_endpoints import zks_estimate_fee_rpc, zks_main_contract_rpc, zks_get_confirmed_tokens_rpc, \
    zks_get_token_price_rpc, zks_l1_chain_id_rpc, zks_get_all_account_balances_rpc, zks_get_bridge_contracts_rpc, \
    zks_get_l2_to_l1_msg_proof_prc, zks_get_l2_to_l1_log_proof_prc, eth_estimate_gas_rpc, \
    zks_set_contract_debug_info_rpc, zks_get_contract_debug_info_rpc, zks_get_transaction_trace_rpc, \
    zks_get_testnet_paymaster_address


class ZkSync(Eth, ABC):
    _zks_estimate_fee: Method[Callable[[Transaction], ZksEstimateFee]] = Method(
        zks_estimate_fee_rpc,
        mungers=[default_root_munger],
        request_formatters=zksync_get_request_formatters,
        result_formatters=zksync_get_result_formatters
    )

    _zks_main_contract: Method[Callable[[], ZksMainContract]] = Method(
        zks_main_contract_rpc,
        mungers=None
    )

    _zks_get_confirmed_tokens: Method[Callable[[From, Limit], ZksTokens]] = Method(
        zks_get_confirmed_tokens_rpc,
        mungers=[default_root_munger],
        result_formatters=zksync_get_result_formatters
    )

    _zks_get_token_price: Method[Callable[[TokenAddress], ZksTokenPrice]] = Method(
        zks_get_token_price_rpc,
        mungers=[default_root_munger]
    )

    _zks_l1_chain_id: Method[Callable[[], ZksL1ChainId]] = Method(
        zks_l1_chain_id_rpc,
        mungers=None
    )

    _zks_get_all_account_balances: Method[Callable[[Address], ZksAccountBalances]] = Method(
        zks_get_all_account_balances_rpc,
        mungers=[default_root_munger],
        result_formatters=zksync_get_result_formatters
    )

    _zks_get_bridge_contracts: Method[Callable[[], ZksBridgeAddresses]] = Method(
        zks_get_bridge_contracts_rpc,
        mungers=[default_root_munger],
        result_formatters=zksync_get_result_formatters
    )

    _zks_get_l2_to_l1_msg_proof: Method[Callable[[int, Address, str, Optional[int]], ZksMessageProof]] = Method(
        zks_get_l2_to_l1_msg_proof_prc,
        mungers=[default_root_munger],
        request_formatters=zksync_get_request_formatters,
        result_formatters=zksync_get_result_formatters
    )

    _zks_get_l2_to_l1_log_proof: Method[Callable[[Address, Optional[int]], ZksMessageProof]] = Method(
        zks_get_l2_to_l1_log_proof_prc,
        mungers=[default_root_munger],
        request_formatters=zksync_get_request_formatters,
        result_formatters=zksync_get_result_formatters
    )

    _eth_estimate_gas: Method[Callable[[Transaction], int]] = Method(
        eth_estimate_gas_rpc,
        mungers=[default_root_munger],
        request_formatters=zksync_get_request_formatters
    )

    # TODO: implement it
    _zks_set_contract_debug_info: Method[Callable[[Address,
                                                   ContractSourceDebugInfo],
    ZksSetContractDebugInfoResult]] = Method(
        zks_set_contract_debug_info_rpc,
        mungers=[default_root_munger]
    )
    _zks_get_contract_debug_info: Method[Callable[[Address], ContractSourceDebugInfo]] = Method(
        zks_get_contract_debug_info_rpc,
        mungers=[default_root_munger]
    )

    _zks_get_transaction_trace: Method[Callable[[Address], ZksTransactionTrace]] = Method(
        zks_get_transaction_trace_rpc,
        mungers=[default_root_munger]
    )

    _zks_get_testnet_paymaster_address: Method[Callable[[], HexStr]] = Method(
        zks_get_testnet_paymaster_address,
        mungers=[default_root_munger]
    )

    def __init__(self, web3: "Web3"):
        super(ZkSync, self).__init__(web3)
        self.main_contract_address = None
        self.bridge_addresses = None

    def zks_estimate_fee(self, transaction: Transaction) -> Fee:
        return self._zks_estimate_fee(transaction)

    def zks_main_contract(self) -> HexStr:
        if self.main_contract_address is None:
            self.main_contract_address = self._zks_main_contract()
        return self.main_contract_address

    def zks_get_confirmed_tokens(self, offset: From, limit: Limit) -> List[Token]:
        return self._zks_get_confirmed_tokens(offset, limit)

    def zks_get_token_price(self, token_address: TokenAddress) -> ZksTokenPrice:
        return self._zks_get_token_price(token_address)

    def zks_l1_chain_id(self) -> int:
        return self._zks_l1_chain_id()

    def zks_get_all_account_balances(self, addr: Address) -> ZksAccountBalances:
        return self._zks_get_all_account_balances(addr)

    def zks_get_bridge_contracts(self) -> BridgeAddresses:
        if self.bridge_addresses is None:
            self.bridge_addresses = self._zks_get_bridge_contracts()
        return self.bridge_addresses

    def zks_get_l2_to_l1_msg_proof(self,
                                   block: int,
                                   sender: HexStr,
                                   message: str,
                                   l2log_pos: Optional[int]) -> ZksMessageProof:
        return self._zks_get_l2_to_l1_msg_proof(block, sender, message, l2log_pos)

    def zks_get_log_proof(self, tx_hash: HexStr, index: int = None) -> ZksMessageProof:
        return self._zks_get_l2_to_l1_log_proof(tx_hash, index)

    def zks_get_testnet_paymaster_address(self) -> HexStr:
        return Web3.to_checksum_address(self._zks_get_testnet_paymaster_address())

    def eth_estimate_gas(self, tx: Transaction) -> int:
        return self._eth_estimate_gas(tx)

    @staticmethod
    def get_l2_hash_from_priority_op(tx_receipt: TxReceipt, main_contract: ZkSyncContract):
        # TODO: wrong tx hash log extraction, wait transaction on ZkSync side provides timeout error
        tx_hash = None
        for log in tx_receipt["logs"]:
            if log.address.lower() == main_contract.address.lower():
                tx_hash = log.transactionHash
                break
        if tx_hash is None:
            raise RuntimeError("Failed to parse tx logs")
        return tx_hash

    def get_l2_transaction_from_priority_op(self, tx_receipt, main_contract: ZkSyncContract):
        l2_hash = self.get_l2_hash_from_priority_op(tx_receipt, main_contract)
        # INFO: loop to get the transaction in chain
        self.wait_for_transaction_receipt(l2_hash)
        return self.get_transaction(l2_hash)

    def get_priority_op_response(self, tx_receipt, main_contract: ZkSyncContract):
        tx = self.get_l2_transaction_from_priority_op(tx_receipt, main_contract)
        return tx

    def wait_for_transaction_receipt(self,
                                     transaction_hash: _Hash32,
                                     timeout: float = 120,
                                     poll_latency: float = 0.1) -> TxReceipt:
        try:
            with Timeout(timeout) as _timeout:
                while True:
                    try:
                        tx_receipt = self.get_transaction_receipt(transaction_hash)
                    except TransactionNotFound:
                        tx_receipt = None
                    if tx_receipt is not None and \
                            tx_receipt["blockHash"] is not None:
                        break
                    _timeout.sleep(poll_latency)
            return tx_receipt

        except Timeout:
            raise TimeExhausted(
                f"Transaction {HexBytes(transaction_hash) !r} is not in the chain "
                f"after {timeout} seconds"
            )

    def wait_finalized(self,
                       transaction_hash: _Hash32,
                       timeout: float = 120,
                       poll_latency: float = 0.1) -> TxReceipt:
        try:
            with Timeout(timeout) as _timeout:
                while True:
                    try:
                        block = self.get_block('finalized')
                        tx_receipt = self.get_transaction_receipt(transaction_hash)
                    except TransactionNotFound:
                        tx_receipt = None
                    if tx_receipt is not None and \
                            tx_receipt["blockHash"] is not None and \
                            block['number'] >= tx_receipt['blockNumber']:
                        break
                    _timeout.sleep(poll_latency)
            return tx_receipt

        except Timeout:
            raise TimeExhausted(
                f"Transaction {HexBytes(transaction_hash) !r} is not in the chain "
                f"after {timeout} seconds"
            )
