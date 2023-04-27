from eth_account.signers.base import BaseAccount
from web3.contract import AsyncContract
from eth_typing import HexStr
from web3.types import TxReceipt, TxParams

from zksync2_async.module.zksync_web3 import AsyncZkSyncWeb3
from zksync2_async.utils.abi import l2_bridge_abi_default


class AsyncL2Bridge:
    def __init__(self,
                 contract_address: HexStr,
                 web3_zks: AsyncZkSyncWeb3,
                 zksync_account: BaseAccount,
                 abi=None):
        check_sum_address = AsyncZkSyncWeb3.to_checksum_address(contract_address)
        self.web3 = web3_zks
        self.addr = check_sum_address
        self.zksync_account = zksync_account
        if abi is None:
            abi = l2_bridge_abi_default()
        self.contract: AsyncContract = self.web3.eth.contract(self.addr, abi=abi)

    async def _get_nonce(self):
        return await self.web3.zksync.get_transaction_count(self.zksync_account.address)

    async def finalize_deposit(self,
                         l1_sender: HexStr,
                         l2_receiver: HexStr,
                         l1_token: HexStr,
                         amount: int,
                         data: bytes) -> TxReceipt:
        tx = self.contract.functions.finalizeDeposit(l1_sender,
                                                     l2_receiver,
                                                     l1_token,
                                                     amount,
                                                     data).build_transaction(
            {
                "from": self.zksync_account.address,
                "nonce": self._get_nonce(),
            })
        signed_tx = self.zksync_account.sign_transaction(tx)
        txn_hash = await self.web3.zksync.send_raw_transaction(signed_tx.rawTransaction)
        txn_receipt = await self.web3.zksync.wait_for_transaction_receipt(txn_hash)
        return txn_receipt

    async def l1_bridge(self) -> HexStr:
        return await self.contract.functions.l1Bridge().call()

    async def l1_token_address(self, l2_token: HexStr):
        return await self.contract.functions.l1TokenAddress(l2_token).call()

    async def l2_token_address(self, l1_token: HexStr):
        return await self.contract.functions.l2TokenAddress(l1_token).call()

    async def withdraw_tx(self,
                    l1_receiver: HexStr,
                    l2_token: HexStr,
                    amount: int,
                    gas: int,
                    gas_price: int = None) -> TxParams:
        if gas_price is None:
            gas_price = await self.web3.zksync.gas_price

        tx = self.contract.functions.withdraw(l1_receiver,
                                              l2_token,
                                              amount).build_transaction(
            {
                "chain_id": await self.web3.zksync.chain_id,
                "from": self.zksync_account.address,
                "nonce": await self._get_nonce(),
                "gas": gas,
                "gas_price": gas_price
            })
        return tx
