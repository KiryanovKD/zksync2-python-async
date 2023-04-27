from abc import ABC

import asyncio
from hexbytes import HexBytes
from web3 import AsyncWeb3
from web3.exceptions import TransactionNotFound, TimeExhausted

from web3.eth import AsyncEth
from web3.types import _Hash32, TxReceipt
from zksync2_async.core.response_types import ZksEstimateFee, ZksMainContract, ZksTokens, ZksTokenPrice, \
    ZksL1ChainId, ZksAccountBalances, ZksBridgeAddresses, ZksTransactionTrace, ZksSetContractDebugInfoResult
from zksync2_async.core.types import Limit, From, ContractSourceDebugInfo, \
    BridgeAddresses, TokenAddress, ZksMessageProof, Fee, Token
from zksync2_async.manage_contracts.zksync_contract import AsyncZkSyncContract
from zksync2_async.utils.formatters import zksync_get_request_formatters, zksync_get_result_formatters
from zksync2_async.core.request_types import *
from eth_typing import Address
from web3.method import Method, default_root_munger
from typing import Callable, List, Awaitable

from zksync2_async.utils.rpc_endpoints import zks_estimate_fee_rpc, zks_main_contract_rpc, zks_get_confirmed_tokens_rpc, \
    zks_get_token_price_rpc, zks_l1_chain_id_rpc, zks_get_all_account_balances_rpc, zks_get_bridge_contracts_rpc, \
    zks_get_l2_to_l1_msg_proof_prc, zks_get_l2_to_l1_log_proof_prc, eth_estimate_gas_rpc, \
    zks_set_contract_debug_info_rpc, zks_get_contract_debug_info_rpc, zks_get_transaction_trace_rpc, \
    zks_get_testnet_paymaster_address


