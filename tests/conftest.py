import os
import shutil

import pytest
from httpx import ASGITransport, AsyncClient

from gnosis_api.admin import create_key
from gnosis_api.config import settings


@pytest.fixture(autouse=True)
def _setup_test_db(tmp_path):
    src = os.path.join(os.path.dirname(__file__), "..", "data", "gnosis.db")
    if not os.path.exists(src):
        pytest.skip("gnosis.db not found in data/")

    test_gnosis = tmp_path / "gnosis.db"
    shutil.copy2(src, test_gnosis)
    settings.gnosis_db_path = test_gnosis

    test_keys = tmp_path / "keys.db"
    settings.keys_db_path = test_keys


@pytest.fixture
def api_key(_setup_test_db):
    return create_key("test@example.com", "free")


@pytest.fixture
async def client(_setup_test_db):
    from gnosis_api.db import close_db, init_db

    await init_db()
    try:
        from gnosis_api.main import app

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as c:
            yield c
    finally:
        await close_db()
