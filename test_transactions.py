from datetime import date

import pytest


@pytest.fixture
def sample_transaction(client):
    response = client.post(
        '/transactions',
        json={
            'title': 'Groceries',
            'amount': 45.50,
            'type': 'expense',
            'category': 'Food',
            'date': str(date.today()),
        },
    )
    return response.json()


def test_create_transaction(client):
    response = client.post(
        '/transactions',
        json={
            'title': 'Salary',
            'amount': 3000,
            'type': 'income',
            'category': 'Job',
            'date': str(date.today()),
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == 'Salary'
    assert data['owner_id'] == 1



def test_get_transactions(client, sample_transaction):
    response = client.get('/transactions')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_specific_transaction(client, sample_transaction):
    transaction_id = sample_transaction['id']
    response = client.get(f'/transactions/{transaction_id}')
    assert response.status_code == 200
    assert response.json()['id'] == transaction_id


def test_get_specific_transaction_not_found(client):
    response = client.get('/transactions/99999')
    assert response.status_code == 404


def test_update_transaction(client, sample_transaction):
    transaction_id = sample_transaction['id']
    response = client.put(
        f'/transactions/{transaction_id}',
        json={
            'title': 'Groceries Updated',
            'amount': 60.0,
            'type': 'expense',
            'category': 'Food',
            'date': str(date.today()),
        },
    )
    assert response.status_code == 200
    assert response.json()['title'] == 'Groceries Updated'
    assert response.json()['amount'] == 60.0


def test_delete_transaction(client, sample_transaction):
    transaction_id = sample_transaction['id']
    response = client.delete(f'/transactions/{transaction_id}')
    assert response.status_code == 200

    check = client.get(f'/transactions/{transaction_id}')
    assert check.status_code == 404


def test_filter_transactions(client):
    client.post(
        '/transactions',
        json={
            'title': 'Bus ticket',
            'amount': 5,
            'type': 'expense',
            'category': 'Transport',
            'date': str(date.today()),
        },
    )
    response = client.get('/transactions/filter?type=expense&category=Transport')
    assert response.status_code == 200
    data = response.json()
    assert all(t['type'] == 'expense' and t['category'] == 'Transport' for t in data)
