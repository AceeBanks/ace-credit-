"""
GLX FORGE Basic Integration Tests

Basic tests to verify GLX FORGE modules can be imported and instantiated.
Tests focus on core functionality without complex API validation.

Version: 0.1.0
"""

import pytest


class TestPhase1DomainLanguage:
    """Test Phase 1: Domain Language"""
    
    def test_imports(self):
        """Test domain language imports"""
        from forge.domain.types import Price, Quantity, Timestamp, Money
        from forge.domain.contracts import AssetClass, InstrumentType, Side, OrderType
        assert Price(100.0) == 100.0
        assert Quantity(10.0) == 10.0


class TestPhase1EventContracts:
    """Test Phase 1: Event Contracts"""
    
    def test_imports(self):
        """Test event contract imports"""
        from forge.events.trading import OrderSubmitted, OrderFilled, PositionOpened
        from forge.events.market import TickReceived, QuoteUpdated
        assert OrderSubmitted is not None
        assert OrderFilled is not None


class TestPhase1Governance:
    """Test Phase 1: Governance"""
    
    def test_imports(self):
        """Test governance imports"""
        from forge.governance.authority import AuthorityLevel, Permission, Authority
        from forge.governance.roles import RoleType, Role
        assert AuthorityLevel.ADMIN.value == "admin"
        assert AuthorityLevel.READ.value == "read"


class TestPhase1GateValidation:
    """Test Phase 1: Gate Validation"""
    
    def test_imports(self):
        """Test gate validation imports"""
        from forge.gates.validation import GateStatus, Gate, GateCondition
        assert GateStatus.PASSED.value == "passed"
        assert GateStatus.FAILED.value == "failed"


class TestPhase2RuntimeFoundry:
    """Test Phase 2: Runtime Foundry"""
    
    def test_imports(self):
        """Test runtime foundry imports"""
        from forge.runtime.service import ServiceType, ServiceStatus, Service
        from forge.runtime.topology import ServiceNode, ServiceTopology
        from forge.runtime.control_plane import ControlPlane
        from forge.runtime.worker import WorkerType, WorkerStatus, WorkerPool
        assert ServiceType.DATA_PROVIDER.value == "data_provider"
        assert WorkerType.BACKTEST.value == "backtest"


class TestPhase3DataForge:
    """Test Phase 3: Data Forge"""
    
    def test_imports(self):
        """Test data forge imports"""
        from forge.data.contracts import DataType, DataQuality, DataSchema
        from forge.data.provider import ProviderType, ProviderStatus, DataProvider
        from forge.data.gateway import DataGateway
        from forge.data.market_lake import MarketReferenceLake
        assert DataType.TICK.value == "tick"
        assert ProviderType.EXCHANGE.value == "exchange"


class TestPhase4IntelligenceForge:
    """Test Phase 4: Intelligence Forge"""
    
    def test_imports(self):
        """Test intelligence forge imports"""
        from forge.intelligence.contracts import IntelligenceType, IntelligenceSignal
        from forge.intelligence.observers import ObserverType, ObserverState, Observer
        from forge.intelligence.causal import CausalRelationship, CausalGraph
        assert IntelligenceType.SIGNAL.value == "signal"
        assert ObserverType.MOMENTUM.value == "momentum"


class TestPhase5DiscoveryForge:
    """Test Phase 5: Discovery Forge"""
    
    def test_imports(self):
        """Test discovery forge imports"""
        from forge.discovery.contracts import DiscoveryType, DiscoveryResult
        from forge.discovery.scanner import ScannerType, ScannerState, Scanner
        from forge.discovery.ranking import RankingMethod, RankingEngine
        assert DiscoveryType.OPPORTUNITY.value == "opportunity"
        assert RankingMethod.SCORE.value == "score"


class TestPhase6StrategyForge:
    """Test Phase 6: Strategy Forge"""
    
    def test_imports(self):
        """Test strategy forge imports"""
        from forge.strategy.contracts import StrategyType, StrategyStatus, StrategyConfig
        from forge.strategy.blocks import BlockType, StrategyBlock
        from forge.strategy.compiler import CompilationStatus, StrategyCompiler
        assert StrategyType.MOMENTUM.value == "momentum"
        assert BlockType.INDICATOR.value == "indicator"


class TestPhase7ValidationForge:
    """Test Phase 7: Validation Forge"""
    
    def test_imports(self):
        """Test validation forge imports"""
        from forge.validation.contracts import ValidationType, ValidationStatus, ValidationCriteria
        from forge.validation.engines import EngineType, ValidationEngine
        from forge.validation.robustness import QualificationLevel, RobustnessQualification
        assert ValidationType.STRATEGY.value == "strategy"
        assert EngineType.BACKTEST.value == "backtest"
        assert QualificationLevel.GOLD.value == "gold"


class TestPhase8SimulationForge:
    """Test Phase 8: Simulation Forge"""
    
    def test_imports(self):
        """Test simulation forge imports"""
        from forge.simulation.deployment import DeploymentStatus, DeploymentManager
        from forge.simulation.health import HealthStatus, HealthMonitor
        from forge.simulation.paper_trading import TradeStatus, PaperTradingEngine
        from forge.simulation.shadow_trading import ShadowMode, ShadowTradingEngine
        assert DeploymentStatus.DEPLOYED.value == "deployed"
        assert HealthStatus.HEALTHY.value == "healthy"


class TestPhase9ExecutionForge:
    """Test Phase 9: Execution Forge"""
    
    def test_imports(self):
        """Test execution forge imports"""
        from forge.execution.contracts import ExecutionType, ExecutionStatus, ExecutionOrder
        from forge.execution.adapters import AdapterType, AdapterStatus, ExecutionAdapter
        from forge.execution.lifecycle import LifecycleState, LifecycleManager
        assert ExecutionType.MARKET.value == "market"
        assert AdapterType.BINANCE.value == "binance"


class TestPhase10PortfolioForge:
    """Test Phase 10: Portfolio Forge"""
    
    def test_imports(self):
        """Test portfolio forge imports"""
        from forge.portfolio.contracts import PortfolioType, PortfolioStatus, PortfolioContract
        from forge.portfolio.capital import EnvelopeType, CapitalEnvelope, CapitalManager
        from forge.portfolio.stress import StressLevel, StressControl
        assert PortfolioType.SINGLE_STRATEGY.value == "single_strategy"
        assert EnvelopeType.STRATEGY.value == "strategy"


class TestPhase11SovereignOperations:
    """Test Phase 11: Sovereign Operations"""
    
    def test_imports(self):
        """Test operations imports"""
        from forge.operations.contracts import OperationType, OperationStatus, OperationsContract
        from forge.operations.command_center import CommandType, CommandStatus, CommandCenter
        from forge.operations.incidents import IncidentSeverity, IncidentStatus, IncidentManager
        assert OperationType.DEPLOYMENT.value == "deployment"
        assert CommandType.DEPLOY.value == "deploy"
        assert IncidentSeverity.CRITICAL.value == "critical"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
