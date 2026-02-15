"""Pytest configuration and fixtures."""

import sys
from pathlib import Path
import pytest
from copy import deepcopy

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    initial_state = deepcopy(activities)
    yield
    # Restore original state
    activities.clear()
    activities.update(initial_state)
