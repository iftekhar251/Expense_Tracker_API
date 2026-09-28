import os
import sys
import pytest
from fastapi.testclient import TestClient
from main import app
from routers.auth import get_current_user

TEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'test_expense_tracker.db')
os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB_PATH}'

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))




def override_get_current_user():
   
    return {'username': 'testuser', 'id': 1}


app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture(scope='session')
def client():
    test_client = TestClient(app)
    yield test_client
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass
