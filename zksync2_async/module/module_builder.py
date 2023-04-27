from typing import Optional

from web3 import AsyncHTTPProvider
from web3.providers import AsyncBaseProvider

from zksync2_async.module.zksync_web3 import AsyncZkSyncWeb3
from zksync2_async.module.zksync_module import AsyncZkSyncModule
from zksync2_async.module.zksync_provider import AsyncZkSyncProvider
from zksync2_async.module.middleware import zksync_construct_async_middleware


class AsyncZkSyncBuilder:
    @classmethod
    async def build(cls, zksync_provider: AsyncZkSyncProvider, web3_provider: Optional[AsyncBaseProvider] = None) -> AsyncZkSyncWeb3:
        if not web3_provider:
            web3_provider = AsyncHTTPProvider()
        web3_module = AsyncZkSyncWeb3(web3_provider)
        zksync_middleware = await zksync_construct_async_middleware(zksync_provider)
        web3_module.middleware_onion.add(zksync_middleware)
        web3_module.attach_modules({"zksync": (AsyncZkSyncModule,)})
        return web3_module
