"""
PyTest Configuration and Fixtures

Shared fixtures and configuration for all tests.
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_env():
    """Setup test environment variables"""
    # Ensure test environment is configured
    os.environ["ENVIRONMENT"] = "test"
    yield
    # Cleanup
    os.environ.pop("ENVIRONMENT", None)


@pytest.fixture
def sample_maintenance_request():
    """Sample maintenance request for testing"""
    return {
        "type": "maintenance_request",
        "location": "Zone-A",
        "user_request": "Schedule pipeline inspection",
        "activity": "inspection",
        "priority": "medium"
    }


@pytest.fixture
def sample_emergency_request():
    """Sample emergency request for testing"""
    return {
        "type": "emergency_response",
        "location": "Zone-B",
        "user_request": "Critical water leak",
        "severity": "critical",
        "incident_type": "major_leak"
    }


@pytest.fixture
def sample_shift_request():
    """Sample shift request for testing"""
    return {
        "type": "schedule_shift_request",
        "location": "Zone-C",
        "user_request": "Delay work by 2 days",
        "requested_shift_days": 2,
        "reason": "Weather conditions"
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    from unittest.mock import Mock
    
    response = Mock()
    response.choices = [Mock(message=Mock(
        content='{"intent": "coordinate_maintenance", "risk_level": "low"}'
    ))]
    return response


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "llm: marks tests that require LLM"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Add unit marker to tests in test_unit_nodes.py
        if "test_unit_nodes" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests in test_integration_workflow.py
        if "test_integration_workflow" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add llm marker to tests in test_llm_robustness.py
        if "test_llm_robustness" in str(item.fspath):
            item.add_marker(pytest.mark.llm)
        
        # Add slow marker to loop and concurrent tests
        if "test_loop_detection" in str(item.fspath) or "concurrent" in item.name.lower():
            item.add_marker(pytest.mark.slow)
