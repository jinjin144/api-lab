import pytest

STARS_ERROR = "number of stars must be between 1 and 5 (inclusive)"


# Boundary updates save 1/5 and refuse 0/6 without changing stored data.
@pytest.mark.parametrize("stars,expected_status", [(0, 400), (1, 200), (5, 200), (6, 400)])
def test_update_boundaries(api, auth, rating, stars, expected_status):
    path = f"/api/ratings/{rating['id']}"
    res = api.put(path, json={"stars": stars}, headers=auth)
    assert res.status_code == expected_status
    if expected_status == 400:
        assert res.json() == {"error": STARS_ERROR}
    else:
        assert res.json()["stars"] == stars
    read = api.get(path, headers=auth)
    assert read.status_code == 200
    assert read.json() == {**rating, "stars": stars if expected_status == 200 else rating["stars"]}
