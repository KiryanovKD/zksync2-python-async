from eth_account.signers.base import BaseAccount
from eth_typing import HexStr
from web3.types import Nonce

from zksync2_async.module.zksync_web3 import AsyncZkSyncWeb3
from zksync2_async.utils.abi import nonce_holder_abi_default
from zksync2_async.utils.deploy_addresses import ZkSyncAddresses


class AsyncNonceHolder:

    def __init__(self,
                 web3: AsyncZkSyncWeb3,
                 account: BaseAccount):
        self.web3 = web3
        self.account = account
        self.contract = self.web3.zksync.contract(address=ZkSyncAddresses.NONCE_HOLDER_ADDRESS.value,
                                                  abi=nonce_holder_abi_default())

    async def get_account_nonce(self) -> Nonce:
        return await self.contract.functions.getAccountNonce().call(
            {
                "from": self.account.address
            })

    async def get_deployment_nonce(self, addr: HexStr) -> Nonce:
        return await self.contract.functions.getDeploymentNonce(addr).call(
            {
                "from": self.account.address
            })

    async def get_raw_nonce(self, addr: HexStr) -> Nonce:
        return await self.contract.functions.getRawNonce(addr).call(
            {
                "from": self.account.address
            })

    async def increment_deployment_nonce(self, addr: HexStr):
        return await self.contract.functions.incrementDeploymentNonce(addr).call(
            {
                "from": self.account.address
            })

    async def increment_nonce(self):
        return await self.contract.functions.incrementNonce().call(
            {
                "from": self.account.address
            })

    async def increment_nonce_if_equals(self, expected_nonce: Nonce):
        return await self.contract.functions.incrementNonceIfEquals(expected_nonce).call(
            {
                "from": self.account.address
            })
