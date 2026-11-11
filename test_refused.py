import uuid


def new_user():
    return {"username": "lab-" + uuid.uuid4().hex[:12], "password": uuid.uuid4().hex}


# A duplicate username is refused with the specified error.
def test_duplicate_username(api):
    user = new_user()
    assert api.post("/api/users", json=user).status_code == 201
    res = api.post("/api/users", json=user)
    assert res.status_code == 400
    assert res.json() == {"error": "username already taken"}


# A wrong password cannot authenticate a newly created user.
def test_wrong_password(api):
    user = new_user()
    assert api.post("/api/users", json=user).status_code == 201
    res = api.post("/api/users/token/login", json={**user, "password": "Wrong-Pizza"})
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}


# An empty username is refused with the specified error.
def test_empty_username(api):
    res = api.post("/api/users", json={"username": "", "password": uuid.uuid4().hex})
    assert res.status_code == 400
    assert res.json() == {"error": "username field is empty"}
