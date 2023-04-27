from typing import Optional
from eth_typing import HexStr
from web3 import AsyncWeb3
from web3.contract import AsyncContract
from eth_account.signers.base import BaseAccount
from web3.eth import AsyncEth
from web3.types import TxReceipt

from zksync2_async.module.zksync_web3 import AsyncZkSyncWeb3
from zksync2_async.utils.abi import erc_20_abi_default
from zksync2_async.manage_contracts.contract_encoder_base import BaseContractEncoder


class AsyncERC20Contract:
    MAX_ERC20_APPROVE_AMOUNT = 2 ^ 256 - 1
    ERC20_APPROVE_THRESHOLD = 2 ^ 255

    def __init__(self, web3: AsyncEth,
                 contract_address: HexStr,
                 account: BaseAccount):
        check_sum_address = AsyncWeb3.to_checksum_address(contract_address)
        self.contract_address = check_sum_address
        self.module = web3
        self.contract: AsyncContract = self.module.contract(self.contract_address, abi=erc_20_abi_default())
        self.account = account

    async def _nonce(self) -> int:
        return await self.module.get_transaction_count(self.account.address)

    async def approve(self,
                      zksync_address: HexStr,
                      amount,
                      gas_limit: int) -> TxReceipt:
        nonce = await self._nonce()
        gas_price = await self.module.gas_price
        tx = self.contract.functions.approve(zksync_address,
                                             amount).build_transaction(
            {
                "chainId": self.module.chain_id,
                "from": self.account.address,
                "gasPrice": gas_price,
                "gas": gas_limit,
                "nonce": nonce
            })
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = await self.module.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = await self.module.wait_for_transaction_receipt(tx_hash)
        return tx_receipt

    async def allowance(self, owner: HexStr, sender: HexStr) -> int:
        return await self.contract.functions.allowance(owner, sender).call(
            {
                "chainId": self.module.chain_id,
                "from": self.account.address,
            })

    async def transfer(self, _to: str, _value: int):
        return await self.contract.functions.transfer(_to, _value).call(
            {
                "chainId": self.module.chain_id,
                "from": self.account.address,
            })

    async def balance_of(self, addr: HexStr):
        return await self.contract.functions.balanceOf(addr).call(
            {
                "chainId": self.module.chain_id,
                "from": self.account.address
            })


class ERC20Encoder(BaseContractEncoder):

    def __init__(self, web3: AsyncZkSyncWeb3, abi: Optional[dict] = None):
        if abi is None:
            abi = erc_20_abi_default()
        super(ERC20Encoder, self).__init__(web3, abi)
