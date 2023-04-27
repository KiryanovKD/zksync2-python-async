from web3 import AsyncWeb3

from zksync2_async.module.zksync_module import AsyncZkSyncModule


class AsyncZkSyncWeb3(AsyncWeb3):
    zksync: AsyncZkSyncModule
