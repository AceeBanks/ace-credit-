"""
GLX FORGE Market Reference Lake

This module defines the market reference lake for the GLX FORGE trading infrastructure.
The market lake stores and manages historical market data.

Version: 0.1.0
Phase: Phase 3 - Data Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4

from forge.data.contracts import DataType, DataRecord, DataSchema


class PartitionType(Enum):
    """Partition type enumeration."""
    DATE = "date"
    INSTRUMENT = "instrument"
    DATA_TYPE = "data_type"
    QUALITY = "quality"
    PROVIDER = "provider"


@dataclass
class DataPartition:
    """Data partition contract."""
    partition_id: str
    partition_type: PartitionType
    partition_key: str
    record_count: int = 0
    size_bytes: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.partition_id, str) or not self.partition_id:
            self.partition_id = str(uuid4())
        if not isinstance(self.partition_type, PartitionType):
            raise ValueError("Partition type must be PartitionType enum")
        if not isinstance(self.partition_key, str) or not self.partition_key:
            raise ValueError("Partition key cannot be empty")
    
    @property
    def is_empty(self) -> bool:
        """Check if partition is empty."""
        return self.record_count == 0
    
    def add_record(self, size_bytes: int = 0) -> None:
        """Add a record to the partition."""
        self.record_count += 1
        self.size_bytes += size_bytes
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class LakeConfig:
    """Lake configuration contract."""
    lake_id: str
    name: str
    storage_path: str
    max_size_bytes: int = 10 * 1024 * 1024 * 1024  # 10GB default
    retention_days: int = 365
    compression_enabled: bool = True
    indexing_enabled: bool = True
    partitioning_enabled: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.lake_id, str) or not self.lake_id:
            raise ValueError("Lake ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.storage_path, str) or not self.storage_path:
            raise ValueError("Storage path cannot be empty")
        if not isinstance(self.max_size_bytes, int) or self.max_size_bytes < 1:
            raise ValueError(f"Max size must be >= 1, got {self.max_size_bytes}")


@dataclass
class QueryRequest:
    """Query request contract."""
    query_id: str
    instrument_id: str
    data_type: DataType
    start_date: datetime
    end_date: datetime
    filters: Dict = field(default_factory=dict)
    limit: Optional[int] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.query_id, str) or not self.query_id:
            self.query_id = str(uuid4())
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
        if not isinstance(self.data_type, DataType):
            raise ValueError("Data type must be DataType enum")
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before end date")
    
    @property
    def date_range(self) -> timedelta:
        """Get the date range of the query."""
        return self.end_date - self.start_date


@dataclass
class QueryResult:
    """Query result contract."""
    query_id: str
    records: List[DataRecord]
    record_count: int
    execution_time_seconds: float
    queried_at: datetime
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.query_id, str) or not self.query_id:
            raise ValueError("Query ID cannot be empty")
        if not isinstance(self.records, list):
            raise ValueError("Records must be a list")
        self.record_count = len(self.records)
    
    @property
    def is_empty(self) -> bool:
        """Check if result is empty."""
        return self.record_count == 0
    
    @property
    def size_bytes(self) -> int:
        """Estimate size in bytes."""
        return sum(len(str(record.data)) for record in self.records)


@dataclass
class MarketReferenceLake:
    """Market reference lake contract."""
    lake_id: str
    name: str
    config: LakeConfig
    partitions: Dict[str, DataPartition] = field(default_factory=dict)
    schemas: Dict[str, DataSchema] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.lake_id, str) or not self.lake_id:
            raise ValueError("Lake ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.config, LakeConfig):
            raise ValueError("Config must be a LakeConfig instance")
    
    def add_schema(self, schema: DataSchema) -> None:
        """Add a schema to the lake."""
        self.schemas[schema.schema_id] = schema
        self.updated_at = datetime.now(timezone.utc)
    
    def get_schema(self, schema_id: str) -> Optional[DataSchema]:
        """Get a schema by ID."""
        return self.schemas.get(schema_id)
    
    def add_partition(self, partition: DataPartition) -> None:
        """Add a partition to the lake."""
        self.partitions[partition.partition_id] = partition
        self.updated_at = datetime.now(timezone.utc)
    
    def get_partition(self, partition_id: str) -> Optional[DataPartition]:
        """Get a partition by ID."""
        return self.partitions.get(partition_id)
    
    def get_partitions_by_type(self, partition_type: PartitionType) -> List[DataPartition]:
        """Get all partitions of a type."""
        return [
            partition for partition in self.partitions.values()
            if partition.partition_type == partition_type
        ]
    
    def get_partition_by_key(self, partition_type: PartitionType, partition_key: str) -> Optional[DataPartition]:
        """Get a partition by type and key."""
        for partition in self.partitions.values():
            if partition.partition_type == partition_type and partition.partition_key == partition_key:
                return partition
        return None
    
    def ingest_record(self, record: DataRecord) -> None:
        """Ingest a data record into the lake."""
        # Validate against schema
        schema = self.get_schema(record.schema_id)
        if schema is None:
            raise ValueError(f"Schema not found: {record.schema_id}")
        
        if not schema.validate_record(record.data):
            raise ValueError(f"Record validation failed for schema: {record.schema_id}")
        
        # Update partitions
        date_partition_key = record.timestamp.strftime("%Y-%m-%d")
        date_partition = self.get_partition_by_key(PartitionType.DATE, date_partition_key)
        size_bytes = len(str(record.data))
        
        if date_partition is None:
            date_partition = DataPartition(
                partition_id=str(uuid4()),
                partition_type=PartitionType.DATE,
                partition_key=date_partition_key,
            )
            self.add_partition(date_partition)
        
        date_partition.add_record(size_bytes)
        
        # Update instrument partition
        instrument_partition_key = record.data.get("instrument_id", "unknown")
        instrument_partition = self.get_partition_by_key(PartitionType.INSTRUMENT, instrument_partition_key)
        
        if instrument_partition is None:
            instrument_partition = DataPartition(
                partition_id=str(uuid4()),
                partition_type=PartitionType.INSTRUMENT,
                partition_key=instrument_partition_key,
            )
            self.add_partition(instrument_partition)
        
        instrument_partition.add_record(size_bytes)
        
        self.updated_at = datetime.now(timezone.utc)
    
    def query(self, request: QueryRequest) -> QueryResult:
        """Query the lake for data."""
        start_time = datetime.now(timezone.utc)
        
        # In a real implementation, this would query the actual storage
        # For now, return empty result
        records = []
        
        execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        return QueryResult(
            query_id=request.query_id,
            records=records,
            record_count=len(records),
            execution_time_seconds=execution_time,
            queried_at=datetime.now(timezone.utc),
        )
    
    @property
    def partition_count(self) -> int:
        """Get the number of partitions."""
        return len(self.partitions)
    
    @property
    def schema_count(self) -> int:
        """Get the number of schemas."""
        return len(self.schemas)
    
    @property
    def total_record_count(self) -> int:
        """Get the total record count across all partitions."""
        return sum(partition.record_count for partition in self.partitions.values())
    
    @property
    def total_size_bytes(self) -> int:
        """Get the total size in bytes across all partitions."""
        return sum(partition.size_bytes for partition in self.partitions.values())
    
    @property
    def storage_utilization(self) -> float:
        """Get storage utilization as a percentage."""
        if self.config.max_size_bytes == 0:
            return 0.0
        return (self.total_size_bytes / self.config.max_size_bytes) * 100.0


def create_lake(name: str, storage_path: str, config: Optional[LakeConfig] = None) -> MarketReferenceLake:
    """Create a new market reference lake."""
    if config is None:
        config = LakeConfig(
            lake_id=str(uuid4()),
            name=name,
            storage_path=storage_path,
        )
    
    return MarketReferenceLake(
        lake_id=config.lake_id,
        name=name,
        config=config,
    )


def create_query(
    instrument_id: str,
    data_type: DataType,
    start_date: datetime,
    end_date: datetime,
    filters: Optional[Dict] = None,
    limit: Optional[int] = None,
) -> QueryRequest:
    """Create a new query request."""
    return QueryRequest(
        query_id=str(uuid4()),
        instrument_id=instrument_id,
        data_type=data_type,
        start_date=start_date,
        end_date=end_date,
        filters=filters or {},
        limit=limit,
    )
