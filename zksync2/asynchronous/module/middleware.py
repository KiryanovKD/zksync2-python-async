from typing import Callable

from web3 import AsyncWeb3
from web3.middleware import AsyncMiddleware
from web3.types import RPCEndpoint, RPCResponse
from typing import Any

from zksync2.asynchronous.module.zksync_provider import AsyncZkSyncProvider


def build_zksync_async_middleware(zksync_provider: AsyncZkSyncProvider) -> AsyncMiddleware:
    def zksync_async_middleware(make_request: Callable[[RPCEndpoint, Any], Any],
                          w3: AsyncWeb3) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            return await zksync_provider.make_request(method, params)
        return middleware
    return zksync_async_middleware
