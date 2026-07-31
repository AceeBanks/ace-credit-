"""
GLX FORGE Integration Tests

Comprehensive integration tests for the GLX FORGE trading infrastructure.
Tests verify core functionality across all 11 phases.

Version: 0.1.0
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

# Phase 1: Forge Constitution
from forge.domain.types import Price, Quantity, Timestamp, Money, Percentage
from forge.domain.contracts import AssetClass, InstrumentType, Side, OrderType, Currency, Exchange, Asset, Instrument
from forge.domain.schemas import Quote, Tick, Bar, Order, Trade, Position
from forge.events.trading import OrderSubmitted, OrderFilled, PositionOpened
from forge.governance.authority import AuthorityLevel, Permission, Authority
from forge.governance.roles import RoleType, Role
from forge.gates.validation import GateStatus, Gate, GateCondition

# Phase 2: Runtime Foundry
from forge.runtime.service import ServiceType, ServiceStatus, ServiceConfig, Service
from forge.runtime.topology import ServiceNode, ServiceEdge, ServiceTopology
from forge.runtime.control_plane import ControlCommandType, ControlPlane
from forge.runtime.worker import WorkerType, WorkerStatus, Worker, WorkerPool

# Phase 3: Data Forge
from forge.data.contracts import DataType, DataQuality, DataSchema, DataRecord
from forge.data.provider import ProviderType, ProviderStatus, DataProvider
from forge.data.gateway import SubscriptionStatus, DataGateway
from forge.data.market_lake import PartitionType, MarketReferenceLake

# Phase 4: Intelligence Forge
from forge.intelligence.contracts import IntelligenceType, IntelligenceSignal, SignalStrength
from forge.intelligence.observers import ObserverType, ObserverState, Observer
from forge.intelligence.causal import CausalRelationship, CausalNode, CausalGraph

# Phase 5: Discovery Forge
from forge.discovery.contracts import DiscoveryType, DiscoveryResult
from forge.discovery.scanner import ScannerType, ScannerState, Scanner
from forge.discovery.ranking import RankingMethod, RankingEngine

# Phase 6: Strategy Forge
from forge.strategy.contracts import StrategyType, StrategyStatus, StrategyConfig, StrategySignal
from forge.strategy.blocks import BlockType, StrategyBlock
from forge.strategy.compiler import CompilationStatus, StrategyCompiler

# Phase 7: Validation Forge
from forge.validation.contracts import ValidationType, ValidationStatus, ValidationCriteria
from forge.validation.engines import EngineType, ValidationEngine
from forge.validation.robustness import QualificationLevel, RobustnessQualification

# Phase 8: Simulation Forge
from forge.simulation.deployment import DeploymentStatus, DeploymentManager
from forge.simulation.health import HealthStatus, HealthMonitor
from forge.simulation.paper_trading import TradeStatus, PaperTradingEngine
from forge.simulation.shadow_trading import ShadowMode, ShadowTradingEngine

# Phase 9: Execution Forge
from forge.execution.contracts import ExecutionType, ExecutionStatus, ExecutionOrder
from forge.execution.adapters import AdapterType, AdapterStatus, ExecutionAdapter
from forge.execution.lifecycle import LifecycleState, LifecycleManager

# Phase 10: Portfolio Forge
from forge.portfolio.contracts import PortfolioType, PortfolioStatus, PortfolioContract, Position
from forge.portfolio.capital import EnvelopeType, CapitalEnvelope, CapitalManager
from forge.portfolio.stress import StressLevel, StressControl

# Phase 11: Sovereign Operations
from forge.operations.contracts import OperationType, OperationStatus, OperationsContract
from forge.operations.command_center import CommandType, CommandStatus, CommandCenter
from forge.operations.incidents import IncidentSeverity, IncidentStatus, IncidentManager


class TestPhase1DomainLanguage:
    """Test Phase 1: Domain Language"""
    
    def test_price_validation(self):
        """Test Price type validation"""
        price = Price(100.0)
        assert price == 100.0
        assert isinstance(price, float)
    
    def test_quantity_validation(self):
        """Test Quantity type validation"""
        quantity = Quantity(10.0)
        assert quantity == 10.0
        assert isinstance(quantity, float)
    
    def test_money_operations(self):
        """Test Money dataclass operations"""
        money = Money(amount=1000.0, currency="USD")
        assert money.amount == 1000.0
        assert money.currency == "USD"
    
    def test_asset_creation(self):
        """Test Asset creation"""
        asset = Asset(
            asset_class=AssetClass.CRYPTO,
            symbol="BTC",
            name="Bitcoin"
        )
        assert asset.asset_class == AssetClass.CRYPTO
        assert asset.symbol == "BTC"


class TestPhase1EventContracts:
    """Test Phase 1: Event Contracts"""
    
    def test_order_submitted_event(self):
        """Test OrderSubmitted event"""
        event = OrderSubmitted(
            event_id=str(uuid4()),
            order_id=str(uuid4()),
            order_type="market",
            exchange="binance",
            instrument_id="BTCUSDT",
            side="buy",
            quantity=1.0,
            price=50000.0,
            timestamp=datetime.now(timezone.utc)
        )
        assert event.side == "buy"
        assert event.quantity == 1.0
    
    def test_order_filled_event(self):
        """Test OrderFilled event"""
        event = OrderFilled(
            event_id=str(uuid4()),
            order_id=str(uuid4()),
            trade_id=str(uuid4()),
            side="buy",
            exchange="binance",
            instrument_id="BTCUSDT",
            filled_quantity=1.0,
            fill_price=50000.0,
            timestamp=datetime.now(timezone.utc)
        )
        assert event.filled_quantity == 1.0


class TestPhase1Governance:
    """Test Phase 1: Governance"""
    
    def test_authority_levels(self):
        """Test AuthorityLevel enum"""
        assert AuthorityLevel.ADMIN.value == "admin"
        assert AuthorityLevel.READ.value == "read"
    
    def test_role_creation(self):
        """Test Role creation"""
        role = Role(
            role_id=str(uuid4()),
            role_type=RoleType.ADMIN,
            name="Administrator"
        )
        assert role.role_type == RoleType.ADMIN


class TestPhase1GateValidation:
    """Test Phase 1: Gate Validation"""
    
    def test_gate_status(self):
        """Test GateStatus enum"""
        assert GateStatus.PASSED.value == "passed"
        assert GateStatus.FAILED.value == "failed"
    
    def test_gate_creation(self):
        """Test Gate creation"""
        gate = Gate(
            gate_id=str(uuid4()),
            gate_name="Phase 1 Gate",
            phase="phase-1"
        )
        assert gate.phase == "phase-1"


class TestPhase2RuntimeFoundry:
    """Test Phase 2: Runtime Foundry"""
    
    def test_service_creation(self):
        """Test Service creation"""
        service = Service(
            service_id=str(uuid4()),
            name="Test Service",
            service_type=ServiceType.DATA_PROVIDER
        )
        assert service.service_type == ServiceType.DATA_PROVIDER
    
    def test_worker_pool(self):
        """Test WorkerPool creation"""
        pool = WorkerPool(
            pool_id=str(uuid4()),
            name="Test Pool",
            worker_type=WorkerType.BACKTEST
        )
        assert pool.worker_type == WorkerType.BACKTEST
        assert pool.worker_count == 0


class TestPhase3DataForge:
    """Test Phase 3: Data Forge"""
    
    def test_data_record_creation(self):
        """Test DataRecord creation"""
        record = DataRecord(
            record_id=str(uuid4()),
            schema_id=str(uuid4()),
            data={"price": 50000.0, "volume": 100.0},
            timestamp=datetime.now(timezone.utc),
            quality=DataQuality.HIGH
        )
        assert record.is_high_quality
    
    def test_data_provider(self):
        """Test DataProvider creation"""
        from forge.data.provider import ProviderConfig
        provider = DataProvider(
            provider_id=str(uuid4()),
            name="Test Provider",
            provider_type=ProviderType.EXCHANGE,
            config=ProviderConfig(
                provider_id=str(uuid4()),
                provider_type=ProviderType.EXCHANGE
            ),
            status=ProviderStatus.STOPPED
        )
        assert provider.provider_type == ProviderType.EXCHANGE


class TestPhase4IntelligenceForge:
    """Test Phase 4: Intelligence Forge"""
    
    def test_intelligence_signal(self):
        """Test IntelligenceSignal creation"""
        from forge.intelligence.contracts import IntelligenceSource
        signal = IntelligenceSignal(
            signal_id=str(uuid4()),
            intelligence_type=IntelligenceType.SIGNAL,
            source=IntelligenceSource.OBSERVER,
            instrument_id="BTCUSDT",
            strength=SignalStrength.STRONG,
            confidence="high",
            direction="long",
            timestamp=datetime.now(timezone.utc),
            value=0.8
        )
        assert signal.is_long
        assert signal.is_strong
    
    def test_observer_creation(self):
        """Test Observer creation"""
        from forge.intelligence.observers import ObserverConfig
        observer = Observer(
            observer_id=str(uuid4()),
            name="Test Observer",
            observer_type=ObserverType.MOMENTUM,
            config=ObserverConfig(
                observer_id=str(uuid4()),
                observer_type=ObserverType.MOMENTUM
            ),
            state=ObserverState.STOPPED
        )
        assert observer.is_stopped


class TestPhase5DiscoveryForge:
    """Test Phase 5: Discovery Forge"""
    
    def test_discovery_result(self):
        """Test DiscoveryResult creation"""
        from forge.discovery.contracts import DiscoverySource
        result = DiscoveryResult(
            result_id=str(uuid4()),
            discovery_type=DiscoveryType.OPPORTUNITY,
            source=DiscoverySource.SCANNER,
            instrument_id="BTCUSDT",
            status="discovered",
            confidence=0.8,
            value=0.1,
            timestamp=datetime.now(timezone.utc)
        )
        assert result.is_discovered
        assert result.is_high_confidence
    
    def test_ranking_engine(self):
        """Test RankingEngine creation"""
        engine = RankingEngine(
            engine_id=str(uuid4()),
            name="Test Engine",
            ranking_method=RankingMethod.SCORE
        )
        assert engine.ranking_method == RankingMethod.SCORE


class TestPhase6StrategyForge:
    """Test Phase 6: Strategy Forge"""
    
    def test_strategy_config(self):
        """Test StrategyConfig creation"""
        from forge.strategy.contracts import StrategyParameters
        config = StrategyConfig(
            strategy_id=str(uuid4()),
            name="Test Strategy",
            strategy_type=StrategyType.MOMENTUM,
            instrument_ids=["BTCUSDT"],
            parameters=StrategyParameters()
        )
        assert config.strategy_type == StrategyType.MOMENTUM
    
    def test_strategy_block(self):
        """Test StrategyBlock creation"""
        block = StrategyBlock(
            block_id=str(uuid4()),
            name="Test Block",
            block_type=BlockType.INDICATOR
        )
        assert block.block_type == BlockType.INDICATOR
    
    def test_strategy_compiler(self):
        """Test StrategyCompiler creation"""
        compiler = StrategyCompiler(
            compiler_id=str(uuid4()),
            name="Test Compiler"
        )
        assert compiler.block_count == 0


class TestPhase7ValidationForge:
    """Test Phase 7: Validation Forge"""
    
    def test_validation_criteria(self):
        """Test ValidationCriteria creation"""
        criteria = ValidationCriteria(
            criteria_id=str(uuid4()),
            name="Test Criteria",
            description="Test validation",
            threshold=0.7,
            operator=">="
        )
        assert criteria.evaluate(0.8) == True
        assert criteria.evaluate(0.6) == False
    
    def test_validation_engine(self):
        """Test ValidationEngine creation"""
        from forge.validation.engines import EngineConfig
        engine = ValidationEngine(
            engine_id=str(uuid4()),
            name="Test Engine",
            engine_type=EngineType.BACKTEST,
            config=EngineConfig(
                engine_id=str(uuid4()),
                engine_type=EngineType.BACKTEST
            )
        )
        assert engine.test_count == 0
    
    def test_robustness_qualification(self):
        """Test RobustnessQualification creation"""
        qualification = RobustnessQualification(
            qualification_id=str(uuid4()),
            target_id=str(uuid4()),
            level=QualificationLevel.GOLD,
            metrics=None
        )
        assert qualification.is_qualified


class TestPhase8SimulationForge:
    """Test Phase 8: Simulation Forge"""
    
    def test_deployment_manager(self):
        """Test DeploymentManager creation"""
        manager = DeploymentManager(
            manager_id=str(uuid4()),
            name="Test Manager"
        )
        assert manager.deployment_count == 0
    
    def test_health_monitor(self):
        """Test HealthMonitor creation"""
        monitor = HealthMonitor(
            monitor_id=str(uuid4()),
            name="Test Monitor"
        )
        assert monitor.metric_count == 0
    
    def test_paper_trading_engine(self):
        """Test PaperTradingEngine creation"""
        from forge.simulation.paper_trading import PaperTradeConfig, PaperPortfolio
        engine = PaperTradingEngine(
            engine_id=str(uuid4()),
            name="Test Engine",
            config=PaperTradeConfig(
                config_id=str(uuid4()),
                initial_capital=100000.0
            ),
            portfolio=PaperPortfolio(
                portfolio_id=str(uuid4()),
                cash=100000.0
            )
        )
        assert engine.trade_count == 0


class TestPhase9ExecutionForge:
    """Test Phase 9: Execution Forge"""
    
    def test_execution_order(self):
        """Test ExecutionOrder creation"""
        order = ExecutionOrder(
            order_id=str(uuid4()),
            instrument_id="BTCUSDT",
            side="buy",
            quantity=1.0,
            price=50000.0
        )
        assert order.side == "buy"
        assert not order.is_filled
    
    def test_execution_adapter(self):
        """Test ExecutionAdapter creation"""
        from forge.execution.adapters import AdapterConfig
        adapter = ExecutionAdapter(
            adapter_id=str(uuid4()),
            name="Test Adapter",
            adapter_type=AdapterType.BINANCE,
            config=AdapterConfig(
                adapter_id=str(uuid4()),
                adapter_type=AdapterType.BINANCE
            ),
            status=AdapterStatus.DISCONNECTED
        )
        assert adapter.adapter_type == AdapterType.BINANCE
    
    def test_lifecycle_manager(self):
        """Test LifecycleManager creation"""
        manager = LifecycleManager(
            manager_id=str(uuid4()),
            name="Test Manager"
        )
        assert manager.lifecycle_count == 0


class TestPhase10PortfolioForge:
    """Test Phase 10: Portfolio Forge"""
    
    def test_portfolio_contract(self):
        """Test PortfolioContract creation"""
        from forge.portfolio.contracts import PortfolioConfig
        portfolio = PortfolioContract(
            contract_id=str(uuid4()),
            contract_name="Test Portfolio",
            portfolio_type=PortfolioType.SINGLE_STRATEGY,
            config=PortfolioConfig(
                config_id=str(uuid4()),
                portfolio_type=PortfolioType.SINGLE_STRATEGY
            ),
            status=PortfolioStatus.ACTIVE
        )
        assert portfolio.portfolio_type == PortfolioType.SINGLE_STRATEGY
        assert portfolio.is_active
    
    def test_capital_envelope(self):
        """Test CapitalEnvelope creation"""
        envelope = CapitalEnvelope(
            envelope_id=str(uuid4()),
            name="Test Envelope",
            envelope_type=EnvelopeType.STRATEGY,
            total_capital=100000.0
        )
        assert envelope.total_capital == 100000.0
        assert envelope.utilization_pct == 0.0
    
    def test_stress_control(self):
        """Test StressControl creation"""
        control = StressControl(
            control_id=str(uuid4()),
            name="Test Control",
            portfolio_id=str(uuid4())
        )
        assert control.is_enabled


class TestPhase11SovereignOperations:
    """Test Phase 11: Sovereign Operations"""
    
    def test_operations_contract(self):
        """Test OperationsContract creation"""
        from forge.operations.contracts import OperationConfig
        contract = OperationsContract(
            contract_id=str(uuid4()),
            contract_name="Test Operation",
            operation_type=OperationType.DEPLOYMENT,
            config=OperationConfig(
                config_id=str(uuid4()),
                operation_type=OperationType.DEPLOYMENT
            ),
            status=OperationStatus.PENDING
        )
        assert contract.operation_type == OperationType.DEPLOYMENT
        assert not contract.is_running
    
    def test_command_center(self):
        """Test CommandCenter creation"""
        center = CommandCenter(
            center_id=str(uuid4()),
            name="Test Center"
        )
        assert center.command_count == 0
    
    def test_incident_manager(self):
        """Test IncidentManager creation"""
        manager = IncidentManager(
            manager_id=str(uuid4()),
            name="Test Manager"
        )
        assert manager.incident_count == 0


class TestCrossPhaseIntegration:
    """Test cross-phase integration"""
    
    def test_strategy_to_execution_flow(self):
        """Test strategy signal to execution order flow"""
        # Create strategy signal
        signal = StrategySignal(
            signal_id=str(uuid4()),
            strategy_id=str(uuid4()),
            instrument_id="BTCUSDT",
            direction="buy",
            strength=0.8,
            confidence=0.9,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Create execution order from signal
        order = ExecutionOrder(
            order_id=str(uuid4()),
            instrument_id=signal.instrument_id,
            side=signal.direction,
            quantity=1.0,
            price=50000.0
        )
        
        assert order.side == signal.direction
        assert order.instrument_id == signal.instrument_id
    
    def test_portfolio_position_tracking(self):
        """Test portfolio position tracking"""
        from forge.portfolio.contracts import PortfolioConfig
        portfolio = PortfolioContract(
            contract_id=str(uuid4()),
            contract_name="Test Portfolio",
            portfolio_type=PortfolioType.SINGLE_STRATEGY,
            config=PortfolioConfig(
                config_id=str(uuid4()),
                portfolio_type=PortfolioType.SINGLE_STRATEGY
            ),
            status=PortfolioStatus.ACTIVE,
            cash=100000.0
        )
        
        position = Position(
            position_id=str(uuid4()),
            instrument_id="BTCUSDT",
            side="long",
            quantity=1.0,
            avg_entry_price=50000.0
        )
        
        portfolio.add_position(position)
        
        assert portfolio.position_count == 1
        assert portfolio.total_value == 100000.0  # Cash only initially


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
