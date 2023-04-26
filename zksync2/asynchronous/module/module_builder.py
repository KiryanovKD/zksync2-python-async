from zksync2.asynchronous.module.zksync_module import AsyncZkSync
from zksync2.asynchronous.module.zksync_provider import AsyncZkSyncProvider
from zksync2.asynchronous.module.middleware import build_zksync_async_middleware

from typing import Union
from web3._utils.module import attach_modules
from eth_typing import URI
from web3 import AsyncWeb3


class AsyncZkSyncBuilder:
    @classmethod
    def build(cls, url: Union[URI, str]) -> AsyncWeb3:
        web3_module = AsyncWeb3()
        zksync_provider = AsyncZkSyncProvider(url)
        zksync_middleware = build_zksync_async_middleware(zksync_provider)
        web3_module.middleware_onion.add(zksync_middleware)
        attach_modules(web3_module, {"zksync": (AsyncZkSync,)})
        return web3_module
