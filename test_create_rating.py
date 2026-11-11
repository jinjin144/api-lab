import pytest

STARS_ERROR = "number of stars must be between 1 and 5 (inclusive)"


# Base choice: whole-number 3 stars, an existing pizza and the owner's token.
def test_base_choice_is_saved(api, auth, pizza_id, saved_ratings):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 3}, headers=auth)
    if res.status_code == 201:
        saved_ratings.append(res.json()["id"])
    assert res.status_code == 201
    assert res.json()["stars"] == 3
    assert res.json()["pizza_id"] == pizza_id


# C1 changes only the star-value block while all other inputs stay at base.
@pytest.mark.parametrize("stars", [0, 6])
def test_stars_out_of_range(api, auth, pizza_id, stars):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": stars}, headers=auth)
    assert res.status_code == 400
    assert res.json() == {"error": STARS_ERROR}


# C2 varies only the representation/presence of stars, using curl-observed messages.
@pytest.mark.parametrize("stars,error", [
    (3.5, "json: cannot unmarshal number 3.5 into Go struct field Rating.stars of type int"),
    ("3", "json: cannot unmarshal string into Go struct field Rating.stars of type int"),
    (None, STARS_ERROR),
], ids=["decimal", "text", "missing"])
def test_stars_type_is_refused(api, auth, pizza_id, stars, error):
    body = {"pizza_id": pizza_id}
    if stars is not None:
        body["stars"] = stars
    res = api.post("/api/ratings", json=body, headers=auth)
    assert res.status_code == 400
    assert res.json() == {"error": error}


# C3 changes only whether the pizza exists.
def test_nonexistent_pizza_is_refused(api, auth, pizza_id):
    res = api.post("/api/ratings", json={"pizza_id": 999999999, "stars": 3}, headers=auth)
    assert res.status_code == 400
    assert res.json() == {"error": "pizza ID 999999999 not found"}


# C4 changes only the token to absent or the wrong length.
@pytest.mark.parametrize("headers", [{}, {"Authorization": "token short"}], ids=["none", "wrong-length"])
def test_invalid_token_is_refused(api, auth, pizza_id, headers):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 3}, headers=headers)
    assert res.status_code == 401
    assert res.json() == {"error": "authentication failed"}
