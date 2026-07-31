"""
GLX FORGE Strategy Blocks (Cerebus)

This module defines the Cerebus building blocks for the GLX FORGE trading infrastructure.
Cerebus blocks are the fundamental building blocks for constructing trading strategies.

Version: 0.1.0
Phase: Phase 6 - Strategy Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Any, Callable
from uuid import UUID, uuid4


class BlockType(Enum):
    """Block type enumeration."""
    DATA_SOURCE = "data_source"
    INDICATOR = "indicator"
    SIGNAL = "signal"
    FILTER = "filter"
    RISK = "risk"
    POSITION = "position"
    EXECUTION = "execution"
    OUTPUT = "output"
    LOGIC = "logic"
    CUSTOM = "custom"


@dataclass
class BlockInput:
    """Block input contract."""
    input_id: str
    input_name: str
    input_type: str  # "price", "volume", "indicator", "signal", etc.
    required: bool = True
    default_value: Optional[Any] = None
    description: str = ""
    
    def __post_init__(self):
        if not isinstance(self.input_id, str) or not self.input_id:
            self.input_id = str(uuid4())
        if not isinstance(self.input_name, str) or not self.input_name:
            raise ValueError("Input name cannot be empty")
        if not isinstance(self.input_type, str) or not self.input_type:
            raise ValueError("Input type cannot be empty")


@dataclass
class BlockOutput:
    """Block output contract."""
    output_id: str
    output_name: str
    output_type: str  # "price", "volume", "indicator", "signal", etc.
    description: str = ""
    
    def __post_init__(self):
        if not isinstance(self.output_id, str) or not self.output_id:
            self.output_id = str(uuid4())
        if not isinstance(self.output_name, str) or not self.output_name:
            raise ValueError("Output name cannot be empty")
        if not isinstance(self.output_type, str) or not self.output_type:
            raise ValueError("Output type cannot be empty")


@dataclass
class BlockConnection:
    """Block connection contract."""
    connection_id: str
    from_block_id: str
    from_output_id: str
    to_block_id: str
    to_input_id: str
    
    def __post_init__(self):
        if not isinstance(self.connection_id, str) or not self.connection_id:
            self.connection_id = str(uuid4())
        if not isinstance(self.from_block_id, str) or not self.from_block_id:
            raise ValueError("From block ID cannot be empty")
        if not isinstance(self.from_output_id, str) or not self.from_output_id:
            raise ValueError("From output ID cannot be empty")
        if not isinstance(self.to_block_id, str) or not self.to_block_id:
            raise ValueError("To block ID cannot be empty")
        if not isinstance(self.to_input_id, str) or not self.to_input_id:
            raise ValueError("To input ID cannot be empty")


@dataclass
class StrategyBlock:
    """Strategy block contract."""
    block_id: str
    name: str
    block_type: BlockType
    inputs: List[BlockInput] = field(default_factory=list)
    outputs: List[BlockOutput] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    logic: Optional[str] = None  # Logic description or code
    position: Dict[str, float] = field(default_factory=dict)  # x, y coordinates for UI
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.block_id, str) or not self.block_id:
            self.block_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.block_type, BlockType):
            raise ValueError("Block type must be BlockType enum")
    
    def add_input(self, input: BlockInput) -> None:
        """Add an input to the block."""
        self.inputs.append(input)
    
    def add_output(self, output: BlockOutput) -> None:
        """Add an output to the block."""
        self.outputs.append(output)
    
    def get_input(self, input_name: str) -> Optional[BlockInput]:
        """Get an input by name."""
        for input in self.inputs:
            if input.input_name == input_name:
                return input
        return None
    
    def get_output(self, output_name: str) -> Optional[BlockOutput]:
        """Get an output by name."""
        for output in self.outputs:
            if output.output_name == output_name:
                return output
        return None
    
    def set_parameter(self, key: str, value: Any) -> None:
        """Set a parameter value."""
        self.parameters[key] = value
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get a parameter value."""
        return self.parameters.get(key, default)
    
    @property
    def input_count(self) -> int:
        """Get the number of inputs."""
        return len(self.inputs)
    
    @property
    def output_count(self) -> int:
        """Get the number of outputs."""
        return len(self.outputs)


