import pytest

from app.services.index_manager import IndexManager, set_index_manager
from helpers import CountingEmbedder, FakeRepo, sample_catalogue


@pytest.fixture(autouse=True)
def reset_index_manager():
    """Make sure no test leaks a manager into another, or accidentally builds the real one."""
    set_index_manager(None)
    yield
    set_index_manager(None)


@pytest.fixture
def repo():
    return FakeRepo(sample_catalogue())


@pytest.fixture
def manager(repo):
    m = IndexManager(repo, CountingEmbedder(), index_dir=None, refresh_interval=0)
    m.refresh()
    return m


@pytest.fixture
def client(manager):
    from fastapi.testclient import TestClient
    from app.main import app

    set_index_manager(manager)
    return TestClient(app)
