"""
GLX FORGE Strategy Compiler

This module defines the strategy compiler for the GLX FORGE trading infrastructure.
The compiler compiles Cerebus block strategies into executable bytecode.

Version: 0.1.0
Phase: Phase 6 - Strategy Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4

from forge.strategy.blocks import StrategyBlock, BlockConnection
from forge.strategy.contracts import StrategyContract, StrategyConfig


class CompilationStatus(Enum):
    """Compilation status enumeration."""
    PENDING = "pending"
    COMPILING = "compiling"
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class StrategyBytecode:
    """Strategy bytecode contract."""
    bytecode_id: str
    version: str = "1.0.0"
    instructions: List[Dict] = field(default_factory=list)
    constants: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.bytecode_id, str) or not self.bytecode_id:
            self.bytecode_id = str(uuid4())
    
    @property
    def instruction_count(self) -> int:
        """Get the number of instructions."""
        return len(self.instructions)
    
    def add_instruction(self, opcode: str, operands: Dict) -> None:
        """Add an instruction to the bytecode."""
        self.instructions.append({
            "opcode": opcode,
            "operands": operands,
        })
    
    def add_constant(self, name: str, value: Any) -> None:
        """Add a constant to the bytecode."""
        self.constants[name] = value


@dataclass
class CompiledStrategy:
    """Compiled strategy contract."""
    compiled_id: str
    strategy_id: str
    bytecode: StrategyBytecode
    compilation_timestamp: datetime
    compiler_version: str = "0.1.0"
    source_hash: Optional[str] = None
    bytecode_hash: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.compiled_id, str) or not self.compiled_id:
            self.compiled_id = str(uuid4())
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValueError("Strategy ID cannot be empty")
        if not isinstance(self.bytecode, StrategyBytecode):
            raise ValueError("Bytecode must be a StrategyBytecode instance")


@dataclass
class CompilationResult:
    """Compilation result contract."""
    result_id: str
    strategy_id: str
    status: CompilationStatus
    compiled_strategy: Optional[CompiledStrategy] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    compilation_time_seconds: float = 0.0
    compiled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.strategy_id, str) or not self.strategy_id:
            raise ValueError("Strategy ID cannot be empty")
        if not isinstance(self.status, CompilationStatus):
            raise ValueError("Status must be CompilationStatus enum")
    
    @property
    def is_success(self) -> bool:
        """Check if compilation succeeded."""
        return self.status == CompilationStatus.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        """Check if compilation failed."""
        return self.status == CompilationStatus.FAILED
    
    @property
    def has_warnings(self) -> bool:
        """Check if compilation has warnings."""
        return len(self.warnings) > 0
    
    @property
    def has_errors(self) -> bool:
        """Check if compilation has errors."""
        return len(self.errors) > 0
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)


@dataclass
class StrategyCompiler:
    """Strategy compiler contract."""
    compiler_id: str
    name: str
    version: str = "0.1.0"
    blocks: Dict[str, StrategyBlock] = field(default_factory=dict)
    connections: List[BlockConnection] = field(default_factory=list)
    results: List[CompilationResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.compiler_id, str) or not self.compiler_id:
            self.compiler_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    def add_block(self, block: StrategyBlock) -> None:
        """Add a block to the compiler."""
        self.blocks[block.block_id] = block
    
    def remove_block(self, block_id: str) -> None:
        """Remove a block from the compiler."""
        if block_id in self.blocks:
            del self.blocks[block_id]
            # Remove connections involving this block
            self.connections = [
                conn for conn in self.connections
                if conn.from_block_id != block_id and conn.to_block_id != block_id
            ]
    
    def add_connection(self, connection: BlockConnection) -> None:
        """Add a connection between blocks."""
        self.connections.append(connection)
    
    def remove_connection(self, connection_id: str) -> None:
        """Remove a connection from the compiler."""
        self.connections = [conn for conn in self.connections if conn.connection_id != connection_id]
    
    def get_block(self, block_id: str) -> Optional[StrategyBlock]:
        """Get a block by ID."""
        return self.blocks.get(block_id)
    
    def get_connections_for_block(self, block_id: str) -> List[BlockConnection]:
        """Get all connections for a block."""
        return [
            conn for conn in self.connections
            if conn.from_block_id == block_id or conn.to_block_id == block_id
        ]
    
    def validate_blocks(self) -> List[str]:
        """Validate all blocks and return errors."""
        errors = []
        
        # Check that all blocks have at least one input or output
        for block_id, block in self.blocks.items():
            if not block.inputs and not block.outputs:
                errors.append(f"Block {block.name} has no inputs or outputs")
        
        # Check that all connections reference valid blocks
        for connection in self.connections:
            if connection.from_block_id not in self.blocks:
                errors.append(f"Connection references invalid from_block: {connection.from_block_id}")
            if connection.to_block_id not in self.blocks:
                errors.append(f"Connection references invalid to_block: {connection.to_block_id}")
            
            # Check that output exists in from_block
            from_block = self.get_block(connection.from_block_id)
            if from_block:
                from_output = from_block.get_output_by_name(connection.from_output_id)
                if not from_output:
                    errors.append(f"Connection references invalid output: {connection.from_output_id}")
            
            # Check that input exists in to_block
            to_block = self.get_block(connection.to_block_id)
            if to_block:
                to_input = to_block.get_input_by_name(connection.to_input_id)
                if not to_input:
                    errors.append(f"Connection references invalid input: {connection.to_input_id}")
        
        return errors
    
    def compile_strategy(self, strategy_id: str) -> CompilationResult:
        """Compile a strategy from blocks and connections."""
        start_time = datetime.now(timezone.utc)
        
        result = CompilationResult(
            result_id=str(uuid4()),
            strategy_id=strategy_id,
            status=CompilationStatus.COMPILING,
        )
        
        # Validate blocks
        errors = self.validate_blocks()
        if errors:
            for error in errors:
                result.add_error(error)
            result.status = CompilationStatus.FAILED
            result.compilation_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
            self.results.append(result)
            return result
        
        # Generate bytecode
        bytecode = StrategyBytecode(
            bytecode_id=str(uuid4()),
        )
        
        # Add constants from block parameters
        for block_id, block in self.blocks.items():
            for key, value in block.parameters.items():
                bytecode.add_constant(f"{block_id}_{key}", value)
        
        # Generate instructions from blocks (simplified)
        # In a real implementation, this would traverse the block graph and generate actual bytecode
        for block_id, block in self.blocks.items():
            bytecode.add_instruction(
                opcode="LOAD_BLOCK",
                operands={"block_id": block_id, "block_type": block.block_type.value},
            )
            
            # Load inputs
            for input in block.inputs:
                bytecode.add_instruction(
                    opcode="LOAD_INPUT",
                    operands={"input_id": input.input_id, "input_type": input.input_type},
                )
            
            # Load outputs
            for output in block.outputs:
                bytecode.add_instruction(
                    opcode="LOAD_OUTPUT",
                    operands={"output_id": output.output_id, "output_type": output.output_type},
                )
        
        # Generate instructions from connections
        for connection in self.connections:
            bytecode.add_instruction(
                opcode="CONNECT",
                operands={
                    "from_block": connection.from_block_id,
                    "from_output": connection.from_output_id,
                    "to_block": connection.to_block_id,
                    "to_input": connection.to_input_id,
                },
            )
        
        compiled_strategy = CompiledStrategy(
            compiled_id=str(uuid4()),
            strategy_id=strategy_id,
            bytecode=bytecode,
            compilation_timestamp=datetime.now(timezone.utc),
        )
        
        result.status = CompilationStatus.SUCCESS
        result.compiled_strategy = compiled_strategy
        result.compilation_time_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        self.results.append(result)
        
        return result
    
    @property
    def block_count(self) -> int:
        """Get the number of blocks."""
        return len(self.blocks)
    
    @property
    def connection_count(self) -> int:
        """Get the number of connections."""
        return len(self.connections)
    
    @property
    def result_count(self) -> int:
        """Get the number of compilation results."""
        return len(self.results)


def create_strategy_compiler(name: str) -> StrategyCompiler:
    """Create a new strategy compiler."""
    return StrategyCompiler(
        compiler_id=str(uuid4()),
        name=name,
    )


def create_strategy_bytecode() -> StrategyBytecode:
    """Create a new strategy bytecode."""
    return StrategyBytecode(
        bytecode_id=str(uuid4()),
    )
