from eth_account.signers.base import BaseAccount
from eth_typing import HexStr
from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.eth import AsyncEth
from web3.module import Module

from zksync2_async.utils.abi import eth_token_abi_default
from zksync2_async.core.types import EthBlockParams


class AsyncEthToken:
    MAX_ERC20_APPROVE_AMOUNT = 2 ^ 256 - 1
    ERC20_APPROVE_THRESHOLD = 2 ^ 255

    def __init__(self, web3: AsyncEth,
                 contract_address: HexStr,
                 account: BaseAccount,
                 ):
        check_sum_address = AsyncWeb3.to_checksum_address(contract_address)
        self.contract_address = check_sum_address
        self.module = web3
        self.contract: AsyncContract = self.module.contract(self.contract_address, abi=eth_token_abi_default())
        self.account = account

    async def _nonce(self) -> int:
        return await self.module.get_transaction_count(self.account.address, EthBlockParams.LATEST.value)

    async def withdraw_tx(self,
                          to: HexStr,
                          amount: int,
                          gas: int,
                          gas_price: int = None):
        if gas_price is None:
            gas_price = await self.module.gas_price

        return self.contract.functions.withdraw(to).build_transaction({
            "nonce": await self._nonce(),
            "chainId": await self.module.chain_id,
            "gas": gas,
            "gasPrice": gas_price,
            "value": amount,
            "from": self.account.address,
        })
