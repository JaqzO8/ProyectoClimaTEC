import os
import sys

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure app is in path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.api.v1.endpoints import _provider
from app.main import app


@pytest.fixture(autouse=True)
async def clear_cache():
    await _provider.cache.clear()
    yield
    await _provider.cache.clear()


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
