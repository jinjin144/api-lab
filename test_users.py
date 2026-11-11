# A new user can log in and starts with no ratings.
def test_new_user_has_no_ratings(api, auth):
    res = api.get("/api/ratings", headers=auth)
    assert res.status_code == 200
    assert res.json() == {"ratings": []}
