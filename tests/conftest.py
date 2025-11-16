"""Test configuration and fixtures."""
from unittest.mock import MagicMock

# Mock the prometheus_client for tests
import sys
from types import ModuleType

# Create a mock module
mock_prometheus = ModuleType('prometheus_client')
mock_prometheus.Counter = MagicMock()
mock_prometheus.Histogram = MagicMock()
mock_prometheus.generate_latest = MagicMock(return_value=b'')
mock_prometheus.CONTENT_TYPE_LATEST = 'text/plain'

# Add to sys.modules
sys.modules['prometheus_client'] = mock_prometheus
