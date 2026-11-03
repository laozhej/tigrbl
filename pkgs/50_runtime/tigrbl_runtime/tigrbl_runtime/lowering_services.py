"""Lazy runtime bridge to canonical kernel lowering services.

Functions retain their kernel identity. Loading one service does not import
unrelated protocol chains during concrete model initialization.
"""
from __future__ import annotations

from typing import Any

__all__ = ["compile_opview_from_specs", "build_websocket_jsonrpc_session_handler"]


def __getattr__(name: str) -> Any:
    if name == "compile_opview_from_specs":
        from tigrbl_kernel.opview_compiler import compile_opview_from_specs

        return compile_opview_from_specs
    if name == "build_websocket_jsonrpc_session_handler":
        from tigrbl_kernel.protocol_chains.websocket import build_websocket_jsonrpc_session_handler

        return build_websocket_jsonrpc_session_handler
    raise AttributeError(name)
