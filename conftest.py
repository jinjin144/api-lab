import uuid

import pytest
import requests

SITE = "https://quickpizza.grafana.com"


class QuickPizza(requests.Session):
    """Keep load-balancer cookies and use a bounded request timeout."""

    def request(self, method, url, *args, **kwargs):
        kwargs.setdefault("timeout", 30)
        return super().request(method, SITE + url, *args, **kwargs)


@pytest.fixture(scope="session")
def api():
    with QuickPizza() as session:
        yield session


def log_in_new_user(api):
    user = {"username": "lab-" + uuid.uuid4().hex[:12], "password": uuid.uuid4().hex}
    res = api.post("/api/users", json=user)
    assert res.status_code == 201, res.text
    res = api.post("/api/users/token/login", json=user)
    assert res.status_code == 200, res.text
    return {"Authorization": "token " + res.json()["token"]}


@pytest.fixture
def auth(api):
    return log_in_new_user(api)


@pytest.fixture
def other_auth(api):
    return log_in_new_user(api)


@pytest.fixture
def pizza_id(api, auth):
    res = api.post("/api/pizza", json={}, headers=auth)
    assert res.status_code == 200, res.text
    return res.json()["pizza"]["id"]


@pytest.fixture
def rating(api, auth, pizza_id):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 3}, headers=auth)
    assert res.status_code == 201, res.text
    made = res.json()
    yield made
    path = f"/api/ratings/{made['id']}"
    read = api.get(path, headers=auth)
    if read.status_code == 404:
        return
    assert read.status_code == 200, read.text
    assert api.delete(path, headers=auth).status_code == 204


@pytest.fixture
def saved_ratings(api, auth):
    """Clean up successful creates, including when an assertion fails."""
    ids = []
    yield ids
    for rating_id in ids:
        res = api.delete(f"/api/ratings/{rating_id}", headers=auth)
        assert res.status_code in (204, 404), res.text
