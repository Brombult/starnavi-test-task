import pytest


def test_auth(client, test_db):
    data = {"email": "user@example.com", "password": "password12345"}
    r = client.post("/auth/register", json=data)
    print(r.text)