class AsyncZkSyncModule(AsyncEth, ABC):
    _zks_estimate_fee: Method[Callable[[Transaction], Awaitable[ZksEstimateFee]]] = Method(
        zks_estimate_fee_rpc,
        mungers=[default_root_munger],
        request_formatters=zksync_get_request_formatters,
        result_formatters=zksync_get_result_formatters
    )

    _zks_main_contract: Method[Callable[[], Awaitable[ZksMainContract]]] = Method(
        zks_main_contract_rpc,
        mungers=None
    )

    _zks_get_confirmed_tokens: Method[Callable[[From, Limit], Awaitable[ZksTokens]]] = Method(
        zks_get_confirmed_tokens_rpc,
        mungers=[default_root_munger],
        result_formatters=zksync_get_result_formatters
    )

    _zks_get_token_price: Method[Callable[[TokenAddress], Awaitable[ZksTokenPrice]]] = Method(
        zks_get_token_price_rpc,
        mungers=[default_root_munger]
    )

    _zks_l1_chain_id: Method[Callable[[], Awaitable[ZksL1ChainId]]] = Method(
        zks_l1_chain_id_rpc,
        mungers=None
    )

    _zks_get_all_account_balances: Method[Callable[[Address], Awaitable[ZksAccountBalances]]] = Method(
        zks_get_all_account_balances_rpc,
        mungers=[default_root_munger],
        result_formatters=zksync_get_result_formatters
    )

    _zks_get_bridge_contracts: Method[Callable[[], Awaitable[ZksBridgeAddresses]]] = Method(
        zks_get_bridge_contracts_rpc,
        mungers=[default_root_munger],
        result_formatters=zksync_get_result_formatters
    )

    _zks_get_l2_to_l1_msg_proof: Method[Callable[[int, Address, str, Optional[int]], Awaitable[ZksMessageProof]]] = Method(
        zks_get_l2_to_l1_msg_proof_prc,
        mungers=[default_root_munger],
        request_formatters=zksync_get_request_formatters,
        result_formatters=zksync_get_result_formatters
    )

    _zks_get_l2_to_l1_log_proof: Method[Callable[[Address, Optional[int]], Awaitable[ZksMessageProof]]] = Method(
        zks_get_l2_to_l1_log_proof_prc,
        mungers=[default_root_munger],
        request_formatters=zksync_get_request_formatters,
        result_formatters=zksync_get_result_formatters
    )

    _eth_estimate_gas: Method[Callable[[Transaction], Awaitable[int]]] = Method(
        eth_estimate_gas_rpc,
        mungers=[default_root_munger],
        request_formatters=zksync_get_request_formatters
    )

    # TODO: implement it
    _zks_set_contract_debug_info: Method[Callable[[Address,
                                                   Awaitable[ContractSourceDebugInfo]],
    ZksSetContractDebugInfoResult]] = Method(
        zks_set_contract_debug_info_rpc,
        mungers=[default_root_munger]
    )
    _zks_get_contract_debug_info: Method[Callable[[Address], Awaitable[ContractSourceDebugInfo]]] = Method(
        zks_get_contract_debug_info_rpc,
        mungers=[default_root_munger]
    )

    _zks_get_transaction_trace: Method[Callable[[Address], Awaitable[ZksTransactionTrace]]] = Method(
        zks_get_transaction_trace_rpc,
        mungers=[default_root_munger]
    )

    _zks_get_testnet_paymaster_address: Method[Callable[[], Awaitable[HexStr]]] = Method(
        zks_get_testnet_paymaster_address,
        mungers=[default_root_munger]
    )

    def __init__(self, web3: "AsyncWeb3"):
        super(AsyncZkSyncModule, self).__init__(web3)
        self.main_contract_address = None
        self.bridge_addresses = None

    async def zks_estimate_fee(self, transaction: Transaction) -> Fee:
        return await self._zks_estimate_fee(transaction)

    async def zks_main_contract(self) -> HexStr:
        if self.main_contract_address is None:
            self.main_contract_address = await self._zks_main_contract()
        return self.main_contract_address

    async def zks_get_confirmed_tokens(self, offset: From, limit: Limit) -> List[Token]:
        return await self._zks_get_confirmed_tokens(offset, limit)

    async def zks_get_token_price(self, token_address: TokenAddress) -> ZksTokenPrice:
        return await self._zks_get_token_price(token_address)

    async def zks_l1_chain_id(self) -> int:
        return await self._zks_l1_chain_id()

    async def zks_get_all_account_balances(self, addr: Address) -> ZksAccountBalances:
        return await self._zks_get_all_account_balances(addr)

    async def zks_get_bridge_contracts(self) -> BridgeAddresses:
        if self.bridge_addresses is None:
            self.bridge_addresses = await self._zks_get_bridge_contracts()
        return self.bridge_addresses

    async def zks_get_l2_to_l1_msg_proof(self,
                                   block: int,
                                   sender: HexStr,
                                   message: str,
                                   l2log_pos: Optional[int]) -> ZksMessageProof:
        return await self._zks_get_l2_to_l1_msg_proof(block, sender, message, l2log_pos)

    async def zks_get_log_proof(self, tx_hash: HexStr, index: int = None) -> ZksMessageProof:
        return await self._zks_get_l2_to_l1_log_proof(tx_hash, index)

    async def zks_get_testnet_paymaster_address(self) -> HexStr:
        return AsyncWeb3.to_checksum_address(await self._zks_get_testnet_paymaster_address())

    async def eth_estimate_gas(self, tx: Transaction) -> int:
        return await self._eth_estimate_gas(tx)

    @staticmethod
    def get_l2_hash_from_priority_op(tx_receipt: TxReceipt, main_contract: AsyncZkSyncContract):
        # TODO: wrong tx hash log extraction, wait transaction on ZkSync side provides timeout error
        tx_hash = None
        for log in tx_receipt["logs"]:
            if log.address.lower() == main_contract.address.lower():
                tx_hash = log.transactionHash
                break
        if tx_hash is None:
            raise RuntimeError("Failed to parse tx logs")
        return tx_hash

    async def get_l2_transaction_from_priority_op(self, tx_receipt, main_contract: AsyncZkSyncContract):
        l2_hash = self.get_l2_hash_from_priority_op(tx_receipt, main_contract)
        # INFO: loop to get the transaction in chain
        await self.wait_for_transaction_receipt(l2_hash)
        return await self.get_transaction(l2_hash)

    async def get_priority_op_response(self, tx_receipt, main_contract: AsyncZkSyncContract):
        tx = await self.get_l2_transaction_from_priority_op(tx_receipt, main_contract)
        return tx

    async def wait_for_transaction_receipt(
            self, transaction_hash: _Hash32, timeout: float = 120, poll_latency: float = 0.1
    ) -> TxReceipt:
        async def _wait_for_tx_receipt_with_timeout(
                _tx_hash: _Hash32, _poll_latency: float
        ) -> TxReceipt:
            while True:
                try:
                    tx_receipt = await self.get_transaction_receipt(_tx_hash)
                except TransactionNotFound:
                    tx_receipt = None
                if tx_receipt is not None and \
                        tx_receipt["blockHash"] is not None:
                    break
                await asyncio.sleep(_poll_latency)
            return tx_receipt

        try:
            return await asyncio.wait_for(
                _wait_for_tx_receipt_with_timeout(transaction_hash, poll_latency),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise TimeExhausted(
                f"Transaction {HexBytes(transaction_hash) !r} is not in the chain "
                f"after {timeout} seconds"
            )

    async def wait_finalized(self,
                             transaction_hash: _Hash32,
                             timeout: float = 120,
                             poll_latency: float = 0.1) -> TxReceipt:

        async def _wait_finalized_with_timeout(
                _tx_hash: _Hash32, _poll_latency: float
        ) -> TxReceipt:
            while True:
                block = await self.get_block('finalized')
                try:
                    tx_receipt = await self.get_transaction_receipt(transaction_hash)
                except TransactionNotFound:
                    tx_receipt = None
                if tx_receipt is not None and \
                        tx_receipt["blockHash"] is not None and \
                        block['number'] >= tx_receipt['blockNumber']:
                    break
                await asyncio.sleep(_poll_latency)
            return tx_receipt

        try:
            return await asyncio.wait_for(
                _wait_finalized_with_timeout(transaction_hash, poll_latency),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise TimeExhausted(
                f"Transaction {HexBytes(transaction_hash) !r} is not in the chain "
                f"after {timeout} seconds"
            )
