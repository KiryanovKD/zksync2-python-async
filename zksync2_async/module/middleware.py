from typing import Callable

from web3 import AsyncWeb3
from web3.middleware import AsyncMiddleware
from web3.types import RPCEndpoint, RPCResponse, AsyncMiddlewareCoroutine, Middleware
from typing import Any

from zksync2_async.module.zksync_provider import AsyncZkSyncProvider


async def zksync_construct_async_middleware(zksync_provider: AsyncZkSyncProvider) -> AsyncMiddleware:
    async def _zksync_async_middleware(make_request: Callable[[RPCEndpoint, Any], Any],
                                      w3: AsyncWeb3) -> AsyncMiddlewareCoroutine:
        async def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            return await zksync_provider.make_request(method, params)

        return middleware

    return _zksync_async_middleware


async def zksync_async_middleware(make_request: Callable[[RPCEndpoint, Any], Any], async_w3: "AsyncZkSyncProvider") -> Middleware:
    middleware = await zksync_construct_async_middleware(async_w3)
    return await middleware(make_request, async_w3)