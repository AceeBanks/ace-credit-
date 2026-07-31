"""
GLX FORGE Data Contracts

This module defines the data contracts for the GLX FORGE trading infrastructure.
Data contracts define the structure and quality of data flowing through the system.

Version: 0.1.0
Phase: Phase 3 - Data Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4


class DataType(Enum):
    """Data type enumeration."""
    TICK = "tick"
    QUOTE = "quote"
    BAR = "bar"
    ORDER_BOOK = "order_book"
    TRADE = "trade"
    FUNDAMENTAL = "fundamental"
    REFERENCE = "reference"
    SIGNAL = "signal"
    METADATA = "metadata"


class DataQuality(Enum):
    """Data quality enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class FieldDefinition:
    """Field definition contract."""
    field_name: str
    field_type: str
    required: bool = True
    description: str = ""
    constraints: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.field_name, str) or not self.field_name:
            raise ValueError("Field name cannot be empty")
        if not isinstance(self.field_type, str) or not self.field_type:
            raise ValueError("Field type cannot be empty")


@dataclass
class DataSchema:
    """Data schema contract."""
    schema_id: str
    schema_name: str
    data_type: DataType
    version: str = "1.0.0"
    fields: List[FieldDefinition] = field(default_factory=list)
    description: str = ""
    
    def __post_init__(self):
        if not isinstance(self.schema_id, str) or not self.schema_id:
            self.schema_id = str(uuid4())
        if not isinstance(self.schema_name, str) or not self.schema_name:
            raise ValueError("Schema name cannot be empty")
        if not isinstance(self.data_type, DataType):
            raise ValueError("Data type must be DataType enum")
    
    def add_field(self, field: FieldDefinition) -> None:
        """Add a field to the schema."""
        self.fields.append(field)
    
    def get_field(self, field_name: str) -> Optional[FieldDefinition]:
        """Get a field by name."""
        for field in self.fields:
            if field.field_name == field_name:
                return field
        return None
    
    def validate_record(self, record: Dict) -> bool:
        """Validate a record against this schema."""
        for field in self.fields:
            if field.required and field.field_name not in record:
                return False
        return True


@dataclass
class DataRecord:
    """Data record contract."""
    record_id: str
    schema_id: str
    data: Dict
    timestamp: datetime
    quality: DataQuality = DataQuality.UNKNOWN
    source: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.record_id, str) or not self.record_id:
            self.record_id = str(uuid4())
        if not isinstance(self.schema_id, str) or not self.schema_id:
            raise ValueError("Schema ID cannot be empty")
        if not isinstance(self.data, dict):
            raise ValueError("Data must be a dictionary")
        if not isinstance(self.quality, DataQuality):
            raise ValueError("Quality must be DataQuality enum")
    
    @property
    def is_high_quality(self) -> bool:
        """Check if record is high quality."""
        return self.quality == DataQuality.HIGH
    
    @property
    def is_low_quality(self) -> bool:
        """Check if record is low quality."""
        return self.quality == DataQuality.LOW


@dataclass
class DataContract:
    """Data contract contract."""
    contract_id: str
    contract_name: str
    data_type: DataType
    schema: DataSchema
    quality_requirement: DataQuality
    retention_policy: str = "30d"
    access_policy: str = "read_write"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.contract_id, str) or not self.contract_id:
            self.contract_id = str(uuid4())
        if not isinstance(self.contract_name, str) or not self.contract_name:
            raise ValueError("Contract name cannot be empty")
        if not isinstance(self.data_type, DataType):
            raise ValueError("Data type must be DataType enum")
        if not isinstance(self.schema, DataSchema):
            raise ValueError("Schema must be a DataSchema instance")
        if not isinstance(self.quality_requirement, DataQuality):
            raise ValueError("Quality requirement must be DataQuality enum")
    
    def validate_record(self, record: DataRecord) -> bool:
        """Validate a record against this contract."""
        if record.schema_id != self.schema.schema_id:
            return False
        
        if record.quality != DataQuality.UNKNOWN and record.quality != self.quality_requirement:
            return False
        
        return self.schema.validate_record(record.data)


# Default data schemas for common data types
DEFAULT_SCHEMAS = {
    "tick": DataSchema(
        schema_id="schema-tick",
        schema_name="Tick Data Schema",
        data_type=DataType.TICK,
        fields=[
            FieldDefinition(field_name="instrument_id", field_type="string", required=True),
            FieldDefinition(field_name="timestamp", field_type="datetime", required=True),
            FieldDefinition(field_name="price", field_type="float", required=True),
            FieldDefinition(field_name="size", field_type="float", required=True),
            FieldDefinition(field_name="side", field_type="string", required=True),
        ],
        description="Schema for individual trade ticks",
    ),
    
    "quote": DataSchema(
        schema_id="schema-quote",
        schema_name="Quote Data Schema",
        data_type=DataType.QUOTE,
        fields=[
            FieldDefinition(field_name="instrument_id", field_type="string", required=True),
            FieldDefinition(field_name="timestamp", field_type="datetime", required=True),
            FieldDefinition(field_name="bid_price", field_type="float", required=True),
            FieldDefinition(field_name="ask_price", field_type="float", required=True),
            FieldDefinition(field_name="bid_size", field_type="float", required=True),
            FieldDefinition(field_name="ask_size", field_type="float", required=True),
        ],
        description="Schema for market quotes",
    ),
    
    "bar": DataSchema(
        schema_id="schema-bar",
        schema_name="Bar Data Schema",
        data_type=DataType.BAR,
        fields=[
            FieldDefinition(field_name="instrument_id", field_type="string", required=True),
            FieldDefinition(field_name="timestamp", field_type="datetime", required=True),
            FieldDefinition(field_name="open", field_type="float", required=True),
            FieldDefinition(field_name="high", field_type="float", required=True),
            FieldDefinition(field_name="low", field_type="float", required=True),
            FieldDefinition(field_name="close", field_type="float", required=True),
            FieldDefinition(field_name="volume", field_type="float", required=True),
        ],
        description="Schema for OHLCV bars",
    ),
    
    "order_book": DataSchema(
        schema_id="schema-order-book",
        schema_name="Order Book Schema",
        data_type=DataType.ORDER_BOOK,
        fields=[
            FieldDefinition(field_name="instrument_id", field_type="string", required=True),
            FieldDefinition(field_name="timestamp", field_type="datetime", required=True),
            FieldDefinition(field_name="bids", field_type="list", required=True),
            FieldDefinition(field_name="asks", field_type="list", required=True),
        ],
        description="Schema for order book snapshots",
    ),
}


def create_data_contract(
    contract_name: str,
    data_type: DataType,
    schema: DataSchema,
    quality_requirement: DataQuality = DataQuality.HIGH,
) -> DataContract:
    """Create a new data contract."""
    return DataContract(
        contract_id=str(uuid4()),
        contract_name=contract_name,
        data_type=data_type,
        schema=schema,
        quality_requirement=quality_requirement,
    )


def create_data_record(
    schema_id: str,
    data: Dict,
    timestamp: datetime,
    quality: DataQuality = DataQuality.UNKNOWN,
    source: str = "",
) -> DataRecord:
    """Create a new data record."""
    return DataRecord(
        record_id=str(uuid4()),
        schema_id=schema_id,
        data=data,
        timestamp=timestamp,
        quality=quality,
        source=source,
    )
