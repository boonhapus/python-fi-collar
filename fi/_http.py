from typing import Any
import asyncio
import time

import httpx


class RateLimitedHTTPClient(httpx.AsyncClient):
    """
    HTTPX client with token rate limiting.
    """
    def __init__(self, tokens: float, seconds: float, *, max_tokens: float = None, **opts):
        super().__init__(**opts)
        self.tokens = tokens
        self.seconds = seconds
        self.max_tokens = max_tokens or tokens
        self.updated_at = time.monotonic()

    @property
    def rate(self) -> float:
        """
        Rate limit expressed as "tokens per second".
        """
        return self.max_tokens / self.seconds

    async def wait_for_token(self) -> None:
        """
        Block the context until a token is available.
        """
        while self.tokens < 1:
            self.add_new_tokens()
            await asyncio.sleep(0.1)

        self.tokens -= 1

    def add_new_tokens(self) -> None:
        """
        Determine if tokens should be added.
        """
        now = time.monotonic()
        new_tokens = (now - self.updated_at) * self.rate

        if self.tokens + new_tokens >= 1:
            self.tokens = min(self.tokens + new_tokens, self.max_tokens)
            self.updated_at = now

    async def get(self, *a, **kw) -> Any:
        """
        HTTP GET.
        """
        await self.wait_for_token()
        return await self.request('GET', *a, **kw)

    async def post(self, *a, **kw) -> Any:
        """
        HTTP POST.
        """
        await self.wait_for_token()
        return await self.request('POST', *a, **kw)
