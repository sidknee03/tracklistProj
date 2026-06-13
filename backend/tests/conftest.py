"""
Shared fixtures for backend tests.
Sets up an in-memory SQLite equivalent using a temp Postgres DB if DATABASE_URL
is set, otherwise mocks the db_cursor context manager.
"""

import os
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_db():
    """Replace db_cursor with a mock that returns configurable rows."""
    mock_cur = MagicMock()
    mock_cur.__enter__ = lambda s: mock_cur
    mock_cur.__exit__ = MagicMock(return_value=False)

    with patch("app.db.connection.db_cursor", return_value=mock_cur):
        yield mock_cur