# Default Cerebus blocks for common strategy components
DEFAULT_BLOCKS = {
    "data_source": StrategyBlock(
        block_id="block-data-source",
        name="Data Source",
        block_type=BlockType.DATA_SOURCE,
        inputs=[],
        outputs=[
            BlockOutput(
                output_id="output-price",
                output_name="price",
                output_type="price",
                description="Market price data",
            ),
            BlockOutput(
                output_id="output-volume",
                output_name="volume",
                output_type="volume",
                description="Market volume data",
            ),
        ],
        parameters={
            "instrument_id": "BTCUSDT",
            "data_type": "tick",
        },
        logic="Fetch market data from data provider",
        position={"x": 0.0, "y": 0.0},
    ),
    
    "sma": StrategyBlock(
        block_id="block-sma",
        name="Simple Moving Average",
        block_type=BlockType.INDICATOR,
        inputs=[
            BlockInput(
                input_id="input-price",
                input_name="price",
                input_type="price",
                required=True,
                description="Price data for SMA calculation",
            ),
        ],
        outputs=[
            BlockOutput(
                output_id="output-sma",
                output_name="sma",
                output_type="indicator",
                description="Simple Moving Average value",
            ),
        ],
        parameters={
            "period": 20,
        },
        logic="Calculate Simple Moving Average over specified period",
        position={"x": 200.0, "y": 0.0},
    ),
    
    "ema": StrategyBlock(
        block_id="block-ema",
        name="Exponential Moving Average",
        block_type=BlockType.INDICATOR,
        inputs=[
            BlockInput(
                input_id="input-price",
                input_name="price",
                input_type="price",
                required=True,
                description="Price data for EMA calculation",
            ),
        ],
        outputs=[
            BlockOutput(
                output_id="output-ema",
                output_name="ema",
                output_type="indicator",
                description="Exponential Moving Average value",
            ),
        ],
        parameters={
            "period": 20,
            "smoothing": 2.0,
        },
        logic="Calculate Exponential Moving Average over specified period",
        position={"x": 200.0, "y": 100.0},
    ),
    
    "rsi": StrategyBlock(
        block_id="block-rsi",
        name="Relative Strength Index",
        block_type=BlockType.INDICATOR,
        inputs=[
            BlockInput(
                input_id="input-price",
                input_name="price",
                input_type="price",
                required=True,
                description="Price data for RSI calculation",
            ),
        ],
        outputs=[
            BlockOutput(
                output_id="output-rsi",
                output_name="rsi",
                output_type="indicator",
                description="RSI value (0-100)",
            ),
        ],
        parameters={
            "period": 14,
        },
        logic="Calculate Relative Strength Index over specified period",
        position={"x": 200.0, "y": 200.0},
    ),
    
    "signal": StrategyBlock(
        block_id="block-signal",
        name="Signal Generator",
        block_type=BlockType.SIGNAL,
        inputs=[
            BlockInput(
                input_id="input-indicator",
                input_name="indicator",
                input_type="indicator",
                required=True,
                description="Indicator value for signal generation",
            ),
        ],
        outputs=[
            BlockOutput(
                output_id="output-signal",
                output_name="signal",
                output_type="signal",
                description="Trading signal (long/short/close)",
            ),
            BlockOutput(
                output_id="output-strength",
                output_name="strength",
                output_type="float",
                description="Signal strength (0-1)",
            ),
        ],
        parameters={
            "threshold": 0.5,
            "direction": "long",
        },
        logic="Generate trading signal based on indicator threshold",
        position={"x": 400.0, "y": 0.0},
    ),
    
    "filter": StrategyBlock(
        block_id="block-filter",
        name="Signal Filter",
        block_type=BlockType.FILTER,
        inputs=[
            BlockInput(
                input_id="input-signal",
                input_name="signal",
                input_type="signal",
                required=True,
                description="Trading signal to filter",
            ),
            BlockInput(
                input_id="input-strength",
                input_name="strength",
                input_type="float",
                required=False,
                description="Signal strength for filtering",
            ),
        ],
        outputs=[
            BlockOutput(
                output_id="output-filtered",
                output_name="filtered",
                output_type="signal",
                description="Filtered trading signal",
            ),
        ],
        parameters={
            "min_strength": 0.7,
            "max_signals": 1,
        },
        logic="Filter signals based on strength and other criteria",
        position={"x": 400.0, "y": 100.0},
    ),
    
    "risk": StrategyBlock(
        block_id="block-risk",
        name="Risk Manager",
        block_type=BlockType.RISK,
        inputs=[
            BlockInput(
                input_id="input-signal",
                input_name="signal",
                input_type="signal",
                required=True,
                description="Trading signal to evaluate",
            ),
        ],
        outputs=[
            BlockOutput(
                output_id="output-approved",
                output_name="approved",
                output_type="signal",
                description="Risk-approved trading signal",
            ),
        ],
        parameters={
            "max_position_size": 1.0,
            "stop_loss_pct": 0.05,
            "take_profit_pct": 0.10,
        },
        logic="Evaluate signal against risk limits",
        position={"x": 600.0, "y": 0.0},
    ),
    
    "position": StrategyBlock(
        block_id="block-position",
        name="Position Manager",
        block_type=BlockType.POSITION,
        inputs=[
            BlockInput(
                input_id="input-signal",
                input_name="signal",
                input_type="signal",
                required=True,
                description="Trading signal to execute",
            ),
        ],
        outputs=[
            BlockOutput(
                output_id="output-order",
                output_name="order",
                output_type="order",
                description="Order to execute",
            ),
        ],
        parameters={
            "max_positions": 10,
            "position_sizing": "fixed",
        },
        logic="Manage position sizing and execution",
        position={"x": 600.0, "y": 100.0},
    ),
    
    "execution": StrategyBlock(
        block_id="block-execution",
        name="Execution",
        block_type=BlockType.EXECUTION,
        inputs=[
            BlockInput(
                input_id="input-order",
                input_name="order",
                input_type="order",
                required=True,
                description="Order to execute",
            ),
        ],
        outputs=[
            BlockOutput(
                output_id="output-fill",
                output_name="fill",
                output_type="fill",
                description="Order fill confirmation",
            ),
        ],
        parameters={
            "order_type": "market",
            "time_in_force": "ioc",
        },
        logic="Execute order on exchange",
        position={"x": 800.0, "y": 0.0},
    ),
}


