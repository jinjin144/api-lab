# A new rating comes back with an id, its stars and its pizza.
def test_create_rating(api, auth, pizza_id, saved_ratings):
    res = api.post("/api/ratings", json={"pizza_id": pizza_id, "stars": 5}, headers=auth)
    if res.status_code == 201:
        saved_ratings.append(res.json()["id"])
    assert res.status_code == 201
    body = res.json()
    assert body["stars"] == 5
    assert body["pizza_id"] == pizza_id
    assert isinstance(body["id"], int)


# A saved rating can be read back by its id.
def test_read_rating(api, auth, rating):
    res = api.get(f"/api/ratings/{rating['id']}", headers=auth)
    assert res.status_code == 200
    assert res.json() == rating


# Changing the stars of a rating returns the new number of stars.
def test_update_rating(api, auth, rating):
    res = api.put(f"/api/ratings/{rating['id']}", json={"stars": 4}, headers=auth)
    assert res.status_code == 200
    assert res.json()["stars"] == 4


# A deleted rating can no longer be read.
def test_delete_rating(api, auth, rating):
    path = f"/api/ratings/{rating['id']}"
    assert api.delete(path, headers=auth).status_code == 204
    assert api.get(path, headers=auth).status_code == 404
