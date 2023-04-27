from eth_account.signers.base import BaseAccount
from web3.contract import AsyncContract
from eth_typing import HexStr
from typing import List, Optional
from web3.types import TxReceipt

from zksync2_async.module.zksync_web3 import AsyncZkSyncWeb3
from zksync2_async.utils.abi import l1_bridge_abi_default
from zksync2_async.manage_contracts.contract_encoder_base import BaseContractEncoder


class AsyncL1Bridge:
    def __init__(self,
                 contract_address: HexStr,
                 web3: AsyncZkSyncWeb3,
                 eth_account: BaseAccount,
                 # gas_provider: GasProvider,
                 abi=None):
        check_sum_address = AsyncZkSyncWeb3.to_checksum_address(contract_address)
        self.web3 = web3
        self.addr = check_sum_address
        self.account = eth_account
        # self.gas_provider = gas_provider
        if abi is None:
            abi = l1_bridge_abi_default()
        self.contract: AsyncContract = self.web3.eth.contract(self.addr, abi=abi)

    async def _get_nonce(self):
        return await self.web3.eth.get_transaction_count(self.account.address)

    async def claim_failed_deposit(self,
                                   deposit_sender: HexStr,
                                   l1_token: HexStr,
                                   l2tx_hash: bytes,
                                   l2_block_number: int,
                                   l2_msg_index: int,
                                   l2_tx_number_in_block: int,
                                   merkle_proof: List[bytes]):
        params = {
            "chainId": self.web3.eth.chain_id,
            "from": self.account.address,
            "nonce": self._get_nonce()
        }
        await self.contract.functions.claimFailedDeposit(deposit_sender,
                                                         l1_token,
                                                         l2tx_hash,
                                                         l2_block_number,
                                                         l2_msg_index,
                                                         l2_tx_number_in_block,
                                                         merkle_proof).call(params)

    async def deposit(self,
                      l2_receiver: HexStr,
                      l1_token: HexStr,
                      amount: int,
                      l2_tx_gas_limit: int,
                      l2_tx_gas_per_pubdata_byte: int) -> TxReceipt:
        tx = self.contract.functions.deposit(l2_receiver,
                                             l1_token,
                                             amount,
                                             l2_tx_gas_limit,
                                             l2_tx_gas_per_pubdata_byte
                                             ).build_transaction(
            {
                "chainId": self.web3.eth.chain_id,
                "from": self.account.address,
                "nonce": self._get_nonce(),
                # "gas": self.gas_provider.gas_limit(),
                # "gasPrice": self.gas_provider.gas_price(),
                "value": amount
            })
        signed_tx = self.account.sign_transaction(tx)
        txn_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        txn_receipt = await self.web3.eth.wait_for_transaction_receipt(txn_hash)
        return txn_receipt

    async def finalize_withdrawal(self,
                                  l2_block_number: int,
                                  l2_msg_index: int,
                                  msg: bytes,
                                  merkle_proof: List[bytes]) -> TxReceipt:
        tx = self.contract.functions.finalizeWithdrawal(l2_block_number,
                                                        l2_msg_index,
                                                        msg,
                                                        merkle_proof).build_transaction(
            {
                "chainId": self.web3.eth.chain_id,
                "from": self.account.address,
                "nonce": self._get_nonce(),
                # "gas": self.gas_provider.gas_limit(),
                # "gasPrice": self.gas_provider.gas_price()
            })
        signed_tx = self.account.sign_transaction(tx)
        txn_hash = await self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        txn_receipt = await self.web3.eth.wait_for_transaction_receipt(txn_hash)
        return txn_receipt

    async def is_withdrawal_finalized(self, l2_block_number: int, l2_msg_index: int) -> bool:
        return await self.contract.functions.isWithdrawalFinalized(l2_block_number, l2_msg_index).call()

    async def l2_token_address(self, l1_token: HexStr) -> HexStr:
        return await self.contract.functions.l2TokenAddress(l1_token).call()

    @property
    def address(self):
        return self.contract.address


class L1BridgeEncoder(BaseContractEncoder):

    def __init__(self, web3: AsyncZkSyncWeb3, abi: Optional[dict] = None):
        if abi is None:
            abi = l1_bridge_abi_default()
        super(L1BridgeEncoder, self).__init__(web3, abi)