def create_strategy_block(
    name: str,
    block_type: BlockType,
    inputs: Optional[List[BlockInput]] = None,
    outputs: Optional[List[BlockOutput]] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> StrategyBlock:
    """Create a new strategy block."""
    return StrategyBlock(
        block_id=str(uuid4()),
        name=name,
        block_type=block_type,
        inputs=inputs or [],
        outputs=outputs or [],
        parameters=parameters or {},
    )


def create_block_input(
    input_name: str,
    input_type: str,
    required: bool = True,
    default_value: Optional[Any] = None,
) -> BlockInput:
    """Create a new block input."""
    return BlockInput(
        input_id=str(uuid4()),
        input_name=input_name,
        input_type=input_type,
        required=required,
        default_value=default_value,
    )


def create_block_output(
    output_name: str,
    output_type: str,
) -> BlockOutput:
    """Create a new block output."""
    return BlockOutput(
        output_id=str(uuid4()),
        output_name=output_name,
        output_type=output_type,
    )


def create_block_connection(
    from_block_id: str,
    from_output_id: str,
    to_block_id: str,
    to_input_id: str,
) -> BlockConnection:
    """Create a new block connection."""
    return BlockConnection(
        connection_id=str(uuid4()),
        from_block_id=from_block_id,
        from_output_id=from_output_id,
        to_block_id=to_block_id,
        to_input_id=to_input_id,
    )
