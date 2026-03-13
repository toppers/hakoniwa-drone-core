#!/usr/bin/env python3
from __future__ import annotations

from hakosim_async_shared_rpc import AsyncSharedHakoniwaRpcDroneClient


class AssetAsyncSharedHakoniwaRpcDroneClient(AsyncSharedHakoniwaRpcDroneClient):
    """Asset mode wrapper for async_shared RPC client.

    Hakoniwa initialization is handled by asset registration, so external init
    must not be performed here.
    """

    @classmethod
    def _ensure_external_initialized(cls) -> None:
        return


__all__ = ["AssetAsyncSharedHakoniwaRpcDroneClient"]
