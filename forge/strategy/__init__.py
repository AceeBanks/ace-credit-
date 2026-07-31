"""
GLX FORGE Strategy Forge

This module defines the strategy infrastructure for the GLX FORGE trading infrastructure.
Strategy includes contracts, Cerebus building blocks, and compiler.

Version: 0.1.0
Phase: Phase 6 - Strategy Forge
"""

__version__ = "0.1.0"

from forge.strategy.contracts import (
    StrategyContract,
    StrategyType,
    StrategyStatus,
    StrategyConfig,
    StrategyParameters,
    StrategySignal,
)

from forge.strategy.blocks import (
    StrategyBlock,
    BlockType,
    BlockInput,
    BlockOutput,
    BlockConnection,
    DEFAULT_BLOCKS,
)

from forge.strategy.compiler import (
    StrategyCompiler,
    CompilationResult,
    CompilationStatus,
    CompiledStrategy,
    StrategyBytecode,
)

__all__ = [
    # Contracts
    "StrategyContract",
    "StrategyType",
    "StrategyStatus",
    "StrategyConfig",
    "StrategyParameters",
    "StrategySignal",
    # Blocks
    "StrategyBlock",
    "BlockType",
    "BlockInput",
    "BlockOutput",
    "BlockConnection",
    "DEFAULT_BLOCKS",
    # Compiler
    "StrategyCompiler",
    "CompilationResult",
    "CompilationStatus",
    "CompiledStrategy",
    "StrategyBytecode",
]
